
import os
import time
import re
import requests
import argparse
import logging
import sys
import multiprocessing as mp
from multiprocessing import Pool, Manager
import traceback
import asyncio
sys.path.append(os.path.join(os.path.dirname("..")))
from graph_utils.chatgpt.config.config import (
    GENERAL_CONFIG,
    OPENAI_CONFIG,
    ARXIV_CONFIG,
    NOUGAT_CONFIG,
    LOGGER_MODES,
    get_application_prompts,
)
from graph_utils.chatgpt.utils import init_logging
from graph_utils.graph_generate_bak import Knowledge_Graph
import json
import concurrent.futures
from tqdm import tqdm

def extract_tables_from_text(text, filename):
    """
    从文本中提取Markdown表格并保存到新文件
    
    Args:
        text (str): 包含表格的文本内容
        filename (str): 原文件名（不含扩展名）
    
    Returns:
        str: 保存的表格文件路径，如果没有找到表格则返回None
    """
    if not text or not filename:
        return None
    
    # 查找所有Markdown表格
    # 表格模式：以|开头的行，后面跟着分隔符行（包含-和|），然后是数据行
    table_pattern = r'(\|[^\n]*\|\s*\n\|[-\s|:]+\|\s*\n(?:\|[^\n]*\|\s*\n)*)'
    tables = re.findall(table_pattern, text, re.MULTILINE)
    
    if not tables:
        print(f"No tables found in {filename}")
        return None
    
    # 生成输出文件名
    output_filename = f"{filename}_tables.md"
    
    # 构建表格文档内容
    content = f"# 从 {filename} 中提取的表格\n\n"
    content += f"本文档包含从原文档中提取的所有表格数据。\n\n"
    content += f"提取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    content += "---\n\n"
    
    # 处理每个表格
    for i, table in enumerate(tables, 1):
        content += f"## 表格 {i}\n\n"
        
        # 清理表格格式
        table_lines = table.strip().split('\n')
        cleaned_table = []
        
        for line in table_lines:
            # 确保每行都是有效的表格行
            if line.strip() and line.strip().startswith('|') and line.strip().endswith('|'):
                cleaned_table.append(line.strip())
        
        if cleaned_table:
            content += '\n'.join(cleaned_table) + '\n\n'
            
            # 尝试提取表格标题（查找表格前的文本）
            table_start = text.find(table)
            if table_start > 0:
                # 查找表格前100个字符中的标题信息
                before_table = text[max(0, table_start-200):table_start]
                title_patterns = [
                    r'Table\s+\d+[:\.]?\s*([^\n]+)',
                    r'表\s*\d+[：:：]?\s*([^\n]+)',
                    r'####\s+([^\n]+)',
                    r'###\s+([^\n]+)',
                    r'##\s+([^\n]+)'
                ]
                
                for pattern in title_patterns:
                    match = re.search(pattern, before_table, re.IGNORECASE)
                    if match:
                        table_title = match.group(1).strip()
                        content += f"**说明**: {table_title}\n\n"
                        break
        
        content += "---\n\n"
    
    # 添加总结
    content += f"## 总结\n\n"
    content += f"本文档共提取了 {len(tables)} 个表格。\n"
    content += f"原始文档: {filename}\n"
    
    return content, output_filename

def save_extracted_tables(text, filename, save_path):
    """
    提取表格并保存到指定路径
    
    Args:
        text (str): 包含表格的文本内容
        filename (str): 原文件名（不含扩展名）
        save_path (str): 保存路径
    
    Returns:
        str: 保存的文件路径，如果没有表格则返回None
    """
    result = extract_tables_from_text(text, filename)
    if not result:
        return None
    
    content, output_filename = result
    
    # 确保保存目录存在
    os.makedirs(save_path, exist_ok=True)
    
    # 保存文件
    output_path = os.path.join(save_path, output_filename)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Tables extracted and saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error saving tables to {output_path}: {str(e)}")
        return None

def group_pdf_files_with_si(subfolder_path):
    """
    将PDF文件按主文件和补充材料分组
    返回: [(main_pdf, si_pdf_list), ...]
    适用于DSS命名模式：文件名以"-SI"或"-si"结尾为补充材料，其他为主文件
    使用标准化文件名处理特殊字符和大小写不一致问题
    """
    if not (os.path.exists(subfolder_path) and os.path.isdir(subfolder_path)):
        return []
    
    all_files = [f for f in os.listdir(subfolder_path) if f.endswith('.pdf')]
    
    def normalize_filename_for_matching(filename):
        """
        标准化文件名用于匹配，移除特殊字符和统一大小写
        """
        # 移除.pdf后缀和-SI后缀
        name = filename.replace('.pdf', '')
        name = re.sub(r'-[sS][iI]$', '', name)
        
        # 转换为小写
        name = name.lower()
        
        # 移除所有标点符号和特殊字符，只保留字母数字和空格
        name = re.sub(r'[^\w\s]', ' ', name)
        
        # 移除多余空格并统一为单个空格
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    # 分离主文件和SI文件
    main_files = {}  # {标准化名称: (原始文件名, 标准化名称)}
    si_files = {}    # {标准化名称: [(原始文件名, 标准化名称), ...]}
    
    for file in all_files:
        # 检查文件是否以-SI或-si结尾
        if re.search(r'-[sS][iI]\.pdf$', file):
            # 这是补充材料文件，标准化文件名用于匹配
            normalized_name = normalize_filename_for_matching(file)
            if normalized_name not in si_files:
                si_files[normalized_name] = []
            si_files[normalized_name].append((file, normalized_name))
        else:
            # 这是主文件，标准化文件名用于匹配
            normalized_name = normalize_filename_for_matching(file)
            main_files[normalized_name] = (file, normalized_name)
    
    # 组合主文件和对应的SI文件
    grouped_files = []
    processed_normalized_names = set()
    
    # 处理有主文件的情况
    for normalized_name, (main_file, _) in main_files.items():
        main_path = os.path.join(subfolder_path, main_file)
        si_paths = []
        
        if normalized_name in si_files:
            si_file_list = si_files[normalized_name]
            si_paths = [os.path.join(subfolder_path, si_file) for si_file, _ in si_file_list]
            # 按文件名排序，确保处理顺序一致
            si_paths.sort()
            
            # 打印匹配信息用于调试
            si_names = [si_file for si_file, _ in si_file_list]
            # print(f"匹配成功: {main_file} <-> {si_names}")
        else:
            # 只有主文件，没有对应的SI文件
            print(f"只有主文件: {main_file} (无对应SI文件)")
        
        grouped_files.append((main_path, si_paths))
        processed_normalized_names.add(normalized_name)
    
    # 处理只有SI文件没有主文件的情况
    for normalized_name, si_file_list in si_files.items():
        if normalized_name not in processed_normalized_names:
            # 找不到对应的主文件，将SI文件作为独立文件处理
            for si_file, _ in si_file_list:
                si_path = os.path.join(subfolder_path, si_file)
                grouped_files.append((si_path, []))
                # print(f"警告：未找到匹配主文件的SI文件: {si_file}")
    
    return grouped_files

def send_post_request(path):
    """发送 POST 请求处理PDF文件"""
    session = requests.Session()
    session.trust_env = False
    post_data = {
        'filepath': path,
    }
    try:
        response = session.post("http://127.0.0.1:2675/marker", data=json.dumps(post_data))
        response.raise_for_status()
        return response.json().get('output', '')
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error for path {path}: {str(e)}")

def process_pdf_group(main_pdf, si_pdfs):
    """
    处理一组PDF文件（主文件+补充材料）
    返回合并后的markdown文本
    """
    combined_text = ""
    
    # 处理主文件
    try:
        main_content = send_post_request(main_pdf)
        combined_text += main_content + "\n\n"
        print(f"Successfully processed main file: {main_pdf}")
    except Exception as e:
        print(f"Error processing main file {main_pdf}: {str(e)}")
        return ""
    
    # 处理补充材料文件
    for si_pdf in si_pdfs:
        try:
            si_content = send_post_request(si_pdf)
            combined_text += si_content + "\n\n"
            print(f"Successfully processed SI file: {si_pdf}")
        except Exception as e:
            print(f"Error processing SI file {si_pdf}: {str(e)}")
            continue
    
    return combined_text

def table_generate(template, table):
    head1=0
    head2=0
    head3=0
    head4=0
    for doc in template:
        for k, v in doc.metadata.items():
            if k == "Header 1" and (table == [] or "# "+v != table[head1]):
                table.append("# "+v)
                head1 = table.index("# "+v)
            elif k == "Header 2" and (table == [] or "## "+v != table[head2]):
                table.append("## "+v)
                head2 = table.index("## "+v)
            elif k == "Header 3" and (table == [] or "### "+v != table[head3]):
                table.append("### "+v)
                head3 = table.index("### "+v)
            elif k == "Header 4" and (table == [] or "#### "+v != table[head4]):
                table.append("#### "+v)
                head4 = table.index("#### "+v)
    return table

def position(doc):
    if 'Header 3' in doc.metadata:
        return doc.metadata['Header 3']
    elif 'Header 2' in doc.metadata:
        return doc.metadata['Header 2']
    elif 'Header 1' in doc.metadata:
        return doc.metadata['Header 1']
    elif 'Header 4' in doc.metadata:
        return doc.metadata['Header 4']
    else:
        return None
    
def position_count(doc):
    if 'Header 3' in doc.metadata:
        return doc.metadata['Header 3'], 3
    elif 'Header 2' in doc.metadata:
        return doc.metadata['Header 2'], 2
    elif 'Header 1' in doc.metadata:
        return doc.metadata['Header 1'], 1
    elif 'Header 4' in doc.metadata:
        return doc.metadata['Header 4'], 4
    else:
        return None

async def process_single_pdf_group(main_pdf, si_pdfs, result_path, type_name):
    """
    处理单个PDF组（主文件+补充材料），生成独立的markdown文件
    """
    # Initialize logging
    init_logging()
    logger = logging.getLogger(__name__)
    logger.setLevel(LOGGER_MODES)

    # 动态获取对应的APPLICATION_PROMPTS配置
    APPLICATION_PROMPTS = get_application_prompts(type_name)
    
    # Load configurations
    api_key = OPENAI_CONFIG['api_key']
    base_url = OPENAI_CONFIG['base_url']
    
    # Validate API key and base URL
    if not (api_key and base_url):
        raise ValueError("API key and base URL must be provided either via --api_key and --base_url or in the config file.")

    template_graph = Knowledge_Graph(filtered=False, type_name=type_name+"Template")
    # import pdb;pdb.set_trace()
    # 处理这一组PDF文件
    group_text = process_pdf_group(main_pdf, si_pdfs)
    
    if not group_text.strip():
        print(f"No valid PDF content found for {main_pdf}")
        return

    # 从主文件名生成标题和输出文件名
    main_filename = os.path.basename(main_pdf)
    output_filename = main_filename.replace('.pdf', '.md')
    
    # # 提取并保存表格（暂不提供保存表格功能）
    # filename_without_ext = main_filename.replace('.pdf', '')
    # table_save_path = os.path.join(result_path, type_name)
    # save_extracted_tables(group_text, filename_without_ext, table_save_path)
    
    knowledge_graph = Knowledge_Graph(markdown=group_text, type_name=type_name+"Framework", filtered=False)
    # import pdb;pdb.set_trace()
    if knowledge_graph.title == "None":
        knowledge_graph.title = main_filename.replace('.pdf', '')
    knowledge_graph.title = knowledge_graph.title.replace('"True"','')
    generate_graph = "False" in str(knowledge_graph.graph.query("""MATCH (d:Document)
    WHERE d.title = "{title}"
    RETURN COUNT(d) > 0 AS exists LIMIT 1""".replace("{title}",knowledge_graph.title)))

    if generate_graph:
        knowledge_graph.filter_content()
        
        logging.info("Converting Documents to Graph...")
        async def process_documents():
            documents = await knowledge_graph.llm_transformer.aconvert_to_graph_documents(knowledge_graph.splits)
            return documents
        
        # 直接await异步函数
        documents = await process_documents()
        logging.info("Converting Documents to Graph...Complete!")
        logging.info("Adding Documents to Graph...")
        knowledge_graph.graph.add_graph_documents(
            documents,
            baseEntityLabel=True,
            include_source=True
        )
        logging.info("Adding Documents to Graph...Complete!")
        logging.info("Graph generated!!!")
        knowledge_graph.graph.query("""CREATE FULLTEXT INDEX entity IF NOT EXISTS
    FOR (n:__Entity__)
    ON EACH [n.id];""")

    summary = knowledge_graph.reason_answer(APPLICATION_PROMPTS["decompose_prompts"]["ft_summary_generation_simplified"].replace("{title}", knowledge_graph.title))
    new_table = table_generate(template_graph.splits, table=[])

    leaf_section = []
    for doc in template_graph.splits:
        title, cnt = position_count(doc)
        title = cnt*"#" + " " + title
        leaf_section.append(title)

    # 处理章节生成（保持原有逻辑）
    section_results = []
    delay = 30
    max_retries = 3
    
    def process_qa_chunk(args):
        template_num, chunk_questions, chunk_start = args
        question_str = "\n".join(chunk_questions)
        
        for retry in range(max_retries):
            try:
                if template_num == 7:
                    result = knowledge_graph.reason_answer(f"Please provide detailed answers to the following questions, marking each answer with the corresponding question. Use the format 'Q: [Original Question], A: [Answer]'. Write out the original question but do not use numbered indexes.**you should note that all questions should clearly exclude the activation processes existing in the characterization techniques.**\n<question>"+question_str+"\n</question>")
                elif template_num in (len(template_graph.splits)-1, len(template_graph.splits)-2):
                    result = knowledge_graph.graph_answer(f"Please provide detailed answers to the following questions, marking each answer with the corresponding question. Use the format 'Q: [Original Question], A: [Answer]'. Write out the original question but do not use numbered indexes.\n<question>"+question_str+"\n</question>")
                else:
                    result = knowledge_graph.mini_answer(f"Please provide detailed answers to the following questions, marking each answer with the corresponding question. Use the format 'Q: [Original Question], A: [Answer]'. Write out the original question but do not use numbered indexes.\n<question>"+question_str+"\n</question>")
                
                if result is None or result.strip() == "":
                    print(f"\x1b[31mSection {template_num+1} QA Chunk {chunk_start//5+1} Error: Empty result returned\x1b[0m")
                    if retry < max_retries - 1:
                        time.sleep(delay)
                        continue
                    return (chunk_start, ["No answer could be generated for these questions."])
                
                return (chunk_start, result.split("\n"))
            except Exception as e:
                print(f"\x1b[31mSection {template_num+1} QA Chunk {chunk_start//5+1} Error ({retry+1}/{max_retries}):\x1b[0m", str(e))
                if retry < max_retries - 1:
                    time.sleep(delay)
        return (chunk_start, ["No answer could be generated for these questions."])

    def process_section(args):
        template_num, sec = args
        message = [
            {"role": "system", "content": APPLICATION_PROMPTS["decompose_prompts"]["system_prompt"]},
            {"role": "user", "content": APPLICATION_PROMPTS["decompose_prompts"]["decoompose_table_prompt"]
            .replace('{table}', "\n".join(new_table), 1)
            .replace('{describe}', sec.page_content, 1)
            .replace('{summary}', summary, 1)
            .replace('{example}', APPLICATION_PROMPTS["decompose_prompts"][str(template_num+1)], 1)}
            # .replace('{example}', APPLICATION_PROMPTS["decompose_prompts"][template_graph.example_dict[str(template_num+1)]], 1)}
        ]
        
        questions = None
        for retry in range(max_retries):
            try:
                response = knowledge_graph.reasonllm.invoke(message)
                questions = response.content.replace("```", "").replace("json", "")
                questions = json.loads(questions)
                decompose_questions = [questions[str(i+1)]['question'] for i in range(len(questions))]
                print(f"Section {template_num+1} Generate {len(questions)} Questions")
                break
            except Exception as e:
                print(f"\x1b[31mSection {template_num+1} Questions Generation Error ({retry+1}/{max_retries}):\x1b[0m", str(e))
                if retry < max_retries - 1:
                    time.sleep(delay)
        else:
            print(f"\x1b[31mSection {template_num+1} questions generation failed after {max_retries} retries\x1b[0m")
            return None
        
        # 问答处理部分并行化
        results = []
        chunk_args = []
        for chunk_start in range(0, len(decompose_questions), 5):
            chunk_questions = decompose_questions[chunk_start:chunk_start+5]
            chunk_args.append((template_num, chunk_questions, chunk_start))
        
        chunk_results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as qa_executor:
            qa_progress = tqdm(qa_executor.map(process_qa_chunk, chunk_args), 
                            total=len(chunk_args), 
                            desc=f"Processing section {template_num+1} QA", 
                            position=0, leave=False)
            
            for chunk_start, chunk_result in qa_progress:
                if chunk_result is not None:
                    chunk_results[chunk_start] = chunk_result
        
        for chunk_start in sorted(chunk_results.keys()):
            chunk_result = chunk_results[chunk_start]
            if chunk_result:
                results.extend(chunk_result)
        
        qa_pair = "\n".join([s for s in results if s.strip()])
        
        # 章节生成部分
        section_generation = [
            {"role": "system", "content": APPLICATION_PROMPTS["decompose_prompts"]["system_prompt"]},
            {"role": "user", "content": APPLICATION_PROMPTS["decompose_prompts"]["section_generation_just_from_table"]
            .replace('{position}', position(sec), 1)
            .replace('{qa}', qa_pair, 1)
            .replace('{summary}', summary, 1)
            .replace('{table}', "\n".join(new_table), 1)
            .replace('{describe}', leaf_section[template_num] + "\n" + sec.page_content, 1)
            .replace('{origin_title}', knowledge_graph.title, 1)}
        ]
        
        for retry in range(max_retries):
            try:
                if template_num in (len(template_graph.splits)-1, len(template_graph.splits)-2):
                    section_result = knowledge_graph.graphllm.invoke(section_generation).content
                else:
                    section_result = knowledge_graph.reasonllm.invoke(section_generation).content
                return section_result
            except Exception as e:
                print(f"\x1b[31mSection {template_num+1} Generation Error ({retry+1}/{max_retries}):\x1b[0m", str(e))
                if retry < max_retries - 1:
                    time.sleep(delay)
        return None

    # 并行处理部分
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        tasks = [(template_num, sec) for template_num, sec in enumerate(template_graph.splits)]
        progress_bar = tqdm(executor.map(process_section, tasks), 
                            total=len(tasks), 
                            desc=f"Processing {output_filename}", 
                            position=0, leave=True)
        
        for result in progress_bar:
            if result is not None:
                section_results.append(result)
            else:
                section_results.append("Section processing failed (all retries exhausted)")

    full_article=["# "+knowledge_graph.title]
    cnt=0
    for v in new_table[1:]:
        if any(re.match(f"{re.escape(section)}", v) for section in leaf_section):
            current=section_results[cnt]
            full_article.append(current.replace("```markdown","").replace("```",""))
            cnt+=1
        else:
            full_article.append(v.replace("```markdown","").replace("```",""))
    
    article_result = "\n\n".join(full_article)
    
    # 保存结果
    save_path = os.path.join(result_path, type_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    # 保存最终处理结果
    save_dir = os.path.join(save_path, output_filename)
    with open(save_dir, "w", encoding="utf-8") as f:
        f.write(article_result)
    
    # # 保存原始PDF转换的markdown内容（暂不提供保存原文档功能）
    # raw_output_filename = main_filename.replace('.pdf', '_raw.md')
    # raw_save_dir = os.path.join(save_path, raw_output_filename)
    # with open(raw_save_dir, "w", encoding="utf-8") as f:
    #     f.write(group_text)
    
    print(f"Results saved to: {save_dir}")
    # print(f"Raw PDF content saved to: {raw_save_dir}")

def process_pdf_group_wrapper(args):
    """
    多进程处理PDF组的包装函数
    args: (main_pdf, si_pdfs, result_path, type_name, process_id)
    """
    main_pdf, si_pdfs, result_path, type_name, process_id = args
    
    try:
        # 设置进程标识用于日志
        process_name = f"Process-{process_id}"
        main_filename = os.path.basename(main_pdf)
        output_filename = main_filename.replace('.pdf', '.md')
        
        print(f"[{process_name}] 开始处理: {main_filename}")
        
        # 检查输出文件是否已存在
        save_path = os.path.join(result_path, type_name)
        output_file = os.path.join(save_path, output_filename)
        
        if os.path.exists(output_file):
            print(f"[{process_name}] {output_filename} 已存在，跳过...")
            return {"status": "skipped", "file": main_filename, "process_id": process_id}
        
        # 调用原始处理函数
        asyncio.run(process_single_pdf_group(main_pdf, si_pdfs, result_path, type_name))
        
        print(f"[{process_name}] 成功处理: {output_filename}")
        return {"status": "success", "file": main_filename, "process_id": process_id}
        
    except Exception as e:
        error_msg = f"处理 {os.path.basename(main_pdf)} 时出错: {str(e)}"
        print(f"[Process-{process_id}] 错误: {error_msg}")
        print(f"[Process-{process_id}] 详细错误信息:")
        traceback.print_exc()
        return {"status": "error", "file": os.path.basename(main_pdf), "error": str(e), "process_id": process_id}

def process_pdfs_multiprocessing(pdf_groups, result_path, type_name, max_workers=None):
    """
    使用多进程处理PDF文件组
    
    Args:
        pdf_groups: PDF文件组列表 [(main_pdf, si_pdfs), ...]
        result_path: 结果保存路径
        type_name: 类型名称
        max_workers: 最大进程数，默认为CPU核心数
    
    Returns:
        dict: 处理结果统计
    """
    if max_workers is None:
        max_workers = min(mp.cpu_count(), len(pdf_groups))
    
    print(f"使用 {max_workers} 个进程并行处理 {len(pdf_groups)} 个PDF组...")
    
    # 准备参数列表
    args_list = []
    for i, (main_pdf, si_pdfs) in enumerate(pdf_groups):
        args_list.append((main_pdf, si_pdfs, result_path, type_name, i+1))
    
    # 创建输出目录
    save_path = os.path.join(result_path, type_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    results = {"success": 0, "error": 0, "skipped": 0, "details": []}
    
    try:
        # 使用多进程池处理
        with Pool(processes=max_workers) as pool:
            # 使用tqdm显示进度条
            with tqdm(total=len(args_list), desc="处理PDF文件", unit="文件") as pbar:
                # 使用imap_unordered获取结果并更新进度条
                for result in pool.imap_unordered(process_pdf_group_wrapper, args_list):
                    results["details"].append(result)
                    results[result["status"]] += 1
                    
                    # 更新进度条描述
                    pbar.set_postfix({
                        "成功": results["success"],
                        "错误": results["error"], 
                        "跳过": results["skipped"]
                    })
                    pbar.update(1)
    
    except KeyboardInterrupt:
        print("\n收到中断信号，正在停止进程...")
        pool.terminate()
        pool.join()
        raise
    except Exception as e:
        print(f"多进程处理过程中发生错误: {str(e)}")
        raise
    
    return results

if __name__ == "__main__":
    # Windows多进程支持
    try:
        mp.set_start_method('spawn')
    except RuntimeError:
        # 如果已经设置过start method，忽略错误
        pass
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='多进程处理PDF文件生成知识图谱')
    parser.add_argument('--workers', type=int, default=3, 
                       help='并行进程数 (默认: CPU核心数)')
    parser.add_argument('--type', type=str, default="DSS", 
                       help='处理类型 (默认: DSS)')
    parser.add_argument('--result-path', type=str, 
                    #    default="/mnt/d/work/ustc/yuancheng/ft_pack_3/papersavings/",
                        default="/home/lijie/lixiaohui/ft_pack_3/papersavings/",
                       help='结果保存路径')
    parser.add_argument('--base-folder', type=str,
                    #    default="/mnt/d/work/ustc/yuancheng/ft_pack_3/origin_paper/DSS",
                        default="/home/lijie/lixiaohui/ft_pack_3/origin_paper/DSS",
                       help='PDF文件源文件夹')
    parser.add_argument('--single-process', action='store_true',
                       help='使用单进程模式 (用于调试)')
    
    args = parser.parse_args()
    
    type_name = args.type
    result_path = args.result_path
    base_folder = args.base_folder
    
    # 直接处理DSS文件夹中的PDF文件
    if not os.path.exists(base_folder):
        print(f"Base folder {base_folder} does not exist!")
    else:
        print(f"Processing folder: {base_folder}...")
        
        # 获取并分组PDF文件
        pdf_groups = group_pdf_files_with_si(base_folder)
        
        if not pdf_groups:
            print(f"No PDF files found in {base_folder}")
        else:
            print(f"Found {len(pdf_groups)} PDF groups")
            
            # 打印分组结果预览用于调试
            print("\n=== 分组结果预览 ===")
            for i, (main_pdf, si_pdfs) in enumerate(pdf_groups[:10]):  # 打印前10个用于调试
                main_name = os.path.basename(main_pdf)
                si_names = [os.path.basename(si) for si in si_pdfs]
                print(f"Group {i+1}: {main_name}")
                if si_names:
                    for si_name in si_names:
                        print(f"    -> {si_name}")
                else:
                    print("    -> 无SI文件")
                print()
            
            # 根据参数选择处理模式
            if args.single_process:
                print(f"\n使用单进程模式处理...")
                start_time = time.time()
                
                # 创建输出目录
                save_path = os.path.join(result_path, type_name)
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                
                success_count = 0
                error_count = 0
                skip_count = 0
                
                for main_pdf, si_pdfs in tqdm(pdf_groups, desc="处理PDF文件", unit="文件"):
                    main_filename = os.path.basename(main_pdf)
                    output_filename = main_filename.replace('.pdf', '.md')
                    output_file = os.path.join(save_path, output_filename)
                    
                    if os.path.exists(output_file):
                        print(f"{output_filename} already exists, skipping...")
                        skip_count += 1
                        continue
                    
                    print(f"Processing: {main_filename} with {len(si_pdfs)} SI files...")
                    try:
                        asyncio.run(process_single_pdf_group(main_pdf, si_pdfs, result_path, type_name))
                        print(f"Successfully processed: {output_filename}")
                        success_count += 1
                    except Exception as e:
                        print(f"Error processing {main_filename}: {str(e)}")
                        error_count += 1
                        continue
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                print(f"\n=== 单进程处理完成 ===")
                print(f"总处理时间: {processing_time:.2f} 秒")
                print(f"成功处理: {success_count} 个文件")
                print(f"跳过文件: {skip_count} 个文件")
                print(f"处理失败: {error_count} 个文件")
                print(f"平均每个文件处理时间: {processing_time/len(pdf_groups):.2f} 秒")
                
            else:
                # 使用多进程处理PDF组
                print(f"\n开始多进程处理...")
                start_time = time.time()
                
                try:
                    # 使用命令行参数或环境变量控制进程数
                    max_workers = args.workers or int(os.environ.get('MAX_WORKERS', mp.cpu_count()))
                    results = process_pdfs_multiprocessing(pdf_groups, result_path, type_name, max_workers)
                    
                    end_time = time.time()
                    processing_time = end_time - start_time
                    
                    # 打印处理结果统计
                    print(f"\n=== 处理完成 ===")
                    print(f"总处理时间: {processing_time:.2f} 秒")
                    print(f"成功处理: {results['success']} 个文件")
                    print(f"跳过文件: {results['skipped']} 个文件")
                    print(f"处理失败: {results['error']} 个文件")
                    
                    if results['error'] > 0:
                        print(f"\n失败的文件:")
                        for detail in results['details']:
                            if detail['status'] == 'error':
                                print(f"  - {detail['file']}: {detail['error']}")
                    
                    print(f"\n平均每个文件处理时间: {processing_time/len(pdf_groups):.2f} 秒")
                    
                except KeyboardInterrupt:
                    print("\n用户中断处理过程")
                except Exception as e:
                    print(f"\n多进程处理失败: {str(e)}")
                    print("回退到单进程处理...")
                    
                    # 回退到原始的单进程处理方式
                    for main_pdf, si_pdfs in pdf_groups:
                        main_filename = os.path.basename(main_pdf)
                        output_filename = main_filename.replace('.pdf', '.md')
                        output_file = os.path.join(result_path, type_name, output_filename)
                        
                        if os.path.exists(output_file):
                            print(f"{output_filename} already exists, skipping...")
                            continue
                        
                        print(f"Processing: {main_filename} with {len(si_pdfs)} SI files...")
                        try:
                            asyncio.run(process_single_pdf_group(main_pdf, si_pdfs, result_path, type_name))
                            print(f"Successfully processed: {output_filename}")
                        except Exception as e:
                            print(f"Error processing {main_filename}: {str(e)}")
                            continue
# %%
import os
import time
import re
import requests
import argparse
import logging
import sys
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

def group_pdf_files_with_si(subfolder_path):
    """
    将PDF文件按主文件和补充材料分组
    返回: [(main_pdf, si_pdf_list), ...]
    适用于OWS命名模式：数字_si/SI为补充材料，纯数字开头为主文件
    """
    if not (os.path.exists(subfolder_path) and os.path.isdir(subfolder_path)):
        return []
    
    all_files = [f for f in os.listdir(subfolder_path) if f.endswith('.pdf')]
    # 分离主文件和SI文件
    main_files = {}  # {数字: 主文件名}
    si_files = {}    # {数字: [si文件列表]}
    
    for file in all_files:
        # 匹配以数字开头的文件
        match = re.match(r'^(\d+)(_[sS][iI](_\d+)?)?', file)
        if match:
            number = match.group(1)  # 提取数字部分
            si_part = match.group(2)  # _si或_SI部分
            
            if si_part:  # 这是补充材料文件
                if number not in si_files:
                    si_files[number] = []
                si_files[number].append(file)
            else:  # 这是主文件（只有数字开头，没有_si/_SI）
                main_files[number] = file
    
    # 组合主文件和对应的SI文件
    grouped_files = []
    
    # 处理有主文件的情况
    for number, main_file in main_files.items():
        main_path = os.path.join(subfolder_path, main_file)
        si_paths = []
        
        if number in si_files:
            si_paths = [os.path.join(subfolder_path, si_file) for si_file in si_files[number]]
            # 按文件名排序，确保处理顺序一致
            si_paths.sort()
        
        grouped_files.append((main_path, si_paths))
    
    # 处理只有SI文件没有主文件的情况
    for number, si_file_list in si_files.items():
        if number not in main_files:
            # 找不到对应的主文件，将SI文件作为独立文件处理
            for si_file in si_file_list:
                si_path = os.path.join(subfolder_path, si_file)
                grouped_files.append((si_path, []))
    
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

def process_single_pdf_group(main_pdf, si_pdfs, result_path, type_name):
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
    
    knowledge_graph = Knowledge_Graph(markdown=group_text, type_name=type_name+"Framework", filtered=False)
    if knowledge_graph.title == "None":
        knowledge_graph.title = main_filename.replace('.pdf', '')
    #import pdb;pdb.set_trace()
    generate_graph = "False" in str(knowledge_graph.graph.query("""MATCH (d:Document)
    WHERE d.title = "{title}"
    RETURN COUNT(d) > 0 AS exists LIMIT 1""".replace("{title}",knowledge_graph.title)))

    if generate_graph:
        knowledge_graph.filter_content()
        
        logging.info("Converting Documents to Graph...")
        async def process_documents():
            documents = await knowledge_graph.llm_transformer.aconvert_to_graph_documents(knowledge_graph.splits)
            return documents
        
        import asyncio
        documents = asyncio.run(process_documents())
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
    save_dir = os.path.join(save_path, output_filename)
    with open(save_dir, "w", encoding="utf-8") as f:
        f.write(article_result)
    
    print(f"Results saved to: {save_dir}")

if __name__ == "__main__":
    type_name = "OWS"  # 改为OWS
    result_path = "/home/user/shizhou/Agent/ft_pack/papersavings/"
    base_folder = "/home/user/shizhou/Agent/ft_pack/origin_paper/OWS"  # 改为OWS文件夹
    
    # 由于OWS文件夹直接包含PDF文件，不需要子文件夹处理
    # 直接处理OWS文件夹中的PDF文件
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
            
            # 创建输出目录
            save_path = os.path.join(result_path, type_name)
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            
            # 处理每个PDF组
            for main_pdf, si_pdfs in pdf_groups:
                main_filename = os.path.basename(main_pdf)
                output_filename = main_filename.replace('.pdf', '.md')
                output_file = os.path.join(save_path, output_filename)
                
                # 检查输出文件是否已存在
                if os.path.exists(output_file):
                    print(f"{output_filename} already exists, skipping...")
                    continue
                
                print(f"Processing: {main_filename} with {len(si_pdfs)} SI files...")
                try:
                    process_single_pdf_group(main_pdf, si_pdfs, result_path, type_name)
                    print(f"Successfully processed: {output_filename}")
                except Exception as e:
                    print(f"Error processing {main_filename}: {str(e)}")
                    continue
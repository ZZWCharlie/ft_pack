# %%
import os
import time
import re
import requests
import logging
import sys
import json
import concurrent.futures
from tqdm import tqdm
from functools import lru_cache
import asyncio
import aiohttp

sys.path.append(os.path.join(os.path.dirname("..")))
from graph_utils.chatgpt.config.config import (
    GENERAL_CONFIG,
    OPENAI_CONFIG,
    ARXIV_CONFIG,
    NOUGAT_CONFIG,
    LOGGER_MODES,
    APPLICATION_PROMPTS,
)
from graph_utils.chatgpt.utils import init_logging
from graph_utils.graph_generate_bak import Knowledge_Graph

# 优化后的PDF处理函数 - 异步批量处理
async def send_post_request_async(session, path):
    """异步PDF解析请求"""
    post_data = {'filepath': path}
    try:
        async with session.post("http://127.0.0.1:2675/marker", 
                               json=post_data,
                               timeout=aiohttp.ClientTimeout(total=300)) as response:
            response.raise_for_status()
            result = await response.json()
            return result.get('output', '')
    except Exception as e:
        logging.error(f"PDF解析失败 {path}: {str(e)}")
        return ""

async def process_pdfs_batch(paths):
    """批量异步处理PDF文件"""
    async with aiohttp.ClientSession() as session:
        tasks = [send_post_request_async(session, path) for path in paths if os.path.exists(path)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if isinstance(r, str)]

# 缓存装饰器用于避免重复计算
@lru_cache(maxsize=128)
def cached_table_generate(template_splits_hash, table_hash=None):
    """缓存版本的table生成函数"""
    # 这里需要重新实现table_generate逻辑，但使用缓存
    pass

def table_generate(template, table):
    """优化的table生成函数 - 减少重复计算"""
    head1 = head2 = head3 = head4 = 0
    for doc in template:
        for k, v in doc.metadata.items():
            if k == "Header 1" and (not table or "# "+v != (table[head1] if head1 < len(table) else None)):
                table.append("# "+v)
                head1 = len(table) - 1
            elif k == "Header 2" and (not table or "## "+v != (table[head2] if head2 < len(table) else None)):
                table.append("## "+v)
                head2 = len(table) - 1
            elif k == "Header 3" and (not table or "### "+v != (table[head3] if head3 < len(table) else None)):
                table.append("### "+v)
                head3 = len(table) - 1
            elif k == "Header 4" and (not table or "#### "+v != (table[head4] if head4 < len(table) else None)):
                table.append("#### "+v)
                head4 = len(table) - 1
    return table

def position(doc):
    """优化的position函数"""
    headers = ['Header 3', 'Header 2', 'Header 1', 'Header 4']
    for header in headers:
        if header in doc.metadata:
            return doc.metadata[header]
    return None
    
def position_count(doc):
    """优化的position_count函数"""
    headers = [('Header 3', 3), ('Header 2', 2), ('Header 1', 1), ('Header 4', 4)]
    for header, count in headers:
        if header in doc.metadata:
            return doc.metadata[header], count
    return None, 0

# 简化的问答处理函数
def process_qa_simplified(knowledge_graph, questions, template_num, total_templates):
    """简化的问答处理 - 减少重试和延迟"""
    if not questions:
        return ""
    
    question_str = "\n".join(questions)
    try:
        # 根据模板类型选择不同的处理方式
        if template_num == 7:  # 特殊处理活化相关问题
            prompt = f"请详细回答以下问题，每个答案前标注对应问题。格式：'Q: [原问题], A: [答案]'。注意排除表征技术中的活化过程：\n{question_str}"
            result = knowledge_graph.reason_answer(prompt)
        elif template_num in (total_templates-1, total_templates-2):  # 最后两个模板使用图谱查询
            prompt = f"请详细回答以下问题，每个答案前标注对应问题。格式：'Q: [原问题], A: [答案]'：\n{question_str}"
            result = knowledge_graph.graph_answer(prompt)
        else:  # 其他使用简化模型
            prompt = f"请详细回答以下问题，每个答案前标注对应问题。格式：'Q: [原问题], A: [答案]'：\n{question_str}"
            result = knowledge_graph.mini_answer(prompt)
        return result
    except Exception as e:
        logging.error(f"问答处理失败 Section {template_num+1}: {str(e)}")
        return ""

def process_section_optimized(args, knowledge_graph, new_table, summary, leaf_section):
    """优化的段落处理函数"""
    template_num, sec = args
    
    try:
        # 问题生成
        message = [
            {"role": "system", "content": APPLICATION_PROMPTS["decompose_prompts"]["system_prompt"]},
            {"role": "user", "content": APPLICATION_PROMPTS["decompose_prompts"]["decoompose_table_prompt"]
            .replace('{table}', "\n".join(new_table), 1)
            .replace('{describe}', sec.page_content, 1)
            .replace('{summary}', summary, 1)
            .replace('{example}', APPLICATION_PROMPTS["decompose_prompts"][knowledge_graph.template_example_dict[template_num]], 1)}
        ]
        
        response = knowledge_graph.reasonllm.invoke(message)
        questions_text = response.content.replace("```", "").replace("json", "")
        questions = json.loads(questions_text)
        decompose_questions = [questions[str(i+1)]['question'] for i in range(len(questions))]
        
        print(f"Section {template_num+1} 生成 {len(questions)} 个问题")
        
        # 简化的问答处理 - 批量处理而非分块
        qa_result = process_qa_simplified(knowledge_graph, decompose_questions, template_num, len(knowledge_graph.template_splits))
        
        # 生成最终段落
        section_generation = [
            {"role": "system", "content": APPLICATION_PROMPTS["decompose_prompts"]["system_prompt"]},
            {"role": "user", "content": APPLICATION_PROMPTS["decompose_prompts"]["section_generation_just_from_table"]
            .replace('{position}', position(sec), 1)
            .replace('{qa}', qa_result, 1)
            .replace('{summary}', summary, 1)
            .replace('{table}', "\n".join(new_table), 1)
            .replace('{describe}', leaf_section[template_num] + "\n" + sec.page_content, 1)
            .replace('{origin_title}', knowledge_graph.title, 1)}
        ]
        
        total_templates = len(knowledge_graph.template_splits)
        if template_num in (total_templates-1, total_templates-2):
            section_result = knowledge_graph.graphllm.invoke(section_generation).content
        else:
            section_result = knowledge_graph.reasonllm.invoke(section_generation).content
            
        return section_result
        
    except Exception as e:
        logging.error(f"Section {template_num+1} 处理失败: {str(e)}")
        return f"Section {template_num+1} 处理失败"

async def main_optimized(pdf_id):
    """优化后的主函数"""
    # 初始化日志
    init_logging()
    logger = logging.getLogger(__name__)
    logger.setLevel(LOGGER_MODES)

    start_time = time.time()
    
    # 检查输出文件是否已存在
    save_dir = f"./papersavings/Paper_{pdf_id}.md"
    if os.path.exists(save_dir):
        print(f"Paper_{pdf_id} 已存在，跳过处理...")
        return

    # 加载配置
    api_key = OPENAI_CONFIG['api_key']
    base_url = OPENAI_CONFIG['base_url']
    if not (api_key and base_url):
        raise ValueError("API key 和 base URL 必须在配置文件中提供")

    # 初始化模板图谱（只初始化一次）
    print("初始化模板图谱...")
    template_graph = Knowledge_Graph(filtered=False, type_name="FTTemplate")
    
    # 批量处理PDF文件
    print(f"开始处理 Paper_{pdf_id}...")
    base_path = "./origin_paper/more_paper/"
    paths = [base_path + str(pdf_id) + ".pdf"]
    if pdf_id < 125:  # 避免索引越界
        si_path = base_path + str(pdf_id+1) + "-si.pdf"
        if os.path.exists(si_path):
            paths.append(si_path)

    # 异步批量处理PDF
    print("正在解析PDF文件...")
    pdf_start = time.time()
    existing_paths = [p for p in paths if os.path.exists(p)]
    if existing_paths:
        md_texts = await process_pdfs_batch(existing_paths)
        md_text = "\n\n".join(md_texts)
    else:
        md_text = ""
    pdf_time = time.time() - pdf_start
    print(f"PDF解析完成，耗时: {pdf_time:.2f}秒")

    # 构建知识图谱
    print("构建知识图谱...")
    graph_start = time.time()
    knowledge_graph = Knowledge_Graph(markdown=md_text, type_name="FT Framework", filtered=False)
    if knowledge_graph.title == "None":
        knowledge_graph.title = f"Paper {pdf_id}"

    # 检查是否需要生成图谱
    generate_graph = "False" in str(knowledge_graph.graph.query("""MATCH (d:Document)
    WHERE d.title = "{title}"
    RETURN COUNT(d) > 0 AS exists LIMIT 1""".replace("{title}", knowledge_graph.title)))

    if generate_graph:
        knowledge_graph.filter_content()
        
        logging.info("转换文档到图谱...")
        documents = await knowledge_graph.llm_transformer.aconvert_to_graph_documents(knowledge_graph.splits)
        
        logging.info("添加文档到图谱...")
        knowledge_graph.graph.add_graph_documents(
            documents,
            baseEntityLabel=True,
            include_source=True
        )
        
        # 创建索引
        knowledge_graph.graph.query("""CREATE FULLTEXT INDEX entity IF NOT EXISTS
    FOR (n:__Entity__)
    ON EACH [n.id];""")
        
    graph_time = time.time() - graph_start
    print(f"知识图谱构建完成，耗时: {graph_time:.2f}秒")

    # 生成摘要和表格
    print("生成摘要...")
    summary = knowledge_graph.reason_answer(
        APPLICATION_PROMPTS["decompose_prompts"]["ft_summary_generation_simplified"].replace("{title}", knowledge_graph.title)
    )
    
    new_table = table_generate(template_graph.splits, table=[])
    
    # 准备叶子段落
    leaf_section = []
    for doc in template_graph.splits:
        title, cnt = position_count(doc)
        title = cnt*"#" + " " + title
        leaf_section.append(title)
    
    # 存储模板相关信息到knowledge_graph以供后续使用
    knowledge_graph.template_splits = template_graph.splits
    knowledge_graph.template_example_dict = template_graph.example_dict

    # 并行处理段落 - 增加并发数
    print("并行处理段落...")
    section_start = time.time()
    section_results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:  # 增加并发数
        tasks = [(template_num, sec) for template_num, sec in enumerate(template_graph.splits)]
        
        # 使用partial来传递额外参数
        from functools import partial
        process_func = partial(process_section_optimized, 
                             knowledge_graph=knowledge_graph,
                             new_table=new_table,
                             summary=summary,
                             leaf_section=leaf_section)
        
        progress_bar = tqdm(executor.map(process_func, tasks), 
                            total=len(tasks), 
                            desc="并行处理段落", 
                            position=0, leave=True)
        
        for result in progress_bar:
            section_results.append(result)
    
    section_time = time.time() - section_start
    print(f"段落处理完成，耗时: {section_time:.2f}秒")

    # 组装最终文章
    print("组装最终文章...")
    full_article = ["# " + knowledge_graph.title]
    cnt = 0
    for v in new_table[1:]:
        if any(re.match(f"{re.escape(section)}", v) for section in leaf_section):
            current = section_results[cnt]
            full_article.append(current.replace("```markdown", "").replace("```", ""))
            cnt += 1
        else:
            full_article.append(v.replace("```markdown", "").replace("```", ""))
    
    article_result = "\n\n".join(full_article)
    
    # 保存结果
    os.makedirs("./papersavings", exist_ok=True)
    with open(save_dir, "w", encoding="utf-8") as f:
        f.write(article_result)
    
    total_time = time.time() - start_time
    print(f"Paper_{pdf_id} 处理完成!")
    print(f"总耗时: {total_time:.2f}秒 (PDF解析: {pdf_time:.2f}s, 图谱构建: {graph_time:.2f}s, 段落处理: {section_time:.2f}s)")

def main_sync(pdf_id):
    """同步包装器"""
    return asyncio.run(main_optimized(pdf_id))

if __name__ == "__main__":
    # 批量处理
    base_path = "./papersavings/"
    os.makedirs(base_path, exist_ok=True)
    
    # 处理前几个文档进行测试
    for pdf_id in range(1, 6):  # 先处理5个文档测试性能
        if os.path.exists(base_path + f"Paper_{pdf_id}.md"):
            print(f"Paper_{pdf_id} 已存在，跳过...")
            continue
        
        print(f"开始处理 Paper_{pdf_id}...")
        try:
            main_sync(pdf_id)
        except Exception as e:
            print(f"处理 Paper_{pdf_id} 时出错: {str(e)}")
            logging.error(f"处理 Paper_{pdf_id} 时出错: {str(e)}") 
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
    # DOCUMENT_PROMPTS,
    # SECTION_PROMPTS,
    # ALIGNMENT_CONFIG,
    LOGGER_MODES,
    get_application_prompts,
)
from graph_utils.chatgpt.utils import init_logging
# from fsm_generation.fsm_generator import Manager
from graph_utils.graph_generate_bak import Knowledge_Graph
import json
import concurrent.futures
from tqdm import tqdm  # 假设已安装tqdm
# from paper_decompose.paper_decompose import Paper_Decompose
# from paper_decompose.section_generator import SectionGeneration

def process_pdf_list(pdf_ls):
    """Process a list of PDFs or directories, extracting individual PDF files."""
    if not isinstance(pdf_ls, list):
        pdf_ls = [pdf_ls]
    temp_ls = []
    for pdf in pdf_ls:
        if os.path.isdir(pdf):
            temp_ls.extend([os.path.join(pdf, file) for file in os.listdir(pdf) if file.endswith('.pdf')])
        else:
            temp_ls.append(pdf)
            
    for num in range(len(temp_ls)):
        file_path = pdf_ls[num][:-4]+"/"+pdf_ls[num][:-4].split("/")[-1]+".md"
        temp_ls[num] = file_path
    return temp_ls


# 定义发送 POST 请求的函数
def send_post_request(path):
    session = requests.Session()
    session.trust_env = False
    post_data = {
        'filepath': path,
        # 在这里添加其他参数
    }
    try:
        response = session.post("http://127.0.0.1:2675/marker", data=json.dumps(post_data))
        response.raise_for_status()  # 检查是否有 HTTP 错误
        return response.json().get('output', '')  # 返回 'output' 字段，如果没有则返回空字符串
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error for path {path}: {str(e)}")


def table_generate(template, table):
    head1=0
    head2=0
    head3=0
    head4=0
    for doc in template:
        # print(doc.metadata)
        for k, v in doc.metadata.items():
            # print(k, v)
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

# from enhanced_pre_recall import enhanced_retry

def main(subfolder_path, result_path, type_name):
    # Initialize logging
    init_logging()
    logger = logging.getLogger(__name__)
    logger.setLevel(LOGGER_MODES)

    # 动态获取对应的APPLICATION_PROMPTS配置
    APPLICATION_PROMPTS = get_application_prompts(type_name)
    
    # Load configurations, giving priority to command line arguments
    api_key = OPENAI_CONFIG['api_key']
    base_url = OPENAI_CONFIG['base_url']
    # organization = OPENAI_CONFIG['organization']
    # pdf_ls = NOUGAT_CONFIG['pdf']
    # keyword = ARXIV_CONFIG['key_word']
    # download = True
    # daily_type = ARXIV_CONFIG['daily_type']
    # run_all = True
    # specific_app = "blog"
    # recompute = True
    # Validate API key and base URL
    if not (api_key and base_url):
        raise ValueError("API key and base URL must be provided either via --api_key and --base_url or in the config file.")

    # Initialize generators
    # model_config = OPENAI_CONFIG["model_config"]

    # decompose_generator = Paper_Decompose(api_key=api_key, base_url=base_url, organization=organization, model_config=model_config,
    #                                 proxy=GENERAL_CONFIG["proxy"])
    # section_generator = SectionGeneration(api_key=api_key, base_url=base_url, organization=organization, model_config=model_config,
    #                                 proxy=GENERAL_CONFIG["proxy"])

    template_graph = Knowledge_Graph(filtered=False,type_name=type_name+"Template")

    # 修改：处理指定子文件夹下的所有PDF文件
    md_text = ""
    
    # 获取子文件夹中所有PDF文件
    pdf_files = []
    if os.path.exists(subfolder_path) and os.path.isdir(subfolder_path):
        for file in os.listdir(subfolder_path):
            if file.endswith('.pdf'):
                pdf_files.append(os.path.join(subfolder_path, file))
    
    # 处理所有找到的PDF文件
    for pdf_path in pdf_files:
        try:
            md_text += send_post_request(pdf_path) + "\n\n"
            print(f"Successfully processed: {pdf_path}")
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            continue
    
    if not md_text.strip():
        print(f"No valid PDF content found in {subfolder_path}")
        return
    
    # 从子文件夹名称生成标题
    subfolder_name = os.path.basename(subfolder_path)
    
    knowledge_graph = Knowledge_Graph(markdown=md_text, type_name=type_name+"Framework", filtered=False)
    if knowledge_graph.title == "None":
        knowledge_graph.title = subfolder_name

    generate_graph = "False" in str(knowledge_graph.graph.query("""MATCH (d:Document)
    WHERE d.title = "{title}"
    RETURN COUNT(d) > 0 AS exists LIMIT 1""".replace("{title}",knowledge_graph.title)))

    if generate_graph:
        knowledge_graph.filter_content()
        
        logging.info("Converting Documnets to Graph...")
        async def process_documents():
            documents = await knowledge_graph.llm_transformer.aconvert_to_graph_documents(knowledge_graph.splits)
            return documents
        
        # Call the async function using an event loop
        import asyncio
        documents = asyncio.run(process_documents())
        logging.info("Converting Documnets to Graph...Complete!")
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
        title, cnt= position_count(doc)
        title = cnt*"#" + " " + title
        leaf_section.append(title)

    leaf_section = []
    for doc in template_graph.splits:
        title, cnt= position_count(doc)
        title = cnt*"#" + " " + title
        leaf_section.append(title)
    new_table = table_generate(template_graph.splits, table=[])

    ###################################################################################################
    # all parallel

    section_results = []
    delay = 30
    max_retries = 3
    
    # @enhanced_retry(max_retries=max_retries, delay=delay)
    def process_qa_chunk(args):
        template_num, chunk_questions, chunk_start = args
        question_str = "\n".join(chunk_questions)
        
        for retry in range(max_retries):
            try:
                # 添加错误处理，检查返回结果是否为None
                if template_num == 7:
                    result = knowledge_graph.reason_answer(f"Please provide detailed answers to the following questions, marking each answer with the corresponding question. Use the format 'Q: [Original Question], A: [Answer]'. Write out the original question but do not use numbered indexes.**you should note that all questions should clearly exclude the activation processes existing in the characterization techniques.**\n<question>"+question_str+"\n</question>")
                elif template_num in (len(template_graph.splits)-1, len(template_graph.splits)-2):
                    result = knowledge_graph.graph_answer(f"Please provide detailed answers to the following questions, marking each answer with the corresponding question. Use the format 'Q: [Original Question], A: [Answer]'. Write out the original question but do not use numbered indexes.\n<question>"+question_str+"\n</question>")
                else:
                    result = knowledge_graph.mini_answer(f"Please provide detailed answers to the following questions, marking each answer with the corresponding question. Use the format 'Q: [Original Question], A: [Answer]'. Write out the original question but do not use numbered indexes.\n<question>"+question_str+"\n</question>")
                
                # 检查result是否为None或为空字符串
                if result is None or result.strip() == "":
                    print(f"\x1b[31mSection {template_num+1} QA Chunk {chunk_start//5+1} Error: Empty result returned\x1b[0m")
                    # 如果不是最后一次重试，则继续下一次重试
                    if retry < max_retries - 1:
                        time.sleep(delay)
                        continue
                    # 如果是最后一次重试，返回一个默认值
                    return (chunk_start, ["No answer could be generated for these questions."])
                
                return (chunk_start, result.split("\n"))
            except Exception as e:
                print(f"\x1b[31mSection {template_num+1} QA Chunk {chunk_start//5+1} Error ({retry+1}/{max_retries}):\x1b[0m", str(chunk_questions))
                print(f"\x1b[31mSection {template_num+1} QA Chunk {chunk_start//5+1} Error ({retry+1}/{max_retries}):\x1b[0m", str(e))
                if retry < max_retries - 1:
                    time.sleep(delay)
        return (chunk_start, ["No answer could be generated for these questions."])  # 返回默认值而不是None
    # @enhanced_retry(max_retries=max_retries, delay=delay)
    def process_section(args):
        template_num, sec = args
        message = [
            {"role": "system", "content": APPLICATION_PROMPTS["decompose_prompts"]["system_prompt"]},
            {"role": "user", "content": APPLICATION_PROMPTS["decompose_prompts"]["decoompose_table_prompt"]
            .replace('{table}', "\n".join(new_table), 1)
            .replace('{describe}', sec.page_content, 1)
            .replace('{summary}', summary, 1)
            .replace('{example}', APPLICATION_PROMPTS["decompose_prompts"][template_graph.example_dict[template_num]], 1)}
        ]
        
        # 问题生成部分的重试逻辑
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
            return None  # 所有重试失败
        
        # 问答处理部分并行化
        results = []
        chunk_args = []
        for chunk_start in range(0, len(decompose_questions), 5):
            chunk_questions = decompose_questions[chunk_start:chunk_start+5]
            chunk_args.append((template_num, chunk_questions, chunk_start))
        
        chunk_results = {}  # 用于保存各块结果的有序字典
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as qa_executor:
            qa_progress = tqdm(qa_executor.map(process_qa_chunk, chunk_args), 
                            total=len(chunk_args), 
                            desc=f"Processing section {template_num+1} QA", 
                            position=0, leave=False)
            
            for chunk_start, chunk_result in qa_progress:
                if chunk_result is not None:
                    chunk_results[chunk_start] = chunk_result  # 按chunk_start保存结果
        
        # 按原始顺序合并块结果（确保顺序正确）
        for chunk_start in sorted(chunk_results.keys()):  # 按起始位置排序
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
        return None  # 章节生成最终失败

    # 并行处理部分（保持不变）
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        tasks = [(template_num, sec) for template_num, sec in enumerate(template_graph.splits)]
        progress_bar = tqdm(executor.map(process_section, tasks), 
                            total=len(tasks), 
                            desc="Parallel Section Processing", 
                            position=0, leave=True)
        
        for result in progress_bar:
            if result is not None:
                section_results.append(result)
            else:
                section_results.append("Section processing failed (all retries exhausted)")  # 添加错误占位符

    full_article=["# "+knowledge_graph.title]
    cnt=0
    for v in new_table[1:]:
    # 检查当前行是否匹配任何叶子章节v
        if any(re.match(f"{re.escape(section)}", v) for section in leaf_section):
            current=section_results[cnt]
            # already="\n".join(full_article)
            # regen_section_result = section_generator.results_regeneration(
            #     current=current,
            #     already=already,
            #     reset_messages=True,
            #     response_only=True,
            # )
            full_article.append(current.replace("```markdown","").replace("```",""))
            cnt+=1
        else:
            full_article.append(v.replace("```markdown","").replace("```",""))
    article_result = "\n\n".join(full_article)
    # print(article_result)
    # save_dir = "./papersavings/"+knowledge_graph.title.replace(" ","_").replace("/","_")+".md"
    # import pdb;pdb.set_trace()
    save_path = os.path.join(result_path,type_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    save_dir = os.path.join(save_path, f"{subfolder_name}.md")
    with open(save_dir,"w",encoding="utf-8") as f:
        f.write(article_result)


if __name__ == "__main__":
    type_name = "MoF"
    result_path = "/home/user/shizhou/Agent/ft_pack/papersavings/"
    base_folder = "/home/user/shizhou/Agent/ft_pack/origin_paper/MoF-20250802"
    # base_folder = "/home/user/shizhou/Agent/ft_pack/origin_paper/debug"
    # import pdb;pdb.set_trace()
    # 获取所有子文件夹
    if os.path.exists(base_folder):
        subfolders = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]
        
        for subfolder in subfolders:
            subfolder_path = os.path.join(base_folder, subfolder)
            output_file = os.path.join(result_path, type_name, f"{subfolder}.md")
            
            # 检查输出文件是否已存在
            if os.path.exists(output_file):
                print(f"{subfolder} already exists, skipping...")
                continue
                
            print(f"Processing subfolder: {subfolder}...")
            try:
                main(subfolder_path, result_path, type_name)
                print(f"Successfully processed: {subfolder}")
            except Exception as e:
                print(f"Error processing {subfolder}: {str(e)}")
                continue
    else:
        print(f"Base folder {base_folder} does not exist!")
import os
import uuid
import json
import datetime
import time
import asyncio
import re
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import concurrent.futures
from tqdm import tqdm
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname("..")))
from graph_utils.graph_generate_bak import Knowledge_Graph
from graph_utils.chatgpt.config.config import (
    GENERAL_CONFIG,
    OPENAI_CONFIG,
    ARXIV_CONFIG,
    NOUGAT_CONFIG,
    LOGGER_MODES,
    get_application_prompts,
    get_supported_domains,
    update_supported_domains_config,
    get_domains_config_info,
)
from graph_search_dss import process_single_pdf_group, group_pdf_files_with_si
from graph_utils.chatgpt.utils import init_logging

# 导入提示词生成相关模块
try:
    from change_prompt_DSS import (
        generate_prompts_api,
        PromptGenerationRequest,
        PromptGenerationResponse
    )
    PROMPT_GENERATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: 提示词生成功能不可用: {e}")
    PROMPT_GENERATION_AVAILABLE = False

# 创建FastAPI实例
app = FastAPI(title="Sci Assistant", description="上传PDF文档，自动生成规范的Protocol报告")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源，生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 配置静态文件和模板
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 配置参数
UPLOAD_FOLDER = "uploads"
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB 上传限制
ALLOWED_EXTENSIONS = {"pdf"}
REPORTS_FOLDER = "papersavings"

# 从配置文件读取支持的领域类型
SUPPORTED_DOMAINS = get_supported_domains()

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

# 数据模型定义
class ReportRequest(BaseModel):
    files: List[str]
    domain: str = "FT"  # 领域选择

class ReportResponse(BaseModel):
    status: str
    message: str
    report_id: Optional[str] = None
    report_path: Optional[str] = None

class SaveReportRequest(BaseModel):
    report_id: str
    content: str

class FileResponse(BaseModel):
    status: str
    message: str
    files: Optional[List[dict]] = None

class OutlineUploadResponse(BaseModel):
    status: str
    message: str
    subject: Optional[str] = None
    outline_file: Optional[str] = None
    prompt_generation_result: Optional[dict] = None

class PromptGenerationStatusResponse(BaseModel):
    status: str
    message: str
    available: bool
    supported_domains: Optional[List[str]] = None

class GeneratedFilesResponse(BaseModel):
    status: str
    message: str
    subject: Optional[str] = None
    files: Optional[List[dict]] = None

class PromptFileContentResponse(BaseModel):
    status: str
    message: str
    subject: Optional[str] = None
    file_type: Optional[str] = None
    file_path: Optional[str] = None
    content: Optional[str] = None

class SavePromptFileRequest(BaseModel):
    subject: str
    file_type: str  # 'template', 'kg_prompt', 'prompts_config'
    content: str

# 工具函数
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_outline_file(filename):
    """检查是否为允许的大纲文件格式"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"md", "txt"}

def extract_subject_from_filename(filename):
    """从文件名中提取subject"""
    # 移除文件扩展名
    name_without_ext = Path(filename).stem
    # 清理文件名，移除特殊字符但保留空格和字母数字
    subject = re.sub(r'[^\w\s-]', '', name_without_ext).strip()
    return subject

def update_supported_domains(new_subject):
    """动态更新支持的领域列表并写入配置文件"""
    global SUPPORTED_DOMAINS
    if new_subject not in SUPPORTED_DOMAINS:
        # 使用subject作为key和描述
        SUPPORTED_DOMAINS[new_subject] = new_subject
        
        # 写入配置文件
        success = update_supported_domains_config(new_subject, new_subject)
        if success:
            print(f"Added new domain to config: {new_subject}")
        else:
            print(f"Failed to add domain to config: {new_subject}")
            
    return SUPPORTED_DOMAINS

# 从graph_search.py移植的函数
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


# 发送PDF解析请求 - 与graph_search.py保持一致
async def send_post_request(path):
    import aiohttp
    
    # 确保使用绝对路径
    absolute_path = os.path.abspath(path) if not os.path.isabs(path) else path
    print(f"发送PDF解析请求: {absolute_path}")
    
    # 验证文件是否存在
    if not os.path.exists(absolute_path):
        raise FileNotFoundError(f"文件不存在: {absolute_path}")
    
    async with aiohttp.ClientSession() as session:
        post_data = {
            'filepath': absolute_path,
        }
        try:
            # 与graph_search.py保持一致的请求方式
            json_str = json.dumps(post_data)
            headers = {'Content-Type': 'application/json'}
            
            async with session.post(
                "http://127.0.0.1:2675/marker", 
                data=json_str,  # 直接使用JSON字符串
                headers=headers
            ) as response:
                response.raise_for_status()
                result = await response.json()
                return result.get('output', '')
        except Exception as e:
            raise RuntimeError(f"Error for path {path}: {str(e)}")

# 路由定义
@app.get("/")
async def index(request: Request):
    """首页 - 显示上传界面"""
    # 获取已生成的报告列表
    reports = []
    if os.path.exists(REPORTS_FOLDER):
        # 按领域分类获取报告
        for domain in SUPPORTED_DOMAINS.keys():
            domain_path = os.path.join(REPORTS_FOLDER, domain)
            if os.path.exists(domain_path):
                for file in os.listdir(domain_path):
                    if file.endswith('.md'):
                        reports.append({
                            'filename': file,
                            'domain': domain,
                            'path': f"{domain}/{file}"
                        })
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "reports": reports, "domains": SUPPORTED_DOMAINS}
    )

@app.get("/api/domains")
async def get_domains():
    """获取支持的领域列表"""
    return {"domains": SUPPORTED_DOMAINS}

@app.post("/api/domains/reload")
async def reload_domains():
    """重新加载配置文件中的支持领域"""
    global SUPPORTED_DOMAINS
    try:
        SUPPORTED_DOMAINS = get_supported_domains()
        return {
            "status": "success",
            "message": "成功重新加载支持的领域配置",
            "domains": SUPPORTED_DOMAINS
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"重新加载配置失败: {str(e)}"
        )

@app.get("/api/domains/config-info")
async def get_domains_config_info_api():
    """获取领域配置文件的详细信息"""
    try:
        config_info = get_domains_config_info()
        return {
            "status": "success",
            "config_info": config_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取配置信息失败: {str(e)}"
        )

@app.get("/api/prompt-generation/status")
async def get_prompt_generation_status():
    """获取提示词生成功能状态"""
    return PromptGenerationStatusResponse(
        status="success" if PROMPT_GENERATION_AVAILABLE else "unavailable",
        message="提示词生成功能可用" if PROMPT_GENERATION_AVAILABLE else "提示词生成功能不可用",
        available=PROMPT_GENERATION_AVAILABLE,
        supported_domains=list(SUPPORTED_DOMAINS.keys()) if PROMPT_GENERATION_AVAILABLE else None
    )

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """处理文件上传请求"""
    uploaded_files = []
    
    for file in files:
        if file.filename == '':
            continue
            
        if allowed_file(file.filename):
            # 生成安全的文件名并保存
            filename = file.filename.replace(" ", "_")  # 简单的文件名安全处理
            # unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # 异步写入文件
            contents = await file.read()
            with open(filepath, "wb") as f:
                f.write(contents)
            
            uploaded_files.append({
                'original_name': filename,
                'saved_path': filepath
            })
    
    if uploaded_files:
        # 返回成功信息和上传的文件列表
        return FileResponse(
            status="success",
            message=f"成功上传 {len(uploaded_files)} 个文件",
            files=uploaded_files
        )
    else:
        return FileResponse(
            status="error",
            message="没有成功上传任何文件"
        )

@app.post("/upload-outline", response_model=OutlineUploadResponse)
async def upload_outline_and_generate_prompts(file: UploadFile = File(...)):
    """
    上传大纲文件并生成提示词
    
    功能：
    1. 接收用户上传的文件（如 "Duplex Stainless Steel.md"）
    2. 从文件名提取subject（如 "Duplex Stainless Steel"）
    3. 将文件重命名为 outline_{subject}.md
    4. 调用change_prompt_DSS生成该领域的提示词
    5. 更新SUPPORTED_DOMAINS列表
    """
    
    print("\n" + "="*60)
    print("📤 开始处理大纲文件上传请求")
    print("="*60)
    
    # 检查提示词生成功能是否可用
    print(f"🔍 检查提示词生成功能状态: {PROMPT_GENERATION_AVAILABLE}")
    if not PROMPT_GENERATION_AVAILABLE:
        return OutlineUploadResponse(
            status="error",
            message="提示词生成功能不可用，请检查change_prompt_DSS模块"
        )
    
    # 检查文件是否为空
    print(f"📄 接收到文件: {file.filename}")
    if not file.filename:
        print("❌ 错误: 文件名为空")
        return OutlineUploadResponse(
            status="error",
            message="未选择文件"
        )
    
    # 检查文件格式
    print(f"🔍 检查文件格式: {file.filename}")
    if not allowed_outline_file(file.filename):
        print(f"❌ 错误: 不支持的文件格式")
        return OutlineUploadResponse(
            status="error",
            message="不支持的文件格式，请上传.md或.txt文件"
        )
    
    try:
        # 从文件名提取subject
        print(f"🔍 从文件名提取主题...")
        subject = extract_subject_from_filename(file.filename)
        print(f"✅ 提取的主题: '{subject}'")
        
        if not subject:
            print("❌ 错误: 无法提取有效的主题名称")
            return OutlineUploadResponse(
                status="error",
                message="无法从文件名提取有效的主题名称"
            )
        
        # 创建目标文件名
        outline_filename = f"outline_{subject}.md"
        outline_filepath = os.path.join(".", outline_filename)
        print(f"📝 目标文件路径: {outline_filepath}")
        
        # 读取并保存文件内容
        print(f"📥 读取文件内容...")
        contents = await file.read()
        file_size = len(contents)
        print(f"✅ 文件大小: {file_size} 字节")
        
        print(f"💾 保存文件到: {outline_filepath}")
        with open(outline_filepath, "wb") as f:
            f.write(contents)
        print(f"✅ 文件保存成功")
        
        # 调用提示词生成功能
        print(f"\n🚀 开始生成提示词...")
        print(f"   主题: {subject}")
        print(f"   使用模型: DeepSeek")
        try:
            print(f"📦 创建生成请求...")
            request = PromptGenerationRequest(subject=subject, use_deepseek=True)
            print(f"✅ 请求创建成功")
            
            print(f"🔄 调用 generate_prompts_api...")
            prompt_result = generate_prompts_api(request)
            print(f"✅ generate_prompts_api 调用完成")
            
            # 转换为字典格式以便JSON序列化
            print(f"📊 处理生成结果...")
            print(f"   成功状态: {prompt_result.success}")
            if prompt_result.error:
                print(f"   错误信息: {prompt_result.error}")
            
            prompt_result_dict = {
                "success": prompt_result.success,
                "subject": prompt_result.subject,
                "files_generated": prompt_result.files_generated,
                "error": prompt_result.error,
                "error_type": prompt_result.error_type
            }
            
            if prompt_result.success:
                print(f"✅ 提示词生成成功！")
                print(f"📁 生成的文件:")
                if prompt_result.files_generated:
                    for key, path in prompt_result.files_generated.items():
                        print(f"   - {key}: {path}")
                # 只有在提示词生成成功后才更新支持的领域列表
                print(f"🔄 更新支持的领域列表...")
                update_supported_domains(subject)
                print(f"✅ 领域列表更新完成")
                
                print(f"\n" + "="*60)
                print(f"✅ 大纲上传和提示词生成全部完成！")
                print(f"="*60 + "\n")
                
                return OutlineUploadResponse(
                    status="success",
                    message=f"成功上传大纲文件并生成 '{subject}' 领域的提示词",
                    subject=subject,
                    outline_file=outline_filepath,
                    prompt_generation_result=prompt_result_dict
                )
            else:
                print(f"⚠️ 提示词生成失败")
                print(f"   错误: {prompt_result.error}")
                print(f"   错误类型: {prompt_result.error_type}")
                return OutlineUploadResponse(
                    status="partial_success",
                    message=f"大纲文件上传成功，但提示词生成失败: {prompt_result.error}",
                    subject=subject,
                    outline_file=outline_filepath,
                    prompt_generation_result=prompt_result_dict
                )
                
        except Exception as e:
            print(f"\n❌ 提示词生成过程中发生异常")
            print(f"   异常类型: {type(e).__name__}")
            print(f"   异常信息: {str(e)}")
            import traceback
            print(f"   堆栈跟踪:")
            traceback.print_exc()
            
            return OutlineUploadResponse(
                status="partial_success",
                message=f"大纲文件上传成功，但提示词生成时出错: {str(e)}",
                subject=subject,
                outline_file=outline_filepath,
                prompt_generation_result={"success": False, "error": str(e)}
            )
            
    except Exception as e:
        print(f"\n❌ 文件处理过程中发生异常")
        print(f"   异常类型: {type(e).__name__}")
        print(f"   异常信息: {str(e)}")
        import traceback
        print(f"   堆栈跟踪:")
        traceback.print_exc()
        print(f"="*60 + "\n")
        
        return OutlineUploadResponse(
            status="error",
            message=f"处理文件时出错: {str(e)}"
        )

@app.get("/api/prompts/generated-files/{subject}")
async def get_generated_files(subject: str):
    """
    获取某个主题生成的所有提示词文件列表
    
    返回：
    - template文件路径
    - kg_prompt文件路径
    - prompts_config文件路径
    """
    try:
        from change_prompt_DSS import get_file_paths
        
        file_paths = get_file_paths(subject)
        files = []
        
        # 检查模板文件
        if os.path.exists(file_paths["subject_template_file"]):
            files.append({
                "type": "template",
                "name": "实验提取模板",
                "path": file_paths["subject_template_file"],
                "exists": True,
                "size": os.path.getsize(file_paths["subject_template_file"])
            })
        else:
            files.append({
                "type": "template",
                "name": "实验提取模板",
                "path": file_paths["subject_template_file"],
                "exists": False
            })
        
        # 检查知识图谱提示词文件
        if os.path.exists(file_paths["subject_kg_prompt_file"]):
            files.append({
                "type": "kg_prompt",
                "name": "知识图谱提示词",
                "path": file_paths["subject_kg_prompt_file"],
                "exists": True,
                "size": os.path.getsize(file_paths["subject_kg_prompt_file"])
            })
        else:
            files.append({
                "type": "kg_prompt",
                "name": "知识图谱提示词",
                "path": file_paths["subject_kg_prompt_file"],
                "exists": False
            })
        
        # # 检查配置文件（暂不提供修改）
        # if os.path.exists(file_paths["prompts_config_file"]):
        #     files.append({
        #         "type": "prompts_config",
        #         "name": "应用提示词配置",
        #         "path": file_paths["prompts_config_file"],
        #         "exists": True,
        #         "size": os.path.getsize(file_paths["prompts_config_file"])
        #     })
        # else:
        #     files.append({
        #         "type": "prompts_config",
        #         "name": "应用提示词配置",
        #         "path": file_paths["prompts_config_file"],
        #         "exists": False
        #     })
        
        return GeneratedFilesResponse(
            status="success",
            message=f"成功获取 '{subject}' 的生成文件列表",
            subject=subject,
            files=files
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取文件列表时出错: {str(e)}"
        )

@app.get("/api/prompts/file-content/{subject}/{file_type}")
async def get_prompt_file_content(subject: str, file_type: str):
    """
    获取指定提示词文件的内容
    
    参数：
    - subject: 主题名称
    - file_type: 文件类型 ('template', 'kg_prompt', 'prompts_config')
    """
    try:
        from change_prompt_DSS import get_file_paths
        
        file_paths = get_file_paths(subject)
        
        # 根据文件类型选择对应的文件路径
        file_type_map = {
            "template": "subject_template_file",
            "kg_prompt": "subject_kg_prompt_file",
            "prompts_config": "prompts_config_file"
        }
        
        if file_type not in file_type_map:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file_type}"
            )
        
        file_path = file_paths[file_type_map[file_type]]
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"文件不存在: {file_path}"
            )
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return PromptFileContentResponse(
            status="success",
            message="成功读取文件内容",
            subject=subject,
            file_type=file_type,
            file_path=file_path,
            content=content
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"读取文件内容时出错: {str(e)}"
        )

@app.post("/api/prompts/save-file")
async def save_prompt_file(request: SavePromptFileRequest):
    """
    保存编辑后的提示词文件
    
    参数：
    - subject: 主题名称
    - file_type: 文件类型 ('template', 'kg_prompt', 'prompts_config')
    - content: 文件内容
    """
    try:
        from change_prompt_DSS import get_file_paths
        
        file_paths = get_file_paths(request.subject)
        
        # 根据文件类型选择对应的文件路径
        file_type_map = {
            "template": "subject_template_file",
            "kg_prompt": "subject_kg_prompt_file",
            "prompts_config": "prompts_config_file"
        }
        
        if request.file_type not in file_type_map:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {request.file_type}"
            )
        
        file_path = file_paths[file_type_map[request.file_type]]
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 保存文件内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(request.content)
        
        return {
            "status": "success",
            "message": f"成功保存 '{request.subject}' 的 {request.file_type} 文件",
            "file_path": file_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"保存文件时出错: {str(e)}"
        )

@app.post("/generate-prompts", response_model=PromptGenerationResponse)
async def generate_prompts_for_existing_subject(request: PromptGenerationRequest):
    """
    为已存在的主题生成提示词
    
    要求：
    1. 对应的outline_{subject}.md文件必须存在
    2. 提示词生成功能必须可用
    """
    
    # 检查提示词生成功能是否可用
    if not PROMPT_GENERATION_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="提示词生成功能不可用，请检查change_prompt_DSS模块"
        )
    
    # 检查大纲文件是否存在
    outline_file = f"outline_{request.subject}.md"
    if not os.path.exists(outline_file):
        raise HTTPException(
            status_code=404,
            detail=f"找不到大纲文件: {outline_file}，请先上传对应的大纲文件"
        )
    
    try:
        # 调用提示词生成功能
        result = generate_prompts_api(request)
        
        # 如果生成成功，更新支持的领域列表
        if result.success:
            update_supported_domains(request.subject)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成提示词时出错: {str(e)}"
        )

@app.post("/generate")
async def generate_report(request: ReportRequest):
    """生成报告 - 处理上传的文件并在成功后删除PDF文件"""
    file_paths = request.files
    domain = request.domain
    
    if not file_paths:
        raise HTTPException(status_code=400, detail="没有提供文件路径")
    
    if domain not in SUPPORTED_DOMAINS:
        raise HTTPException(status_code=400, detail=f"不支持的领域: {domain}")
    
    try:
        # 将相对路径转换为绝对路径并验证文件存在
        absolute_file_paths = []
        for path in file_paths:
            if not os.path.isabs(path):
                absolute_path = os.path.abspath(path)
            else:
                absolute_path = path
                
            if not os.path.exists(absolute_path):
                return ReportResponse(
                    status="error",
                    message=f"文件不存在: {absolute_path}"
                )
            absolute_file_paths.append(absolute_path)
        
        # 直接对上传的文件进行分组处理
        # 手动实现文件分组逻辑，不使用临时文件夹
        def group_uploaded_files(file_paths):
            """
            对上传的文件进行分组，返回 [(main_pdf, si_pdf_list), ...]
            """
            import re
            
            def normalize_filename_for_matching(filename):
                """标准化文件名用于匹配"""
                name = os.path.basename(filename).replace('.pdf', '')
                name = re.sub(r'-[sS][iI]$', '', name)
                return name.lower().replace('_', '').replace('-', '').replace(' ', '')
            
            # 分离主文件和SI文件
            main_files = []
            si_files = []
            
            for file_path in file_paths:
                filename = os.path.basename(file_path)
                if re.search(r'-[sS][iI]\.pdf$', filename):
                    si_files.append(file_path)
                else:
                    main_files.append(file_path)
            
            # 为每个主文件找到对应的SI文件
            groups = []
            for main_file in main_files:
                main_normalized = normalize_filename_for_matching(main_file)
                matched_si_files = []
                
                for si_file in si_files:
                    si_normalized = normalize_filename_for_matching(si_file)
                    if main_normalized == si_normalized:
                        matched_si_files.append(si_file)
                
                groups.append((main_file, matched_si_files))
            
            return groups
        
        # 对上传的文件进行分组
        pdf_groups = group_uploaded_files(absolute_file_paths)
        
        if not pdf_groups:
            return ReportResponse(
                status="error",
                message="无法对上传的PDF文件进行分组"
            )
        
        print(f"Found {len(pdf_groups)} PDF groups from uploaded files")
        print(f"pdf_groups--------------------------------: {pdf_groups}")
        
        # 处理所有PDF组
        processed_files = []
        success_count = 0
        error_count = 0
        files_to_delete = []  # 记录需要删除的原始文件
        
        for main_pdf, si_pdfs in pdf_groups:
            main_filename = os.path.basename(main_pdf)
            output_filename = main_filename.replace('.pdf', '.md')
            output_path = os.path.join(REPORTS_FOLDER, domain, output_filename)
            
            # 检查文件是否已存在
            if os.path.exists(output_path):
                print(f"{output_filename} already exists, skipping...")
                continue
            
            try:
                print(f"Processing: {main_filename} with {len(si_pdfs)} SI files...")
                await process_single_pdf_group(main_pdf, si_pdfs, REPORTS_FOLDER, domain)
                processed_files.append(output_filename.replace('.md', ''))
                success_count += 1
                
                # 记录成功处理的文件，准备删除原始文件
                files_to_delete.append(main_pdf)
                files_to_delete.extend(si_pdfs)
                            
            except Exception as e:
                print(f"Error processing {main_filename}: {str(e)}")
                error_count += 1
                continue
        
        if success_count == 0:
            return ReportResponse(
                status="error",
                message=f"所有文件处理失败。错误数量: {error_count}"
            )
        
        # 删除成功处理的原始PDF文件
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"Deleted processed file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {str(e)}")
        
        # 返回第一个成功处理的文件信息用于跳转
        first_processed = processed_files[0] if processed_files else None
        
        return ReportResponse(
            status="success",
            message=f"成功处理 {success_count} 个文件，失败 {error_count} 个文件，删除 {deleted_count} 个PDF文件",
            report_id=first_processed,
            report_path=os.path.join(REPORTS_FOLDER, domain, f"{first_processed}.md") if first_processed else None
        )
    
    except Exception as e:
        return ReportResponse(
            status="error",
            message=f"生成报告时出错: {str(e)}"
        )

@app.get("/report/{domain}/{report_id}")
async def view_report(request: Request, domain: str, report_id: str):
    """查看报告内容"""
    if domain not in SUPPORTED_DOMAINS:
        raise HTTPException(status_code=400, detail="不支持的领域")
    
    report_path = os.path.join(REPORTS_FOLDER, domain, f"{report_id}.md")
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="报告不存在")
    
    # 读取报告内容
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return templates.TemplateResponse(
        "report.html",
        {"request": request, "report_id": report_id, "domain": domain, "content": content}
    )

@app.post("/save_report")
async def save_report(request: SaveReportRequest):
    """保存编辑后的报告内容"""
    report_id = request.report_id
    content = request.content
    
    # 从report_id中提取领域信息
    # 新的文件名格式是基于PDF文件名，需要在所有领域中搜索
    report_path = None
    domain = None
    
    for domain_key in SUPPORTED_DOMAINS.keys():
        potential_path = os.path.join(REPORTS_FOLDER, domain_key, f"{report_id}.md")
        if os.path.exists(potential_path):
            report_path = potential_path
            domain = domain_key
            break
    
    if not report_path:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    try:
        # 保存编辑后的内容
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {"status": "success", "message": "报告保存成功"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存报告时出错: {str(e)}")

@app.get("/reports")
async def list_reports(request: Request):
    """列出所有报告"""
    reports = []
    if os.path.exists(REPORTS_FOLDER):
        for domain in SUPPORTED_DOMAINS.keys():
            domain_path = os.path.join(REPORTS_FOLDER, domain)
            if os.path.exists(domain_path):
                for file in os.listdir(domain_path):
                    if file.endswith('.md'):
                        reports.append({
                            'filename': file,
                            'domain': domain,
                            'domain_name': SUPPORTED_DOMAINS[domain],
                            'path': f"{domain}/{file}"
                        })
    
    return templates.TemplateResponse(
        "reports.html",
        {"request": request, "reports": reports, "domains": SUPPORTED_DOMAINS}
    )

@app.get("/domain-upload")
async def domain_upload_page(request: Request):
    """新增支持领域页面"""
    return templates.TemplateResponse(
        "domain_upload.html",
        {"request": request}
    )

@app.get("/test-connection")
async def test_connection_page(request: Request):
    """连接测试页面"""
    return templates.TemplateResponse(
        "test_connection.html",
        {"request": request}
    )

@app.get("/prompts-manager")
async def prompts_manager_page(request: Request):
    """提示词文件管理页面"""
    return templates.TemplateResponse(
        "prompts_manager.html",
        {"request": request, "domains": SUPPORTED_DOMAINS}
    )

@app.get("/prompts-editor/{subject}/{file_type}")
async def prompts_editor_page(request: Request, subject: str, file_type: str):
    """提示词文件编辑页面"""
    return templates.TemplateResponse(
        "prompts_editor.html",
        {"request": request, "subject": subject, "file_type": file_type}
    )

def get_local_ip():
    """获取本机IP地址"""
    import socket
    try:
        # 创建一个UDP socket连接到外部地址来获取本机IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        try:
            # 备用方法：获取hostname对应的IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except Exception:
            return "127.0.0.1"

def get_all_network_interfaces():
    """获取所有网络接口的IP地址"""
    import socket
    import subprocess
    import platform
    
    interfaces = []
    
    try:
        if platform.system() == "Windows":
            # Windows系统使用ipconfig命令
            result = subprocess.run(['ipconfig'], capture_output=True, text=True, encoding='gbk')
            lines = result.stdout.split('\n')
            current_adapter = ""
            
            for line in lines:
                line = line.strip()
                if "适配器" in line or "adapter" in line.lower():
                    current_adapter = line
                elif "IPv4" in line and ":" in line:
                    ip = line.split(":")[-1].strip()
                    if ip and ip != "127.0.0.1":
                        interfaces.append(f"{current_adapter}: {ip}")
        else:
            # Linux/Unix系统使用ip命令
            try:
                result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
                lines = result.stdout.split('\n')
                current_interface = ""
                
                for line in lines:
                    if line.startswith((' ', '\t')) and 'inet ' in line and '127.0.0.1' not in line:
                        ip = line.split()[1].split('/')[0]
                        interfaces.append(f"{current_interface}: {ip}")
                    elif not line.startswith((' ', '\t')) and ':' in line:
                        current_interface = line.split(':')[1].strip().split('@')[0]
            except:
                # 备用方法
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                interfaces.append(f"hostname: {local_ip}")
                
    except Exception as e:
        print(f"获取网络接口信息时出错: {e}")
        
    return interfaces

if __name__ == "__main__":
    import uvicorn
    
    # 获取服务器IP信息
    local_ip = get_local_ip()
    all_interfaces = get_all_network_interfaces()
    
    print("=" * 60)
    print("🚀 FastAPI 服务启动信息")
    print("=" * 60)
    print(f"📍 主要IP地址: {local_ip}")
    print(f"🌐 服务端口: 30800")
    print(f"🔗 主要访问地址: http://{local_ip}:30800")
    print()
    print("📋 所有可用的网络接口:")
    if all_interfaces:
        for interface in all_interfaces:
            if interface:
                print(f"   • {interface}")
    else:
        print(f"   • 默认: {local_ip}")
    print()
    print("🌍 可能的访问地址:")
    print(f"   • 本地访问: http://localhost:30800")
    print(f"   • 本地访问: http://127.0.0.1:30800")
    print(f"   • 网络访问: http://{local_ip}:30800")
    print()
    print("📖 可用页面:")
    print(f"   • 主页: http://{local_ip}:30800/")
    print(f"   • API文档: http://{local_ip}:30800/docs")
    print(f"   • 报告列表: http://{local_ip}:30800/reports")
    print(f"   • 领域上传: http://{local_ip}:30800/domain-upload")
    print(f"   • 提示词管理: http://{local_ip}:30800/prompts-manager")
    print("=" * 60)
    print("⚡ 服务正在启动...")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=30800)
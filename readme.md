# 费托合成代码库 (Fischer-Tropsch Synthesis Toolkit)  

## 🚀 项目概览  

费托合成（Fischer-Tropsch Synthesis）智能研究平台。本项目通过大模型驱动的知识图谱构建技术，结合PDF文献智能解析系统，实现从学术文献中自动提取实验参数并生成可复现的合成流程方案。  


## 🔧 环境安装指南  

### 1.1 主代码环境配置  
```bash
# 创建并激活conda环境
conda env create -f freeze.yml
conda activate ftpack

# 配置OpenAI接口参数（修改API密钥）
vi graph_utils/chatgpt/config/config.yaml
```  

### 1.2 Neo4j知识图谱数据库部署  
#### 安装步骤（推荐v5.10+版本）：  
1. 下载并安装Neo4j社区版  
2. 启动服务后，修改数据库连接参数：  
```python
# 路径：graph_utils/graph_generate_bak.py
# 原始配置（45-46行）
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "password"
# ↓↓↓ 请替换为实际账户密码 ↓↓↓
os.environ["NEO4J_USERNAME"] = "your_username"
os.environ["NEO4J_PASSWORD"] = "your_password"
```  

### 1.3 PDF文献解析环境  
```bash
# 创建独立虚拟环境
conda create -n marker python=3.10.0
conda activate marker

# 安装解析服务依赖
pip install marker-pdf
pip install -U uvicorn fastapi python-multipart
```  


## 📡 快速启动流程  

### 第一步：启动PDF解析服务  
```bash
marker_server --port 2675
```  
**服务状态提示**：  
启动后可通过 `http://localhost:2675/marker` 访问API交互文档  


### 第二步：运行主程序生成知识图谱  
```bash
python graph_search.py
```  
**输出结果说明**：  
- 控制台实时显示图谱构建进度条  
- 最终生成的催化剂合成流程可视化图表存储于 `papersavings/` 目录  


## 🤖 大模型配置自定义  

如需更换LLM模型，修改以下核心参数（支持多模型协同工作）：  
```python
# 路径：graph_utils/graph_generate_bak.py
class Knowledge_Graph:
    def __init__(self):
        # 核心图谱生成模型（建议使用GPT-4系列）
        self.graphllm = ChatOpenAI(temperature=0, model_name="gpt-4.1-2025-04-14")
        # 轻量级推理模型（用于快速参数推断）
        self.reasonllm = ChatOpenAI(model_name="o3-mini")
        # 优化调参专用模型
        self.minillm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
``` 

## 📁 项目目录结构  

```
fischer-tropsch/
├── graph_utils/            # 知识图谱核心模块
│   ├── chatgpt/            # OpenAI接口配置文件夹
│   └── graph_generate_bak.py  # 图谱构建主逻辑文件
├── papersavings/           # 结果存储目录（自动生成）
├── freeze.yml              # Conda环境依赖文件
├── graph_search.py         # 项目主程序入口
└── origin_paper/           # 待解析文献目录
    └── more_paper/         # 扩展文献存储文件夹
```  


## 📝 待解析文献配置  

如需修改待处理文献路径，调整以下参数：  
```python
# 路径：graph_search.py 第146行
文献路径 = "./origin_paper/more_paper/"
# 可修改为自定义文献存储目录
```  


## 🚦 快速上手提示  

1. **首次运行前检查**：  
   ▶️ 确保Neo4j服务已启动（默认端口7687）  
   ▶️ 确认OpenAI API密钥已正确写入`config.yaml`  

2. **PDF解析常见问题**：  
   ⚠️ 若解析失败，尝试升级`marker-pdf`到最新版本：  
   ```bash
   pip install marker-pdf --upgrade
   ```  

3. **大模型调用优化**：  
   🌐 国内用户可配置代理服务器（修改`config.yaml`中的`proxy`字段）  


## 🌟 项目特色功能  

- 🧠 基于知识图谱的催化剂设计推荐系统  
- ⚙️ 自动生成实验报告与参数敏感性分析  


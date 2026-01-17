# FastAPI 科学助手使用说明文档

## 📋 项目概述

本FastAPI应用是一个科学文献处理平台，名为"Sci Assistant"，专门用于上传PDF文档并自动生成规范的Protocol报告。该系统支持多领域的学术文献处理，包括费托合成(FT)、双相不锈钢(DSS)、加氢甲酰化反应(Hydroformylation)、海水淡化(OWS)等领域。

## 🚀 快速启动

### 环境要求
- Python 3.10+
- FastAPI
- 依赖包：见 `requirements.txt`

### 启动服务
```bash
python fastapi_app.py
```

服务启动后将在端口30800运行，可通过以下地址访问：
- 本地访问: http://localhost:30800
- 网络访问: http://your-ip:30800
- API文档: http://localhost:30800/docs

## 📚 API 端点详细说明

### 1. 首页和页面路由

#### 1.1 首页
- **端点**: `GET /`
- **功能**: 显示主页面，包含文件上传界面和已生成报告列表
- **返回**: HTML页面

**请求示例**:
```bash
curl -X GET "http://localhost:30800/"
```

#### 1.2 报告列表页面
- **端点**: `GET /reports`
- **功能**: 显示所有已生成的报告列表
- **返回**: HTML页面

**请求示例**:
```bash
curl -X GET "http://localhost:30800/reports"
```

#### 1.3 领域上传页面
- **端点**: `GET /domain-upload`
- **功能**: 显示新增支持领域的页面
- **返回**: HTML页面

**请求示例**:
```bash
curl -X GET "http://localhost:30800/domain-upload"
```

### 2. 领域管理API

#### 2.1 获取支持的领域列表
- **端点**: `GET /api/domains`
- **功能**: 获取当前系统支持的所有研究领域
- **返回**: JSON格式的领域列表

**请求示例**:
```bash
curl -X GET "http://localhost:30800/api/domains"
```

**响应示例**:
```json
{
  "domains": {
    "FT": "费托合成",
    "DSS": "双相不锈钢",
    "Hydroformylation": "加氢甲酰化反应",
    "OWS": "海水淡化"
  }
}
```

#### 2.2 重新加载领域配置
- **端点**: `POST /api/domains/reload`
- **功能**: 重新从配置文件加载支持的领域列表
- **返回**: 操作结果和更新后的领域列表

**请求示例**:
```bash
curl -X POST "http://localhost:30800/api/domains/reload"
```

**响应示例**:
```json
{
  "status": "success",
  "message": "成功重新加载支持的领域配置",
  "domains": {
    "FT": "费托合成",
    "DSS": "双相不锈钢"
  }
}
```

#### 2.3 获取领域配置信息
- **端点**: `GET /api/domains/config-info`
- **功能**: 获取领域配置文件的详细信息
- **返回**: 配置文件信息

**请求示例**:
```bash
curl -X GET "http://localhost:30800/api/domains/config-info"
```

### 3. 文件上传API

#### 3.1 上传PDF文件
- **端点**: `POST /upload`
- **功能**: 上传一个或多个PDF文件到服务器
- **参数**: 
  - `files`: 文件列表（multipart/form-data）
- **限制**: 
  - 文件大小：最大100MB
  - 文件格式：仅支持PDF
- **返回**: 上传结果和文件信息

**请求示例**:
```bash
# 上传单个文件
curl -X POST "http://localhost:30800/upload" \
  -F "files=@/path/to/your/document.pdf"

# 上传多个文件
curl -X POST "http://localhost:30800/upload" \
  -F "files=@/path/to/document1.pdf" \
  -F "files=@/path/to/document2.pdf"
```

**响应示例**:
```json
{
  "status": "success",
  "message": "成功上传 2 个文件",
  "files": [
    {
      "original_name": "document1.pdf",
      "saved_path": "uploads/document1.pdf"
    },
    {
      "original_name": "document2.pdf", 
      "saved_path": "uploads/document2.pdf"
    }
  ]
}
```

#### 3.2 上传大纲文件并生成提示词
- **端点**: `POST /upload-outline`
- **功能**: 上传研究领域大纲文件，自动提取主题并生成对应的提示词
- **参数**:
  - `file`: 大纲文件（.md或.txt格式）
- **返回**: 上传结果和提示词生成结果

**请求示例**:
```bash
curl -X POST "http://localhost:30800/upload-outline" \
  -F "file=@/path/to/Duplex_Stainless_Steel.md"
```

**响应示例**:
```json
{
  "status": "success",
  "message": "成功上传大纲文件并生成 'Duplex Stainless Steel' 领域的提示词",
  "subject": "Duplex Stainless Steel",
  "outline_file": "./outline_Duplex_Stainless_Steel.md",
  "prompt_generation_result": {
    "success": true,
    "subject": "Duplex Stainless Steel",
    "files_generated": [
      "template/deepseek/DSS_kg_prompt.md",
      "template/deepseek/DSS.md"
    ],
    "error": null,
    "error_type": null
  }
}
```

### 4. 报告生成API

#### 4.1 生成报告
- **端点**: `POST /generate`
- **功能**: 基于上传的PDF文件生成研究报告
- **参数**:
  - `files`: 文件路径列表
  - `domain`: 研究领域（如"FT", "DSS"等）
- **返回**: 生成结果和报告信息

**请求示例**:
```bash
curl -X POST "http://localhost:30800/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "files": ["uploads/document1.pdf", "uploads/document2.pdf"],
    "domain": "DSS"
  }'
```

**Python客户端示例**:
```python
import requests

url = "http://localhost:30800/generate"
data = {
    "files": ["uploads/document1.pdf", "uploads/document2.pdf"],
    "domain": "DSS"
}

response = requests.post(url, json=data)
result = response.json()
print(result)
```

**响应示例**:
```json
{
  "status": "success",
  "message": "成功处理 2 个文件，失败 0 个文件，删除 2 个PDF文件",
  "report_id": "document1",
  "report_path": "papersavings/DSS/document1.md"
}
```

### 5. 报告管理API

#### 5.1 查看报告
- **端点**: `GET /report/{domain}/{report_id}`
- **功能**: 查看指定领域和ID的报告内容
- **参数**:
  - `domain`: 研究领域
  - `report_id`: 报告ID
- **返回**: HTML页面显示报告内容

**请求示例**:
```bash
curl -X GET "http://localhost:30800/report/DSS/document1"
```

#### 5.2 保存报告
- **端点**: `POST /save_report`
- **功能**: 保存编辑后的报告内容
- **参数**:
  - `report_id`: 报告ID
  - `content`: 报告内容
- **返回**: 保存结果

**请求示例**:
```bash
curl -X POST "http://localhost:30800/save_report" \
  -H "Content-Type: application/json" \
  -d '{
    "report_id": "document1",
    "content": "# 更新后的报告内容\n\n这是编辑后的报告..."
  }'
```

**响应示例**:
```json
{
  "status": "success",
  "message": "报告保存成功"
}
```

### 6. 提示词生成API

#### 6.1 检查提示词生成功能状态
- **端点**: `GET /api/prompt-generation/status`
- **功能**: 检查提示词生成功能是否可用
- **返回**: 功能状态和支持的领域

**请求示例**:
```bash
curl -X GET "http://localhost:30800/api/prompt-generation/status"
```

**响应示例**:
```json
{
  "status": "success",
  "message": "提示词生成功能可用",
  "available": true,
  "supported_domains": ["FT", "DSS", "Hydroformylation", "OWS"]
}
```

#### 6.2 为现有主题生成提示词
- **端点**: `POST /generate-prompts`
- **功能**: 为已存在大纲文件的主题生成提示词
- **参数**:
  - `subject`: 主题名称
  - `use_deepseek`: 是否使用DeepSeek模型（可选，默认true）
- **返回**: 生成结果

**请求示例**:
```bash
curl -X POST "http://localhost:30800/generate-prompts" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Duplex Stainless Steel",
    "use_deepseek": true
  }'
```

**响应示例**:
```json
{
  "success": true,
  "subject": "Duplex Stainless Steel",
  "files_generated": [
    "template/deepseek/DSS_kg_prompt.md",
    "template/deepseek/DSS.md"
  ],
  "error": null,
  "error_type": null
}
```

### 7. 提示词文件管理API

#### 7.1 获取生成文件列表
- **端点**: `GET /api/prompts/generated-files/{subject}`
- **功能**: 获取某个主题生成的所有提示词文件列表
- **参数**:
  - `subject`: 主题名称
- **返回**: 包含文件信息的列表（模板、知识图谱提示词）

**请求示例**:
```bash
curl -X GET "http://localhost:30800/api/prompts/generated-files/Duplex%20Stainless%20Steel"
```

**响应示例**:
```json
{
  "status": "success",
  "message": "成功获取 'Duplex Stainless Steel' 的生成文件列表",
  "subject": "Duplex Stainless Steel",
  "files": [
    {
      "type": "template",
      "name": "实验提取模板",
      "path": "./template/Duplex Stainless Steel.md",
      "exists": true,
      "size": 15234
    },
    {
      "type": "kg_prompt",
      "name": "知识图谱提示词",
      "path": "./graph_utils/Duplex Stainless Steel_kg_prompt.md",
      "exists": true,
      "size": 8456
    }
  ]
}
```

#### 7.2 获取文件内容
- **端点**: `GET /api/prompts/file-content/{subject}/{file_type}`
- **功能**: 读取指定提示词文件的内容
- **参数**:
  - `subject`: 主题名称
  - `file_type`: 文件类型（template | kg_prompt）
- **返回**: 文件内容

**请求示例**:
```bash
curl -X GET "http://localhost:30800/api/prompts/file-content/Duplex%20Stainless%20Steel/template"
```

**响应示例**:
```json
{
  "status": "success",
  "message": "成功读取文件内容",
  "subject": "Duplex Stainless Steel",
  "file_type": "template",
  "file_path": "./template/Duplex Stainless Steel.md",
  "content": "# Duplex Stainless Steel 实验提取模板\n\n## 1. 材料准备\n..."
}
```

#### 7.3 保存文件
- **端点**: `POST /api/prompts/save-file`
- **功能**: 保存编辑后的提示词文件
- **参数**:
  - `subject`: 主题名称
  - `file_type`: 文件类型（template | kg_prompt）
  - `content`: 文件内容
- **返回**: 保存结果

**请求示例**:
```bash
curl -X POST "http://localhost:30800/api/prompts/save-file" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Duplex Stainless Steel",
    "file_type": "template",
    "content": "# 更新后的模板内容\n\n..."
  }'
```

**响应示例**:
```json
{
  "status": "success",
  "message": "成功保存 'Duplex Stainless Steel' 的 template 文件",
  "file_path": "./template/Duplex Stainless Steel.md"
}
```

#### 7.4 提示词管理页面
- **端点**: `GET /prompts-manager`
- **功能**: 显示提示词文件管理页面
- **返回**: HTML页面

**功能特性**:
- 选择领域查看生成的文件列表
- 显示文件状态（已生成/未生成）
- 显示文件大小和路径
- 提供查看/编辑和下载按钮

**请求示例**:
```bash
curl -X GET "http://localhost:30800/prompts-manager"
```

#### 7.5 提示词编辑器页面
- **端点**: `GET /prompts-editor/{subject}/{file_type}`
- **功能**: 显示提示词文件编辑器页面
- **参数**:
  - `subject`: 主题名称
  - `file_type`: 文件类型
- **返回**: HTML页面

**功能特性**:
- 左侧编辑器：编辑文件内容
- 右侧预览：实时预览Markdown或JSON
- 显示字符数和行数统计
- 支持Ctrl+S快捷键保存
- 离开页面时提示未保存的更改

**请求示例**:
```bash
curl -X GET "http://localhost:30800/prompts-editor/Duplex%20Stainless%20Steel/template"
```

## 🔧 数据模型

### ReportRequest
```json
{
  "files": ["string"],  // 文件路径列表
  "domain": "string"    // 研究领域，默认"FT"
}
```

### ReportResponse
```json
{
  "status": "string",        // 状态：success/error
  "message": "string",       // 消息描述
  "report_id": "string",     // 报告ID（可选）
  "report_path": "string"    // 报告路径（可选）
}
```

### SaveReportRequest
```json
{
  "report_id": "string",  // 报告ID
  "content": "string"     // 报告内容
}
```

### PromptGenerationRequest
```json
{
  "subject": "string",      // 主题名称
  "use_deepseek": boolean   // 是否使用DeepSeek（可选）
}
```

### SavePromptFileRequest
```json
{
  "subject": "string",      // 主题名称
  "file_type": "string",    // 文件类型：template | kg_prompt
  "content": "string"       // 文件内容
}
```

### GeneratedFilesResponse
```json
{
  "status": "string",       // 状态：success/error
  "message": "string",      // 消息描述
  "subject": "string",      // 主题名称（可选）
  "files": [                // 文件列表（可选）
    {
      "type": "string",     // 文件类型
      "name": "string",     // 文件名称
      "path": "string",     // 文件路径
      "exists": boolean,    // 是否存在
      "size": number        // 文件大小（字节）
    }
  ]
}
```

## 🛠️ 完整工作流程示例

### 1. 完整的文档处理流程

```python
import requests
import json

base_url = "http://localhost:30800"

# 步骤1: 检查支持的领域
response = requests.get(f"{base_url}/api/domains")
domains = response.json()["domains"]
print("支持的领域:", domains)

# 步骤2: 上传PDF文件
files = [
    ('files', ('document1.pdf', open('path/to/document1.pdf', 'rb'), 'application/pdf')),
    ('files', ('document2.pdf', open('path/to/document2.pdf', 'rb'), 'application/pdf'))
]
response = requests.post(f"{base_url}/upload", files=files)
upload_result = response.json()
print("上传结果:", upload_result)

# 步骤3: 生成报告
generate_data = {
    "files": [file["saved_path"] for file in upload_result["files"]],
    "domain": "DSS"
}
response = requests.post(f"{base_url}/generate", json=generate_data)
generate_result = response.json()
print("生成结果:", generate_result)

# 步骤4: 查看生成的报告（通过浏览器访问）
if generate_result["status"] == "success":
    report_url = f"{base_url}/report/DSS/{generate_result['report_id']}"
    print(f"报告查看地址: {report_url}")
```

### 2. 新增研究领域流程

```python
import requests

base_url = "http://localhost:30800"

# 步骤1: 上传新领域的大纲文件
with open('path/to/New_Research_Area.md', 'rb') as f:
    files = {'file': ('New_Research_Area.md', f, 'text/markdown')}
    response = requests.post(f"{base_url}/upload-outline", files=files)
    result = response.json()
    print("大纲上传结果:", result)

# 步骤2: 检查更新后的领域列表
response = requests.get(f"{base_url}/api/domains")
updated_domains = response.json()["domains"]
print("更新后的领域:", updated_domains)

# 步骤3: 使用新领域处理文档
# ... 继续使用上面的文档处理流程
```

### 3. 提示词文件管理流程

```python
import requests

base_url = "http://localhost:30800"
subject = "Duplex Stainless Steel"

# 步骤1: 获取生成的文件列表
response = requests.get(f"{base_url}/api/prompts/generated-files/{subject}")
files_info = response.json()
print("生成的文件:", files_info)

# 步骤2: 读取模板文件内容
response = requests.get(f"{base_url}/api/prompts/file-content/{subject}/template")
file_content = response.json()
print("文件内容长度:", len(file_content["content"]))

# 步骤3: 编辑并保存文件
updated_content = file_content["content"] + "\n\n## 新增章节\n..."
save_data = {
    "subject": subject,
    "file_type": "template",
    "content": updated_content
}
response = requests.post(f"{base_url}/api/prompts/save-file", json=save_data)
save_result = response.json()
print("保存结果:", save_result)

# 步骤4: 通过浏览器访问管理页面
print(f"管理页面: {base_url}/prompts-manager")
print(f"编辑器页面: {base_url}/prompts-editor/{subject}/template")
```

### 4. 完整的领域扩展和管理流程

```python
import requests

base_url = "http://localhost:30800"

# 步骤1: 上传新领域大纲并生成提示词
with open('Duplex_Stainless_Steel.md', 'rb') as f:
    files = {'file': ('Duplex_Stainless_Steel.md', f, 'text/markdown')}
    response = requests.post(f"{base_url}/upload-outline", files=files)
    result = response.json()
    subject = result["subject"]
    print(f"新领域 '{subject}' 创建成功")

# 步骤2: 查看生成的提示词文件
response = requests.get(f"{base_url}/api/prompts/generated-files/{subject}")
files = response.json()["files"]
for file in files:
    print(f"- {file['name']}: {file['path']} ({file['size']} bytes)")

# 步骤3: 编辑模板文件（通过API或浏览器）
# 方式A: 通过API编辑
response = requests.get(f"{base_url}/api/prompts/file-content/{subject}/template")
content = response.json()["content"]
# 修改内容...
modified_content = content.replace("旧内容", "新内容")
requests.post(f"{base_url}/api/prompts/save-file", json={
    "subject": subject,
    "file_type": "template",
    "content": modified_content
})

# 方式B: 通过浏览器编辑
print(f"浏览器编辑: {base_url}/prompts-editor/{subject}/template")

# 步骤4: 使用新领域处理PDF文档
files_to_upload = [
    ('files', ('paper1.pdf', open('paper1.pdf', 'rb'), 'application/pdf'))
]
response = requests.post(f"{base_url}/upload", files=files_to_upload)
uploaded = response.json()

# 生成报告
generate_data = {
    "files": [f["saved_path"] for f in uploaded["files"]],
    "domain": subject
}
response = requests.post(f"{base_url}/generate", json=generate_data)
print("报告生成结果:", response.json())
```

## ⚠️ 注意事项

### 文件上传和处理
1. **文件大小限制**: 单个文件最大100MB
2. **支持格式**: 仅支持PDF格式的文档上传
3. **大纲文件格式**: 支持.md和.txt格式
4. **服务依赖**: 需要PDF解析服务在端口2675运行
5. **文件清理**: 成功处理后原始PDF文件会被自动删除
6. **并发处理**: 系统支持多文件并发处理

### 提示词文件管理
7. **文件编码**: 所有提示词文件使用UTF-8编码
8. **保存前确认**: 离开编辑器页面前会提示未保存的更改
9. **实时生效**: 保存后的提示词立即可用于PDF处理
10. **备份建议**: 重要修改前建议先备份原文件
11. **文件类型**: 支持编辑模板文件(template)和知识图谱提示词(kg_prompt)
12. **预览功能**: 编辑器支持实时Markdown预览

## 🔍 错误处理

常见错误及解决方案：

### 400 Bad Request
- 检查请求参数是否正确
- 确认文件格式是否支持
- 验证领域名称是否存在

### 404 Not Found
- 检查文件路径是否正确
- 确认报告ID是否存在
- 验证大纲文件是否已上传
- 确认提示词文件是否已生成

### 500 Internal Server Error
- 检查PDF解析服务是否运行
- 确认依赖模块是否正确安装
- 查看服务器日志获取详细错误信息
- 验证提示词文件路径和权限

## 📊 生成的文件类型

### 提示词文件结构

系统为每个新领域生成以下文件：

1. **实验提取模板 (template)**
   - 路径: `./template/{subject}.md`
   - 格式: Markdown
   - 内容: 详细的实验提取指南和格式要求

2. **知识图谱提示词 (kg_prompt)**
   - 路径: `./graph_utils/{subject}_kg_prompt.md`
   - 格式: Markdown
   - 内容: 知识图谱节点和关系提取规则

## 📞 技术支持

如需技术支持或有问题反馈，请查看：
- **API文档**: http://localhost:30800/docs
- **提示词管理**: http://localhost:30800/prompts-manager
- **领域上传**: http://localhost:30800/domain-upload
- **报告列表**: http://localhost:30800/reports
- **项目README**: readme.md
- **日志文件**: app.log

---

*本文档基于FastAPI应用版本生成，如有更新请及时同步文档内容。*

# 提示词文件管理功能说明

## 功能概述

为"上传大纲文件并生成提示词"功能新增了查看、编辑和保存生成的提示词文件的能力。

## 新增的API端点

### 1. 获取生成文件列表
- **路径**: GET /api/prompts/generated-files/{subject}
- **功能**: 获取某个主题生成的所有提示词文件列表
- **返回**: 包含3个文件的信息（模板、知识图谱提示词、配置文件）

### 2. 获取文件内容
- **路径**: GET /api/prompts/file-content/{subject}/{file_type}
- **功能**: 读取指定提示词文件的内容
- **参数**: 
  - subject: 主题名称
  - file_type: template | kg_prompt | prompts_config

### 3. 保存文件
- **路径**: POST /api/prompts/save-file
- **功能**: 保存编辑后的提示词文件
- **请求体**:
```json
{
  "subject": "主题名称",
  "file_type": "文件类型",
  "content": "文件内容"
}
```

## 新增的页面

### 1. 提示词管理页面
- **路径**: /prompts-manager
- **功能**: 
  - 选择领域查看生成的文件列表
  - 显示文件状态（已生成/未生成）
  - 显示文件大小和路径
  - 提供查看/编辑和下载按钮

### 2. 提示词编辑器页面
- **路径**: /prompts-editor/{subject}/{file_type}
- **功能**:
  - 左侧编辑器：编辑文件内容
  - 右侧预览：实时预览Markdown或JSON
  - 显示字符数和行数统计
  - 支持Ctrl+S快捷键保存
  - 离开页面时提示未保存的更改

## 使用流程

### 完整工作流程

1. **上传大纲文件**
   - 访问 /domain-upload
   - 上传新领域的大纲文件（如 "Duplex Stainless Steel.md"）
   - 系统自动生成3个提示词文件

2. **查看生成的文件**
   - 访问 /prompts-manager
   - 从下拉菜单选择领域
   - 查看生成的文件列表和状态

3. **编辑文件**
   - 点击"查看/编辑"按钮
   - 在编辑器中修改内容
   - 右侧实时预览效果
   - 点击"保存"按钮或按Ctrl+S保存

4. **使用提示词**
   - 保存后的提示词文件会立即生效
   - 可用于处理该领域的PDF文档

## 技术特点

### 前端特性
- 响应式设计，适配不同屏幕
- 实时Markdown预览（使用marked.js）
- JSON格式化显示
- 编辑器统计信息
- 保存状态提示
- 未保存提醒

### 后端特性
- RESTful API设计
- 文件存在性检查
- 错误处理和异常捕获
- 自动创建目录
- UTF-8编码支持

## 生成的文件类型

### 1. 实验提取模板 (template)
- **路径**: ./template/{subject}.md
- **格式**: Markdown
- **内容**: 详细的实验提取指南和格式要求

### 2. 知识图谱提示词 (kg_prompt)
- **路径**: ./graph_utils/{subject}_kg_prompt.md
- **格式**: Markdown
- **内容**: 知识图谱节点和关系提取规则

### 3. 应用提示词配置 (prompts_config)
- **路径**: ./graph_utils/chatgpt/config/prompts_config_{subject}.json
- **格式**: JSON
- **内容**: 分解提示词、摘要生成等配置

## 示例

### API调用示例

```javascript
// 获取文件列表
const response = await fetch('/api/prompts/generated-files/Duplex Stainless Steel');
const data = await response.json();

// 获取文件内容
const content = await fetch('/api/prompts/file-content/Duplex Stainless Steel/template');
const fileData = await content.json();

// 保存文件
await fetch('/api/prompts/save-file', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    subject: 'Duplex Stainless Steel',
    file_type: 'template',
    content: '修改后的内容'
  })
});
```

## 注意事项

1. **文件编码**: 所有文件使用UTF-8编码
2. **保存前确认**: 离开页面前会提示未保存的更改
3. **实时生效**: 保存后的提示词立即可用于PDF处理
4. **备份建议**: 重要修改前建议先备份原文件
5. **JSON格式**: 编辑prompts_config时注意JSON语法正确性

## 访问入口

- 主页导航栏
- 领域上传成功后的提示
- 直接访问: http://localhost:30800/prompts-manager

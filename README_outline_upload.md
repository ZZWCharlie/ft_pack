# 大纲文件上传和提示词生成功能

本文档介绍了新增的大纲文件上传和提示词生成功能，该功能允许用户上传大纲文件并自动生成对应领域的提示词。

## 新增功能概述

### 主要特性
1. **文件上传和重命名**：上传文件（如 "Duplex Stainless Steel.md"），自动提取subject并重命名为 `outline_{subject}.md`
2. **自动提示词生成**：调用 `change_prompt_DSS.py` 的 `generate_prompts_api` 函数生成提示词
3. **智能领域管理**：只有在提示词生成成功后才更新 `SUPPORTED_DOMAINS` 列表，确保数据一致性
4. **完整错误处理**：提供详细的错误信息和状态反馈

## 新增API接口

### 1. 大纲文件上传接口

**POST** `/upload-outline`

上传大纲文件并自动生成提示词。

**请求参数：**
- `file`: 上传的文件（支持 .md 和 .txt 格式）

**响应示例：**
```json
{
  "status": "success",
  "message": "成功上传大纲文件并生成 'Duplex Stainless Steel' 领域的提示词",
  "subject": "Duplex Stainless Steel",
  "outline_file": "./outline_Duplex Stainless Steel.md",
  "prompt_generation_result": {
    "success": true,
    "subject": "Duplex Stainless Steel",
    "files_generated": {
      "template_file": "./template/Duplex Stainless Steel.md",
      "kg_prompt_file": "./graph_utils/Duplex Stainless Steel_kg_prompt.md",
      "prompts_config_file": "./graph_utils/chatgpt/config/prompts_config_Duplex Stainless Steel.json"
    },
    "error": null,
    "error_type": null
  }
}
```

### 2. 提示词生成接口

**POST** `/generate-prompts`

为已存在的主题生成提示词（要求对应的大纲文件已存在）。

**请求体：**
```json
{
  "subject": "Duplex Stainless Steel",
  "use_deepseek": true
}
```

**响应示例：**
```json
{
  "success": true,
  "subject": "Duplex Stainless Steel",
  "files_generated": {
    "template_file": "./template/Duplex Stainless Steel.md",
    "kg_prompt_file": "./graph_utils/Duplex Stainless Steel_kg_prompt.md",
    "prompts_config_file": "./graph_utils/chatgpt/config/prompts_config_Duplex Stainless Steel.json"
  },
  "generated_content": {
    "new_outlines": "...",
    "new_subject_template": "...",
    "new_subject_nodes_rels": "...",
    "new_subject_kg_prompt": "...",
    "new_subject_summary": "..."
  },
  "error": null,
  "error_type": null
}
```

### 3. 提示词生成状态接口

**GET** `/api/prompt-generation/status`

获取提示词生成功能的状态和支持的领域列表。

**响应示例：**
```json
{
  "status": "success",
  "message": "提示词生成功能可用",
  "available": true,
  "supported_domains": ["FT", "MoF", "Duplex Stainless Steel"]
}
```

## 使用流程

### 方式一：文件上传 + 自动生成
1. 准备大纲文件（如 "Duplex Stainless Steel.md"）
2. 调用 `/upload-outline` 接口上传文件
3. 系统自动：
   - 提取subject："Duplex Stainless Steel"
   - 重命名文件为：`outline_Duplex Stainless Steel.md`
   - 调用提示词生成功能
   - **仅在提示词生成成功后**更新支持的领域列表

### 方式二：手动生成（大纲文件已存在）
1. 确保对应的 `outline_{subject}.md` 文件存在
2. 调用 `/generate-prompts` 接口
3. 传入subject参数生成提示词

## 生成的文件

成功执行后会生成以下文件：

1. **大纲文件**：`outline_{subject}.md`
   - 用户上传的原始大纲内容

2. **模板文件**：`./template/{subject}.md`
   - 实验提取模板

3. **知识图谱提示词**：`./graph_utils/{subject}_kg_prompt.md`
   - 知识图谱生成指令

4. **提示词配置**：`./graph_utils/chatgpt/config/prompts_config_{subject}.json`
   - 应用提示词配置

## 错误处理

### 常见错误情况
1. **提示词生成功能不可用**
   - 状态码：503
   - 原因：change_prompt_DSS模块导入失败

2. **文件格式不支持**
   - 状态码：400
   - 原因：上传的文件不是.md或.txt格式

3. **大纲文件不存在**
   - 状态码：404
   - 原因：调用 `/generate-prompts` 时对应的大纲文件不存在

4. **文件名无效**
   - 状态码：400
   - 原因：无法从文件名提取有效的subject

### 错误响应示例
```json
{
  "status": "error",
  "message": "不支持的文件格式，请上传.md或.txt文件",
  "subject": null,
  "outline_file": null,
  "prompt_generation_result": null
}
```

## 前端集成示例

### JavaScript 文件上传
```javascript
async function uploadOutlineFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/upload-outline', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            console.log('上传成功:', result.subject);
            console.log('生成的文件:', result.prompt_generation_result.files_generated);
        } else {
            console.error('上传失败:', result.message);
        }
    } catch (error) {
        console.error('请求失败:', error);
    }
}
```

### HTML 表单示例
```html
<form id="outline-upload-form" enctype="multipart/form-data">
    <div>
        <label for="outline-file">选择大纲文件：</label>
        <input type="file" id="outline-file" name="file" accept=".md,.txt" required>
    </div>
    <button type="submit">上传并生成提示词</button>
</form>

<script>
document.getElementById('outline-upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('outline-file');
    const file = fileInput.files[0];
    
    if (file) {
        await uploadOutlineFile(file);
    }
});
</script>
```

## 注意事项

1. **文件命名规范**：文件名应该清晰地表达主题，避免特殊字符
2. **文件大小限制**：建议大纲文件不超过10MB
3. **并发处理**：提示词生成过程可能需要较长时间，建议使用异步处理
4. **权限控制**：生产环境中建议添加适当的权限验证
5. **文件备份**：重要的大纲文件建议做好备份
6. **领域更新逻辑**：系统只有在提示词生成完全成功后才会将新领域添加到支持列表中，避免不完整的配置

## 测试建议

### 测试用例
1. 上传正常的.md文件
2. 上传.txt文件
3. 上传不支持的文件格式
4. 上传空文件
5. 文件名包含特殊字符的情况
6. 重复上传相同主题的文件
7. 在change_prompt_DSS模块不可用时的错误处理

### 性能测试
- 大文件上传测试
- 并发上传测试
- 提示词生成时间测试

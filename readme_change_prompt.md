# README: 提示词使用指南  
## 概述  
本文档旨在说明如何使用四个核心提示词（大提示词、问题提示词、知识图提示词、摘要提示词）。只需替换每个提示词中的「新主题占位符」，即可通过大模型生成对应主题的结构化内容。  


## 一、核心提示词及替换位置  

### 1. 大提示词（主题迁移框架提示词）  
- **用途**：指导大模型基于范例迁移逻辑，生成新主题的基础框架。  
- **需替换的占位符**：`{subject}`  
- **位置**：直接替换目标文件内容  
  ```  
  ./template/FT/ft.md  
  ```  


### 2. 问题提示词（实验问题生成提示词）  
- **用途**：生成新主题的标准化问题列表（如实验要素、步骤等）。  
- **需替换的占位符**：`{subject}`  
- **位置**：替换指定JSON文件中对应key的内容  
  - 文件路径：  
    ```  
    ./graph_utils/chatgpt/config/prompts_config.json  
    ```  
  - 关联代码引用：  
    ```python  
    from graph_utils.chatgpt.config.config import (  
        GENERAL_CONFIG,  
        OPENAI_CONFIG,  
        ARXIV_CONFIG,  
        NOUGAT_CONFIG,  
        LOGGER_MODES,  
        APPLICATION_PROMPTS,  # 对应JSON配置需替换  
    )  
    ```  
  - 需替换的JSON key列表（已在`change_prompt.py`中定义）：  
    ```python  
    example_dict = [  
        "reagents_questions",  
        "specific_equipment_questions",  
        "common_equipment_questions",  
        "synthesis_method_questions",  
        "reagents_preparation_questions",  
        "detailed_steps_questions",  
        "characterization_questions",  
        "activation_questions",  
        "reaction_questions",  
        "characterization_results_questions",  
        "catalyst_performance_questions"  
    ]  
    ```  


### 3. 知识图提示词（知识图谱生成说明提示词）  
- **用途**：生成新主题的知识图谱节点、关系及规则说明。  
- **需替换的占位符**：`{subject}`  
- **位置**：替换指定Python文件中的字符串片段  
  ```  
  ./graph_utils/graph_generate_bak.py （从378行开始的字符串）  
  ```  


### 4. 摘要提示词（论文摘要提取提示词）  
- **用途**：生成新主题的结构化论文摘要。  
- **需替换的占位符**：`{subject}`  
- **位置**：替换`prompts_config.json`中对应key的内容  
  - 目标JSON key：`"ft_summary_generation_simplified"`  


## 二、使用步骤  
1. **确定新主题**：明确目标主题（如“锂电池研发”“光伏材料测试”“Metal organic framework (MOF) materials”）。  
2. **替换占位符**：在上述四个提示词中，将所有`{subject}`替换为具体新主题。  
   - 快捷替换：直接修改`change_prompt.py`文件第14行即可批量更新。  


## 三、注意事项  
- 确保`{subject}`替换为清晰具体的主题名称（如避免使用模糊表述“材料研发”，建议细化为“纳米催化剂材料研发”）。  
- 需将`change_prompt.py`与`question_and_other.json`文件放置在`graph_search.py`的同一目录下，确保脚本正常运行。  
- 替换后建议检查文件路径和JSON key是否匹配，避免遗漏未更新的占位符。  
  
## 四、**日志配置补充**：  
- `save_chat.py`需保存在与`./graph_utils/graph_generate_bak.py`相同的目录中。  
- 在`./graph_utils/graph_generate_bak.py`中添加导入语句：  
  ```python  
  from .save_chat import logging_handler  
  ```  
- 在`chat`函数中为LLM实例添加日志回调：  
  ```python  
  self.graphllm = ChatOpenAI(temperature=0, model_name="gpt-4.1-2025-04-14", callbacks=[logging_handler])  
  self.reasonllm = ChatOpenAI(model_name="o3-mini", callbacks=[logging_handler])  
  self.minillm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", callbacks=[logging_handler])  
  ```
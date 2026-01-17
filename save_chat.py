from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult
import asyncio
import uuid
import json
from datetime import datetime

class AsyncLoggingCallbackHandler(AsyncCallbackHandler):
    def __init__(self, save_path="conversation_logs.jsonl"):
        self.save_path = save_path
        self._current_inputs = {}

    # ✅ 支持标准 LLM（非 chat）
    async def on_llm_start(self, serialized, prompts, run_id, **kwargs):
        self._current_inputs[run_id] = prompts

    # ✅ 支持 Chat 模型（如 ChatOpenAI）
    async def on_chat_model_start(self, serialized, messages, run_id, **kwargs):
        # print(messages[0][0].content)
        self._current_inputs[run_id] = messages

    async def on_llm_end(self, response: LLMResult, run_id, **kwargs):
        input_record = self._current_inputs.pop(run_id, None)

        # 提取 output 文本
        output = response.generations[0][0].text if response.generations else ""
        if output == "":
            output = str(response.generations[0][0].message.additional_kwargs['tool_calls'][0]['function']['arguments'])
        # output = str(response)

        record = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "input": input_record[0][0].content,
            "output": output,
        }
        asyncio.create_task(self._async_save(record))

    async def _async_save(self, record: dict):
        try:
            async with asyncio.Lock():
                with open(self.save_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[ERROR] 保存记录失败: {e}")
# 创建一个记录 handler
logging_handler = AsyncLoggingCallbackHandler("chat_log.jsonl")
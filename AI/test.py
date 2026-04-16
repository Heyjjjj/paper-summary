from openai import OpenAI
import os

client = OpenAI(
    api_key='sk-95efe5f35b934a9e9114d2daad4d7d8a',
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
)

response = client.chat.completions.create(
    model="qwen3.5-plus",
    messages=[
        {"role":"system","content":"你是一个ai助理"},
        #{"role":"assisant","content":"你是ai助理"},
        {"role":"user","content":"帮我对ai算法工程师需要的技能进行分析和展示"},
    ],
    stream=True
)
is_answering = False  # 是否进入回复阶段
for chunk in response:
    delta = chunk.choices[0].delta
    if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
        if not is_answering:
            print(delta.reasoning_content, end="", flush=True)
    if hasattr(delta, "content") and delta.content:
        if not is_answering:
            print("\n" + "=" * 20 + "完整回复" + "=" * 20)
            is_answering = True
        print(delta.content, end="", flush=True)
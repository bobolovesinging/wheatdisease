import os
from openai import OpenAI


client = OpenAI(
    api_key="2117f26b-14f9-4e56-9b91-fb8b8868c093",
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# Non-streaming:
# print("----- standard request -----")
# completion = client.chat.completions.create(
#     model = "ep-20250227001800-vltb2",  # your model endpoint ID
#     messages = [
#         {"role": "system", "content": "你是人工智能助手"},
#         {"role": "user", "content": "常见的十字花科植物有哪些？"},
#     ],
# )
# print(completion.choices[0].message.content)

# Streaming:
# 打印提示信息，表明接下来要进行流式请求
print("----- streaming request -----")

# 调用 client 对象的 chat.completions.create 方法来创建一个流式对话请求
# 该方法会返回一个可迭代的对象，用于逐块接收模型的响应
stream = client.chat.completions.create(
    # 指定要使用的模型端点 ID，这里的 "ep-20250227001800-vltb2" 是具体的模型标识
    model = "ep-20250227001800-vltb2",  
    # messages 参数是一个列表，用于描述对话的上下文信息
    messages = [
        # 系统消息，用于设定助手的角色和行为，告知模型它是一个人工智能助手
        {"role": "system", "content": "你是人工智能助手"},
        # 用户消息，包含用户提出的具体问题，即询问常见的十字花科植物有哪些
        {"role": "user", "content": "你好？"},
    ],
    # 设置 stream 参数为 True，表示使用流式响应模式
    # 流式响应意味着模型会逐块返回响应内容，而不是一次性返回完整的结果
    stream=True
)

# 遍历 stream 可迭代对象，逐块处理模型返回的响应内容
for chunk in stream:
    # 检查当前的数据块是否包含选择项
    # 如果不包含选择项，说明该数据块可能为空或者无效，跳过本次循环继续处理下一个数据块
    if not chunk.choices:
        continue
    # 打印当前数据块中第一个选择的增量内容
    # end="" 参数用于避免每次打印后换行，从而实现连续输出
    print(chunk.choices[0].delta.content, end="")

# 最后打印一个空行，用于分隔输出结果，使输出更加清晰易读
print()

STARCHAT_QS_QUESTION_GENERATOR_RPROMOPT = '''
你是一个建筑施工行业资深的质量检查员，你能够高精度判别出施工工地中施工质量风险，请根据用户的施工场景图片和隐患内容描述，请生成能够描述该图片场景的1个问题，如下为用户隐患内容描述输入：
隐患内容描述：{content}

请采用如下json格式进行输出：
[
    {
        question:xxx
    }  
]
'''

STARCHAT_QS_ANSWER_GENERATOR_RPROMOPT = '''
你是一个建筑施工行业资深的质量检查员，你能够高精度识别出施工工地中施工质量验收标准，请根据用户的场景图片、隐患内容和用户输入问题进行高质量的回复，需要重点分析出隐患类别、质量分析、整改要求和法规依据
隐患内容：{content1}
用户问题：{content2}
'''


PROMPT_TEST = '''
你是一个智能助手，你能够根据用户输入的时事新闻内容和上下文信息，能够解读其中主要时政问题,解读需要简要清楚，重点指出问题,字数不超过200字,如下为用户提供搜索上下文信息,如果用户输入于该主题不相关，请自己进行回复
{context}
'''


GENERATOR_QA_PROMPT = (
    "<Task> The user will send a long text. Generate a Question and Answer pairs only using the knowledge"
    " in the long text. Please think step by step."
    "Step 1: Understand and summarize the main content of this text.\n"
    "Step 2: What key information or concepts are mentioned in this text?\n"
    "Step 3: Decompose or combine multiple pieces of information and concepts.\n"
    "Step 4: Generate questions and answers based on these key information and concepts.\n"
    "<Constraints> The questions should be clear and detailed, and the answers should be detailed and complete. "
    "You must answer in {language}, in a style that is clear and detailed in {language}."
    " No language other than {language} should be used. \n"
    "<Format> Use the following format: Q1:\nA1:\nQ2:\nA2:...\n"
    "<QA Pairs>"
)

##source:https://github.com/wangxb96/RAG-QA-Generator/blob/main/Code/AutoQAGPro-EN.py
GENERATOR_QA_PROMPT_EN_1 = """Based on the following given text, generate a set of high-quality question-answer pairs. Please follow these guidelines:

1. Question part:
- Create as many different phrasings of questions (e.g., K questions) as you can for the same topic.
- Questions should cover key information and main concepts in the text.
- Use various questioning methods, such as direct inquiries, requests for confirmation, seeking explanations, etc.

2. Answer part:
- Provide a comprehensive, informative answer that covers all possible angles of the questions.
- The answer should be directly based on the given text, ensuring accuracy.
- Include relevant details such as dates, names, positions, and other specific information.

3. Format:
- Use "Q:" to mark the beginning of the question set, all questions should be in one paragraph.
- Use "A:" to mark the beginning of the answer.
- Separate question-answer pairs with a blank line.

4. Content requirements:
- Ensure that the question-answer pairs closely revolve around the text's topic.
- Avoid adding information not mentioned in the text.
- If the text information is insufficient to answer a certain aspect, you can state "Cannot be determined based on the given information" in the answer.

Example structure (for reference only, actual content should be based on the given text):

Q: [Question 1]? [Question 2]? [Question 3]? ...... [Question K]?

A: [Comprehensive, detailed answer covering all angles of the questions]

Given text:
{chunk}

Please generate question-answer pairs based on this text.
"""

GENERATOR_QA_PROMPT_ZH_1 = """基于以下给定的文本，生成一组高质量的问答对。请遵循以下指南：

            1. 问题部分：
            - 为同一个主题创建尽你所能多的（如K个）不同表述的问题。
            - 问题应涵盖文本中的关键信息和主要概念。
            - 使用多种提问方式，如直接询问、请求确认、寻求解释等。

            2. 答案部分：
            - 提供一个全面、信息丰富的答案，涵盖问题的所有可能角度。
            - 答案应直接基于给定文本，确保准确性。
            - 包含相关的细节，如日期、名称、职位等具体信息。

            3. 格式：
            - 使用"Q:"标记问题集合的开始，所有问题应在一个段落内。
            - 使用"A:"标记答案的开始。
            - 问答对之间用空行分隔。

            4. 内容要求：
            - 确保问答对紧密围绕文本主题。
            - 避免添加文本中未提及的信息。
            - 如果文本信息不足以回答某个方面，可以在答案中说明"根据给定信息无法确定"。

            示例结构（仅供参考，实际内容应基于给定文本）：

            Q: [问题1]？ [问题2]？ [问题3]？ ...... [问题K]？

            A: [全面、详细的答案，涵盖所有问题的角度]

            给定文本：
            {chunk}

            请基于这个文本生成问答对。
"""
import openai
import requests
from jieba import analyse
openai.api_key = "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"

def extract_keywords(prompt):
    """
    使用TF-IDF或其他关键词提取方法，从用户问题中提取更为准确和相关的关键词，以提高搜索结果的质量。

    Args:
    prompt: str, 用户的查询

    Returns:
    list, 包含关键词的列表
    """
    # 使用jieba库的TF-IDF算法提取关键词
    keywords = analyse.extract_tags(prompt, topK=5)
    return keywords


def gpt4_should_search_online(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是大语言模型，数据截止到2021年，判断问题是否需要联网，只能给出‘yes’或者‘no’,不需要对问题做解答"},
            {"role": "user", "content": f"问题：{prompt}"}
        ],
        max_tokens=10,
        n=1,
        temperature=0,
    )
    answer = response.choices[0].message.content.strip()
    print(f"gpt4判断结果 {answer}")
    if "no" in answer or "不需要" in answer:
        return False
    else:
        return True


def custom_should_search_online(prompt):
    # 在此处添加你的自定义判断逻辑，例如：
    # 检测问题中是否包含特定关键词，或评估问题的复杂程度等
    keywords = analyse.extract_tags(prompt, topK=5)

    should_search = False
    for keyword in keywords:
        if keyword in ["最新","天气"]:  # 举例：如果问题包含特定关键词，则需要在线搜索
            should_search = True
            break
    return should_search

def should_search_online(prompt):
    custom_result = custom_should_search_online(prompt)
    if custom_result:
        return True
    else:
        gpt4_result = gpt4_should_search_online(prompt)
        return gpt4_result


import requests
from bs4 import BeautifulSoup

def search_online(keywords):
    # 使用DuckDuckGo搜索引擎进行查询
    url = f"https://duckduckgo.com/html/?q={' '.join(keywords)}"
    print(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all('a', {'class': 'result__url'})
    return results[0].get('href')


def answer_question(prompt):
    if should_search_online(prompt):
        keywords = extract_keywords(prompt)
        search_result = search_online(keywords)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是ChatGPT, 一个由OpenAI训练的大型语言模型, 你旨在回答并解决人们的任何问题，并且可以使用多种语言与人交流。"},
                {"role": "assistant", "content": f"{search_result}"},             
                {"role": "user", "content": f"{prompt}"}
            ],
            max_tokens=2000,
            n=1,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是ChatGPT, 一个由OpenAI训练的大型语言模型, 你旨在回答并解决人们的任何问题，并且可以使用多种语言与人交流。"},
                {"role": "user", "content": f"{prompt}"}
            ],
            max_tokens=2000,
            n=1,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()



#user_question = "你能告诉我地球的半径是多少吗？"
user_question = "深圳今天的天气怎么样"
answer = answer_question(user_question)
print(answer)
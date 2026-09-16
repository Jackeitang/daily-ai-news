import os
import feedparser
from datetime import datetime
from openai import OpenAI


RSS_FEEDS = {
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "Google AI": "https://blog.google/technology/ai/rss/",
}


def get_news():
    news = []

    for source, url in RSS_FEEDS.items():
        print(f"正在获取：{source}")

        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            news.append({
                "source": source,
                "title": entry.title,
                "link": entry.link
            })

    return news


def summarize_with_deepseek(news):

    api_key = os.environ.get("DEEPSEEK_API_KEY")

    if not api_key:
        raise ValueError("没有找到 DEEPSEEK_API_KEY")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    news_text = ""

    for i, item in enumerate(news, 1):
        news_text += (
            f"{i}. 来源：{item['source']}\n"
            f"标题：{item['title']}\n"
            f"链接：{item['link']}\n\n"
        )

    prompt = f"""
下面是今天收集到的 AI 资讯：

{news_text}

请生成一份中文「AI 每日早报」。

要求：
1. 从这些资讯中选择最值得关注的内容。
2. 用中文简洁解释每条新闻讲了什么。
3. 不要编造输入中不存在的事实。
4. 保留原始链接。
5. 相似内容合并。
6. 最后增加「今日值得关注」部分，总结 3 个重点。
7. 输出适合手机阅读，不要写得太长。
"""

    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {
                "role": "system",
                "content": "你是一名科技资讯编辑，负责整理准确、简洁的每日科技早报。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        stream=False
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    print("=" * 50)
    print("Daily AI News")
    print("运行时间：", datetime.now())
    print("=" * 50)

    news = get_news()

    print(f"\n共获取 {len(news)} 条资讯")

    print("\n正在调用 DeepSeek...\n")

    report = summarize_with_deepseek(news)

    print("=" * 50)
    print("AI 每日早报")
    print("=" * 50)

    print(report)

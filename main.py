import feedparser
from datetime import datetime

RSS_FEEDS = {
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "Google AI": "https://blog.google/technology/ai/rss/",
}

def get_news():
    news = []

    for source, url in RSS_FEEDS.items():
        print(f"\n正在获取：{source}")

        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            news.append({
                "source": source,
                "title": entry.title,
                "link": entry.link
            })

    return news


if __name__ == "__main__":

    print("=" * 50)
    print("Daily AI News")
    print("运行时间：", datetime.now())
    print("=" * 50)

    news = get_news()

    print(f"\n共获取 {len(news)} 条资讯\n")

    for i, item in enumerate(news, 1):
        print(f"{i}. [{item['source']}]")
        print(item["title"])
        print(item["link"])
        print()

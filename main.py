import os
import time
import calendar
import feedparser
from datetime import datetime, timezone
from openai import OpenAI


# =========================
# RSS 新闻源
# =========================

RSS_FEEDS = {
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "Google AI": "https://blog.google/technology/ai/rss/",
    "NVIDIA": "https://blogs.nvidia.com/feed/",
    "MIT AI": "https://news.mit.edu/rss/topic/artificial-intelligence2",
}


# =========================
# 新闻分类
# =========================

def classify_news(title):
    title = title.lower()

    if any(word in title for word in [
        "agent", "agentic", "tool use"
    ]):
        return "🤖 Agent"

    if any(word in title for word in [
        "robot", "robotics", "humanoid", "embodied"
    ]):
        return "🦾 机器人"

    if any(word in title for word in [
        "vision", "image", "video",
        "multimodal", "3d"
    ]):
        return "👁️ CV / 多模态"

    if any(word in title for word in [
        "open source", "github",
        "release", "framework"
    ]):
        return "💻 开源 / 工具"

    return "🔥 AI / 大模型"


# =========================
# 解析 RSS 时间
# =========================

def get_entry_timestamp(entry):

    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return calendar.timegm(entry.published_parsed)

    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        return calendar.timegm(entry.updated_parsed)

    return None


# =========================
# 获取最近 24 小时新闻
# =========================

def get_news():

    news = []

    now = time.time()
    last_24_hours = now - 24 * 60 * 60

    for source, url in RSS_FEEDS.items():

        print(f"正在获取：{source}")

        feed = feedparser.parse(url)

        if feed.bozo:
            print(f"⚠️ {source} RSS 可能存在问题")

        count = 0

        for entry in feed.entries:

            timestamp = get_entry_timestamp(entry)

            # 没有发布时间的文章先跳过
            if timestamp is None:
                continue

            # 只保留最近24小时
            if timestamp < last_24_hours:
                continue

            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()

            if not title or not link:
                continue

            news.append({
                "source": source,
                "title": title,
                "link": link,
                "category": classify_news(title),
                "timestamp": timestamp
            })

            count += 1

        print(f"找到最近24小时资讯：{count} 条")

    # 最新的排前面
    news.sort(
        key=lambda x: x["timestamp"],
        reverse=True
    )

    return news


# =========================
# DeepSeek 总结
# =========================

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

        publish_time = datetime.fromtimestamp(
            item["timestamp"],
            tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M UTC")

        news_text += (
            f"{i}. [{item['category']}]\n"
            f"来源：{item['source']}\n"
            f"标题：{item['title']}\n"
            f"发布时间：{publish_time}\n"
            f"链接：{item['link']}\n\n"
        )

    prompt = f"""
下面是程序从多个科技资讯源收集到的最近24小时新闻。

{news_text}

请制作一份中文《AI 科技每日早报》。

要求：

1. 最多选择 10 条真正值得关注的资讯。
2. 优先关注：
   - AI 大模型
   - AI Agent
   - 计算机视觉 / 多模态
   - 机器人 / 具身智能
   - 重要开源项目
3. 每条使用 2～3 句话说明发生了什么。
4. 不要编造输入中没有的信息。
5. 保留新闻来源。
6. 保留原始链接。
7. 相似新闻进行合并。
8. 不要为了凑够10条而加入价值较低的内容。
9. 使用简洁中文，适合手机阅读。

最后增加：

【今日值得关注】

选择最多3个值得继续关注的技术方向，
简单解释为什么值得关注。
"""

    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {
                "role": "system",
                "content":
                    "你是一名科技资讯编辑。"
                    "你的任务是从真实新闻源中筛选重要技术资讯，"
                    "不得编造新闻中不存在的事实。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        stream=False
    )

    return response.choices[0].message.content


# =========================
# 主程序
# =========================

if __name__ == "__main__":

    print("=" * 60)
    print("Daily AI News Agent")
    print("UTC运行时间：", datetime.now(timezone.utc))
    print("=" * 60)

    news = get_news()

    print()
    print(f"最近24小时共找到 {len(news)} 条资讯")
    print()

    # 防止没有新闻时还调用 API
    if not news:
        print("最近24小时没有找到符合条件的资讯。")
        raise SystemExit(0)

    # 输出原始结果，方便以后排错
    for i, item in enumerate(news, 1):
        print(
            f"{i}. {item['category']} "
            f"[{item['source']}] "
            f"{item['title']}"
        )

    print()
    print("正在调用 DeepSeek 生成每日早报...")
    print()

    report = summarize_with_deepseek(news)

    print("=" * 60)
    print("AI 科技每日早报")
    print("=" * 60)

    print(report)

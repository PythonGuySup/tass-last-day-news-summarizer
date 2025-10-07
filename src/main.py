import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.news_collector import TASSNewsCollector
from src.text_summarizer import NewsSummarizer


def generate_daily_summary():
    print(f"\n=== Генерация сводки {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")

    try:
        collector = TASSNewsCollector()
        articles = collector.get_last_24h_news()

        if not articles:
            print("Не удалось собрать новости")
            return "Не удалось собрать новости"

        print("Запуск суммаризации...")
        summarizer = NewsSummarizer()
        summary = summarizer.summarize_articles(articles)

        save_results(summary, articles)

        print("\n" + "=" * 60)
        print("СВОДКА НОВОСТЕЙ:")
        print("=" * 60)
        print(summary)
        print("=" * 60)

        return summary

    except Exception as e:
        error_msg = f"Ошибка при генерации сводки: {e}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return error_msg


def save_results(summary: str, articles: list):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"summary_{timestamp}.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"СВОДКА НОВОСТЕЙ ТАСС\n")
        f.write(f"Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Обработано статей: {len(articles)}\n")
        f.write("\n" + "=" * 60 + "\n")
        f.write("КРАТКАЯ СВОДКА:\n")
        f.write("=" * 60 + "\n")
        f.write(summary + "\n\n")
        f.write("=" * 60 + "\n")
        f.write("ИСТОЧНИКИ:\n")
        f.write("=" * 60 + "\n")

        for i, article in enumerate(articles, 1):
            f.write(f"\n{i}. {article['title']}\n")
            f.write(f"   URL: {article['url']}\n")


if __name__ == "__main__":
    print("Запуск системы суммаризации новостей ТАСС")
    print("Модель: Fine-Tuned T5 Small for Text Summarization")

    summary = generate_daily_summary()

    with open("latest_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)

    print("\nСводка сохранена в файлы 'summary_...' и 'latest_summary.txt'")
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from config import MODEL_NAME, MAX_INPUT_TOKENS, MIN_OUTPUT_LENGTH, MAX_OUTPUT_LENGTH


class NewsSummarizer:
    def __init__(self):
        print(f"Загрузка модели суммирования...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(self.device)
        print(f"Модель '{MODEL_NAME}' загружена! (device: {self.device})")

    def _summarize_text(self, text: str, max_new_tokens: int = MAX_OUTPUT_LENGTH) -> str:
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            max_length=MAX_INPUT_TOKENS,
            truncation=True
        ).to(self.device)

        summary_ids = self.model.generate(
            inputs["input_ids"],
            num_beams=5,
            length_penalty=1.0,
            max_new_tokens=max_new_tokens,
            min_length=MIN_OUTPUT_LENGTH,
            no_repeat_ngram_size=3
        )
        return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True).strip()

    def summarize_articles(self, articles: list[dict]) -> str:
        """Создаёт сводку по пунктам для каждой статьи"""
        summaries = []
        for idx, article in enumerate(articles, start=1):
            text = article.get("content", "").strip()
            if not text:
                continue
            try:
                summary = self._summarize_text(text, max_new_tokens=100)
                summaries.append(f"{idx}. {summary}")
            except Exception as e:
                print(f"⚠️ Ошибка при суммировании статьи {idx}: {e}")

        if not summaries:
            return "Не удалось создать сводку."

        # Объединяем в итоговую сводку
        return "\n".join(summaries)


import time
import warnings

warnings.filterwarnings("ignore", category=SyntaxWarning)

import translators as ts


class Translator:
    def __init__(self, target_lang="tr", source_lang="auto", max_retries=3):
        self.target_lang = target_lang
        self.source_lang = source_lang
        self.max_retries = max_retries

    def translate(self, text):
        if not text or not text.strip():
            return ""
        for attempt in range(self.max_retries):
            try:
                result = ts.translate_text(
                    text,
                    translator="google",
                    from_language=self.source_lang if self.source_lang != "auto" else "auto",
                    to_language=self.target_lang,
                )
                return result if result else ""
            except Exception:
                if attempt < self.max_retries - 1:
                    time.sleep(0.5 * (attempt + 1))
                else:
                    return f"[translation error] {text}"
        return text

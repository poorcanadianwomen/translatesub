from faster_whisper import WhisperModel


class Transcriber:
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, audio, language=None):
        segments, info = self.model.transcribe(
            audio,
            language=language,
            beam_size=5,
            vad_filter=False,
        )
        text_parts = [seg.text.strip() for seg in segments]
        return " ".join(text_parts), info.language

    @property
    def detected_language(self):
        return None

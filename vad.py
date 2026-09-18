import numpy as np
import torch


class VoiceActivityDetector:
    def __init__(self, threshold=0.3, sample_rate=16000, speech_ms=300, silence_ms=700):
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.speech_samples = int(sample_rate * speech_ms / 1000)
        self.silence_samples = int(sample_rate * silence_ms / 1000)
        self.model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            force_reload=False,
            onnx=True,
        )
        self._reset()

    def _reset(self):
        self.model.reset_states()
        self._speech_buffer = []
        self._silence_counter = 0
        self._in_speech = False

    def process(self, audio_chunk):
        audio_np = audio_chunk.astype(np.float32)
        if len(audio_np) == 0:
            return None

        audio_tensor = torch.from_numpy(audio_np)
        prob = self.model(audio_tensor, self.sample_rate).item()

        if prob >= self.threshold:
            self._silence_counter = 0
            self._in_speech = True
            self._speech_buffer.append(audio_np)
        elif self._in_speech:
            self._silence_counter += len(audio_np)
            self._speech_buffer.append(audio_np)
            if self._silence_counter >= self.silence_samples:
                speech = np.concatenate(self._speech_buffer)
                self._reset()
                if len(speech) >= self.speech_samples:
                    return speech

        return None

import threading
import queue
import numpy as np
from vad import VoiceActivityDetector
from transcriber import Transcriber
from translator import Translator

VAD_SAMPLES = 512


class UserAudioState:
    def __init__(self):
        self.vad = VoiceActivityDetector(threshold=0.4, speech_ms=250, silence_ms=500)
        self.audio_remainder = np.array([], dtype=np.float32)
        self.username = None


class Pipeline:
    def __init__(self, overlay=None, model_size="base", target_lang="en", on_status=None):
        self.overlay = overlay
        self.on_status = on_status or (lambda s: None)
        self.model_size = model_size
        self._running = False

        self.transcriber = None
        self.translator = Translator(target_lang=target_lang)

        self._user_states = {}
        self._audio_queue = queue.Queue()
        self._stop_event = threading.Event()

    def _log(self, msg):
        self.on_status(msg)

    def start(self):
        if self._running:
            return
        self._stop_event.clear()
        self._running = True

        self._log("Loading STT model...")
        self.transcriber = Transcriber(model_size=self.model_size)

        self._processor_thread = threading.Thread(target=self._process_loop, daemon=True)
        self._processor_thread.start()
        self._log("Ready - waiting for Discord voice")

    def stop(self):
        if not self._running:
            return
        self._running = False
        self._stop_event.set()
        self._processor_thread.join(timeout=3.0)
        self._log("Stopped")

    def on_discord_audio(self, user_id, audio_chunk, username=None):
        self._audio_queue.put((user_id, audio_chunk, username))

    def _get_user_state(self, user_id, username=None):
        if user_id not in self._user_states:
            self._user_states[user_id] = UserAudioState()
        state = self._user_states[user_id]
        if username:
            state.username = username
        return state

    def _process_loop(self):
        while not self._stop_event.is_set():
            try:
                user_id, chunk, username = self._audio_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            state = self._get_user_state(user_id, username)
            audio = np.concatenate([state.audio_remainder, chunk]) if state.audio_remainder.size else chunk

            while len(audio) >= VAD_SAMPLES:
                frame = audio[:VAD_SAMPLES]
                audio = audio[VAD_SAMPLES:]

                speech = state.vad.process(frame)
                if speech is None:
                    continue

                try:
                    name = state.username or str(user_id)
                    duration = len(speech) / 16000
                    self._log(f"[{name}] Transcribing ({duration:.1f}s)...")
                    text, lang = self.transcriber.transcribe(speech)
                    if not text.strip():
                        continue

                    translated = self.translator.translate(text)
                    self._log(f"[{name}] {text} -> {translated}")

                    if self.overlay:
                        self.overlay.signals.update_text.emit(translated, name)
                except Exception as e:
                    self._log(f"Error: {e}")

            state.audio_remainder = audio

    def change_model(self, model_size):
        self.model_size = model_size
        self._log(f"Model will change to {model_size} on next start")

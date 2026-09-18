import threading
import numpy as np
import soundcard as sc


class AudioCapture:
    def __init__(self, sample_rate=48000, channels=2, chunk_duration_ms=300):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_samples = int(sample_rate * chunk_duration_ms / 1000)
        self._stop_event = threading.Event()
        self._recorder = None
        self._loopback = None

    def list_devices(self):
        mics = sc.all_microphones(include_loopback=True)
        devices = []
        for i, mic in enumerate(mics):
            devices.append({"index": i, "name": mic.name, "is_loopback": mic.isloopback})
        return devices

    def select_loopback(self, device_index=None):
        mics = sc.all_microphones(include_loopback=True)
        loopbacks = [m for m in mics if m.isloopback]
        if not loopbacks:
            raise RuntimeError("No loopback audio device found. Is PulseAudio running?")
        if device_index is not None and device_index < len(loopbacks):
            self._loopback = loopbacks[device_index]
        else:
            self._loopback = loopbacks[0]
        return self._loopback.name

    def start(self, callback):
        if self._loopback is None:
            self.select_loopback()

        self._stop_event.clear()
        self._recorder = self._loopback.recorder(
            samplerate=self.sample_rate,
            channels=self.channels,
            blocksize=self.chunk_samples,
        )

        def _capture_loop():
            with self._recorder as recorder:
                while not self._stop_event.is_set():
                    data = recorder.record(numframes=self.chunk_samples)
                    if data is not None and data.size > 0:
                        pcm = self._to_mono_16k(data)
                        callback(pcm)

        self._thread = threading.Thread(target=_capture_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if hasattr(self, "_thread") and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def _to_mono_16k(self, data):
        if data.ndim > 1:
            data = data.mean(axis=1)
        data = data.astype(np.float32)
        if self.sample_rate != 16000:
            ratio = 16000 / self.sample_rate
            new_len = int(len(data) * ratio)
            indices = np.linspace(0, len(data) - 1, new_len).astype(int)
            data = data[indices]
        return data

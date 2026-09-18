import asyncio
import threading
import struct
import discord
from discord.ext import native_voice

discord.opus.load_opus("libopus.so.0")


class DiscordVoiceClient:
    def __init__(self, token, channel_id, on_audio_callback, on_status=None):
        self.token = token
        self.channel_id = channel_id
        self.on_audio = on_audio_callback
        self.on_status = on_status or (lambda s: None)
        self._client = None
        self._voice = None
        self._loop = None
        self._thread = None
        self._decoders = {}
        self._decoder_locks = {}
        self._user_cache = {}
        self._global_lock = threading.Lock()

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._disconnect(), self._loop)

    def _run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._client = discord.Client()

        @self._client.event
        async def on_ready():
            self._log(f"Logged in as {self._client.user}")
            await self._cache_users()
            await self._join_vc()

        self._client.run(self.token)

    async def _cache_users(self):
        channel = self._client.get_channel(self.channel_id)
        if channel and hasattr(channel, 'members'):
            for member in channel.members:
                self._user_cache[member.id] = member.display_name
            self._log(f"Cached {len(self._user_cache)} users")

    def _get_username(self, user_id):
        if user_id in self._user_cache:
            return self._user_cache[user_id]
        member = None
        if self._client:
            for guild in self._client.guilds:
                member = guild.get_member(user_id)
                if member:
                    break
        if member:
            name = member.display_name
            self._user_cache[user_id] = name
            return name
        return str(user_id)

    async def _join_vc(self):
        channel = self._client.get_channel(self.channel_id)
        if channel is None:
            self._log(f"Channel {self.channel_id} not found, trying to fetch...")
            try:
                channel = await self._client.fetch_channel(self.channel_id)
            except Exception as e:
                self._log(f"Failed to fetch channel: {e}")
                return

        self._log(f"Joining: {channel.name} ({channel.guild.name})")

        if hasattr(channel, 'members'):
            for member in channel.members:
                if not member.bot:
                    self._user_cache[member.id] = member.display_name

        try:
            self._voice = await channel.connect(cls=native_voice.VoiceClient)
            self._log("Connected to voice")
            self._voice.listen(self._on_packet)
        except Exception as e:
            self._log(f"Failed to connect: {e}")

    def _on_packet(self, packet):
        if packet.media_type != "audio":
            return

        if packet.user_id == self._client.user.id:
            return

        user_id = packet.user_id
        opus_data = packet.payload

        if not opus_data or len(opus_data) < 4:
            return

        try:
            pcm = self._decode_opus(user_id, opus_data)
        except Exception:
            return

        if pcm and len(pcm) > 0:
            import numpy as np
            audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
            if len(audio) % 2 == 0:
                audio = audio.reshape(-1, 2).mean(axis=1)
            audio = np.interp(
                np.linspace(0, len(audio) - 1, int(len(audio) * 16000 / 48000)),
                np.arange(len(audio)),
                audio,
            )
            username = self._get_username(user_id)
            self.on_audio(user_id, audio, username)

    def _decode_opus(self, user_id, opus_data):
        with self._global_lock:
            if user_id not in self._decoders:
                self._decoders[user_id] = discord.opus.Decoder()
            decoder = self._decoders[user_id]
            return decoder.decode(opus_data)

    async def _disconnect(self):
        if self._voice:
            self._voice.stop()
            await self._voice.disconnect()
        if self._client:
            await self._client.close()

    def _log(self, msg):
        self.on_status(msg)

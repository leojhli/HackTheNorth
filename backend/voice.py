import httpx
from fastapi import UploadFile
from .errors import AppError


class ElevenLabs:
    def __init__(self, config):
        self.config = config

    def ready(self):
        if not self.config.elevenlabs_api_key or not self.config.elevenlabs_voice_id:
            raise AppError('voice_unconfigured', 'Voice is not configured. Continue with typed text.', 503)

    def speech(self, text):
        self.ready()
        try:
            r = httpx.post(f'https://api.elevenlabs.io/v1/text-to-speech/{self.config.elevenlabs_voice_id}',
                headers={'xi-api-key': self.config.elevenlabs_api_key}, json={'text': text, 'model_id': 'eleven_multilingual_v2'}, timeout=25)
            r.raise_for_status()
            if len(r.content) > 10_000_000:
                raise ValueError('Oversized response')
            return r.content
        except Exception:
            raise AppError('speech_unavailable', 'Speech playback failed. The question remains available as text.', 503, True) from None

    def transcribe(self, audio, content_type):
        self.ready()
        try:
            r = httpx.post('https://api.elevenlabs.io/v1/speech-to-text', headers={'xi-api-key': self.config.elevenlabs_api_key},
                files={'file': ('answer.webm', audio, content_type)}, data={'model_id': 'scribe_v2', 'tag_audio_events': 'false', 'diarize': 'false'}, timeout=25)
            r.raise_for_status()
            text = r.json()['text']
            if not isinstance(text, str) or not text.strip() or len(text) > 8000:
                raise ValueError('Invalid transcript')
            return text
        except Exception:
            raise AppError('transcription_unavailable', 'Transcription failed. Type your answer or record again.', 503, True) from None

"""Hosted voice is unavailable in the free local edition."""
from .errors import AppError


class ElevenLabs:
    def __init__(self, config):
        self.config = config

    def ready(self):
        raise AppError('voice_disabled', 'Hosted voice is disabled in this free local edition. Continue with typed text.', 503)

    def speech(self, text):
        self.ready()

    def transcribe(self, audio, content_type):
        self.ready()

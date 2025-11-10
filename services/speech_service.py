"""Speech Service module.

This refactored implementation exposes a provider-based architecture so that
multiple text-to-speech engines can be selected at runtime.
"""

from __future__ import annotations

import base64
import os
from typing import Dict, Optional

from dotenv import load_dotenv

from .tts_providers import (
    DEFAULT_PROVIDERS,
    BaseTTSProvider,
)


project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)


class SpeechService:
    """Orchestrates synthesis calls across configured TTS providers."""

    def __init__(self, output_dir: str = "output", providers: Optional[Dict[str, BaseTTSProvider]] = None):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # Lazy copy so each service instance can customise without mutating the default map
        self.providers: Dict[str, BaseTTSProvider] = providers.copy() if providers else DEFAULT_PROVIDERS.copy()

    def register_provider(self, key: str, provider: BaseTTSProvider) -> None:
        self.providers[key] = provider

    def get_provider(self, key: str) -> Optional[BaseTTSProvider]:
        return self.providers.get(key)

    def list_providers(self) -> Dict[str, str]:
        return {key: provider.__class__.__name__ for key, provider in self.providers.items()}

    def synthesize(
        self,
        *,
        text: str,
        lang_code: str,
        filename: str,
        tts_engine: str,
        voice: Optional[str] = None,
        gender: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
    ) -> Dict[str, object]:
        if not text or not text.strip():
            return {
                "file_path": None,
                "filename": filename,
                "success": False,
                "message": "No text provided for synthesis.",
                "tts_engine": None,
                "audio_base64": None,
                "normalized_text": None,
            }

        provider = self.providers.get(tts_engine)
        if not provider:
            return {
                "file_path": None,
                "filename": filename,
                "success": False,
                "message": f"Unknown TTS engine '{tts_engine}'.",
                "tts_engine": None,
                "audio_base64": None,
                "normalized_text": None,
            }

        normalized_lang = (lang_code or "").split("-")[0].lower()
        if tts_engine == "piper":
            supported_languages = getattr(provider, "supported_languages", set()) or set()
            if supported_languages and normalized_lang not in supported_languages:
                fallback_provider = self.providers.get("indic")
                if fallback_provider:
                    provider = fallback_provider
                    tts_engine = fallback_provider.engine_key
                else:
                    return {
                        "file_path": None,
                        "filename": filename,
                        "success": False,
                        "message": (
                            "Piper does not support language "
                            f"'{lang_code}'. No fallback provider configured."
                        ),
                        "tts_engine": None,
                        "audio_base64": None,
                        "normalized_text": None,
                    }

        file_path = os.path.join(self.output_dir, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            provider_result = provider.synthesize(
                text=text,
                lang=lang_code,
                gender=gender,
                rate=rate,
                pitch=pitch,
                voice=voice,
                output_path=file_path,
            )
        except Exception as exc:
            return {
                "file_path": None,
                "filename": filename,
                "success": False,
                "message": str(exc),
                "tts_engine": tts_engine,
                "audio_base64": None,
                "normalized_text": None,
            }

        audio_bytes = provider_result.get("audio_bytes") if provider_result else None
        if audio_bytes is None and os.path.exists(file_path):
            with open(file_path, "rb") as file_handle:
                audio_bytes = file_handle.read()

        if audio_bytes is None:
            return {
                "file_path": None,
                "filename": filename,
                "success": False,
                "message": "Failed to obtain audio output from provider.",
                "tts_engine": tts_engine,
                "audio_base64": None,
                "normalized_text": None,
            }

        if not os.path.exists(file_path):
            with open(file_path, "wb") as file_handle:
                file_handle.write(audio_bytes)

        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        normalized_text = provider_result.get("normalized_text") if provider_result else None

        return {
            "file_path": file_path,
            "filename": filename,
            "success": True,
            "message": "Synthesis successful.",
            "tts_engine": tts_engine,
            "audio_base64": audio_base64,
            "normalized_text": normalized_text or text,
        }

    @staticmethod
    def get_available_voices():
        return {
            "Female": {
                "nova": "Nova - Clear and expressive female voice",
                "shimmer": "Shimmer - Warm female voice",
            },
            "Male": {
                "onyx": "Onyx - Deep male voice",
                "echo": "Echo - Strong male voice",
            },
            "Neutral": {
                "alloy": "Alloy - Balanced neutral voice",
                "fable": "Fable - Versatile neutral voice",
            },
        }

    @staticmethod
    def get_voice_by_gender_and_age(gender="Female", age_tone="Adult"):
        voice_map = {
            "Female": {
                "Child": "nova",
                "Adult": "shimmer",
                "Senior": "shimmer",
            },
            "Male": {
                "Child": "echo",
                "Adult": "onyx",
                "Senior": "onyx",
            },
        }

        if gender in voice_map and age_tone in voice_map[gender]:
            return voice_map[gender][age_tone]

        if gender == "Female":
            return "nova"
        if gender == "Male":
            return "onyx"
        return "alloy"

    def get_output_path(self, filename="output.mp3"):
        return os.path.join(self.output_dir, filename)


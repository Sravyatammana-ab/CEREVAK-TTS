"""TTS provider implementations used by the speech service."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict, Iterable, Optional, Set

from gtts import gTTS
from openai import OpenAI


class BaseTTSProvider:
    """Base class for all TTS providers."""

    engine_key: str = "base"
    output_extension: str = "mp3"

    def synthesize(
        self,
        text: str,
        lang: str,
        gender: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        voice: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError


class OpenAITTS(BaseTTSProvider):
    """OpenAI powered TTS provider. # cloud option"""

    engine_key = "openai"

    def __init__(self, model: str = "tts-1", default_voice: str = "alloy", api_key: Optional[str] = None):
        self.model = model
        self.default_voice = default_voice
        api_key = api_key or os.getenv("OPENAI_API_KEY", "").strip()
        self._client: Optional[OpenAI] = None
        if api_key:
            try:
                self._client = OpenAI(api_key=api_key)
            except Exception as exc:  # pragma: no cover - defensive
                print(f"❌ Unable to initialise OpenAI client: {exc}")
                self._client = None

    def synthesize(
        self,
        text: str,
        lang: str,
        gender: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        voice: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("OpenAI TTS is not configured. Please provide a valid OPENAI_API_KEY.")

        voice_to_use = voice or self.default_voice
        try:
            # Use streaming response so we can persist and read bytes reliably
            with self._client.audio.speech.with_streaming_response.create(
                model=self.model,
                voice=voice_to_use,
                input=text,
            ) as response:
                audio_bytes: bytes
                if output_path:
                    response.stream_to_file(output_path)
                    with open(output_path, "rb") as file_handle:
                        audio_bytes = file_handle.read()
                else:
                    audio_bytes = response.read()

            return {
                "audio_bytes": audio_bytes,
                "normalized_text": text,
                "format": self.output_extension,
                "voice_used": voice_to_use,
            }
        except Exception as exc:
            raise RuntimeError(f"OpenAI TTS synthesis failed: {exc}") from exc


class PiperTTS(BaseTTSProvider):
    """Run inference through a locally installed Piper binary."""

    engine_key = "piper"
    output_extension = "wav"

    def __init__(
        self,
        model_path: str,
        binary: str = "piper",
        supported_languages: Optional[Iterable[str]] = None,
        models_by_language: Optional[Dict[str, str]] = None,
    ):
        self.model_path = model_path
        self.binary = binary
        self.models_by_language: Dict[str, str] = {
            key.lower(): path for key, path in models_by_language.items()
        } if models_by_language else {}

        if supported_languages is not None:
            self.supported_languages: Set[str] = {lang.lower() for lang in supported_languages}
        elif self.models_by_language:
            # Derive supported languages from explicit model mapping
            self.supported_languages = {key.split("-")[0] for key in self.models_by_language.keys()}
            self.supported_languages.update(self.models_by_language.keys())
        else:
            self.supported_languages = set()

    def synthesize(
        self,
        text: str,
        lang: str,
        gender: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        voice: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not shutil.which(self.binary):
            raise RuntimeError("Piper binary not found. Install Piper and ensure it is on the PATH.")

        normalized_lang_full = (lang or "").lower()
        normalized_lang = normalized_lang_full.split("-")[0]

        model_path = None
        for candidate in (normalized_lang_full, normalized_lang):
            if candidate and candidate in self.models_by_language:
                model_path = self.models_by_language[candidate]
                break

        if not model_path:
            model_path = self.model_path

        if not os.path.exists(model_path):
            raise RuntimeError(f"Piper model not found at '{model_path}'.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_output:
            tmp_out_path = temp_output.name

        try:
            command = [
                self.binary,
                "--model",
                model_path,
                "--output_file",
                tmp_out_path,
            ]
            subprocess.run(
                command,
                input=text.encode("utf-8"),
                check=True,
            )

            with open(tmp_out_path, "rb") as file_handle:
                audio_bytes = file_handle.read()

            if output_path:
                with open(output_path, "wb") as target:
                    target.write(audio_bytes)

            return {
                "audio_bytes": audio_bytes,
                "normalized_text": text,
                "format": self.output_extension,
            }
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"Piper synthesis failed: {exc}") from exc
        finally:
            if os.path.exists(tmp_out_path):
                os.remove(tmp_out_path)


class IndicTTSProvider(BaseTTSProvider):
    """Wrapper around the IIT Madras Indic TTS models (expects external setup)."""

    engine_key = "indic"
    output_extension = "mp3"

    def __init__(self, language_code: str, binary: Optional[str] = None):
        self.language_code = language_code
        self.binary = binary  # Optional CLI to call if available

    def synthesize(
        self,
        text: str,
        lang: str,
        gender: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        voice: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        language = lang or self.language_code
        unsupported = {"as", "or", "pa"}
        if language in unsupported:
            raise RuntimeError(
                f"Language '{language}' is not supported by the fallback gTTS integration. "
                "Configure the Indic-TTS engine for full offline support."
            )

        try:
            synth_lang = language or self.language_code
            tts = gTTS(text=text, lang=synth_lang, slow=False)

            if output_path:
                tts.save(output_path)
                with open(output_path, "rb") as file_handle:
                    audio_bytes = file_handle.read()
            else:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                    tts.save(temp_file.name)
                    temp_file.flush()
                    with open(temp_file.name, "rb") as file_handle:
                        audio_bytes = file_handle.read()
                os.remove(temp_file.name)

            return {
                "audio_bytes": audio_bytes,
                "normalized_text": text,
                "format": "mp3",
            }
        except Exception as exc:
            raise RuntimeError(f"IndicTTS fallback synthesis failed: {exc}") from exc


class CoquiTTSProvider(BaseTTSProvider):
    """Coqui TTS provider (expects the TTS library to be installed)."""

    engine_key = "coqui"
    output_extension = "wav"

    def __init__(self, model_name: str, vocoder: Optional[str] = None):
        self.model_name = model_name
        self.vocoder = vocoder
        try:
            from TTS.api import TTS  # type: ignore

            self._tts_class = TTS
        except Exception:  # pragma: no cover - optional dependency
            self._tts_class = None

    def synthesize(
        self,
        text: str,
        lang: str,
        gender: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        voice: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        if self._tts_class is None:
            raise RuntimeError(
                "Coqui TTS library is not installed. Install 'TTS' and ensure GPU drivers are available."
            )

        tts = self._tts_class(model_name=self.model_name, vocoder_name=self.vocoder)

        if output_path:
            target_path = output_path
        else:
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            target_path = tmp_file.name
            tmp_file.close()

        tts.tts_to_file(text=text, file_path=target_path)

        with open(target_path, "rb") as file_handle:
            audio_bytes = file_handle.read()

        if not output_path and os.path.exists(target_path):
            os.remove(target_path)

        return {
            "audio_bytes": audio_bytes,
            "normalized_text": text,
            "format": self.output_extension,
        }


DEFAULT_PROVIDERS = {
    "openai": OpenAITTS(),
    "piper": PiperTTS(
        "voices/hi_IN-pratham-medium.onnx",
        binary=r"D:\tools\piper\piper.exe",
        models_by_language={
            "hi": "voices/hi_IN-pratham-medium.onnx",
            "en": "voices/en_GB-southern_english_female-low.onnx",
        },
    ),
    "indic": IndicTTSProvider("hi"),
    "coqui": CoquiTTSProvider("tts_models/multilingual/your_model_here"),
}



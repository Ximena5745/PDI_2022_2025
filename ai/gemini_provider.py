"""
Proveedor de IA: Google Gemini (tier gratuito — 60 req/min).
"""

from __future__ import annotations

import os
from ai.base import AIProvider

_ERROR_MARKERS = ("No se pudo generar", "RESOURCE_EXHAUSTED")


class GeminiProvider(AIProvider):
    """
    Implementación de AIProvider usando Google Gemini 2.0 Flash.
    La API key se lee de la variable de entorno GOOGLE_API_KEY
    o de st.secrets (cuando se ejecuta en Streamlit Cloud).
    """

    MODEL = "models/gemini-2.0-flash"

    def __init__(self) -> None:
        self._client = None
        self._init_client()

    def _init_client(self) -> None:
        try:
            from google import genai  # type: ignore

            api_key = os.environ.get("GOOGLE_API_KEY") or self._key_from_secrets()
            if api_key:
                self._client = genai.Client(api_key=api_key)
        except Exception:
            self._client = None

    @staticmethod
    def _key_from_secrets() -> str | None:
        try:
            import streamlit as st  # type: ignore
            return st.secrets.get("GOOGLE_API_KEY", None)
        except Exception:
            return None

    def is_available(self) -> bool:
        return self._client is not None

    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        if not self.is_available():
            return ""
        try:
            response = self._client.models.generate_content(
                model=self.MODEL,
                contents=prompt,
                config={"max_output_tokens": max_tokens, "temperature": 0.7},
            )
            text = response.text or ""
            if any(m in text for m in _ERROR_MARKERS):
                return ""
            return text
        except Exception:
            return ""

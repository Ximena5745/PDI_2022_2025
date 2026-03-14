"""
ai — Capa de inteligencia artificial del Dashboard Estratégico POLI.
Proveedores intercambiables mediante la interfaz AIProvider.
"""

from ai.base import AIProvider
from ai.gemini_provider import GeminiProvider
from ai.static_provider import StaticProvider

__all__ = ["AIProvider", "GeminiProvider", "StaticProvider"]

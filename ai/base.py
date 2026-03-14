"""
Clase base abstracta para proveedores de IA.
Cualquier proveedor nuevo (Claude, OpenAI, Ollama, etc.) solo necesita
implementar el método `generate`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Interfaz común para todos los proveedores de IA del proyecto."""

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Genera texto a partir de un prompt.

        Args:
            prompt: Texto de entrada.
            max_tokens: Límite de tokens en la respuesta.

        Returns:
            Texto generado por el modelo.
        """

    @abstractmethod
    def is_available(self) -> bool:
        """True si el proveedor está configurado y listo para usarse."""

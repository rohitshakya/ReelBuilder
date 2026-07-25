"""Voice-over stubs for Phase 3 (AI narration)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class VoiceOverProvider(ABC):
    """Abstract interface for TTS / voice-over providers (Phase 3)."""

    @abstractmethod
    def synthesize(self, text: str, output_path: Path) -> Path:
        """Synthesize speech from text.

        Args:
            text: Narration script.
            output_path: Destination audio file.

        Returns:
            Path to the generated audio file.
        """


class VoiceOverPlaceholder(VoiceOverProvider):
    """Placeholder provider that raises until Phase 3 is implemented."""

    def synthesize(self, text: str, output_path: Path) -> Path:
        """Raise NotImplementedError for Phase 3 providers.

        Args:
            text: Narration script.
            output_path: Destination audio file.

        Raises:
            NotImplementedError: Always — Phase 3 feature.
        """
        raise NotImplementedError(
            "AI voice-over (OpenAI / ElevenLabs / Piper / Kokoro) "
            "is planned for Phase 3. See the project roadmap."
        )

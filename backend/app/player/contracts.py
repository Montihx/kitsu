from dataclasses import dataclass, field
from typing import List, Optional

from .models import AudioTrack, PlaybackSource, SubtitleTrack


@dataclass
class PlaybackRequest:
    """Input contract for resolving playback metadata.

    No network or streaming is performed; this only carries selection hints.
    """

    anime_id: str
    episode_id: str
    preferred_audio: Optional[str] = None
    preferred_subtitle: Optional[str] = None


@dataclass
class PlaybackMetadata:
    """Normalized playback metadata produced by resolver.

    This remains streaming-agnostic and can be enriched in future phases.
    """

    sources: List[PlaybackSource] = field(default_factory=list)
    audio_tracks: List[AudioTrack] = field(default_factory=list)
    subtitle_tracks: List[SubtitleTrack] = field(default_factory=list)
    intro: dict[str, int] = field(default_factory=lambda: {"start": 0, "end": 0})
    outro: dict[str, int] = field(default_factory=lambda: {"start": 0, "end": 0})

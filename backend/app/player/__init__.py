"""Player domain foundation (no streaming logic)."""

from .contracts import PlaybackMetadata, PlaybackRequest
from .models import AudioTrack, PlaybackSource, SubtitleTrack
from .resolver import resolve_playback

__all__ = [
    "PlaybackMetadata",
    "PlaybackRequest",
    "AudioTrack",
    "PlaybackSource",
    "SubtitleTrack",
    "resolve_playback",
]

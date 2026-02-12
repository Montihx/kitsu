from dataclasses import dataclass
from typing import Optional


@dataclass
class PlaybackSource:
    url: str
    kind: str = "iframe"
    quality: Optional[str] = None
    codec: Optional[str] = None


@dataclass
class AudioTrack:
    language: str
    label: Optional[str] = None
    default: bool = False
    codec: Optional[str] = None


@dataclass
class SubtitleTrack:
    language: str
    label: Optional[str] = None
    url: Optional[str] = None
    format: Optional[str] = None
    default: bool = False

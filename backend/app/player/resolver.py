"""Playback resolver stub.

This module intentionally avoids any streaming or network operations. It
returns deterministic dummy metadata that downstream layers can shape into
player-facing responses in future phases.
"""

from .contracts import PlaybackMetadata, PlaybackRequest
from .models import AudioTrack, PlaybackSource, SubtitleTrack


def resolve_playback(request: PlaybackRequest) -> PlaybackMetadata:
    """Produce mock playback metadata for the requested episode.

    No external calls are made; the data is constructed locally to allow
    wiring and contract validation ahead of real player work (P2.7+).
    """

    source = PlaybackSource(
        url=f"https://example.com/stream/{request.anime_id}/{request.episode_id}",
        kind="iframe",
        quality="auto",
    )
    audio = AudioTrack(
        language=request.preferred_audio or "ja",
        label="Japanese",
        default=True,
    )
    subtitle = SubtitleTrack(
        language=request.preferred_subtitle or "en",
        label="English",
        url="https://example.com/subtitles.vtt",
        format="vtt",
        default=True,
    )

    return PlaybackMetadata(
        sources=[source],
        audio_tracks=[audio],
        subtitle_tracks=[subtitle],
        intro={"start": 0, "end": 0},
        outro={"start": 0, "end": 0},
    )

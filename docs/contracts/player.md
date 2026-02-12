# Player Contract (Foundation — P2.6)

## Purpose

Establish a documented boundary for the future video player without enabling
streaming or altering existing API behavior. This phase is architecture-only.

## Scope

- **In scope (foundation):**
  - Data structures for playback metadata (sources, audio, subtitles, intro/outro).
  - A stub resolver that returns deterministic mock data with **no** network or
    streaming.
  - Shared contract types for backend and frontend.
- **Out of scope (future P2.7+):**
  - Actual streaming (HLS/DASH/MP4), media session, buffering, CDN selection.
  - Player UI, controls, hooks, or state management.
  - New /api/* endpoints or backend write-operations.

## Inputs

The player resolver accepts a `PlaybackRequest` with:
- `anime_id`
- `episode_id`
- optional `preferred_audio`
- optional `preferred_subtitle`

No HTTP or upstream calls are performed at this stage.

## Outputs

`PlaybackMetadata` (mocked):
- `sources`: list of `PlaybackSource` (url, kind, quality, codec)
- `audio_tracks`: list of `AudioTrack` (language, label, default, codec)
- `subtitle_tracks`: list of `SubtitleTrack` (language, label, url, format, default)
- `intro` / `outro`: `{start, end}` markers (ms) — default 0/0

## Non-Goals / Invariants

- No streaming, no HLS/DASH, no video element integration.
- No new API contracts or response changes.
- No RBAC changes; no write-operations.
- No external services or network calls inside resolver.

## Responsibilities Boundary

- **Backend (current phase):** Define player domain models, contracts, and a stub
  resolver returning dummy metadata for wiring and testing.
- **Frontend (current phase):** Type declarations only; no UI/logic/hooks.
- **Future phases:** Replace stub resolver with real source selection and hook it
  into API handlers and UI, maintaining the documented contracts.

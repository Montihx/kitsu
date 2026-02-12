import type {
  AudioTrack,
  PlaybackSource,
  SubtitleTrack,
} from "./types";

export type PlaybackRequest = {
  animeId: string;
  episodeId: string;
  preferredAudio?: string;
  preferredSubtitle?: string;
};

export type PlaybackMetadata = {
  sources: PlaybackSource[];
  audioTracks: AudioTrack[];
  subtitleTracks: SubtitleTrack[];
  intro: { start: number; end: number };
  outro: { start: number; end: number };
};

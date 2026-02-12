export type PlaybackSource = {
  url: string;
  kind: string; // e.g., "iframe", "mp4" (future)
  quality?: string;
  codec?: string;
};

export type AudioTrack = {
  language: string;
  label?: string;
  default?: boolean;
  codec?: string;
};

export type SubtitleTrack = {
  language: string;
  label?: string;
  url?: string;
  format?: string;
  default?: boolean;
};

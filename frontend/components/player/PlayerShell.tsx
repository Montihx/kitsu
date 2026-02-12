"use client";

import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useAnimeSelector } from "@/store/anime-store";
import { useAuthSelector } from "@/store/auth-store";
import { useGetAllEpisodes } from "@/query/get-all-episodes";
import { useGetEpisodeData } from "@/query/get-episode-data";
import { useGetEpisodeServers } from "@/query/get-episode-servers";
import {
  getFallbackServer,
  type ServerKeyState,
  type ValidServerKey,
} from "@/utils/fallback-server";
import { getPlayerStorage, updatePlayerStorage } from "@/utils/player-storage";
import {
  CONTINUE_PROGRESS_MAX,
  CONTINUE_PROGRESS_MIN,
  convertFractionToPercent,
  parseNumber,
} from "@/utils/player-progress";
import { setLocalStorageJSON } from "@/utils/storage";
import { getWatchedDetails } from "@/utils/watched";
import LazyIframe from "@/components/player/LazyIframe";
import EpisodeList from "@/components/player/EpisodeList";
import TranslationSelector from "@/components/player/TranslationSelector";
import PlayerToolbar from "@/components/player/PlayerToolbar";
import {
  useWatchProgress,
  type WatchProgressPayload,
} from "@/hooks/use-watch-progress";

const resolvePlaybackEventName = (payload: unknown): string | null => {
  if (!payload) return null;
  if (typeof payload === "string") {
    const trimmed = payload.trim();
    if (trimmed.startsWith("{")) {
      try {
        return resolvePlaybackEventName(JSON.parse(trimmed));
      } catch {
        return trimmed;
      }
    }
    return trimmed;
  }
  if (typeof payload === "object") {
    const record = payload as Record<string, unknown>;
    const eventName = record.event ?? record.type ?? record.action ?? record.message;
    return typeof eventName === "string" ? eventName : null;
  }
  return null;
};

const isPlaybackEndedMessage = (data: unknown) => {
  const eventName = resolvePlaybackEventName(data);
  if (!eventName) return false;
  const normalized = eventName.toLowerCase();
  return (
    normalized === "ended" ||
    normalized.endsWith(":ended") ||
    normalized.includes("ended")
  );
};

const isPlaybackPausedMessage = (data: unknown) => {
  const eventName = resolvePlaybackEventName(data);
  if (!eventName) return false;
  const normalized = eventName.toLowerCase();
  return (
    normalized === "pause" ||
    normalized === "paused" ||
    normalized.endsWith(":pause") ||
    normalized.endsWith(":paused") ||
    normalized.includes("pause")
  );
};

const parseMessagePayload = (data: unknown): unknown => {
  if (typeof data === "string") {
    const trimmed = data.trim();
    if (!trimmed) return data;
    if (trimmed.startsWith("{")) {
      try {
        return JSON.parse(trimmed);
      } catch {
        return data;
      }
    }
  }
  return data;
};

const resolveNumberValue = (
  record: Record<string, unknown>,
  keys: string[],
): number | undefined => {
  for (const key of keys) {
    const parsed = parseNumber(record[key]);
    if (parsed !== undefined) {
      return parsed;
    }
  }
  return undefined;
};

const extractPlaybackMetrics = (
  data: unknown,
): Pick<WatchProgressPayload, "positionSeconds" | "progressPercent"> | null => {
  const payload = parseMessagePayload(data);
  if (!payload || typeof payload !== "object") return null;
  const record = payload as Record<string, unknown>;
  const nested =
    typeof record.data === "object" && record.data !== null
      ? (record.data as Record<string, unknown>)
      : typeof record.payload === "object" && record.payload !== null
        ? (record.payload as Record<string, unknown>)
        : record;

  const positionSeconds = resolveNumberValue(nested, [
    "currentTime",
    "current",
    "time",
    "position",
    "seconds",
    "played",
  ]);
  const duration = resolveNumberValue(nested, [
    "duration",
    "total",
    "length",
    "timeTotal",
    "end",
  ]);
  let progressPercent = resolveNumberValue(nested, [
    "progressPercent",
    "progress",
    "percent",
  ]);

  if (
    progressPercent === undefined &&
    positionSeconds !== undefined &&
    duration !== undefined &&
    duration > 0
  ) {
    progressPercent = (positionSeconds / duration) * 100;
  }

  progressPercent = convertFractionToPercent(progressPercent);

  if (positionSeconds === undefined && progressPercent === undefined) {
    return null;
  }

  return {
    positionSeconds,
    progressPercent,
  };
};

// Save progress every 10% to limit backend updates while keeping resume accurate.
const PROGRESS_STEP_PERCENT = 10;
const PLAYER_LABELS = {
  continueWatching: "Продолжить просмотр",
  newEpisode: "Новая серия",
  episode: "серия",
};
type PlayerShellProps = {
  layout?: "split" | "stacked";
  preferLatestEpisode?: boolean;
};

const PlayerShell = ({
  layout = "split",
  preferLatestEpisode = false,
}: PlayerShellProps) => {
  const selectedEpisode = useAnimeSelector((state) => state.selectedEpisode);
  const setSelectedEpisode = useAnimeSelector(
    (state) => state.setSelectedEpisode,
  );
  const anime = useAnimeSelector((state) => state.anime);
  const auth = useAuthSelector((state) => state.auth);
  const animeId = anime.anime.info.id || "";

  const { data: episodesData, isLoading: episodesLoading } =
    useGetAllEpisodes(animeId);

  const {
    progress,
    status: progressStatus,
    loadProgress,
    saveProgress,
    fallbackTranslation,
  } = useWatchProgress(animeId);

  const [autoplayNext, setAutoplayNext] = useState(false);
  const [preferredTranslation, setPreferredTranslation] = useState<string>();

  const hasInitializedEpisode = useRef(false);
  const hasHydratedAutoplay = useRef(false);
  const hasHandledAutoplay = useRef<string | null>(null);
  const lastSavedEpisodeRef = useRef<number | null>(null);
  const lastProgressStepRef = useRef<number>(-1);
  const lastProgressPayloadRef = useRef<
    Pick<WatchProgressPayload, "positionSeconds" | "progressPercent"> | null
  >(null);
  const hasHiddenPersistedRef = useRef(false);

  useEffect(() => {
    hasInitializedEpisode.current = false;
    hasHydratedAutoplay.current = false;
  }, [animeId]);

  useEffect(() => {
    if (!animeId) return;
    const stored = getPlayerStorage(animeId);
    setAutoplayNext(Boolean(stored.autoplayNext));
  }, [animeId]);

  useEffect(() => {
    if (!animeId) return;
    setPreferredTranslation(progress?.translationKey ?? fallbackTranslation);
  }, [animeId, fallbackTranslation, progress?.translationKey]);

  useEffect(() => {
    if (!animeId) return;
    void loadProgress();
  }, [animeId, loadProgress]);

  useEffect(() => {
    if (!animeId) return;
    if (!hasHydratedAutoplay.current) {
      hasHydratedAutoplay.current = true;
      return;
    }
    updatePlayerStorage(animeId, { autoplayNext });
  }, [animeId, autoplayNext]);

  useEffect(() => {
    if (!animeId || !episodesData?.episodes.length) return;
    if (progressStatus !== "loaded") return;
    if (hasInitializedEpisode.current) return;
    const selectedEpisodeExists = selectedEpisode
      ? episodesData.episodes.some(
          (episode) => episode.episodeId === selectedEpisode,
        )
      : false;
    if (selectedEpisodeExists) {
      hasInitializedEpisode.current = true;
      return;
    }

    const storedEpisodeNumber = progress?.episode;
    const storedEpisode = storedEpisodeNumber
      ? episodesData.episodes.find(
          (episode) => episode.number === storedEpisodeNumber,
        )
      : undefined;
    const resolvedEpisode =
      storedEpisode ??
      (preferLatestEpisode
        ? episodesData.episodes[episodesData.episodes.length - 1]
        : episodesData.episodes[0]);

    if (resolvedEpisode && resolvedEpisode.episodeId !== selectedEpisode) {
      setSelectedEpisode(resolvedEpisode.episodeId);
    }

    hasInitializedEpisode.current = true;
  }, [
    animeId,
    episodesData,
    progress?.episode,
    progressStatus,
    preferLatestEpisode,
    selectedEpisode,
    setSelectedEpisode,
  ]);

  const { data: serversData } = useGetEpisodeServers(selectedEpisode);

  const [serverName, setServerName] = useState<string>("");
  const [serverKey, setServerKey] = useState<ServerKeyState>("");

  useEffect(() => {
    if (!serversData) return;
    const fallback = getFallbackServer(serversData, preferredTranslation);
    setServerName(fallback.serverName);
    setServerKey(fallback.key);
  }, [serversData, preferredTranslation]);

  const { data: episodeData } = useGetEpisodeData(
    selectedEpisode,
    serverName,
    serverKey || "sub",
  );

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (auth) return;
    if (!episodeData) return;

    const watchedDetails = getWatchedDetails();

    const existingAnime = watchedDetails.find(
      (watchedAnime) => watchedAnime.anime.id === anime.anime.info.id,
    );

    if (!existingAnime) {
      const updatedWatchedDetails = [
        ...watchedDetails,
        {
          anime: {
            id: anime.anime.info.id,
            title: anime.anime.info.name,
            poster: anime.anime.info.poster,
          },
          episodes: [selectedEpisode],
        },
      ];
      setLocalStorageJSON("watched", updatedWatchedDetails);
      return;
    }

    const episodeAlreadyWatched =
      existingAnime.episodes.includes(selectedEpisode);

    if (episodeAlreadyWatched) {
      return;
    }

    const updatedWatchedDetails = watchedDetails.map((watchedAnime) =>
      watchedAnime.anime.id === anime.anime.info.id
        ? {
            ...watchedAnime,
            episodes: [...watchedAnime.episodes, selectedEpisode],
          }
        : watchedAnime,
    );

    setLocalStorageJSON("watched", updatedWatchedDetails);
  }, [
    anime.anime.info.id,
    anime.anime.info.name,
    anime.anime.info.poster,
    auth,
    episodeData,
    selectedEpisode,
  ]);

  const currentEpisodeNumber = useMemo(() => {
    if (!episodesData?.episodes.length || !selectedEpisode) return undefined;
    const episodeDetails = episodesData.episodes.find(
      (episode) => episode.episodeId === selectedEpisode,
    );
    return episodeDetails?.number;
  }, [episodesData, selectedEpisode]);

  const normalizedProgressPercent = useMemo(
    () => convertFractionToPercent(progress?.progressPercent),
    [progress?.progressPercent],
  );

  const continueWatchingEpisode = useMemo(() => {
    if (!episodesData?.episodes.length || !progress?.episode) return undefined;
    return episodesData.episodes.find(
      (episode) => episode.number === progress.episode,
    );
  }, [episodesData, progress?.episode]);

  const shouldShowContinueWatching =
    continueWatchingEpisode &&
    normalizedProgressPercent !== undefined &&
    normalizedProgressPercent >= CONTINUE_PROGRESS_MIN &&
    normalizedProgressPercent <= CONTINUE_PROGRESS_MAX;

  const maxEpisodeNumber = useMemo(() => {
    if (!episodesData?.episodes.length) return undefined;
    return episodesData.episodes.reduce(
      (max, episode) => Math.max(max, episode.number),
      0,
    );
  }, [episodesData]);

  const isOngoingAnime = useMemo(() => {
    const status = anime.anime.moreInfo.status?.toLowerCase() ?? "";
    return (
      status.includes("ongoing") ||
      status.includes("airing") ||
      status.includes("active")
    );
  }, [anime.anime.moreInfo.status]);

  const newEpisodeNumber = useMemo(() => {
    if (!isOngoingAnime || !maxEpisodeNumber || !progress?.episode) {
      return undefined;
    }
    return progress.episode < maxEpisodeNumber ? maxEpisodeNumber : undefined;
  }, [isOngoingAnime, maxEpisodeNumber, progress?.episode]);

  const progressByEpisodeNumber = useMemo(() => {
    const progressMap: Record<number, number> = {};
    if (!episodesData?.episodes.length || !progress?.episode) return progressMap;
    const lastEpisodeNumber = progress.episode;
    for (const episode of episodesData.episodes) {
      if (episode.number < lastEpisodeNumber) {
        progressMap[episode.number] = 100;
      }
    }
    if (normalizedProgressPercent !== undefined) {
      progressMap[lastEpisodeNumber] = normalizedProgressPercent;
    }
    return progressMap;
  }, [episodesData, normalizedProgressPercent, progress?.episode]);

  const handleSelectEpisode = useCallback(
    (episode: string) => {
      setSelectedEpisode(episode);
    },
    [setSelectedEpisode],
  );

  useEffect(() => {
    if (!animeId || currentEpisodeNumber === undefined) return;
    if (lastSavedEpisodeRef.current === currentEpisodeNumber) return;
    lastSavedEpisodeRef.current = currentEpisodeNumber;
    const shouldPreserveProgress = progress?.episode === currentEpisodeNumber;
    void saveProgress({
      episode: currentEpisodeNumber,
      translationKey: preferredTranslation ?? serverName,
      positionSeconds: shouldPreserveProgress
        ? progress?.positionSeconds
        : undefined,
      progressPercent: shouldPreserveProgress ? normalizedProgressPercent : undefined,
    });
  }, [
    animeId,
    currentEpisodeNumber,
    normalizedProgressPercent,
    preferredTranslation,
    progress?.episode,
    progress?.positionSeconds,
    saveProgress,
    serverName,
  ]);

  const handleServerChange = (name: string, key: ValidServerKey) => {
    setServerName(name);
    setServerKey(key);
    setPreferredTranslation(name);
    if (!animeId || currentEpisodeNumber === undefined) return;
    void saveProgress({
      episode: currentEpisodeNumber,
      translationKey: name,
    });
  };

  const handleAutoplayNext = useCallback(() => {
    if (!episodesData?.episodes.length || !selectedEpisode) return;
    if (hasHandledAutoplay.current === selectedEpisode) return;

    const currentIndex = episodesData.episodes.findIndex(
      (episode) => episode.episodeId === selectedEpisode,
    );
    if (currentIndex < 0) return;
    const nextEpisode = episodesData.episodes[currentIndex + 1];
    if (!nextEpisode) return;

    hasHandledAutoplay.current = selectedEpisode;
    setSelectedEpisode(nextEpisode.episodeId);
  }, [episodesData, selectedEpisode, setSelectedEpisode]);

  const playerOrigin = useMemo(() => {
    if (!episodeData?.sources?.[0]?.url) return "";
    try {
      return new URL(episodeData.sources[0].url).origin;
    } catch {
      return "";
    }
  }, [episodeData]);

  const persistLatestProgress = useCallback(() => {
    if (!animeId || currentEpisodeNumber === undefined) return;
    if (hasHiddenPersistedRef.current) return;
    hasHiddenPersistedRef.current = true;
    const payload = lastProgressPayloadRef.current;
    void saveProgress({
      episode: currentEpisodeNumber,
      translationKey: preferredTranslation ?? serverName,
      positionSeconds: payload?.positionSeconds,
      progressPercent: payload?.progressPercent,
    });
  }, [
    animeId,
    currentEpisodeNumber,
    preferredTranslation,
    saveProgress,
    serverName,
  ]);

  useEffect(() => {
    hasHandledAutoplay.current = null;
    lastProgressStepRef.current = -1;
    lastProgressPayloadRef.current = null;
    hasHiddenPersistedRef.current = false;
  }, [selectedEpisode]);

  useEffect(() => {
    if (!playerOrigin || currentEpisodeNumber === undefined) return;

    const handleMessage = (event: MessageEvent) => {
      if (event.origin !== playerOrigin) return;
      if (autoplayNext && isPlaybackEndedMessage(event.data)) {
        handleAutoplayNext();
        return;
      }

      const metrics = extractPlaybackMetrics(event.data);
      if (metrics) {
        lastProgressPayloadRef.current = metrics;
      }

      if (isPlaybackPausedMessage(event.data)) {
        const payload = metrics ?? lastProgressPayloadRef.current;
        if (!payload) return;
        void saveProgress({
          episode: currentEpisodeNumber,
          translationKey: preferredTranslation ?? serverName,
          positionSeconds: payload.positionSeconds,
          progressPercent: payload.progressPercent,
        });
        return;
      }

      if (!metrics) return;
      const progressPercent = metrics.progressPercent;
      if (progressPercent === undefined) return;
      const step = Math.floor(progressPercent / PROGRESS_STEP_PERCENT);
      if (step === lastProgressStepRef.current) return;
      lastProgressStepRef.current = step;
      void saveProgress({
        episode: currentEpisodeNumber,
        translationKey: preferredTranslation ?? serverName,
        positionSeconds: metrics.positionSeconds,
        progressPercent,
      });
    };

    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, [
    autoplayNext,
    currentEpisodeNumber,
    handleAutoplayNext,
    playerOrigin,
    preferredTranslation,
    saveProgress,
    serverName,
  ]);

  useEffect(() => {
    if (!animeId || currentEpisodeNumber === undefined) return;
    const handleVisibilityChange = () => {
      if (document.visibilityState === "hidden") {
        persistLatestProgress();
      } else if (document.visibilityState === "visible") {
        hasHiddenPersistedRef.current = false;
      }
    };
    window.addEventListener("pagehide", persistLatestProgress);
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      window.removeEventListener("pagehide", persistLatestProgress);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [animeId, currentEpisodeNumber, persistLatestProgress]);

  const iframeResetKey = useMemo(
    () => `${selectedEpisode}-${serverName}-${serverKey}`,
    [selectedEpisode, serverName, serverKey],
  );

  const playerSource = episodeData?.sources?.[0]?.url;
  const playerPoster = anime.anime.info.poster;
  const containerRef = useRef<HTMLDivElement>(null);

  const isStackedLayout = layout === "stacked";

  return (
    <div
      className={
        isStackedLayout
          ? "flex w-full flex-col gap-6"
          : "grid lg:grid-cols-4 grid-cols-1 gap-y-5 gap-x-10 h-auto w-full"
      }
    >
      <div className={isStackedLayout ? "w-full" : "lg:col-span-3 col-span-1 lg:mb-0"}>
        <div className="space-y-4">
          {(shouldShowContinueWatching || newEpisodeNumber) && (
            <div className="flex flex-wrap items-center gap-2 text-xs text-slate-200">
              {shouldShowContinueWatching && (
                <span className="inline-flex items-center gap-2 rounded-full bg-pink-500/10 px-3 py-1 font-semibold text-pink-200">
                  {PLAYER_LABELS.continueWatching}
                  <span className="text-[11px] text-pink-200">
                    {PLAYER_LABELS.episode} {continueWatchingEpisode?.number}
                  </span>
                </span>
              )}
              {newEpisodeNumber && (
                <span className="inline-flex items-center gap-2 rounded-full bg-amber-500/20 px-3 py-1 font-semibold text-amber-100">
                  {PLAYER_LABELS.newEpisode}
                  <span className="text-[11px] text-amber-200">
                    {newEpisodeNumber}
                  </span>
                </span>
              )}
            </div>
          )}
          <div ref={containerRef}>
            <LazyIframe
              src={playerSource}
              poster={playerPoster}
              title={anime.anime.info.name}
              resetKey={iframeResetKey}
            />
          </div>
          <div className="flex flex-col gap-4 rounded-md bg-[#0f172a] p-4">
            <TranslationSelector
              serversData={serversData}
              serverName={serverName}
              serverKey={serverKey}
              onChange={handleServerChange}
            />
            <PlayerToolbar
              containerRef={containerRef}
              autoplayNext={autoplayNext}
              onAutoplayNextChange={setAutoplayNext}
            />
          </div>
        </div>
      </div>
      {episodesData && (
        <EpisodeList
          title={
            anime.anime.info.name ||
            (anime.anime.moreInfo.japanese as string)
          }
          subOrDub={anime.anime.info.stats.episodes}
          episodes={episodesData}
          isLoading={episodesLoading}
          selectedEpisodeId={selectedEpisode}
          onSelectEpisode={handleSelectEpisode}
          progressByEpisodeNumber={progressByEpisodeNumber}
          newEpisodeNumber={newEpisodeNumber}
        />
      )}
    </div>
  );
};

export default PlayerShell;

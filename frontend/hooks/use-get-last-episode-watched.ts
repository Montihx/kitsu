"use client";

import { useState, useEffect } from "react";
import { IWatchedAnime } from "@/types/watched-anime";
import { getLocalStorageJSON, removeLocalStorageItem } from "@/utils/storage";

export const useGetLastEpisodeWatched = (animeId: string) => {
  const [lastEpisodeWatched, setLastEpisodeWatched] = useState<string | null>(
    null,
  );

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const watchedDetails = getLocalStorageJSON<Array<IWatchedAnime>>("watched", []);

    if (!Array.isArray(watchedDetails)) {
      removeLocalStorageItem("watched");
      setLastEpisodeWatched(null);
      return;
    }

    const anime = watchedDetails.find(
      (watchedAnime) => watchedAnime.anime.id === animeId,
    );

    if (anime && anime.episodes.length > 0) {
      const lastWatched = anime.episodes[anime.episodes.length - 1]; // Get the last episode
      setLastEpisodeWatched(lastWatched);
    } else {
      setLastEpisodeWatched(null); // No episodes watched
    }
  }, [animeId]);

  return lastEpisodeWatched;
};

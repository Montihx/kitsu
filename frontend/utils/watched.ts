"use client";

import { IWatchedAnime } from "@/types/watched-anime";
import { getLocalStorageJSON, removeLocalStorageItem } from "@/utils/storage";

export const getWatchedDetails = () => {
  const watchedDetails = getLocalStorageJSON<Array<IWatchedAnime>>(
    "watched",
    [],
  );

  if (!Array.isArray(watchedDetails)) {
    removeLocalStorageItem("watched");
    return [];
  }

  return watchedDetails;
};

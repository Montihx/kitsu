"use client";

import React, { useEffect, useState } from "react";
import Image from "next/image";
import { Play } from "lucide-react";
import { cn } from "@/lib/utils";

const TEXT = {
  posterUnavailable: "Постер недоступен",
  sourceUnavailable: "Источник недоступен",
  startPlayback: "Смотреть",
  startPlaybackLabel: "Start playback",
};
const FRAME_CLASSES =
  "relative w-full h-auto aspect-video min-h-[20vh] sm:min-h-[30vh] md:min-h-[40vh] lg:min-h-[60vh] max-h-[500px] lg:max-h-[calc(100vh-150px)] bg-black overflow-hidden";

type Props = {
  src?: string;
  poster?: string;
  title?: string;
  resetKey?: string;
  className?: string;
};

const LazyIframe = ({ src, poster, title, resetKey, className }: Props) => {
  const [isClient, setIsClient] = useState(false);
  const [isActive, setIsActive] = useState(false);

  const canPlay = Boolean(src);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    setIsActive(false);
  }, [resetKey, src]);

  return (
    <div
      className={cn(FRAME_CLASSES, className)}
    >
      {isClient && isActive && src ? (
        <iframe
          title={title ?? "Player"}
          src={src}
          width="100%"
          height="100%"
          loading="lazy"
          sandbox="allow-scripts allow-same-origin allow-presentation"
          referrerPolicy="no-referrer"
          allowFullScreen
          className="h-full w-full"
        />
      ) : (
        <button
          type="button"
          aria-label={
            canPlay ? TEXT.startPlaybackLabel : TEXT.sourceUnavailable
          }
          onClick={() => canPlay && setIsActive(true)}
          disabled={!canPlay}
          className={cn(
            "relative h-full w-full text-left",
            !canPlay && "cursor-not-allowed",
          )}
        >
          {poster ? (
            <Image
              src={poster}
              alt={title ? `${title} poster` : "Poster"}
              fill
              sizes="100vw"
              className="object-cover"
              unoptimized
            />
          ) : (
            <div className="flex h-full w-full items-center justify-center bg-slate-900 text-sm text-slate-200">
              {TEXT.posterUnavailable}
            </div>
          )}
          <div className="absolute inset-0 flex items-center justify-center bg-black/50">
            {canPlay ? (
              <span className="flex items-center gap-2 rounded-md bg-black/60 px-4 py-2 text-sm font-semibold text-white">
                <Play className="h-5 w-5" />
                {TEXT.startPlayback}
              </span>
            ) : (
              <span className="rounded-md bg-black/60 px-4 py-2 text-sm text-white">
                {TEXT.sourceUnavailable}
              </span>
            )}
          </div>
        </button>
      )}
    </div>
  );
};

export default LazyIframe;

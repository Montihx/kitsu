"use client";

import React from "react";
import { Maximize } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
const AUTOPLAY_NEXT_LABEL = "Автовоспроизведение следующей серии";

type Props = {
  containerRef: React.RefObject<HTMLElement>;
  autoplayNext: boolean;
  onAutoplayNextChange: (value: boolean) => void;
};

const PlayerToolbar = ({
  containerRef,
  autoplayNext,
  onAutoplayNextChange,
}: Props) => {
  const handleFullscreen = () => {
    const target = containerRef.current;
    if (!target) return;
    if (document.fullscreenElement) {
      document.exitFullscreen?.();
      return;
    }
    const request =
      target.requestFullscreen ||
      (target as HTMLElement & { webkitRequestFullscreen?: () => void })
        .webkitRequestFullscreen;
    request?.call(target);
  };

  return (
    <div className="flex flex-wrap items-center justify-between gap-4 text-sm">
      <label className="flex items-center gap-2">
        <Switch
          checked={autoplayNext}
          onCheckedChange={onAutoplayNextChange}
          id="autoplay-next"
        />
        <span>{AUTOPLAY_NEXT_LABEL}</span>
      </label>
      <Button
        type="button"
        size="icon"
        variant="secondary"
        onClick={handleFullscreen}
        aria-label="Toggle fullscreen"
      >
        <Maximize className="h-4 w-4" />
      </Button>
    </div>
  );
};

export default PlayerToolbar;

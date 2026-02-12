"use client";

import React, { useMemo } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { IEpisodeServers } from "@/types/episodes";
import { type ServerKey, type ServerKeyState } from "@/utils/fallback-server";

const TEXT = {
  subtitles: "Субтитры",
  dubs: "Озвучка",
  noTranslations: "Нет доступных переводов для выбора.",
};

type ServerOption = {
  key: ServerKey;
  serverName: string;
};

type Props = {
  serversData?: IEpisodeServers;
  serverName: string;
  serverKey: ServerKeyState;
  onChange: (serverName: string, key: ServerKey) => void;
};

const TranslationSelector = ({
  serversData,
  serverName,
  serverKey,
  onChange,
}: Props) => {
  const subtitleServers = useMemo<ServerOption[]>(() => {
    if (!serversData) return [];
    return [
      ...serversData.sub.map((server) => ({
        serverName: server.serverName,
        key: "sub" as const,
      })),
      ...serversData.raw.map((server) => ({
        serverName: server.serverName,
        key: "raw" as const,
      })),
    ];
  }, [serversData]);

  const dubServers = useMemo<ServerOption[]>(() => {
    if (!serversData) return [];
    return serversData.dub.map((server) => ({
      serverName: server.serverName,
      key: "dub" as const,
    }));
  }, [serversData]);

  const renderGroup = (title: string, options: ServerOption[]) => {
    if (!options.length) return null;
    return (
      <div className="flex flex-col gap-2">
      <p className="text-sm font-semibold text-slate-200">{title}</p>
        <div className="flex flex-wrap gap-2">
          {options.map((option) => {
            const isActive =
              option.serverName === serverName && option.key === serverKey;
            return (
              <Button
                key={`${option.key}-${option.serverName}`}
                type="button"
                size="sm"
                variant={isActive ? "secondary" : "outline"}
                className={cn(
                  "text-xs uppercase",
                  isActive && "bg-[#e9376b] text-white hover:bg-[#e9376b]",
                )}
                onClick={() => onChange(option.serverName, option.key)}
              >
                {option.serverName}
              </Button>
            );
          })}
        </div>
      </div>
    );
  };

  if (!serversData) {
    return (
      <p className="text-sm text-slate-400">{TEXT.noTranslations}</p>
    );
  }

  if (!subtitleServers.length && !dubServers.length) {
    return <p className="text-sm text-slate-400">{TEXT.noTranslations}</p>;
  }

  return (
    <div className="flex flex-col gap-4">
      {renderGroup(TEXT.subtitles, subtitleServers)}
      {renderGroup(TEXT.dubs, dubServers)}
    </div>
  );
};

export default TranslationSelector;

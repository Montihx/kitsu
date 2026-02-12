"use client";

import { IEpisodeServers } from "@/types/episodes";

export type ServerKey = "sub" | "dub" | "raw";
export type ServerKeyState = ServerKey | "";
export type ValidServerKey = ServerKey;

export function getFallbackServer(
  serversData: IEpisodeServers | undefined,
  preferredServerName?: string,
): {
  serverName: string;
  key: ServerKeyState;
} {
  if (preferredServerName && serversData) {
    const keys: Array<ServerKey> = ["sub", "dub", "raw"];
    for (const key of keys) {
      const match = serversData[key]?.find(
        (server) => server.serverName === preferredServerName,
      );
      if (match) {
        return {
          serverName: match.serverName,
          key,
        };
      }
    }
  }

  if (serversData) {
    const keys: Array<ServerKey> = ["sub", "dub", "raw"];
    for (const key of keys) {
      const serverList = serversData[key]; // Safely index the object
      if (serverList && serverList[0]?.serverName) {
        return {
          serverName: serverList[0].serverName,
          key,
        };
      }
    }
  }
  return {
    serverName: "",
    key: "",
  }; // Fallback if no valid server is found
}

"use client";
import { useSearchParams } from "next/navigation";
import PlayerShell from "@/components/player/PlayerShell";

const Page = () => {
  const searchParams = useSearchParams();
  const preferLatestEpisode = Boolean(searchParams.get("type"));
  return <PlayerShell preferLatestEpisode={preferLatestEpisode} />;
};

export default Page;

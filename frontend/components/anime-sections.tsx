"use client";

import React from "react";
import Container from "./container";
import AnimeCard from "./anime-card";

import BlurFade from "./ui/blur-fade";
import { IAnime } from "@/types/anime";
import { ROUTES } from "@/constants/routes";

type Props = {
  trendingAnime: IAnime[];
  loading: boolean;
  title: string;
};

const AnimeSections = (props: Props) => {
  if (props.loading) return <LoadingSkeleton />;
  if (!Array.isArray(props.trendingAnime) || props.trendingAnime.length === 0) {
    return <LoadingSkeleton />;
  }
  return (
    <Container className="flex flex-col gap-6 py-10 items-center lg:items-start">
      <div className="flex items-center justify-between w-full">
        <h2 className="text-2xl md:text-3xl font-bold tracking-tight">{props.title}</h2>
        <button className="text-primary hover:text-primary/80 transition-colors duration-200 text-sm font-semibold hidden sm:block">
          Показать всё →
        </button>
      </div>
      <div className="grid lg:grid-cols-5 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-6 2xl:grid-cols-7 w-full gap-4 md:gap-5 content-center">
        {props.trendingAnime.map((anime, idx) => (
          <BlurFade key={idx} delay={idx * 0.05} inView>
            <AnimeCard
              title={anime.name}
              subTitle={anime.type ? anime.type : `Rank: ${anime.rank}`}
              poster={anime.poster}
              className="self-center justify-self-center"
              href={`${ROUTES.ANIME_DETAILS}/${anime.id}`}
              episodeCard
              sub={anime?.episodes?.sub}
              dub={anime?.episodes?.dub}
            />
          </BlurFade>
        ))}
      </div>
    </Container>
  );
};

const LoadingSkeleton = () => {
  return (
    <Container className="flex flex-col gap-6 py-10 items-center lg:items-start">
      <div className="h-8 w-64 skeleton rounded-md"></div>
      <div className="grid lg:grid-cols-5 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-6 2xl:grid-cols-7 w-full gap-4 md:gap-5 content-center">
        {[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1].map((_, idx) => {
          return (
            <div
              key={idx}
              className="rounded-xl h-[15.625rem] min-w-[10.625rem] max-w-[12.625rem] md:h-[18.75rem] md:max-w-[12.5rem] skeleton"
            ></div>
          );
        })}
      </div>
    </Container>
  );
};

export default AnimeSections;

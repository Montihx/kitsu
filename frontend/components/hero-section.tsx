"use client";

import {
  Carousel,
  CarouselApi,
  CarouselContent,
  CarouselItem,
} from "./ui/carousel";

import Container from "./container";
import { Button } from "./ui/button";

import React from "react";
import { ArrowLeft, ArrowRight, Captions, Mic } from "lucide-react";

import { ROUTES } from "@/constants/routes";
import { ButtonLink } from "./common/button-link";
import { SpotlightAnime } from "@/types/anime";
import { Badge } from "./ui/badge";
import { HERO_SPOTLIGHT_FALLBACK } from "@/constants/fallbacks";

type IHeroSectionProps = {
  spotlightAnime: SpotlightAnime[];
  isDataLoading: boolean;
};

const HeroSection = (props: IHeroSectionProps) => {
  const [api, setApi] = React.useState<CarouselApi>();

  const hasSpotlight = Array.isArray(props.spotlightAnime) && props.spotlightAnime.length > 0;
  const shouldUseFallback = props.isDataLoading || !hasSpotlight;
  const spotlightList = shouldUseFallback ? HERO_SPOTLIGHT_FALLBACK : props.spotlightAnime;
  if (!spotlightList.length) return <LoadingSkeleton />;

  return (
    <div className="h-[80vh] w-full relative">
      <Carousel className="w-full" setApi={setApi} opts={{}}>
        <CarouselContent className="">
          {spotlightList.map((anime, index) => (
            <CarouselItem key={index}>
              <HeroCarouselItem anime={anime} />
            </CarouselItem>
          ))}
        </CarouselContent>
      </Carousel>
      <div className="absolute hidden md:flex items-center gap-3 right-10 3xl:bottom-10 bottom-24 z-50 isolate">
        <Button
          onClick={() => {
            api?.scrollPrev();
          }}
          className="rounded-full bg-background/20 backdrop-blur-md border border-foreground/20 h-12 w-12 hover:bg-primary hover:border-primary transition-all duration-300 hover:scale-110"
        >
          <ArrowLeft className="text-foreground shrink-0" />
        </Button>
        <Button
          onClick={() => api?.scrollNext()}
          className="rounded-full bg-background/20 backdrop-blur-md border border-foreground/20 h-12 w-12 hover:bg-primary hover:border-primary transition-all duration-300 hover:scale-110"
        >
          <ArrowRight className="text-foreground shrink-0" />
        </Button>
      </div>
    </div>
  );
};

const HeroCarouselItem = ({ anime }: { anime: SpotlightAnime }) => {
  return (
    <div
      className={`w-full bg-cover bg-no-repeat bg-center h-[80vh] relative overflow-hidden`}
      style={{ backgroundImage: `url(${anime?.poster})` }}
    >
      {/* Gradient Overlay - Enhanced for better readability */}
      <div className="absolute h-full w-full inset-0 m-auto bg-gradient-to-r from-background via-background/70 to-transparent z-10"></div>
      <div className="absolute h-full w-full inset-0 m-auto bg-gradient-to-t from-background via-background/50 to-transparent z-10"></div>

      {/* Content Section */}
      <div className="w-full h-[calc(100%-5.25rem)] relative z-20">
        <Container className="w-full h-full flex flex-col justify-end md:justify-center pb-10">
          <div className="space-y-3 lg:w-[45vw] animate-fade-in">
            {/* Title with better typography */}
            <h1 className="text-4xl md:text-5xl font-bold leading-tight tracking-tight drop-shadow-lg">
              {anime?.name}
            </h1>

            {/* Badges with modern styling */}
            <div className="flex flex-row items-center space-x-2">
              {anime.episodes.sub && (
                <Badge className="bg-primary text-white flex flex-row items-center space-x-1 px-2.5 py-1 font-semibold">
                  <Captions size={16} />
                  <span>SUB {anime.episodes.sub}</span>
                </Badge>
              )}
              {anime.episodes.dub && (
                <Badge className="bg-green-500 text-white flex flex-row items-center space-x-1 px-2.5 py-1 font-semibold">
                  <Mic size={16} />
                  <span>DUB {anime.episodes.dub}</span>
                </Badge>
              )}
              <Badge variant="outline" className="border-foreground/30 text-foreground/80 px-2.5 py-1">
                {anime?.otherInfo?.[0] || anime?.type || "Anime"}
              </Badge>
            </div>

            {/* Description */}
            <p className="text-base md:text-lg line-clamp-3 md:line-clamp-4 text-foreground/90 leading-relaxed">
              {anime?.description}
            </p>

            {/* Action Buttons with hover effects */}
            <div className="flex items-center gap-3 !mt-6">
              <ButtonLink
                href={`${ROUTES.ANIME_DETAILS}/${anime.id}`}
                className="h-11 px-6 text-base bg-primary hover:bg-primary/90 text-white font-semibold shadow-lg shadow-primary/30 transition-all duration-300 hover:scale-105"
              >
                Смотреть
              </ButtonLink>
              <ButtonLink
                href={`${ROUTES.ANIME_DETAILS}/${anime.id}`}
                className="h-11 px-6 text-base border-2 border-foreground/20 bg-background/20 backdrop-blur-sm hover:bg-foreground/10 transition-all duration-300"
                variant="outline"
              >
                Подробнее
              </ButtonLink>
            </div>
          </div>
        </Container>
      </div>
    </div>
  );
};

const LoadingSkeleton = () => {
  return (
    <div className="h-[80vh] w-full relative">
      <div className="w-full h-[calc(100%-5.25rem)] mt-[5.25rem] relative z-20">
        <Container className="w-full h-full flex flex-col justify-end md:justify-center pb-10">
          <div className="space-y-2 lg:w-[40vw]">
            <div className="h-16 animate-pulse bg-slate-700 w-[75%]"></div>
            <div className="h-40 animate-pulse w-full bg-slate-700"></div>
            <div className="flex items-center gap-5">
              <span className="h-10 w-[7.5rem] animate-pulse bg-slate-700"></span>
              <span className="h-10 w-[7.5rem] animate-pulse bg-slate-700"></span>
            </div>
          </div>
        </Container>
      </div>
      <div className="absolute hidden md:flex items-center gap-5 right-10 bottom-32 z-50 isolate">
        <span className="h-10 w-10 rounded-full animate-pulse bg-slate-700"></span>
        <span className="h-10 w-10 rounded-full animate-pulse bg-slate-700"></span>
      </div>
    </div>
  );
};
export default HeroSection;

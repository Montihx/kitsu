import { SpotlightAnime, Type } from "@/types/anime";

export const HERO_SPOTLIGHT_FALLBACK: SpotlightAnime[] = [
  {
    rank: 1,
    id: "kitsune-placeholder",
    name: "Welcome back to Kitsune",
    description:
      "Your feed is loading in the background. Explore while we fetch the latest picks.",
    poster: "/icon.png",
    jname: "Kitsune",
    episodes: { sub: null, dub: null },
    type: Type.Tv,
    otherInfo: [],
  },
];

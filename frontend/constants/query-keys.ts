export const queryKeys = {
  trendingAnime: () => ["get-trending-anime"] as const,
  recentAnime: () => ["get-recent-anime"] as const,
  popularAnime: () => ["get-popular-anime"] as const,
  animeDetails: (animeId: string) => ["get-anime-details", animeId] as const,
  episodeData: (episodeId: string, server: string | undefined, subOrDub: string) =>
    ["get-episode-data", episodeId, server ?? "", subOrDub] as const,
  allEpisodes: (animeId: string) => ["get-all-episodes", animeId] as const,
  searchAnime: (query: string, page: number = 1) =>
    ["search-anime", query, page] as const,
  searchAnimeSuggestions: (query: string) =>
    ["search-anime-suggestions", query] as const,
  episodeServers: (episodeId: string) => ["get-episode-servers", episodeId] as const,
  animeBanner: (anilistId: number) => ["get-anime-banner", anilistId] as const,
  animeSchedule: (date: string) => ["get-anime-schedule", date] as const,
  homePage: () => ["get-home-page-data"] as const,
} as const;

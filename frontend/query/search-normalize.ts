import { SearchAnimeParams } from "@/types/anime";

export const normalizeSearchQuery = (query: string) => query.trim();

export const normalizeSearchParams = (
  params: SearchAnimeParams,
): SearchAnimeParams => {
  const normalizedQuery = normalizeSearchQuery(params.q || "");
  const page = params.page || 1;

  return {
    ...params,
    q: normalizedQuery,
    page,
  };
};

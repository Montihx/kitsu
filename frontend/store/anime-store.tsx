import {
  createContext,
  type ReactNode,
  useContext,
  useRef,
} from "react";
import { useStore } from "zustand";
import { type StoreApi, createStore } from "zustand/vanilla";
import { IAnimeDetails } from "@/types/anime-details";

interface IAnimeStore {
  anime: IAnimeDetails;
  setAnime: (state: IAnimeDetails) => void;
  selectedEpisode: string;
  setSelectedEpisode: (state: string) => void;
}

type AnimeState = Pick<IAnimeStore, "anime" | "selectedEpisode">;
type AnimeStoreApi = StoreApi<IAnimeStore>;

const defaultAnimeDetails: IAnimeDetails = {
  anime: {
    info: {
      id: "",
      anilistId: 0,
      malId: 0,
      name: "",
      poster: "",
      description: "",
      stats: {
        rating: "",
        quality: "",
        episodes: { sub: 0, dub: 0 },
        type: "",
        duration: "",
      },
      promotionalVideos: [],
      charactersVoiceActors: [],
    },
    moreInfo: {
      japanese: "",
      synonyms: "",
      aired: "",
      premiered: "",
      duration: "",
      status: "",
      malscore: "",
      genres: [],
      studios: "",
      producers: [],
    },
  },
  seasons: [],
  mostPopularAnimes: [],
  relatedAnimes: [],
  recommendedAnimes: [],
};

const defaultState: AnimeState = {
  anime: defaultAnimeDetails,
  selectedEpisode: "",
};

const createAnimeStore = (initState: AnimeState = defaultState) =>
  createStore<IAnimeStore>()((set) => ({
    ...defaultState,
    ...initState,
    setAnime: (state: IAnimeDetails) => set({ anime: state }),
    setSelectedEpisode: (state: string) => set({ selectedEpisode: state }),
  }));

let clientStore: AnimeStoreApi | null = null;

const getIsServer = () => typeof document === "undefined";

export const getAnimeStore = (initState?: AnimeState) => {
  if (getIsServer()) {
    return createAnimeStore({ ...defaultState, ...initState });
  }
  if (!clientStore) {
    clientStore = createAnimeStore({ ...defaultState, ...initState });
  } else if (initState) {
    clientStore.setState(
      { ...clientStore.getState(), ...initState },
      true,
    );
  }
  return clientStore;
};

const AnimeStoreContext = createContext<AnimeStoreApi | null>(null);

export const AnimeStoreProvider = ({
  children,
  initialState,
}: {
  children: ReactNode;
  initialState?: AnimeState;
}) => {
  const storeRef = useRef<AnimeStoreApi>();
  if (!storeRef.current) {
    storeRef.current = getAnimeStore(initialState);
  }
  return (
    <AnimeStoreContext.Provider value={storeRef.current}>
      {children}
    </AnimeStoreContext.Provider>
  );
};

const useAnimeStoreApi = () => {
  const store = useContext(AnimeStoreContext);
  if (!store) {
    throw new Error("AnimeStoreProvider is missing in the component tree.");
  }
  return store;
};

export const useAnimeSelector = <T,>(selector: (state: IAnimeStore) => T) => {
  const store = useAnimeStoreApi();
  return useStore(store, selector);
};

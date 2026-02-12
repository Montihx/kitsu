"use client";

import { type ReactNode } from "react";
import { AuthStoreProvider } from "@/store/auth-store";
import { AnimeStoreProvider } from "@/store/anime-store";

type Props = {
  children: ReactNode;
};

const StoreProvider = ({ children }: Props) => {
  return (
    <AuthStoreProvider>
      <AnimeStoreProvider>{children}</AnimeStoreProvider>
    </AuthStoreProvider>
  );
};

export default StoreProvider;

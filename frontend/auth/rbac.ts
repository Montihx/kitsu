"use client";

import { useAuthSelector, type IAuth } from "@/store/auth-store";

export type Role = "guest" | "user" | "admin";
export type Permission =
  | "read:profile"
  | "write:profile"
  | "read:content"
  | "write:content"
  | "admin:*"
  | "anime.view"
  | "anime.edit"
  | "admin:parser.logs"
  | "admin:parser.settings"
  | "admin:parser.emergency";

export const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  guest: ["read:content"],
  user: ["read:profile", "write:profile", "read:content", "write:content"],
  admin: [
    "read:profile",
    "write:profile",
    "read:content",
    "write:content",
    "admin:*",
    "anime.view",
    "anime.edit",
    "admin:parser.logs",
    "admin:parser.settings",
    "admin:parser.emergency",
  ],
};

export const resolveRole = (auth: IAuth | null | undefined): Role => {
  if (!auth?.accessToken) {
    return "guest";
  }
  const claimedRole = (auth as { role?: Role | string | undefined })?.role;
  if (claimedRole === "guest" || claimedRole === "user" || claimedRole === "admin") {
    return claimedRole;
  }
  const isAdmin =
    (auth as { isAdmin?: boolean | undefined }).isAdmin ??
    (auth as { is_admin?: boolean | undefined }).is_admin ??
    (auth as { is_superuser?: boolean | undefined }).is_superuser;
  if (isAdmin) {
    return "admin";
  }
  return "user";
};

export const resolvePermissions = (role: Role): Permission[] => {
  return ROLE_PERMISSIONS[role] ?? [];
};

export const useRole = (): Role => {
  const auth = useAuthSelector((state) => state.auth);
  return resolveRole(auth);
};

export const usePermissions = (): Permission[] => {
  const role = useRole();
  return resolvePermissions(role);
};

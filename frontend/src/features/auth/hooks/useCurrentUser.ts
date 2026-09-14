import { createContext, useContext } from "react";
import type { User } from "../../../shared/types";

export interface CurrentUserContextValue {
  currentUser: User | null;
  users: User[];
  isLoading: boolean;
  loginAs: (userId: string) => void;
  logout: () => void;
}

export const CurrentUserContext = createContext<CurrentUserContextValue | null>(
  null,
);

export function useCurrentUser(): CurrentUserContextValue {
  const ctx = useContext(CurrentUserContext);
  if (!ctx) {
    throw new Error("useCurrentUser must be used within a CurrentUserProvider");
  }
  return ctx;
}

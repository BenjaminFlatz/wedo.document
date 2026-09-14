import { useCallback, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { fetchSeededUsers } from "../api/authApi";
import {
  CurrentUserContext,
  type CurrentUserContextValue,
} from "../hooks/useCurrentUser";
import { CURRENT_USER_STORAGE_KEY } from "../../../shared/lib/apiClient";
import type { User } from "../../../shared/types";

interface Props {
  children: ReactNode;
}

// Loads the seeded users once on mount and keeps the "logged in as" choice
// in localStorage so a page refresh doesn't log the user out (persistence
// across refresh is an explicit requirement for the app's documents too).
export function CurrentUserProvider({ children }: Props) {
  const [users, setUsers] = useState<User[]>([]);
  const [currentUserId, setCurrentUserId] = useState<string | null>(() =>
    localStorage.getItem(CURRENT_USER_STORAGE_KEY),
  );
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetchSeededUsers()
      .then((fetched) => {
        if (!cancelled) setUsers(fetched);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const loginAs = useCallback((userId: string) => {
    localStorage.setItem(CURRENT_USER_STORAGE_KEY, userId);
    setCurrentUserId(userId);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(CURRENT_USER_STORAGE_KEY);
    setCurrentUserId(null);
  }, []);

  const currentUser = useMemo(
    () => users.find((u) => u.id === currentUserId) ?? null,
    [users, currentUserId],
  );

  const value: CurrentUserContextValue = useMemo(
    () => ({ currentUser, users, isLoading, loginAs, logout }),
    [currentUser, users, isLoading, loginAs, logout],
  );

  return (
    <CurrentUserContext.Provider value={value}>
      {children}
    </CurrentUserContext.Provider>
  );
}

import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useCurrentUser } from "../../features/auth/hooks/useCurrentUser";

interface Props {
  children: ReactNode;
}

/**
 * Wraps routes that require a "logged in" (mocked) user. Redirects to
 * /login when there is no current user selected, once the initial user
 * list fetch has settled.
 */
export function ProtectedRoute({ children }: Props) {
  const { currentUser, isLoading } = useCurrentUser();

  if (isLoading) {
    return (
      <div className="page-loading">
        <p>Loading…</p>
      </div>
    );
  }

  if (!currentUser) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

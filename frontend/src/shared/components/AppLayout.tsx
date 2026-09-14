import type { ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useCurrentUser } from "../../features/auth/hooks/useCurrentUser";

interface Props {
  children: ReactNode;
}

/**
 * Shared top-level chrome for authenticated pages: header with app name,
 * current user indicator, and a logout action.
 */
export function AppLayout({ children }: Props) {
  const { currentUser, logout } = useCurrentUser();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <Link to="/documents" className="app-title">
          Collaborative Docs
        </Link>
        {currentUser && (
          <div className="app-header-user">
            <span className="app-header-user-name">{currentUser.name}</span>
            <button type="button" className="link-button" onClick={handleLogout}>
              Log out
            </button>
          </div>
        )}
      </header>
      <main className="app-main">{children}</main>
    </div>
  );
}

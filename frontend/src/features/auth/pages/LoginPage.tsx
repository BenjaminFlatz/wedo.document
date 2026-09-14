import { Navigate } from "react-router-dom";
import { useCurrentUser } from "../hooks/useCurrentUser";

// Mocked "log in as" screen: there is no real auth provider in this
// assignment's scope (see ARCHITECTURE.md), so the user just picks one of
// the seeded identities.
export function LoginPage() {
  const { currentUser, users, isLoading, loginAs } = useCurrentUser();

  if (currentUser) {
    return <Navigate to="/documents" replace />;
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Collaborative Docs</h1>
        <p className="login-subtitle">Pick a user to log in as (demo auth)</p>

        {isLoading && <p>Loading users…</p>}

        {!isLoading && users.length === 0 && (
          <p className="error-text">
            Could not load seeded users. Is the backend running?
          </p>
        )}

        <ul className="login-user-list">
          {users.map((user) => (
            <li key={user.id}>
              <button
                type="button"
                className="login-user-button"
                onClick={() => loginAs(user.id)}
              >
                <span className="login-user-name">{user.name}</span>
                <span className="login-user-email">{user.email}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

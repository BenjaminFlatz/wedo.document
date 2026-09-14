import { useEffect, useState } from "react";
import { listShares, revokeShare, shareDocument } from "../api/sharesApi";
import { extractErrorMessage } from "../../../shared/lib/apiClient";
import type { Permission, Share } from "../../../shared/types";

interface Props {
  documentId: string;
  /** Whether the current user is allowed to manage shares (must be owner). */
  canManage: boolean;
}

/**
 * Panel listing everyone a document is shared with, plus a form (visible
 * only to the owner) to grant a seeded user view/edit access by email, and
 * a revoke action per share.
 */
export function SharePanel({ documentId, canManage }: Props) {
  const [shares, setShares] = useState<Share[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [permission, setPermission] = useState<Permission>("view");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const reload = async () => {
    try {
      const data = await listShares(documentId);
      setShares(data);
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  };

  useEffect(() => {
    reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [documentId]);

  const handleShare = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;
    setError(null);
    setIsSubmitting(true);
    try {
      await shareDocument(documentId, email.trim(), permission);
      setEmail("");
      setPermission("view");
      await reload();
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRevoke = async (userId: string) => {
    setError(null);
    try {
      await revokeShare(documentId, userId);
      await reload();
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  };

  return (
    <div className="share-panel">
      <h3>Sharing</h3>
      {error && <p className="error-text">{error}</p>}

      {shares === null && <p>Loading shares…</p>}

      {shares !== null && shares.length === 0 && (
        <p className="empty-text">Not shared with anyone yet.</p>
      )}

      {shares !== null && shares.length > 0 && (
        <ul className="share-list">
          {shares.map((share) => (
            <li key={share.user_id} className="share-list-item">
              <div>
                <span className="share-user-name">{share.user_name}</span>
                <span className="share-user-email">{share.user_email}</span>
              </div>
              <span className="share-permission">
                {share.permission === "edit" ? "Can edit" : "Can view"}
              </span>
              {canManage && (
                <button
                  type="button"
                  className="link-button"
                  onClick={() => handleRevoke(share.user_id)}
                >
                  Revoke
                </button>
              )}
            </li>
          ))}
        </ul>
      )}

      {canManage && (
        <form className="share-form" onSubmit={handleShare}>
          <input
            type="email"
            placeholder="user@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <select
            value={permission}
            onChange={(e) => setPermission(e.target.value as Permission)}
          >
            <option value="view">Can view</option>
            <option value="edit">Can edit</option>
          </select>
          <button type="submit" className="secondary-button" disabled={isSubmitting}>
            {isSubmitting ? "Sharing…" : "Share"}
          </button>
        </form>
      )}
    </div>
  );
}

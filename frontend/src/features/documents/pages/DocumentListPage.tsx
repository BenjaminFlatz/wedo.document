import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listMyDocuments } from "../api/documentsApi";
import { extractErrorMessage } from "../../../shared/lib/apiClient";
import type { DocumentSummary } from "../../../shared/types";
import { CreateDocumentButton } from "../components/CreateDocumentButton";
import { UploadDocumentButton } from "../components/UploadDocumentButton";

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

/**
 * Landing page after login: lists documents the current user owns and
 * documents shared with them, with actions to create, upload, or open.
 */
export function DocumentListPage() {
  const [documents, setDocuments] = useState<DocumentSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const reload = useCallback(async () => {
    setError(null);
    try {
      const docs = await listMyDocuments();
      setDocuments(docs);
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  const owned = documents?.filter((d) => d.relationship === "owned") ?? [];
  const shared = documents?.filter((d) => d.relationship === "shared") ?? [];

  const openDocument = (id: string) => navigate(`/documents/${id}`);

  return (
    <div className="document-list-page">
      <div className="document-list-actions">
        <CreateDocumentButton
          onCreated={(doc) => navigate(`/documents/${doc.id}`)}
        />
        <UploadDocumentButton
          onImported={(doc) => navigate(`/documents/${doc.id}`)}
        />
      </div>

      {error && <p className="error-text">{error}</p>}
      {documents === null && !error && <p>Loading documents…</p>}

      {documents !== null && (
        <>
          <section className="document-section">
            <h2>Owned by me</h2>
            {owned.length === 0 ? (
              <p className="empty-text">
                You don't own any documents yet. Create one or upload a file to
                get started.
              </p>
            ) : (
              <ul className="document-list">
                {owned.map((doc) => (
                  <li key={doc.id}>
                    <button
                      type="button"
                      className="document-list-item"
                      onClick={() => openDocument(doc.id)}
                    >
                      <span className="document-title">{doc.title}</span>
                      <span className="document-meta">
                        Updated {formatDate(doc.updated_at)}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="document-section">
            <h2>Shared with me</h2>
            {shared.length === 0 ? (
              <p className="empty-text">No documents have been shared with you.</p>
            ) : (
              <ul className="document-list">
                {shared.map((doc) => (
                  <li key={doc.id}>
                    <button
                      type="button"
                      className="document-list-item"
                      onClick={() => openDocument(doc.id)}
                    >
                      <span className="document-title">{doc.title}</span>
                      <span className="document-meta">
                        Owned by {doc.owner_name} · {doc.permission === "edit" ? "Can edit" : "Can view"}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}
    </div>
  );
}

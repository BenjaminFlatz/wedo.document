import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  deleteDocument,
  getDocument,
  renameDocument,
  updateDocumentContent,
} from "../api/documentsApi";
import { extractErrorMessage } from "../../../shared/lib/apiClient";
import type { DocumentDetail, ProseMirrorDoc } from "../../../shared/types";
import { DocumentEditor } from "../components/DocumentEditor";
import { SharePanel } from "../components/SharePanel";

type SaveStatus = "idle" | "saving" | "saved" | "error";

/**
 * Full document view: loads the document, renders the rich-text editor
 * with autosave, a rename control, a delete action (owner only), and the
 * sharing panel. Handles the not-found / forbidden cases the backend can
 * return for a document the requester doesn't own or have access to.
 */
export function DocumentEditorPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [doc, setDoc] = useState<DocumentDetail | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [saveStatus, setSaveStatus] = useState<SaveStatus>("idle");
  const [saveError, setSaveError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const latestContentRef = useRef<ProseMirrorDoc | null>(null);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setDoc(null);
    setLoadError(null);
    getDocument(id)
      .then((data) => {
        if (cancelled) return;
        setDoc(data);
        setTitle(data.title);
      })
      .catch((err) => {
        if (!cancelled) setLoadError(extractErrorMessage(err));
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  const handleContentChange = useCallback(
    async (content: ProseMirrorDoc) => {
      if (!id) return;
      latestContentRef.current = content;
      setSaveStatus("saving");
      setSaveError(null);
      try {
        const updated = await updateDocumentContent(id, content);
        // Only apply if this is still the latest edit (avoids clobbering
        // a newer in-flight save's result with a stale response).
        if (latestContentRef.current === content) {
          setDoc(updated);
          setSaveStatus("saved");
        }
      } catch (err) {
        setSaveStatus("error");
        setSaveError(extractErrorMessage(err));
      }
    },
    [id],
  );

  const handleRename = async () => {
    if (!id || !doc) return;
    const trimmed = title.trim();
    if (!trimmed || trimmed === doc.title) {
      setTitle(doc.title);
      return;
    }
    try {
      const updated = await renameDocument(id, trimmed);
      setDoc(updated);
      setTitle(updated.title);
    } catch (err) {
      setSaveError(extractErrorMessage(err));
      setTitle(doc.title);
    }
  };

  const handleDelete = async () => {
    if (!id) return;
    if (!window.confirm("Delete this document? This cannot be undone.")) return;
    setIsDeleting(true);
    try {
      await deleteDocument(id);
      navigate("/documents", { replace: true });
    } catch (err) {
      setSaveError(extractErrorMessage(err));
      setIsDeleting(false);
    }
  };

  if (loadError) {
    return (
      <div className="document-editor-page">
        <p className="error-text">{loadError}</p>
        <Link to="/documents">← Back to documents</Link>
      </div>
    );
  }

  if (!doc) {
    return (
      <div className="document-editor-page">
        <p>Loading document…</p>
      </div>
    );
  }

  return (
    <div className="document-editor-page">
      <div className="document-editor-page-header">
        <Link to="/documents" className="back-link">
          ← Back to documents
        </Link>

        <div className="document-title-row">
          <input
            className="document-title-input"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onBlur={handleRename}
            disabled={!doc.can_edit}
          />
          <span className="save-status">
            {saveStatus === "saving" && "Saving…"}
            {saveStatus === "saved" && "Saved"}
            {saveStatus === "error" && "Save failed"}
          </span>
        </div>

        {!doc.can_edit && (
          <p className="permission-note">You have view-only access to this document.</p>
        )}
        {saveError && <p className="error-text">{saveError}</p>}

        {doc.can_manage_shares && (
          <button
            type="button"
            className="danger-button"
            onClick={handleDelete}
            disabled={isDeleting}
          >
            {isDeleting ? "Deleting…" : "Delete document"}
          </button>
        )}
      </div>

      <div className="document-editor-page-body">
        <DocumentEditor
          content={doc.content}
          editable={doc.can_edit}
          onChange={handleContentChange}
        />

        <aside className="document-editor-sidebar">
          <SharePanel documentId={doc.id} canManage={doc.can_manage_shares} />
        </aside>
      </div>
    </div>
  );
}

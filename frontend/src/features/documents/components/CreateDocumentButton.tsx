import { useState } from "react";
import { createDocument } from "../api/documentsApi";
import { extractErrorMessage } from "../../../shared/lib/apiClient";
import type { DocumentDetail } from "../../../shared/types";

interface Props {
  onCreated: (doc: DocumentDetail) => void;
}

/**
 * Button that creates a new blank document titled "Untitled document"
 * (renamed later from the editor page).
 */
export function CreateDocumentButton({ onCreated }: Props) {
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleClick = async () => {
    setError(null);
    setIsCreating(true);
    try {
      const doc = await createDocument("Untitled document");
      onCreated(doc);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="create-document">
      <button
        type="button"
        className="primary-button"
        onClick={handleClick}
        disabled={isCreating}
      >
        {isCreating ? "Creating…" : "+ New document"}
      </button>
      {error && <p className="error-text">{error}</p>}
    </div>
  );
}

import { useRef, useState } from "react";
import { importDocument } from "../api/documentsApi";
import { extractErrorMessage } from "../../../shared/lib/apiClient";
import type { DocumentDetail } from "../../../shared/types";

interface Props {
  onImported: (doc: DocumentDetail) => void;
}

/**
 * Button + hidden file input that lets a user upload a .txt/.md file,
 * converting it into a brand-new editable document via the backend's
 * import endpoint.
 */
export function UploadDocumentButton({ onImported }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = ""; // allow re-selecting the same file later
    if (!file) return;

    const lowerName = file.name.toLowerCase();
    if (!lowerName.endsWith(".txt") && !lowerName.endsWith(".md")) {
      setError("Only .txt and .md files are supported.");
      return;
    }

    setError(null);
    setIsUploading(true);
    try {
      const doc = await importDocument(file);
      onImported(doc);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="upload-document">
      <button
        type="button"
        className="secondary-button"
        onClick={() => inputRef.current?.click()}
        disabled={isUploading}
      >
        {isUploading ? "Uploading…" : "Upload .txt / .md"}
      </button>
      <input
        ref={inputRef}
        type="file"
        accept=".txt,.md,text/plain,text/markdown"
        onChange={handleFileChange}
        style={{ display: "none" }}
      />
      {error && <p className="error-text">{error}</p>}
    </div>
  );
}

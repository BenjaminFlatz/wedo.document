import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Underline from "@tiptap/extension-underline";
import { useEffect, useRef } from "react";
import type { ProseMirrorDoc } from "../../../shared/types";
import { EditorToolbar } from "./EditorToolbar";
import { useDebouncedCallback } from "../hooks/useDebouncedCallback";

interface Props {
  content: ProseMirrorDoc;
  editable: boolean;
  onChange: (content: ProseMirrorDoc) => void;
  /** Debounce delay (ms) before onChange fires after the user stops typing. */
  autosaveDelayMs?: number;
}

/**
 * Rich-text document editor built on TipTap. Renders a formatting toolbar
 * and an editable surface, calling `onChange` (debounced) whenever the
 * document content changes so the parent page can autosave.
 */
export function DocumentEditor({
  content,
  editable,
  onChange,
  autosaveDelayMs = 800,
}: Props) {
  const debouncedOnChange = useDebouncedCallback(onChange, autosaveDelayMs);
  const isFirstRender = useRef(true);

  const editor = useEditor({
    extensions: [StarterKit, Underline],
    content,
    editable,
    onUpdate: ({ editor }) => {
      debouncedOnChange(editor.getJSON());
    },
  });

  // Keep editable state in sync (e.g. when permission or save-in-flight
  // status changes) without recreating the editor instance.
  useEffect(() => {
    if (editor) {
      editor.setEditable(editable);
    }
  }, [editor, editable]);

  // If the underlying document content changes from outside this editor
  // (e.g. after loading a different document), reset the editor content.
  useEffect(() => {
    if (!editor) return;
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    const current = JSON.stringify(editor.getJSON());
    const next = JSON.stringify(content);
    if (current !== next) {
      editor.commands.setContent(content);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [content]);

  return (
    <div className="document-editor">
      <EditorToolbar editor={editor} disabled={!editable} />
      <div className="document-editor-surface">
        <EditorContent editor={editor} />
      </div>
    </div>
  );
}

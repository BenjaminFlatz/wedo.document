import type { Editor } from "@tiptap/react";
// Side-effect imports so TypeScript loads each extension's module
// augmentation of `@tiptap/core`'s `Commands` interface (e.g. `toggleBold`).
// Without these, this file (which only imports the `Editor` type) doesn't
// see the chained-command methods used below.
import "@tiptap/starter-kit";
import "@tiptap/extension-underline";

interface Props {
  editor: Editor | null;
  disabled?: boolean;
}

interface ToolbarButtonProps {
  active: boolean;
  disabled?: boolean;
  onClick: () => void;
  label: string;
  children: React.ReactNode;
}

function ToolbarButton({ active, disabled, onClick, label, children }: ToolbarButtonProps) {
  return (
    <button
      type="button"
      className={`toolbar-button${active ? " is-active" : ""}`}
      onClick={onClick}
      disabled={disabled}
      aria-label={label}
      title={label}
    >
      {children}
    </button>
  );
}

/**
 * Formatting toolbar for the TipTap editor: bold, italic, underline,
 * headings, and bulleted/numbered lists.
 */
export function EditorToolbar({ editor, disabled }: Props) {
  if (!editor) return null;

  const isDisabled = disabled ?? false;

  return (
    <div className="editor-toolbar">
      <ToolbarButton
        label="Bold"
        active={editor.isActive("bold")}
        disabled={isDisabled}
        onClick={() => editor.chain().focus().toggleBold().run()}
      >
        <strong>B</strong>
      </ToolbarButton>
      <ToolbarButton
        label="Italic"
        active={editor.isActive("italic")}
        disabled={isDisabled}
        onClick={() => editor.chain().focus().toggleItalic().run()}
      >
        <em>I</em>
      </ToolbarButton>
      <ToolbarButton
        label="Underline"
        active={editor.isActive("underline")}
        disabled={isDisabled}
        onClick={() => editor.chain().focus().toggleUnderline().run()}
      >
        <span style={{ textDecoration: "underline" }}>U</span>
      </ToolbarButton>

      <span className="toolbar-divider" />

      <ToolbarButton
        label="Heading 1"
        active={editor.isActive("heading", { level: 1 })}
        disabled={isDisabled}
        onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
      >
        H1
      </ToolbarButton>
      <ToolbarButton
        label="Heading 2"
        active={editor.isActive("heading", { level: 2 })}
        disabled={isDisabled}
        onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
      >
        H2
      </ToolbarButton>

      <span className="toolbar-divider" />

      <ToolbarButton
        label="Bulleted list"
        active={editor.isActive("bulletList")}
        disabled={isDisabled}
        onClick={() => editor.chain().focus().toggleBulletList().run()}
      >
        • List
      </ToolbarButton>
      <ToolbarButton
        label="Numbered list"
        active={editor.isActive("orderedList")}
        disabled={isDisabled}
        onClick={() => editor.chain().focus().toggleOrderedList().run()}
      >
        1. List
      </ToolbarButton>
    </div>
  );
}

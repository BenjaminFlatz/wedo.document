// Global TypeScript types mirroring the backend's Pydantic schemas
// (backend/src/api/schemas.py). Keep these in sync with that file.

export interface User {
  id: string;
  name: string;
  email: string;
}

export type DocumentRelationship = "owned" | "shared";
export type Permission = "view" | "edit";

export interface DocumentSummary {
  id: string;
  title: string;
  owner_id: string;
  owner_name: string;
  created_at: string;
  updated_at: string;
  relationship: DocumentRelationship;
  permission: Permission;
}

// TipTap/ProseMirror document JSON - intentionally loose, TipTap owns the
// real shape internally via its JSONContent type.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type ProseMirrorDoc = Record<string, any>;

export interface DocumentDetail {
  id: string;
  title: string;
  content: ProseMirrorDoc;
  owner_id: string;
  owner_name: string;
  created_at: string;
  updated_at: string;
  can_edit: boolean;
  can_manage_shares: boolean;
}

export interface Share {
  user_id: string;
  user_name: string;
  user_email: string;
  permission: Permission;
}

export interface ApiError {
  detail: string;
}

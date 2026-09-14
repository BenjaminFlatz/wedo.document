import { apiClient } from "../../../shared/lib/apiClient";
import type { Permission, Share } from "../../../shared/types";

export async function listShares(documentId: string): Promise<Share[]> {
  const { data } = await apiClient.get<Share[]>(
    `/documents/${documentId}/shares`,
  );
  return data;
}

export async function shareDocument(
  documentId: string,
  email: string,
  permission: Permission,
): Promise<Share> {
  const { data } = await apiClient.post<Share>(
    `/documents/${documentId}/shares`,
    { email, permission },
  );
  return data;
}

export async function revokeShare(
  documentId: string,
  targetUserId: string,
): Promise<void> {
  await apiClient.delete(`/documents/${documentId}/shares/${targetUserId}`);
}

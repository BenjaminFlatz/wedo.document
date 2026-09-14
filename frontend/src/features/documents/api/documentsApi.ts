import { apiClient } from "../../../shared/lib/apiClient";
import type { DocumentDetail, DocumentSummary, ProseMirrorDoc } from "../../../shared/types";

export async function listMyDocuments(): Promise<DocumentSummary[]> {
  const { data } = await apiClient.get<DocumentSummary[]>("/documents");
  return data;
}

export async function getDocument(id: string): Promise<DocumentDetail> {
  const { data } = await apiClient.get<DocumentDetail>(`/documents/${id}`);
  return data;
}

export async function createDocument(title: string): Promise<DocumentDetail> {
  const { data } = await apiClient.post<DocumentDetail>("/documents", { title });
  return data;
}

export async function renameDocument(
  id: string,
  title: string,
): Promise<DocumentDetail> {
  const { data } = await apiClient.patch<DocumentDetail>(`/documents/${id}`, {
    title,
  });
  return data;
}

export async function updateDocumentContent(
  id: string,
  content: ProseMirrorDoc,
): Promise<DocumentDetail> {
  const { data } = await apiClient.put<DocumentDetail>(
    `/documents/${id}/content`,
    { content },
  );
  return data;
}

export async function deleteDocument(id: string): Promise<void> {
  await apiClient.delete(`/documents/${id}`);
}

export async function importDocument(file: File): Promise<DocumentDetail> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post<DocumentDetail>(
    "/documents/import",
    formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  );
  return data;
}

import { apiClient } from "../../../shared/lib/apiClient";
import type { User } from "../../../shared/types";

export async function fetchSeededUsers(): Promise<User[]> {
  const { data } = await apiClient.get<User[]>("/auth/users");
  return data;
}

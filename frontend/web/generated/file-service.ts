// File Service Client
import { apiClient } from "../services/apiClient";

export interface FileUpload {
  id: string;
  filename: string;
  size: number;
  type: string;
  url: string;
  uploadedAt: string;
}

export interface FileUploadResponse {
  file: FileUpload;
  success: boolean;
}

export class FileServiceClient {
  async uploadFile(file: File): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post(
      "/api/v1/files/upload",
      formData,
    ) as unknown as Promise<FileUploadResponse>;
  }

  async getFile(id: string): Promise<FileUpload> {
    return apiClient.get(
      `/api/v1/files/${id}`,
    ) as unknown as Promise<FileUpload>;
  }

  async deleteFile(id: string): Promise<void> {
    return apiClient.delete(`/api/v1/files/${id}`) as unknown as Promise<void>;
  }

  async getFiles(params?: {
    page?: number;
    limit?: number;
  }): Promise<{ files: FileUpload[]; total: number }> {
    return apiClient.get("/api/v1/files", { params }) as unknown as Promise<{
      files: FileUpload[];
      total: number;
    }>;
  }
}

export const fileService = new FileServiceClient();

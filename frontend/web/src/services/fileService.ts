/**
 * NEXUS Platform - File Service
 * Handles file operations and uploads
 */

import { apiClient } from "./apiClient";
import { ApiResponse } from "../types/ApiResponse";

export interface FileUploadResponse {
  id: string;
  filename: string;
  size: number;
  type: string;
  url: string;
}

export interface DownloadResponse {
  url: string;
}

export interface FileInfo {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadedAt: string;
  url: string;
}

class FileService {
  async uploadFile(
    file: File,
    category?: string,
  ): Promise<ApiResponse<FileUploadResponse>> {
    const formData = new FormData();
    formData.append("file", file);
    if (category) {
      formData.append("category", category);
    }

    return apiClient.uploadFile("/api/files/upload", file);
  }

  async getFiles(): Promise<ApiResponse<FileInfo[]>> {
    return apiClient.get("/api/files");
  }

  async getFile(id: string): Promise<ApiResponse<FileInfo>> {
    return apiClient.get(`/api/files/${id}`);
  }

  async deleteFile(id: string): Promise<ApiResponse<void>> {
    return apiClient.delete(`/api/files/${id}`);
  }

  async downloadFile(id: string): Promise<void> {
    const response = await apiClient.get<DownloadResponse>(
      `/api/files/${id}/download`,
    );
    if (response.success && response.data?.url) {
      window.open(response.data.url, "_blank");
    }
  }
}

export const fileService = new FileService();
export default fileService;

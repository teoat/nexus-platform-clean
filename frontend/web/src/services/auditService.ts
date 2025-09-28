import { apiClient } from './apiClient';

export interface AuditLog {
  id: string;
  timestamp: string;
  operation: string;
  entity_type: string;
  entity_id: string;
  details: any;
  performed_by: string;
  context: string;
  log_level: string;
  ip_address?: string;
  user_agent?: string;
  session_id?: string;
}

export interface AuditQuery {
  start_date?: string;
  end_date?: string;
  operation_types?: string[];
  entity_types?: string[];
  entity_ids?: string[];
  performed_by?: string[];
  contexts?: string[];
  log_levels?: string[];
  search_text?: string;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface AuditStatistics {
  total_operations: number;
  operation_distribution: Record<string, number>;
  entity_type_distribution: Record<string, number>;
  user_activity: Record<string, number>;
  context_distribution: Record<string, number>;
  log_level_distribution: Record<string, number>;
  hourly_activity: Record<string, number>;
  daily_activity: Record<string, number>;
  most_active_users: [string, number][];
  most_common_operations: [string, number][];
  most_modified_entities: [string, number][];
  query_period: {
    start_date?: string;
    end_date?: string;
  };
}

export interface AuditReport {
  id: string;
  title: string;
  description: string;
  generated_at: string;
  generated_by: string;
  total_records: number;
  format: string;
  file_path?: string;
  summary: AuditStatistics;
}

class AuditService {
  private baseUrl = '/api/v1/audit';

  // Query audit logs
  async queryAuditLogs(query: AuditQuery): Promise<{ data: AuditLog[]; pagination: any }> {
    const response = await apiClient.post(`${this.baseUrl}/query`, query);
    return response.data;
  }

  // Get audit logs with GET parameters
  async getAuditLogs(params: Record<string, any> = {}): Promise<{ data: AuditLog[]; pagination: any }> {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${this.baseUrl}/logs?${queryString}` : `${this.baseUrl}/logs`;
    const response = await apiClient.get(url);
    return response.data;
  }

  // Get audit statistics
  async getAuditStatistics(params: { start_date?: string; end_date?: string; context?: string } = {}): Promise<AuditStatistics> {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${this.baseUrl}/statistics?${queryString}` : `${this.baseUrl}/statistics`;
    const response = await apiClient.get(url);
    return response.data.data;
  }

  // Generate audit report
  async generateAuditReport(
    query: AuditQuery,
    title: string,
    description: string,
    format: 'json' | 'csv' | 'html' | 'excel' = 'json',
    generatedBy?: string
  ): Promise<AuditReport> {
    const response = await apiClient.post(`${this.baseUrl}/reports`, {
      query,
      title,
      description,
      format,
      generated_by: generatedBy,
    });
    return response.data.data;
  }

  // Log audit event manually
  async logAuditEvent(event: {
    operation: string;
    entity_type: string;
    entity_id: string;
    details?: any;
    performed_by?: string;
    context?: string;
    log_level?: string;
    ip_address?: string;
    user_agent?: string;
    session_id?: string;
  }): Promise<{ log_id: string }> {
    const response = await apiClient.post(`${this.baseUrl}/log`, event);
    return response.data.data;
  }

  // Cleanup old audit logs
  async cleanupOldLogs(retentionDays: number = 365): Promise<{ deleted_count: number }> {
    const response = await apiClient.delete(`${this.baseUrl}/cleanup?retention_days=${retentionDays}`);
    return response.data.data;
  }

  // Get audit system health
  async getAuditHealth(): Promise<{
    status: string;
    service: string;
    database_connected: boolean;
    recent_logs_count: number;
    timestamp: string;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/health`);
    return response.data;
  }

  // Utility methods for common queries
  async getRecentLogs(limit: number = 50): Promise<AuditLog[]> {
    const result = await this.getAuditLogs({
      limit,
      sort_by: 'timestamp',
      sort_order: 'desc',
    });
    return result.data;
  }

  async getUserActivity(userId: string, days: number = 30): Promise<AuditLog[]> {
    const endDate = new Date().toISOString();
    const startDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();

    const result = await this.getAuditLogs({
      performed_by: userId,
      start_date: startDate,
      end_date: endDate,
      sort_by: 'timestamp',
      sort_order: 'desc',
    });
    return result.data;
  }

  async getEntityHistory(entityType: string, entityId: string): Promise<AuditLog[]> {
    const result = await this.getAuditLogs({
      entity_type: entityType,
      entity_id: entityId,
      sort_by: 'timestamp',
      sort_order: 'desc',
    });
    return result.data;
  }

  async getSecurityEvents(days: number = 7): Promise<AuditLog[]> {
    const endDate = new Date().toISOString();
    const startDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();

    const result = await this.getAuditLogs({
      log_levels: ['warning', 'error', 'critical'],
      start_date: startDate,
      end_date: endDate,
      sort_by: 'timestamp',
      sort_order: 'desc',
    });
    return result.data;
  }
}

export const auditService = new AuditService();
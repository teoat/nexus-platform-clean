import { apiClient } from '@services/apiClient';

export interface IntegrationConfig {
  integration_id: string;
  name: string;
  integration_type: string;
  status: string;
  config: Record<string, any>;
  webhook_url?: string;
  api_endpoints: string[];
  sync_direction: string;
  sync_frequency: number;
  retry_count: number;
  timeout_seconds: number;
  created_at: string;
  updated_at: string;
  created_by: string;
}

export interface SyncJob {
  job_id: string;
  integration_id: string;
  status: string;
  started_at: string;
  completed_at?: string;
  records_processed: number;
  records_successful: number;
  records_failed: number;
  sync_direction: string;
  error_message?: string;
}

export interface WebhookEvent {
  event_id: string;
  integration_id: string;
  event_type: string;
  received_at: string;
  processed: boolean;
  processed_at?: string;
  error_message?: string;
}

export interface IntegrationHubStatus {
  hub_running: boolean;
  total_integrations: number;
  active_integrations: number;
  total_sync_jobs: number;
  completed_sync_jobs: number;
  failed_sync_jobs: number;
  total_webhook_events: number;
  processed_webhook_events: number;
  supported_integration_types: number;
}

export interface IntegrationType {
  type: string;
  name: string;
  description: string;
}

class IntegrationService {
  private baseUrl = '/api/v1/integrations';

  async getStatus(): Promise<IntegrationHubStatus> {
    const response = await apiClient.get(`${this.baseUrl}/status`);
    return response.data;
  }

  async createIntegration(integrationData: {
    name: string;
    integration_type: string;
    config?: Record<string, any>;
    credentials?: Record<string, any>;
    webhook_url?: string;
    api_endpoints?: string[];
    sync_direction?: string;
    sync_frequency?: number;
    retry_count?: number;
    timeout_seconds?: number;
  }): Promise<{ integration_id: string; message: string }> {
    const response = await apiClient.post(`${this.baseUrl}/create`, integrationData);
    return response.data;
  }

  async testIntegration(integrationId: string): Promise<{
    success: boolean;
    message: string;
    result?: any;
    error?: string;
  }> {
    const response = await apiClient.post(`${this.baseUrl}/test/${integrationId}`);
    return response.data;
  }

  async syncIntegration(
    integrationId: string,
    direction?: string
  ): Promise<{ job_id: string; integration_id: string; status: string; message: string }> {
    const response = await apiClient.post(`${this.baseUrl}/sync/${integrationId}`, {
      direction,
    });
    return response.data;
  }

  async listIntegrations(): Promise<{
    integrations: IntegrationConfig[];
    total_integrations: number;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/list`);
    return response.data;
  }

  async getIntegration(integrationId: string): Promise<IntegrationConfig> {
    const response = await apiClient.get(`${this.baseUrl}/${integrationId}`);
    return response.data;
  }

  async listSyncJobs(): Promise<{
    sync_jobs: SyncJob[];
    total_jobs: number;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/sync-jobs/list`);
    return response.data;
  }

  async getSyncJob(jobId: string): Promise<SyncJob> {
    const response = await apiClient.get(`${this.baseUrl}/sync-jobs/${jobId}`);
    return response.data;
  }

  async listWebhookEvents(): Promise<{
    webhook_events: WebhookEvent[];
    total_events: number;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/webhook-events/list`);
    return response.data;
  }

  async getWebhookEvent(eventId: string): Promise<WebhookEvent> {
    const response = await apiClient.get(`${this.baseUrl}/webhook-events/${eventId}`);
    return response.data;
  }

  async receiveWebhook(
    integrationId: string,
    webhookData: {
      event_type: string;
      payload: Record<string, any>;
    }
  ): Promise<{ event_id: string; integration_id: string; event_type: string; message: string }> {
    const response = await apiClient.post(`${this.baseUrl}/webhook/${integrationId}`, webhookData);
    return response.data;
  }

  async startHub(): Promise<{ message: string }> {
    const response = await apiClient.post(`${this.baseUrl}/start`);
    return response.data;
  }

  async stopHub(): Promise<{ message: string }> {
    const response = await apiClient.post(`${this.baseUrl}/stop`);
    return response.data;
  }

  async getIntegrationTypes(): Promise<{
    integration_types: IntegrationType[];
    total_types: number;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/types`);
    return response.data;
  }

  async healthCheck(): Promise<{
    status: string;
    hub_running: boolean;
    total_integrations: number;
    active_integrations: number;
    total_sync_jobs: number;
    completed_sync_jobs: number;
    total_webhook_events: number;
    processed_webhook_events: number;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/health`);
    return response.data;
  }

  // Integration template methods
  async createRestApiIntegration(
    name: string,
    baseUrl: string,
    apiKey?: string,
    syncEndpoint?: string
  ): Promise<string> {
    const integrationData = {
      name,
      integration_type: 'rest_api',
      config: {
        base_url: baseUrl,
        sync_endpoint: syncEndpoint || '/api/sync',
      },
      credentials: {
        api_key: apiKey,
      },
      sync_direction: 'outbound',
      sync_frequency: 300,
      retry_count: 3,
      timeout_seconds: 30,
    };

    const result = await this.createIntegration(integrationData);
    return result.integration_id;
  }

  async createWebhookIntegration(
    name: string,
    webhookUrl: string,
    eventTypes: string[] = ['webhook']
  ): Promise<string> {
    const integrationData = {
      name,
      integration_type: 'webhook',
      config: {
        event_types: eventTypes,
      },
      webhook_url: webhookUrl,
      sync_direction: 'inbound',
      sync_frequency: 60,
      retry_count: 3,
      timeout_seconds: 30,
    };

    const result = await this.createIntegration(integrationData);
    return result.integration_id;
  }

  async createDatabaseIntegration(
    name: string,
    connectionString: string,
    syncQuery?: string
  ): Promise<string> {
    const integrationData = {
      name,
      integration_type: 'database',
      config: {
        connection_string: connectionString,
        sync_query: syncQuery || 'SELECT * FROM data',
      },
      credentials: {
        connection_string: connectionString,
      },
      sync_direction: 'bidirectional',
      sync_frequency: 600,
      retry_count: 3,
      timeout_seconds: 60,
    };

    const result = await this.createIntegration(integrationData);
    return result.integration_id;
  }

  async createSlackIntegration(
    name: string,
    botToken: string,
    channelId?: string
  ): Promise<string> {
    const integrationData = {
      name,
      integration_type: 'slack',
      config: {
        channel_id: channelId,
        workspace: 'default',
      },
      credentials: {
        bot_token: botToken,
      },
      sync_direction: 'outbound',
      sync_frequency: 300,
      retry_count: 3,
      timeout_seconds: 30,
    };

    const result = await this.createIntegration(integrationData);
    return result.integration_id;
  }

  async createEmailIntegration(
    name: string,
    smtpConfig: {
      host: string;
      port: number;
      username: string;
      password: string;
    }
  ): Promise<string> {
    const integrationData = {
      name,
      integration_type: 'email',
      config: {
        provider: 'smtp',
        smtp_config: smtpConfig,
      },
      credentials: {
        smtp_host: smtpConfig.host,
        smtp_port: smtpConfig.port,
        smtp_username: smtpConfig.username,
        smtp_password: smtpConfig.password,
      },
      sync_direction: 'outbound',
      sync_frequency: 300,
      retry_count: 3,
      timeout_seconds: 30,
    };

    const result = await this.createIntegration(integrationData);
    return result.integration_id;
  }

  async createSalesforceIntegration(
    name: string,
    credentials: {
      client_id: string;
      client_secret: string;
      username: string;
      password: string;
      security_token: string;
    }
  ): Promise<string> {
    const integrationData = {
      name,
      integration_type: 'salesforce',
      config: {
        org_id: 'default',
        api_version: 'v58.0',
      },
      credentials,
      sync_direction: 'bidirectional',
      sync_frequency: 900,
      retry_count: 3,
      timeout_seconds: 60,
    };

    const result = await this.createIntegration(integrationData);
    return result.integration_id;
  }

  async createHubSpotIntegration(
    name: string,
    apiKey: string,
    portalId?: string
  ): Promise<string> {
    const integrationData = {
      name,
      integration_type: 'hubspot',
      config: {
        portal_id: portalId,
        api_version: 'v3',
      },
      credentials: {
        api_key: apiKey,
      },
      sync_direction: 'bidirectional',
      sync_frequency: 600,
      retry_count: 3,
      timeout_seconds: 60,
    };

    const result = await this.createIntegration(integrationData);
    return result.integration_id;
  }

  // Utility methods
  generateIntegrationId(): string {
    return `integration_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  validateIntegration(integration: Partial<IntegrationConfig>): string[] {
    const errors: string[] = [];

    if (!integration.name || integration.name.trim() === '') {
      errors.push('Integration name is required');
    }

    if (!integration.integration_type || integration.integration_type.trim() === '') {
      errors.push('Integration type is required');
    }

    if (integration.sync_frequency && integration.sync_frequency < 60) {
      errors.push('Sync frequency must be at least 60 seconds');
    }

    if (integration.retry_count && (integration.retry_count < 0 || integration.retry_count > 10)) {
      errors.push('Retry count must be between 0 and 10');
    }

    if (integration.timeout_seconds && (integration.timeout_seconds < 10 || integration.timeout_seconds > 300)) {
      errors.push('Timeout must be between 10 and 300 seconds');
    }

    return errors;
  }

  getIntegrationTypeDescription(integrationType: string): string {
    const descriptions: Record<string, string> = {
      rest_api: 'REST API integration for HTTP-based services',
      graphql: 'GraphQL API integration for flexible data queries',
      webhook: 'Webhook integration for real-time event notifications',
      database: 'Database integration for data synchronization',
      message_queue: 'Message queue integration for asynchronous processing',
      file_system: 'File system integration for file-based data exchange',
      email: 'Email integration for notification and communication',
      sms: 'SMS integration for text message notifications',
      slack: 'Slack integration for team communication and notifications',
      microsoft_teams: 'Microsoft Teams integration for collaboration',
      salesforce: 'Salesforce CRM integration for customer data management',
      hubspot: 'HubSpot integration for marketing and sales automation',
      zapier: 'Zapier integration for workflow automation',
      ifttt: 'IFTTT integration for IoT and automation triggers',
    };

    return descriptions[integrationType] || 'Unknown integration type';
  }

  getIntegrationTypeIcon(integrationType: string): string {
    const icons: Record<string, string> = {
      rest_api: '🌐',
      graphql: '🔍',
      webhook: '🔗',
      database: '🗄️',
      message_queue: '📨',
      file_system: '📁',
      email: '📧',
      sms: '📱',
      slack: '💬',
      microsoft_teams: '👥',
      salesforce: '☁️',
      hubspot: '🎯',
      zapier: '⚡',
      ifttt: '🔧',
    };

    return icons[integrationType] || '❓';
  }

  getSyncDirectionDescription(direction: string): string {
    const descriptions: Record<string, string> = {
      inbound: 'Data flows from external system to NEXUS',
      outbound: 'Data flows from NEXUS to external system',
      bidirectional: 'Data flows in both directions',
    };

    return descriptions[direction] || 'Unknown sync direction';
  }

  formatSyncFrequency(frequency: number): string {
    if (frequency < 60) {
      return `${frequency} seconds`;
    } else if (frequency < 3600) {
      return `${Math.floor(frequency / 60)} minutes`;
    } else if (frequency < 86400) {
      return `${Math.floor(frequency / 3600)} hours`;
    } else {
      return `${Math.floor(frequency / 86400)} days`;
    }
  }

  calculateSyncStats(syncJobs: SyncJob[]): {
    totalJobs: number;
    completedJobs: number;
    failedJobs: number;
    totalRecords: number;
    successRate: number;
  } {
    const totalJobs = syncJobs.length;
    const completedJobs = syncJobs.filter(job => job.status === 'completed').length;
    const failedJobs = syncJobs.filter(job => job.status === 'failed').length;
    const totalRecords = syncJobs.reduce((sum, job) => sum + job.records_processed, 0);
    const successRate = totalJobs > 0 ? (completedJobs / totalJobs) * 100 : 0;

    return {
      totalJobs,
      completedJobs,
      failedJobs,
      totalRecords,
      successRate,
    };
  }

  calculateWebhookStats(webhookEvents: WebhookEvent[]): {
    totalEvents: number;
    processedEvents: number;
    failedEvents: number;
    processingRate: number;
  } {
    const totalEvents = webhookEvents.length;
    const processedEvents = webhookEvents.filter(event => event.processed).length;
    const failedEvents = webhookEvents.filter(event => event.error_message).length;
    const processingRate = totalEvents > 0 ? (processedEvents / totalEvents) * 100 : 0;

    return {
      totalEvents,
      processedEvents,
      failedEvents,
      processingRate,
    };
  }
}

export const integrationService = new IntegrationService();
export default integrationService;
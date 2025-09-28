import { apiClient } from '@services/apiClient';

export interface AutomationRule {
  rule_id: string;
  name: string;
  description: string;
  automation_type: 'scheduled' | 'event_driven' | 'conditional' | 'ai_driven' | 'self_optimizing';
  trigger_type: 'time' | 'event' | 'condition' | 'ai_prediction' | 'user_action';
  enabled: boolean;
  priority: number;
  execution_count: number;
  success_count: number;
  failure_count: number;
  created_at: string;
  last_executed?: string;
}

export interface AutomationExecution {
  execution_id: string;
  rule_id: string;
  status: 'active' | 'paused' | 'completed' | 'failed' | 'disabled';
  started_at: string;
  completed_at?: string;
  execution_time?: number;
  result?: any;
  error_message?: string;
}

export interface AutomationMetrics {
  total_rules: number;
  active_rules: number;
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  average_execution_time: number;
  automation_efficiency: number;
  last_updated: string;
}

export interface AutomationTemplate {
  id: string;
  name: string;
  description: string;
  automation_type: string;
  trigger_type: string;
  trigger_config: Record<string, any>;
  actions: Array<{
    type: string;
    config: Record<string, any>;
  }>;
}

class AutomationService {
  private baseUrl = '/api/v1/automation';

  // Rule Management
  async createRule(ruleData: {
    name: string;
    description: string;
    automation_type: string;
    trigger_type: string;
    trigger_config: Record<string, any>;
    actions: Array<{
      type: string;
      config: Record<string, any>;
    }>;
    conditions?: Array<{
      type: string;
      config: Record<string, any>;
    }>;
    priority?: number;
    enabled?: boolean;
  }): Promise<{ rule_id: string; status: string }> {
    const response = await apiClient.post(`${this.baseUrl}/rules`, ruleData);
    return response;
  }

  async getRules(): Promise<{ rules: AutomationRule[] }> {
    const response = await apiClient.get(`${this.baseUrl}/rules`);
    return response;
  }

  async getRule(ruleId: string): Promise<AutomationRule> {
    const response = await apiClient.get(`${this.baseUrl}/rules/${ruleId}`);
    return response;
  }

  async updateRule(ruleId: string, updates: Partial<AutomationRule>): Promise<{ status: string }> {
    const response = await apiClient.put(`${this.baseUrl}/rules/${ruleId}`, updates);
    return response;
  }

  async deleteRule(ruleId: string): Promise<{ status: string }> {
    const response = await apiClient.delete(`${this.baseUrl}/rules/${ruleId}`);
    return response;
  }

  // Rule Execution
  async executeRule(ruleId: string): Promise<{ status: string; result: string }> {
    const response = await apiClient.post(`${this.baseUrl}/rules/${ruleId}/execute`);
    return response;
  }

  // Execution History
  async getExecutions(ruleId?: string): Promise<{ executions: AutomationExecution[] }> {
    const url = ruleId 
      ? `${this.baseUrl}/executions?rule_id=${ruleId}`
      : `${this.baseUrl}/executions`;
    const response = await apiClient.get(url);
    return response;
  }

  // Metrics and Status
  async getMetrics(): Promise<AutomationMetrics> {
    const response = await apiClient.get(`${this.baseUrl}/metrics`);
    return response;
  }

  async getStatus(): Promise<{
    engine_running: boolean;
    total_rules: number;
    active_rules: number;
    total_executions: number;
    metrics: AutomationMetrics;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/status`);
    return response;
  }

  // Templates
  async getTemplates(): Promise<{ templates: AutomationTemplate[] }> {
    const response = await apiClient.get(`${this.baseUrl}/templates`);
    return response;
  }

  async createRuleFromTemplate(
    templateId: string, 
    customizations?: Record<string, any>
  ): Promise<{ rule_id: string; status: string }> {
    const response = await apiClient.post(
      `${this.baseUrl}/templates/${templateId}/create`,
      customizations || {}
    );
    return response;
  }

  // Capabilities
  async getCapabilities(): Promise<{
    automation_types: Record<string, string>;
    trigger_types: Record<string, string>;
    action_types: Record<string, string>;
    condition_types: Record<string, string>;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/capabilities`);
    return response;
  }

  // Utility Methods
  async healthCheck(): Promise<boolean> {
    try {
      const status = await this.getStatus();
      return status.engine_running;
    } catch (error) {
      return false;
    }
  }

  // Get Rule Statistics
  getRuleStatistics(rules: AutomationRule[]): {
    total: number;
    enabled: number;
    disabled: number;
    byType: Record<string, number>;
    byPriority: Record<number, number>;
  } {
    const stats = {
      total: rules.length,
      enabled: rules.filter(r => r.enabled).length,
      disabled: rules.filter(r => !r.enabled).length,
      byType: {} as Record<string, number>,
      byPriority: {} as Record<number, number>
    };

    rules.forEach(rule => {
      stats.byType[rule.automation_type] = (stats.byType[rule.automation_type] || 0) + 1;
      stats.byPriority[rule.priority] = (stats.byPriority[rule.priority] || 0) + 1;
    });

    return stats;
  }

  // Get Execution Statistics
  getExecutionStatistics(executions: AutomationExecution[]): {
    total: number;
    completed: number;
    failed: number;
    active: number;
    averageExecutionTime: number;
    successRate: number;
  } {
    const stats = {
      total: executions.length,
      completed: executions.filter(e => e.status === 'completed').length,
      failed: executions.filter(e => e.status === 'failed').length,
      active: executions.filter(e => e.status === 'active').length,
      averageExecutionTime: 0,
      successRate: 0
    };

    const completedExecutions = executions.filter(e => e.status === 'completed' && e.execution_time);
    if (completedExecutions.length > 0) {
      stats.averageExecutionTime = completedExecutions.reduce((sum, e) => sum + (e.execution_time || 0), 0) / completedExecutions.length;
    }

    if (stats.total > 0) {
      stats.successRate = stats.completed / stats.total;
    }

    return stats;
  }

  // Format Rule for Display
  formatRuleForDisplay(rule: AutomationRule): {
    id: string;
    name: string;
    type: string;
    status: string;
    priority: string;
    lastRun: string;
    successRate: string;
  } {
    const successRate = rule.execution_count > 0 
      ? ((rule.success_count / rule.execution_count) * 100).toFixed(1)
      : '0.0';

    return {
      id: rule.rule_id,
      name: rule.name,
      type: rule.automation_type.replace('_', ' ').toUpperCase(),
      status: rule.enabled ? 'Active' : 'Disabled',
      priority: `Priority ${rule.priority}`,
      lastRun: rule.last_executed 
        ? new Date(rule.last_executed).toLocaleString()
        : 'Never',
      successRate: `${successRate}%`
    };
  }

  // Validate Rule Configuration
  validateRuleConfiguration(ruleData: any): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!ruleData.name || ruleData.name.trim().length === 0) {
      errors.push('Rule name is required');
    }

    if (!ruleData.automation_type) {
      errors.push('Automation type is required');
    }

    if (!ruleData.trigger_type) {
      errors.push('Trigger type is required');
    }

    if (!ruleData.actions || ruleData.actions.length === 0) {
      errors.push('At least one action is required');
    }

    if (ruleData.priority && (ruleData.priority < 1 || ruleData.priority > 4)) {
      errors.push('Priority must be between 1 and 4');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Get Recommended Actions
  getRecommendedActions(automationType: string, triggerType: string): string[] {
    const recommendations: Record<string, Record<string, string[]>> = {
      scheduled: {
        time: ['backup_data', 'cleanup_resources', 'generate_report', 'optimize_system']
      },
      event_driven: {
        event: ['send_notification', 'update_data', 'execute_workflow']
      },
      conditional: {
        condition: ['optimize_system', 'scale_resources', 'send_notification']
      },
      ai_driven: {
        ai_prediction: ['optimize_system', 'scale_resources', 'generate_report']
      },
      self_optimizing: {
        condition: ['optimize_system', 'cleanup_resources', 'scale_resources']
      }
    };

    return recommendations[automationType]?.[triggerType] || [];
  }

  // Get Trigger Configuration Examples
  getTriggerConfigurationExamples(triggerType: string): Record<string, any> {
    const examples: Record<string, Record<string, any>> = {
      time: {
        interval: { interval: 3600 }, // Every hour
        schedule: { schedule: { hour: 2, minute: 0 } }, // Daily at 2 AM
        cron: { cron: "0 2 * * *" } // Daily at 2 AM (cron format)
      },
      event: {
        data_change: { event_type: "data_change", table: "users" },
        user_action: { event_type: "user_action", action: "login" },
        system_event: { event_type: "system_event", event: "high_cpu" }
      },
      condition: {
        performance: { type: "performance_condition", config: { cpu_usage: { greater_than: 80 } } },
        resource: { type: "resource_condition", config: { disk_usage: { greater_than: 90 } } },
        data: { type: "data_condition", config: { record_count: { greater_than: 1000 } } }
      }
    };

    return examples[triggerType] || {};
  }
}

export const automationService = new AutomationService();

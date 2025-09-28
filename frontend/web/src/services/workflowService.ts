import { apiClient } from '@services/apiClient';

export interface TaskDefinition {
  task_id: string;
  name: string;
  task_type: string;
  config: Record<string, any>;
  inputs: string[];
  outputs: string[];
  conditions: string[];
  retry_count: number;
  timeout_seconds: number;
  dependencies: string[];
}

export interface WorkflowDefinition {
  workflow_id: string;
  name: string;
  description: string;
  version: string;
  status: string;
  tasks: TaskDefinition[];
  variables: Record<string, any>;
  triggers: any[];
  created_at: string;
  updated_at: string;
  created_by: string;
}

export interface WorkflowExecution {
  execution_id: string;
  workflow_id: string;
  status: string;
  started_at: string;
  completed_at?: string;
  task_executions: TaskExecution[];
  variables: Record<string, any>;
  result?: any;
  error_message?: string;
  triggered_by: string;
}

export interface TaskExecution {
  execution_id: string;
  task_id: string;
  status: string;
  started_at?: string;
  completed_at?: string;
  result?: any;
  error_message?: string;
  retry_count: number;
}

export interface WorkflowEngineStatus {
  engine_running: boolean;
  total_workflows: number;
  active_executions: number;
  completed_executions: number;
  failed_executions: number;
  registered_task_types: number;
}

export interface TaskType {
  type: string;
  name: string;
  description: string;
}

class WorkflowService {
  private baseUrl = '/api/v1/workflows';

  async getStatus(): Promise<WorkflowEngineStatus> {
    const response = await apiClient.get(`${this.baseUrl}/status`);
    return response.data;
  }

  async createWorkflow(workflowData: {
    name: string;
    description: string;
    tasks: TaskDefinition[];
    variables?: Record<string, any>;
    triggers?: any[];
  }): Promise<{ workflow_id: string; message: string }> {
    const response = await apiClient.post(`${this.baseUrl}/create`, workflowData);
    return response.data;
  }

  async executeWorkflow(
    workflowId: string,
    variables?: Record<string, any>
  ): Promise<{ execution_id: string; workflow_id: string; status: string; message: string }> {
    const response = await apiClient.post(`${this.baseUrl}/execute/${workflowId}`, {
      variables: variables || {},
    });
    return response.data;
  }

  async listWorkflows(): Promise<{
    workflows: WorkflowDefinition[];
    total_workflows: number;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/list`);
    return response.data;
  }

  async getWorkflow(workflowId: string): Promise<WorkflowDefinition> {
    const response = await apiClient.get(`${this.baseUrl}/${workflowId}`);
    return response.data;
  }

  async listExecutions(): Promise<{
    executions: WorkflowExecution[];
    total_executions: number;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/executions/list`);
    return response.data;
  }

  async getExecution(executionId: string): Promise<WorkflowExecution> {
    const response = await apiClient.get(`${this.baseUrl}/executions/${executionId}`);
    return response.data;
  }

  async startEngine(): Promise<{ message: string }> {
    const response = await apiClient.post(`${this.baseUrl}/start`);
    return response.data;
  }

  async stopEngine(): Promise<{ message: string }> {
    const response = await apiClient.post(`${this.baseUrl}/stop`);
    return response.data;
  }

  async getTaskTypes(): Promise<{
    task_types: TaskType[];
    total_types: number;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/task-types`);
    return response.data;
  }

  async healthCheck(): Promise<{
    status: string;
    engine_running: boolean;
    total_workflows: number;
    active_executions: number;
    completed_executions: number;
    registered_task_types: number;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/health`);
    return response.data;
  }

  // Workflow template methods
  async createDataProcessingWorkflow(name: string, description: string): Promise<string> {
    const workflowData = {
      name,
      description,
      tasks: [
        {
          task_id: 'data_input',
          name: 'Data Input',
          task_type: 'api_call',
          config: {
            endpoint: '/api/v1/data/input',
            method: 'GET',
          },
          inputs: [],
          outputs: ['raw_data'],
          retry_count: 3,
          timeout_seconds: 300,
          dependencies: [],
        },
        {
          task_id: 'data_transform',
          name: 'Data Transform',
          task_type: 'data_transform',
          config: {
            transform_type: 'map',
            input_data: '${raw_data}',
          },
          inputs: ['raw_data'],
          outputs: ['transformed_data'],
          retry_count: 2,
          timeout_seconds: 180,
          dependencies: ['data_input'],
        },
        {
          task_id: 'data_validation',
          name: 'Data Validation',
          task_type: 'condition',
          config: {
            condition: 'len(transformed_data) > 0',
          },
          inputs: ['transformed_data'],
          outputs: ['validated_data'],
          retry_count: 1,
          timeout_seconds: 60,
          dependencies: ['data_transform'],
        },
        {
          task_id: 'data_output',
          name: 'Data Output',
          task_type: 'api_call',
          config: {
            endpoint: '/api/v1/data/output',
            method: 'POST',
            data: '${validated_data}',
          },
          inputs: ['validated_data'],
          outputs: [],
          retry_count: 3,
          timeout_seconds: 300,
          dependencies: ['data_validation'],
        },
      ],
      variables: {},
      triggers: [],
    };

    const result = await this.createWorkflow(workflowData);
    return result.workflow_id;
  }

  async createNotificationWorkflow(name: string, description: string, recipients: string[]): Promise<string> {
    const workflowData = {
      name,
      description,
      tasks: [
        {
          task_id: 'check_conditions',
          name: 'Check Conditions',
          task_type: 'condition',
          config: {
            condition: 'variables.alert_level in ["high", "critical"]',
          },
          inputs: [],
          outputs: ['should_notify'],
          retry_count: 1,
          timeout_seconds: 30,
          dependencies: [],
        },
        {
          task_id: 'send_notification',
          name: 'Send Notification',
          task_type: 'notification',
          config: {
            type: 'email',
            message: 'Alert: ${variables.alert_message}',
            recipients,
          },
          inputs: ['should_notify'],
          outputs: [],
          retry_count: 3,
          timeout_seconds: 120,
          dependencies: ['check_conditions'],
        },
      ],
      variables: {
        alert_level: 'medium',
        alert_message: 'System alert',
      },
      triggers: [],
    };

    const result = await this.createWorkflow(workflowData);
    return result.workflow_id;
  }

  async createBatchProcessingWorkflow(name: string, description: string, batchSize: number = 100): Promise<string> {
    const workflowData = {
      name,
      description,
      tasks: [
        {
          task_id: 'get_batch_data',
          name: 'Get Batch Data',
          task_type: 'api_call',
          config: {
            endpoint: '/api/v1/batch/data',
            method: 'GET',
            params: { limit: batchSize },
          },
          inputs: [],
          outputs: ['batch_data'],
          retry_count: 3,
          timeout_seconds: 300,
          dependencies: [],
        },
        {
          task_id: 'process_batch',
          name: 'Process Batch',
          task_type: 'loop',
          config: {
            count: batchSize,
            items: '${batch_data}',
          },
          inputs: ['batch_data'],
          outputs: ['processed_items'],
          retry_count: 2,
          timeout_seconds: 600,
          dependencies: ['get_batch_data'],
        },
        {
          task_id: 'save_results',
          name: 'Save Results',
          task_type: 'api_call',
          config: {
            endpoint: '/api/v1/batch/results',
            method: 'POST',
            data: '${processed_items}',
          },
          inputs: ['processed_items'],
          outputs: [],
          retry_count: 3,
          timeout_seconds: 300,
          dependencies: ['process_batch'],
        },
      ],
      variables: {},
      triggers: [],
    };

    const result = await this.createWorkflow(workflowData);
    return result.workflow_id;
  }

  // Utility methods
  generateTaskId(): string {
    return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  validateWorkflow(workflow: Partial<WorkflowDefinition>): string[] {
    const errors: string[] = [];

    if (!workflow.name || workflow.name.trim() === '') {
      errors.push('Workflow name is required');
    }

    if (!workflow.tasks || workflow.tasks.length === 0) {
      errors.push('At least one task is required');
    }

    if (workflow.tasks) {
      workflow.tasks.forEach((task, index) => {
        if (!task.task_id || task.task_id.trim() === '') {
          errors.push(`Task ${index + 1}: Task ID is required`);
        }
        if (!task.name || task.name.trim() === '') {
          errors.push(`Task ${index + 1}: Task name is required`);
        }
        if (!task.task_type || task.task_type.trim() === '') {
          errors.push(`Task ${index + 1}: Task type is required`);
        }
      });
    }

    return errors;
  }

  getTaskTypeDescription(taskType: string): string {
    const descriptions: Record<string, string> = {
      action: 'Execute a custom action or operation',
      condition: 'Evaluate a condition and branch workflow execution',
      loop: 'Execute tasks in a loop with specified iterations',
      parallel: 'Execute multiple tasks in parallel',
      sequence: 'Execute tasks in a specific sequence',
      timer: 'Add a delay or schedule task execution',
      webhook: 'Make HTTP requests to external webhooks',
      api_call: 'Make API calls to internal or external services',
      data_transform: 'Transform or process data',
      notification: 'Send notifications via email, SMS, or other channels',
    };

    return descriptions[taskType] || 'Unknown task type';
  }

  getTaskTypeIcon(taskType: string): string {
    const icons: Record<string, string> = {
      action: '⚡',
      condition: '🔀',
      loop: '🔄',
      parallel: '⏸️',
      sequence: '▶️',
      timer: '⏰',
      webhook: '🔗',
      api_call: '🌐',
      data_transform: '🔄',
      notification: '📢',
    };

    return icons[taskType] || '❓';
  }
}

export const workflowService = new WorkflowService();
export default workflowService;
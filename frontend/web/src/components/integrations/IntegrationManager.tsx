import React, { useState, useEffect } from "react";
import Button from "../ui/Button";
import Modal from "../ui/Modal";
import { Input } from "../ui/Input";
import { Select } from "../ui/Select";
import { Textarea } from "../ui/Textarea";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import DataTable from "../ui/DataTable";

import "./IntegrationManager.css";

interface Connector {
  connector_id: string;
  name: string;
  description: string;
  integration_type: string;
  base_url?: string;
  config: Record<string, any>;
  authentication: Record<string, any>;
  rate_limits: Record<string, any>;
  retry_policy: Record<string, any>;
  transformation_rules: any[];
  status: string;
  last_connected?: string;
  error_count: number;
  created_at: string;
  updated_at: string;
}

interface IntegrationManagerProps {
  onConnectorSelect?: (connector: Connector) => void;
}

const IntegrationManager: React.FC<IntegrationManagerProps> = ({
  onConnectorSelect,
}) => {
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [templates, setTemplates] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<string>("");
  const [testingConnector, setTestingConnector] = useState<string | null>(null);

  // Form states
  const [connectorForm, setConnectorForm] = useState({
    name: "",
    description: "",
    integration_type: "rest_api",
    base_url: "",
    config: {},
    authentication: {},
  });

  const [templateForm, setTemplateForm] = useState({
    name: "",
    description: "",
    config: {},
  });

  useEffect(() => {
    loadConnectors();
    loadTemplates();
  }, []);

  const loadConnectors = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/v1/integrations/connectors");
      if (response.ok) {
        const data = await response.json();
        setConnectors(data);
      }
    } catch (error) {
      console.error("Failed to load connectors:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await fetch("/api/v1/integrations/templates");
      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
      }
    } catch (error) {
      console.error("Failed to load templates:", error);
    }
  };

  const createConnector = async () => {
    try {
      const response = await fetch("/api/v1/integrations/connectors", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(connectorForm),
      });

      if (response.ok) {
        await loadConnectors();
        setShowCreateModal(false);
        setConnectorForm({
          name: "",
          description: "",
          integration_type: "rest_api",
          base_url: "",
          config: {},
          authentication: {},
        });
      }
    } catch (error) {
      console.error("Failed to create connector:", error);
    }
  };

  const createFromTemplate = async () => {
    try {
      const response = await fetch(
        "/api/v1/integrations/connectors/from-template",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            template_name: selectedTemplate,
            ...templateForm,
          }),
        },
      );

      if (response.ok) {
        await loadConnectors();
        setShowTemplateModal(false);
        setSelectedTemplate("");
        setTemplateForm({
          name: "",
          description: "",
          config: {},
        });
      }
    } catch (error) {
      console.error("Failed to create connector from template:", error);
    }
  };

  const testConnection = async (connectorId: string) => {
    try {
      setTestingConnector(connectorId);
      const response = await fetch(
        `/api/v1/integrations/connectors/${connectorId}/test`,
        {
          method: "POST",
        },
      );

      if (response.ok) {
        const result = await response.json();
        // Update connector status
        await loadConnectors();
        alert(result.message);
      }
    } catch (error) {
      console.error("Failed to test connection:", error);
    } finally {
      setTestingConnector(null);
    }
  };

  const deleteConnector = async (connectorId: string) => {
    if (!confirm("Are you sure you want to delete this connector?")) return;

    try {
      const response = await fetch(
        `/api/v1/integrations/connectors/${connectorId}`,
        {
          method: "DELETE",
        },
      );

      if (response.ok) {
        await loadConnectors();
      }
    } catch (error) {
      console.error("Failed to delete connector:", error);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      connected: { variant: "success", label: "Connected" },
      disconnected: { variant: "secondary", label: "Disconnected" },
      connecting: { variant: "warning", label: "Connecting" },
      error: { variant: "danger", label: "Error" },
      maintenance: { variant: "warning", label: "Maintenance" },
    };

    const config =
      statusConfig[status as keyof typeof statusConfig] ||
      statusConfig.disconnected;
    return <Badge variant={config.variant as any}>{config.label}</Badge>;
  };

  const integrationTypeOptions = [
    { value: "rest_api", label: "REST API" },
    { value: "graphql", label: "GraphQL" },
    { value: "soap", label: "SOAP" },
    { value: "database", label: "Database" },
    { value: "message_queue", label: "Message Queue" },
    { value: "file_system", label: "File System" },
    { value: "cloud_storage", label: "Cloud Storage" },
    { value: "email", label: "Email" },
    { value: "sms", label: "SMS" },
    { value: "webhook", label: "Webhook" },
    { value: "custom", label: "Custom" },
  ];

  return (
    <div className="integration-manager">
      <div className="integration-header">
        <h2>Integration Management</h2>
        <div className="integration-actions">
          <Button
            onClick={() => setShowTemplateModal(true)}
            variant="secondary"
          >
            Create from Template
          </Button>
          <Button onClick={() => setShowCreateModal(true)} variant="primary">
            Create Connector
          </Button>
        </div>
      </div>

      <div className="connectors-grid">
        {connectors.map((connector) => (
          <Card key={connector.connector_id} className="connector-card">
            <div className="connector-header">
              <h3>{connector.name}</h3>
              {getStatusBadge(connector.status)}
            </div>
            <p className="connector-description">{connector.description}</p>
            <div className="connector-meta">
              <span>Type: {connector.integration_type}</span>
              {connector.base_url && <span>URL: {connector.base_url}</span>}
              {connector.last_connected && (
                <span>
                  Last Connected:{" "}
                  {new Date(connector.last_connected).toLocaleString()}
                </span>
              )}
              {connector.error_count > 0 && (
                <span className="error-count">
                  Errors: {connector.error_count}
                </span>
              )}
            </div>
            <div className="connector-actions">
              <Button
                size="small"
                onClick={() => testConnection(connector.connector_id)}
                disabled={testingConnector === connector.connector_id}
                variant="secondary"
              >
                {testingConnector === connector.connector_id
                  ? "Testing..."
                  : "Test"}
              </Button>
              {onConnectorSelect && (
                <Button
                  size="small"
                  onClick={() => onConnectorSelect(connector)}
                  variant="primary"
                >
                  Select
                </Button>
              )}
              <Button
                size="small"
                onClick={() => deleteConnector(connector.connector_id)}
                variant="danger"
              >
                Delete
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Create Connector Modal */}
      <Modal
        open={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        maxWidth="lg"
        fullWidth
      >
        <div className="connector-form">
           <Input
             label="Name"
             value={connectorForm.name}
             onChange={(value) =>
               setConnectorForm({ ...connectorForm, name: value as string })
             }
             placeholder="Connector name"
           />
           <Textarea
             label="Description"
             value={connectorForm.description}
             onChange={(value) =>
               setConnectorForm({
                 ...connectorForm,
                 description: value as string,
               })
             }
             placeholder="Connector description"
           />
           <Select
             label="Integration Type"
             value={connectorForm.integration_type}
             onChange={(value) =>
               setConnectorForm({
                 ...connectorForm,
                 integration_type: value as string,
               })
             }
             options={integrationTypeOptions}
           />
           <Input
             label="Base URL"
             value={connectorForm.base_url}
             onChange={(value) =>
               setConnectorForm({ ...connectorForm, base_url: value as string })
             }
             placeholder="https://api.example.com"
           />
          <div className="modal-actions">
            <Button
              onClick={() => setShowCreateModal(false)}
              variant="secondary"
            >
              Cancel
            </Button>
            <Button onClick={createConnector} variant="primary">
              Create Connector
            </Button>
          </div>
        </div>
      </Modal>

      {/* Create from Template Modal */}
      <Modal
        open={showTemplateModal}
        onClose={() => setShowTemplateModal(false)}
        maxWidth="lg"
        fullWidth
      >
        <div className="template-form">
           <Select
             label="Template"
             value={selectedTemplate}
             onChange={(value) => setSelectedTemplate(value as string)}
             options={Object.keys(templates).map((key) => ({
               value: key,
               label: templates[key].name,
             }))}
           />
          {selectedTemplate && (
            <>
               <Input
                 label="Name"
                 value={templateForm.name}
                 onChange={(value) =>
                   setTemplateForm({ ...templateForm, name: value as string })
                 }
                 placeholder="Connector name"
               />
               <Textarea
                 label="Description"
                 value={templateForm.description}
                 onChange={(value) =>
                   setTemplateForm({
                     ...templateForm,
                     description: value as string,
                   })
                 }
                 placeholder="Connector description"
               />
            </>
          )}
          <div className="modal-actions">
            <Button
              onClick={() => setShowTemplateModal(false)}
              variant="secondary"
            >
              Cancel
            </Button>
            <Button
              onClick={createFromTemplate}
              variant="primary"
              disabled={!selectedTemplate}
            >
              Create from Template
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default IntegrationManager;

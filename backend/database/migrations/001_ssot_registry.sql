-- NEXUS SSOT Registry Migration
-- Version: 001
-- Description: Create SSOT registry tables and initial data

-- Create SSOT registry tables
CREATE TABLE IF NOT EXISTS ssot_api_contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_name VARCHAR(255) NOT NULL UNIQUE,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    base_url VARCHAR(500) NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'deprecated', 'archived')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS ssot_api_aliases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID NOT NULL REFERENCES ssot_api_contracts(id) ON DELETE CASCADE,
    alias_name VARCHAR(255) NOT NULL,
    context VARCHAR(100) NOT NULL,
    alias_type VARCHAR(20) DEFAULT 'permanent' CHECK (alias_type IN ('permanent', 'temporary')),
    expires_at TIMESTAMP WITH TIME ZONE,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255) NOT NULL,
    UNIQUE(alias_name, context)
);

CREATE TABLE IF NOT EXISTS ssot_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    context VARCHAR(100),
    user_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ssot_governance_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(255) NOT NULL UNIQUE,
    rule_type VARCHAR(50) NOT NULL,
    rule_config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255) NOT NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_ssot_api_contracts_canonical_name ON ssot_api_contracts(canonical_name);
CREATE INDEX IF NOT EXISTS idx_ssot_api_contracts_status ON ssot_api_contracts(status);
CREATE INDEX IF NOT EXISTS idx_ssot_api_aliases_contract_id ON ssot_api_aliases(contract_id);
CREATE INDEX IF NOT EXISTS idx_ssot_api_aliases_alias_name ON ssot_api_aliases(alias_name);
CREATE INDEX IF NOT EXISTS idx_ssot_api_aliases_context ON ssot_api_aliases(context);
CREATE INDEX IF NOT EXISTS idx_ssot_api_aliases_active ON ssot_api_aliases(is_active);
CREATE INDEX IF NOT EXISTS idx_ssot_audit_logs_entity ON ssot_audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_ssot_audit_logs_created_at ON ssot_audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_ssot_governance_rules_active ON ssot_governance_rules(is_active);

-- Insert initial governance rules
INSERT INTO ssot_governance_rules (rule_name, rule_type, rule_config, created_by, updated_by) VALUES
('alias_uniqueness', 'validation', '{"enforce_unique_aliases": true, "scope": "context"}', 'system', 'system'),
('canonical_immutability', 'validation', '{"prevent_canonical_changes": true, "allow_deprecation": true}', 'system', 'system'),
('audit_retention', 'retention', '{"retention_years": 7, "archive_after_years": 1}', 'system', 'system'),
('approval_workflow', 'workflow', '{"require_pr_review": true, "min_approvers": 2}', 'system', 'system'),
('temporary_alias_expiry', 'validation', '{"max_duration_days": 365, "auto_expire": true}', 'system', 'system');

-- Insert initial API contracts
INSERT INTO ssot_api_contracts (canonical_name, version, description, base_url, created_by, updated_by) VALUES
('user-management-api', 'v1.0.0', 'User management and authentication API', 'http://localhost:8000/api/users', 'system', 'system'),
('account-management-api', 'v1.0.0', 'Account and financial management API', 'http://localhost:8000/api/accounts', 'system', 'system'),
('transaction-management-api', 'v1.0.0', 'Transaction processing and history API', 'http://localhost:8000/api/transactions', 'system', 'system'),
('monitoring-api', 'v1.0.0', 'System monitoring and metrics API', 'http://localhost:8000/api/monitoring', 'system', 'system'),
('ai-services-api', 'v1.0.0', 'AI and machine learning services API', 'http://localhost:8000/api/ai', 'system', 'system');

-- Insert initial aliases
INSERT INTO ssot_api_aliases (contract_id, alias_name, context, alias_type, description, created_by, updated_by) VALUES
((SELECT id FROM ssot_api_contracts WHERE canonical_name = 'user-management-api'), 'user-api', 'frontend', 'permanent', 'User management API for frontend', 'system', 'system'),
((SELECT id FROM ssot_api_contracts WHERE canonical_name = 'user-management-api'), 'auth-service', 'system', 'permanent', 'Authentication service API', 'system', 'system'),
((SELECT id FROM ssot_api_contracts WHERE canonical_name = 'account-management-api'), 'account-api', 'frontend', 'permanent', 'Account management API for frontend', 'system', 'system'),
((SELECT id FROM ssot_api_contracts WHERE canonical_name = 'transaction-management-api'), 'transaction-api', 'frontend', 'permanent', 'Transaction API for frontend', 'system', 'system'),
((SELECT id FROM ssot_api_contracts WHERE canonical_name = 'monitoring-api'), 'metrics-api', 'system', 'permanent', 'Metrics and monitoring API', 'system', 'system'),
((SELECT id FROM ssot_api_contracts WHERE canonical_name = 'ai-services-api'), 'ai-api', 'frontend', 'permanent', 'AI services API for frontend', 'system', 'system');

-- Create triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_ssot_api_contracts_updated_at BEFORE UPDATE ON ssot_api_contracts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ssot_api_aliases_updated_at BEFORE UPDATE ON ssot_api_aliases FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ssot_governance_rules_updated_at BEFORE UPDATE ON ssot_governance_rules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function for audit logging
CREATE OR REPLACE FUNCTION log_ssot_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO ssot_audit_logs (entity_type, entity_id, action, old_values, context, user_id)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', to_jsonb(OLD), 'system', 'system');
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO ssot_audit_logs (entity_type, entity_id, action, old_values, new_values, context, user_id)
        VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), 'system', 'system');
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO ssot_audit_logs (entity_type, entity_id, action, new_values, context, user_id)
        VALUES (TG_TABLE_NAME, NEW.id, 'INSERT', to_jsonb(NEW), 'system', 'system');
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Create audit triggers
CREATE TRIGGER audit_ssot_api_contracts AFTER INSERT OR UPDATE OR DELETE ON ssot_api_contracts FOR EACH ROW EXECUTE FUNCTION log_ssot_changes();
CREATE TRIGGER audit_ssot_api_aliases AFTER INSERT OR UPDATE OR DELETE ON ssot_api_aliases FOR EACH ROW EXECUTE FUNCTION log_ssot_changes();
CREATE TRIGGER audit_ssot_governance_rules AFTER INSERT OR UPDATE OR DELETE ON ssot_governance_rules FOR EACH ROW EXECUTE FUNCTION log_ssot_changes();

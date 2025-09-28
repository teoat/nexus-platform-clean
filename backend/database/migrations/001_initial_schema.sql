-- NEXUS Platform - Initial Database Schema Migration
-- Version: 001
-- Description: Create initial SSOT database schema
-- Generated: 2025-01-27T12:30:00Z

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create SSOT schema
CREATE SCHEMA IF NOT EXISTS ssot;

-- Users and Authentication
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- User Roles and Permissions
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    PRIMARY KEY (user_id, role_id)
);

-- SSOT Anchors
CREATE TABLE IF NOT EXISTS ssot_anchors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    anchor_id VARCHAR(255) UNIQUE NOT NULL,
    family VARCHAR(100) NOT NULL,
    description TEXT,
    format VARCHAR(50) NOT NULL,
    source_hint VARCHAR(500),
    owner VARCHAR(255),
    version VARCHAR(50) NOT NULL,
    centrality_score DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API Aliases
CREATE TABLE IF NOT EXISTS api_aliases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alias_name VARCHAR(255) NOT NULL,
    canonical_name VARCHAR(255) NOT NULL,
    context VARCHAR(100) NOT NULL,
    alias_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    UNIQUE(alias_name, context)
);

-- API Endpoints
CREATE TABLE IF NOT EXISTS api_endpoints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    path VARCHAR(500) NOT NULL,
    method VARCHAR(10) NOT NULL,
    description TEXT,
    version VARCHAR(20) DEFAULT 'v1',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(255) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    operation_id VARCHAR(255),
    context JSONB DEFAULT '{}'
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_api_endpoints_name ON api_endpoints(name);
CREATE INDEX IF NOT EXISTS idx_api_aliases_alias ON api_aliases(alias_name);
CREATE INDEX IF NOT EXISTS idx_api_aliases_context ON api_aliases(context);
CREATE INDEX IF NOT EXISTS idx_ssot_anchors_family ON ssot_anchors(family);
CREATE INDEX IF NOT EXISTS idx_audit_logs_table_record ON audit_logs(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_changed_at ON audit_logs(changed_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_operation_id ON audit_logs(operation_id);

-- Create triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_users_updated_at') THEN
        CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_api_endpoints_updated_at') THEN
        CREATE TRIGGER update_api_endpoints_updated_at BEFORE UPDATE ON api_endpoints
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_ssot_anchors_updated_at') THEN
        CREATE TRIGGER update_ssot_anchors_updated_at BEFORE UPDATE ON ssot_anchors
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- Insert default roles
INSERT INTO roles (name, description, permissions) VALUES
('admin', 'Administrator with full access', '["*"]'),
('user', 'Standard user with basic access', '["read:own", "write:own"]'),
('viewer', 'Read-only access', '["read:own"]'),
('manager', 'Manager with team access', '["read:team", "write:team", "manage:team"]')
ON CONFLICT (name) DO NOTHING;

-- Insert default API endpoints
INSERT INTO api_endpoints (name, path, method, description, version) VALUES
('health_check', '/health', 'GET', 'Health check endpoint', 'v1'),
('user_profile', '/api/v1/users/profile', 'GET', 'Get user profile', 'v1'),
('user_profile_update', '/api/v1/users/profile', 'PUT', 'Update user profile', 'v1'),
('aliases_list', '/api/v1/aliases', 'GET', 'List aliases', 'v1'),
('aliases_create', '/api/v1/aliases', 'POST', 'Create alias', 'v1'),
('aliases_resolve', '/api/v1/aliases/{alias_name}/resolve', 'POST', 'Resolve alias', 'v1'),
('ssot_query', '/api/v1/ssot/query', 'POST', 'SSOT query endpoint', 'v1')
ON CONFLICT (name) DO NOTHING;

-- Insert default SSOT anchors
INSERT INTO ssot_anchors (anchor_id, family, description, format, source_hint, owner, version, centrality_score) VALUES
('env_config', 'environment', 'Environment configuration', 'yaml', 'config/ssot/environment.env', 'system', '1.0', 0.95),
('docker_config', 'deployment', 'Docker Compose configuration', 'yaml', 'config/ssot/docker/docker-compose.yml', 'system', '1.0', 0.90),
('k8s_config', 'deployment', 'Kubernetes configuration', 'yaml', 'config/ssot/kubernetes/', 'system', '1.0', 0.85),
('monitoring_config', 'monitoring', 'Prometheus configuration', 'yaml', 'config/ssot/monitoring/prometheus.yml', 'system', '1.0', 0.80),
('api_config', 'api', 'API configuration', 'typescript', 'frontend/web/src/config/api.ts', 'system', '1.0', 0.90)
ON CONFLICT (anchor_id) DO NOTHING;

-- Insert default aliases
INSERT INTO api_aliases (alias_name, canonical_name, context, alias_type, description, created_by, is_active) VALUES
('api_health', 'health_check', 'api', 'permanent', 'API health check endpoint alias', (SELECT id FROM users WHERE username = 'system' LIMIT 1), true),
('db_config', 'env_config', 'database', 'permanent', 'Database configuration alias', (SELECT id FROM users WHERE username = 'system' LIMIT 1), true),
('container_config', 'docker_config', 'deployment', 'permanent', 'Docker container configuration alias', (SELECT id FROM users WHERE username = 'system' LIMIT 1), true),
('k8s_deploy', 'k8s_config', 'deployment', 'permanent', 'Kubernetes deployment configuration alias', (SELECT id FROM users WHERE username = 'system' LIMIT 1), true),
('metrics_config', 'monitoring_config', 'observability', 'permanent', 'Monitoring and metrics configuration alias', (SELECT id FROM users WHERE username = 'system' LIMIT 1), true)
ON CONFLICT (alias_name, context) DO NOTHING;

-- Create a system user if it doesn't exist
INSERT INTO users (username, email, password_hash, first_name, last_name, is_active, is_verified)
VALUES ('system', 'system@nexus.local', '$2b$12$system_hash_placeholder', 'System', 'User', true, true)
ON CONFLICT (username) DO NOTHING;

-- Grant permissions
GRANT USAGE ON SCHEMA ssot TO PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ssot TO PUBLIC;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO PUBLIC;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ssot TO PUBLIC;

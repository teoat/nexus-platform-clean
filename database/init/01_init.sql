-- NEXUS Platform - Database Initialization Script

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS nexus_platform;

-- Use the database
\c nexus_platform;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create SSOT aliases table
CREATE TABLE IF NOT EXISTS ssot_aliases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alias_name VARCHAR(255) NOT NULL,
    canonical_name VARCHAR(255) NOT NULL,
    context VARCHAR(100) DEFAULT 'default',
    alias_type VARCHAR(50) DEFAULT 'permanent',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    UNIQUE(alias_name, context)
);

-- Create API metrics table
CREATE TABLE IF NOT EXISTS api_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    response_time INTEGER NOT NULL,
    status_code INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id UUID REFERENCES users(id),
    ip_address INET
);

-- Create system logs table
CREATE TABLE IF NOT EXISTS system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    component VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_ssot_aliases_name ON ssot_aliases(alias_name);
CREATE INDEX IF NOT EXISTS idx_ssot_aliases_context ON ssot_aliases(context);
CREATE INDEX IF NOT EXISTS idx_api_metrics_endpoint ON api_metrics(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_metrics_timestamp ON api_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);
CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp);

-- Insert default admin user
INSERT INTO users (email, username, hashed_password, full_name, is_superuser)
VALUES (
    'admin@nexus-platform.com',
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/9.8.8.8', -- password: admin123
    'NEXUS Platform Administrator',
    true
) ON CONFLICT (email) DO NOTHING;

-- Insert sample SSOT aliases
INSERT INTO ssot_aliases (alias_name, canonical_name, context, description)
VALUES 
    ('user-service', 'api-users', 'frontend', 'User management service'),
    ('auth-service', 'api-auth', 'frontend', 'Authentication service'),
    ('payment-service', 'api-payments', 'frontend', 'Payment processing service'),
    ('notification-service', 'api-notifications', 'frontend', 'Notification service')
ON CONFLICT (alias_name, context) DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ssot_aliases_updated_at BEFORE UPDATE ON ssot_aliases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE nexus_platform TO nexus_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nexus_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO nexus_user;

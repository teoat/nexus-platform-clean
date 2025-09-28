-- Nexus Platform Database Initialization Script
-- This script initializes the database schema for the Financial Examiner POV System

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS nexus;

-- Use the nexus database
\c nexus;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'financial_examiner',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create cases table
CREATE TABLE IF NOT EXISTS cases (
    id SERIAL PRIMARY KEY,
    case_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    amount DECIMAL(15,2),
    status VARCHAR(50) DEFAULT 'pending',
    pov_role VARCHAR(50) NOT NULL,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create fraud_detection table
CREATE TABLE IF NOT EXISTS fraud_detection (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES cases(id),
    risk_score DECIMAL(3,2) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    fraud_flags JSONB,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(50) UNIQUE NOT NULL,
    case_id INTEGER REFERENCES cases(id),
    report_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    generated_by INTEGER REFERENCES users(id),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status);
CREATE INDEX IF NOT EXISTS idx_cases_pov_role ON cases(pov_role);
CREATE INDEX IF NOT EXISTS idx_fraud_detection_case_id ON fraud_detection(case_id);
CREATE INDEX IF NOT EXISTS idx_reports_case_id ON reports(case_id);

-- Insert default admin user
INSERT INTO users (username, email, password_hash, role)
VALUES ('admin', 'admin@nexus.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HSKz8i2', 'admin')
ON CONFLICT (username) DO NOTHING;

-- Create audit log table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create audit log index
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

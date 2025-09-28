-- NEXUS Platform - Database Initialization Script

-- Create database if not exists
SELECT 'CREATE DATABASE nexus_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'nexus_db')\gexec

-- Connect to the database
\c nexus_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create custom types
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'manager', 'user', 'guest');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE account_type AS ENUM ('checking', 'savings', 'credit', 'investment', 'loan');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE transaction_type AS ENUM ('income', 'expense', 'transfer', 'investment', 'loan_payment');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE transaction_status AS ENUM ('pending', 'completed', 'failed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE notification_type AS ENUM ('info', 'warning', 'error', 'success', 'alert');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE audit_action AS ENUM ('create', 'update', 'delete', 'login', 'logout', 'access');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    email_verified_at TIMESTAMP WITH TIME ZONE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create user_preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    theme VARCHAR(20) DEFAULT 'light' NOT NULL,
    language VARCHAR(10) DEFAULT 'en' NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC' NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD' NOT NULL,
    date_format VARCHAR(20) DEFAULT 'YYYY-MM-DD' NOT NULL,
    notifications_enabled BOOLEAN DEFAULT TRUE NOT NULL,
    email_notifications BOOLEAN DEFAULT TRUE NOT NULL,
    push_notifications BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    preferences JSONB DEFAULT '{}'::jsonb,
    UNIQUE(user_id)
);

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_id UUID REFERENCES categories(id),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create accounts table
CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    account_type account_type NOT NULL,
    account_number VARCHAR(50),
    balance DECIMAL(15,2) DEFAULT 0.0 NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT check_balance_positive CHECK (balance >= 0),
    UNIQUE(user_id, name)
);

-- Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id),
    amount DECIMAL(15,2) NOT NULL,
    transaction_type transaction_type NOT NULL,
    status transaction_status DEFAULT 'pending' NOT NULL,
    description TEXT,
    reference_number VARCHAR(100),
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT check_amount_non_zero CHECK (amount != 0)
);

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type notification_type NOT NULL,
    is_read BOOLEAN DEFAULT FALSE NOT NULL,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action audit_action NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create system_config table
CREATE TABLE IF NOT EXISTS system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    value_type VARCHAR(20) NOT NULL,
    description TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_by UUID REFERENCES users(id)
);

-- Create files table
CREATE TABLE IF NOT EXISTS files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    file_size INTEGER NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    is_public BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email_active ON users(email, is_active);
CREATE INDEX IF NOT EXISTS idx_users_username_active ON users(username, is_active);
CREATE INDEX IF NOT EXISTS idx_users_role_active ON users(role, is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_accounts_type_active ON accounts(account_type, is_active);
CREATE INDEX IF NOT EXISTS idx_accounts_user_type ON accounts(user_id, account_type);

CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_category_id ON transactions(category_id);
CREATE INDEX IF NOT EXISTS idx_transactions_type_status ON transactions(transaction_type, status);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_account_date ON transactions(account_id, transaction_date);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(notification_type);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_action ON audit_logs(user_id, action);

CREATE INDEX IF NOT EXISTS idx_categories_parent_id ON categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_categories_active ON categories(is_active);

CREATE INDEX IF NOT EXISTS idx_files_user_id ON files(user_id);
CREATE INDEX IF NOT EXISTS idx_files_content_type ON files(content_type);
CREATE INDEX IF NOT EXISTS idx_files_created_at ON files(created_at);
CREATE INDEX IF NOT EXISTS idx_files_public ON files(is_public);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_files_updated_at BEFORE UPDATE ON files FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default categories
INSERT INTO categories (name, description) VALUES
('Food & Dining', 'Restaurants, groceries, and food expenses'),
('Transportation', 'Gas, public transit, rideshare, and vehicle expenses'),
('Housing', 'Rent, mortgage, utilities, and home maintenance'),
('Entertainment', 'Movies, games, subscriptions, and leisure activities'),
('Healthcare', 'Medical expenses, insurance, and wellness'),
('Shopping', 'Clothing, electronics, and general merchandise'),
('Education', 'Tuition, books, courses, and educational expenses'),
('Travel', 'Vacation, hotels, flights, and travel expenses'),
('Income', 'Salary, freelance, investments, and other income sources'),
('Transfer', 'Money transfers between accounts')
ON CONFLICT (name) DO NOTHING;

-- Insert default system configuration
INSERT INTO system_config (key, value, value_type, description) VALUES
('app_name', 'NEXUS Platform', 'string', 'Application name'),
('app_version', '1.0.0', 'string', 'Application version'),
('maintenance_mode', 'false', 'boolean', 'Maintenance mode flag'),
('max_file_size', '10485760', 'integer', 'Maximum file upload size in bytes'),
('session_timeout', '3600', 'integer', 'Session timeout in seconds'),
('password_min_length', '8', 'integer', 'Minimum password length'),
('enable_registration', 'true', 'boolean', 'Allow new user registration'),
('default_currency', 'USD', 'string', 'Default currency code'),
('timezone', 'UTC', 'string', 'Default timezone'),
('date_format', 'YYYY-MM-DD', 'string', 'Default date format')
ON CONFLICT (key) DO NOTHING;

-- Create a default admin user (password: admin123)
INSERT INTO users (email, username, first_name, last_name, password_hash, role, is_verified) VALUES
('admin@nexus-platform.com', 'admin', 'System', 'Administrator', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Qz8K2O', 'admin', true)
ON CONFLICT (email) DO NOTHING;

-- Create user preferences for admin
INSERT INTO user_preferences (user_id, theme, language, currency, notifications_enabled)
SELECT id, 'dark', 'en', 'USD', true FROM users WHERE email = 'admin@nexus-platform.com'
ON CONFLICT (user_id) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nexus_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO nexus_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO nexus_user;

-- Create a view for user summary
CREATE OR REPLACE VIEW user_summary AS
SELECT
    u.id,
    u.email,
    u.username,
    u.first_name,
    u.last_name,
    u.role,
    u.is_active,
    u.is_verified,
    u.created_at,
    up.theme,
    up.language,
    up.currency,
    up.timezone,
    COUNT(DISTINCT a.id) as account_count,
    COUNT(DISTINCT t.id) as transaction_count,
    COALESCE(SUM(a.balance), 0) as total_balance
FROM users u
LEFT JOIN user_preferences up ON u.id = up.user_id
LEFT JOIN accounts a ON u.id = a.user_id AND a.is_active = true
LEFT JOIN transactions t ON u.id = t.user_id
GROUP BY u.id, u.email, u.username, u.first_name, u.last_name, u.role, u.is_active, u.is_verified, u.created_at, up.theme, up.language, up.currency, up.timezone;

-- Create a view for transaction summary
CREATE OR REPLACE VIEW transaction_summary AS
SELECT
    t.id,
    t.user_id,
    u.username,
    t.account_id,
    a.name as account_name,
    t.category_id,
    c.name as category_name,
    t.amount,
    t.transaction_type,
    t.status,
    t.description,
    t.transaction_date,
    t.created_at
FROM transactions t
JOIN users u ON t.user_id = u.id
JOIN accounts a ON t.account_id = a.id
LEFT JOIN categories c ON t.category_id = c.id;

COMMIT;

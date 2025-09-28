-- NEXUS Platform - Database Optimization Indexes
-- Performance optimization for critical queries

-- Users table optimization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_active ON users(email) WHERE is_active = true;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role_active ON users(role, is_active);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created_at_active ON users(created_at) WHERE is_active = true;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_last_login ON users(last_login) WHERE last_login IS NOT NULL;

-- Transactions table optimization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_user_date_amount ON transactions(user_id, created_at DESC, amount);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_type_status ON transactions(type, status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_category_amount ON transactions(category_id, amount);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_date_range ON transactions(created_at) WHERE created_at >= CURRENT_DATE - INTERVAL '90 days';

-- Accounts table optimization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_accounts_user_type ON accounts(user_id, type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_accounts_balance ON accounts(balance) WHERE balance > 0;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_accounts_status ON accounts(status) WHERE status = 'active';

-- Analytics table optimization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_user_period ON analytics(user_id, period);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_metric_date ON analytics(metric_type, created_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_recent ON analytics(created_at) WHERE created_at >= CURRENT_DATE - INTERVAL '30 days';

-- Sessions table optimization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_user_active ON sessions(user_id, expires_at) WHERE expires_at > NOW();
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_token_active ON sessions(token) WHERE expires_at > NOW();

-- Audit logs optimization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_user_action ON audit_logs(user_id, action);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource, timestamp);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_recent ON audit_logs(timestamp) WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days';

-- Categories table optimization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_categories_user_active ON categories(user_id, active) WHERE active = true;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_categories_type_user ON categories(type, user_id);

-- Budgets table optimization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_budgets_user_period ON budgets(user_id, period_start, period_end);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_budgets_active ON budgets(user_id, active) WHERE active = true;

-- Notifications table optimization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id, read_status) WHERE read_status = false;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_type_date ON notifications(type, created_at);

-- Performance monitoring indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_metrics_service_date ON performance_metrics(service, timestamp);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_metrics_recent ON performance_metrics(timestamp) WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days';

-- Error logs optimization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_error_logs_level_date ON error_logs(level, timestamp);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_error_logs_service ON error_logs(service, timestamp);

-- Composite indexes for complex queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_user_type_date ON transactions(user_id, type, created_at DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_user_category_amount ON transactions(user_id, category_id, amount);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_user_metric_period ON analytics(user_id, metric_type, period);

-- Partial indexes for better performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_recent_active ON users(created_at) WHERE is_active = true AND created_at >= CURRENT_DATE - INTERVAL '30 days';
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_high_value ON transactions(amount) WHERE amount > 1000;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_expired ON sessions(expires_at) WHERE expires_at <= NOW();

-- Text search indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_description_gin ON transactions USING gin(to_tsvector('english', description));
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_name_gin ON users USING gin(to_tsvector('english', full_name));

-- Update table statistics
ANALYZE users;
ANALYZE transactions;
ANALYZE accounts;
ANALYZE analytics;
ANALYZE sessions;
ANALYZE audit_logs;
ANALYZE categories;
ANALYZE budgets;
ANALYZE notifications;
ANALYZE performance_metrics;
ANALYZE error_logs;

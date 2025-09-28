-- NEXUS Platform Database Optimization Script
-- Comprehensive indexing, query optimization, and performance improvements

-- ===========================================
-- INDEX OPTIMIZATION
-- ===========================================

-- Users table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role ON users (role);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_is_active ON users (is_active);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created_at ON users (created_at DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_last_login ON users (last_login DESC);

-- Composite indexes for common queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active_role ON users (is_active, role);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role_created ON users (role, created_at DESC);

-- Accounts table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_accounts_user_id ON accounts (user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_accounts_account_type ON accounts (account_type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_accounts_is_active ON accounts (is_active);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_accounts_balance ON accounts (balance);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_accounts_created_at ON accounts (created_at DESC);

-- Categories table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_categories_user_id ON categories (user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_categories_name ON categories (name);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_categories_is_active ON categories (is_active);

-- Transactions table indexes (most critical for performance)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_user_id ON transactions (user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_account_id ON transactions (account_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_category_id ON transactions (category_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_transaction_type ON transactions (transaction_type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_status ON transactions (status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_transaction_date ON transactions (transaction_date DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_amount ON transactions (amount);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_created_at ON transactions (created_at DESC);

-- Composite indexes for transaction queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_user_date ON transactions (user_id, transaction_date DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_user_type ON transactions (user_id, transaction_type, transaction_date DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_account_date ON transactions (account_id, transaction_date DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_user_status ON transactions (user_id, status, transaction_date DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_date_amount ON transactions (transaction_date DESC, amount);

-- Audit logs table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_user_id ON audit_logs (user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_action ON audit_logs (action);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_table_name ON audit_logs (table_name);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_created_at ON audit_logs (created_at DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_ip_address ON audit_logs (ip_address);

-- Composite indexes for audit queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_user_action ON audit_logs (user_id, action, created_at DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_table_created ON audit_logs (table_name, created_at DESC);

-- API tokens table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_tokens_user_id ON api_tokens (user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_tokens_is_active ON api_tokens (is_active);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_tokens_expires_at ON api_tokens (expires_at);

-- System settings table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_system_settings_key ON system_settings (key);

-- ===========================================
-- PARTITIONING STRATEGY
-- ===========================================

-- Partition transactions table by month for better performance
-- (Uncomment and modify based on your PostgreSQL version)

-- CREATE TABLE transactions_y2024m01 PARTITION OF transactions
--     FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
-- CREATE TABLE transactions_y2024m02 PARTITION OF transactions
--     FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
-- -- Add more partitions as needed

-- ===========================================
-- QUERY OPTIMIZATION
-- ===========================================

-- Create partial indexes for active records
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active_only ON users (id, username, email) WHERE is_active = true;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_accounts_active_only ON accounts (id, user_id, balance) WHERE is_active = true;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_categories_active_only ON categories (id, user_id, name) WHERE is_active = true;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_completed_only ON transactions (id, user_id, amount, transaction_date) WHERE status = 'completed';

-- ===========================================
-- VIEW OPTIMIZATION
-- ===========================================

-- Create materialized view for transaction summaries (refresh periodically)
CREATE MATERIALIZED VIEW IF NOT EXISTS transaction_summaries AS
SELECT
    t.user_id,
    t.account_id,
    t.transaction_type,
    DATE_TRUNC('month', t.transaction_date) as month,
    COUNT(*) as transaction_count,
    SUM(t.amount) as total_amount,
    AVG(t.amount) as avg_amount,
    MIN(t.amount) as min_amount,
    MAX(t.amount) as max_amount
FROM transactions t
WHERE t.status = 'completed'
GROUP BY t.user_id, t.account_id, t.transaction_type, DATE_TRUNC('month', t.transaction_date);

-- Create indexes on materialized view
CREATE INDEX IF NOT EXISTS idx_transaction_summaries_user_month ON transaction_summaries (user_id, month DESC);
CREATE INDEX IF NOT EXISTS idx_transaction_summaries_account_month ON transaction_summaries (account_id, month DESC);

-- ===========================================
-- CONSTRAINTS AND TRIGGERS
-- ===========================================

-- Add check constraints for data integrity
ALTER TABLE users ADD CONSTRAINT chk_users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');
ALTER TABLE accounts ADD CONSTRAINT chk_accounts_balance_positive CHECK (balance >= 0);
ALTER TABLE transactions ADD CONSTRAINT chk_transactions_amount_positive CHECK (amount > 0);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_accounts_updated_at ON accounts;
CREATE TRIGGER update_accounts_updated_at
    BEFORE UPDATE ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_categories_updated_at ON categories;
CREATE TRIGGER update_categories_updated_at
    BEFORE UPDATE ON categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_transactions_updated_at ON transactions;
CREATE TRIGGER update_transactions_updated_at
    BEFORE UPDATE ON transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ===========================================
-- PERFORMANCE MONITORING
-- ===========================================

-- Create function to analyze table statistics
CREATE OR REPLACE FUNCTION analyze_table_stats(table_name TEXT)
RETURNS TABLE (
    schemaname TEXT,
    tablename TEXT,
    attname TEXT,
    n_distinct BIGINT,
    correlation REAL
) AS $$
BEGIN
    RETURN QUERY
    EXECUTE format('SELECT schemaname, tablename, attname, n_distinct, correlation FROM pg_stats WHERE tablename = %L', table_name);
END;
$$ LANGUAGE plpgsql;

-- Create function to get slow queries (requires pg_stat_statements extension)
-- CREATE OR REPLACE FUNCTION get_slow_queries(limit_count INTEGER DEFAULT 10)
-- RETURNS TABLE (
--     query TEXT,
--     calls BIGINT,
--     total_time REAL,
--     mean_time REAL,
--     rows BIGINT
-- ) AS $$
-- BEGIN
--     RETURN QUERY
--     SELECT
--         LEFT(query, 100) as query,
--         calls,
--         ROUND(total_time::numeric, 2) as total_time,
--         ROUND(mean_time::numeric, 2) as mean_time,
--         rows
--     FROM pg_stat_statements
--     ORDER BY mean_time DESC
--     LIMIT limit_count;
-- END;
-- $$ LANGUAGE plpgsql;

-- ===========================================
-- MAINTENANCE FUNCTIONS
-- ===========================================

-- Function to rebuild indexes (run during maintenance windows)
CREATE OR REPLACE FUNCTION rebuild_indexes()
RETURNS VOID AS $$
DECLARE
    index_record RECORD;
BEGIN
    FOR index_record IN
        SELECT indexname, tablename
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND indexname LIKE 'idx_%'
    LOOP
        RAISE NOTICE 'Rebuilding index: % on table: %', index_record.indexname, index_record.tablename;
        EXECUTE format('REINDEX INDEX CONCURRENTLY %I', index_record.indexname);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Function to vacuum and analyze tables
CREATE OR REPLACE FUNCTION vacuum_analyze_all()
RETURNS VOID AS $$
DECLARE
    table_record RECORD;
BEGIN
    FOR table_record IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
    LOOP
        RAISE NOTICE 'Vacuuming and analyzing table: %', table_record.tablename;
        EXECUTE format('VACUUM ANALYZE %I', table_record.tablename);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ===========================================
-- MONITORING QUERIES
-- ===========================================

-- Query to check index usage
-- SELECT
--     schemaname, tablename, indexname,
--     idx_scan, idx_tup_read, idx_tup_fetch
-- FROM pg_stat_user_indexes
-- ORDER BY idx_scan DESC;

-- Query to check table bloat
-- SELECT
--     schemaname, tablename,
--     n_dead_tup, n_live_tup,
--     ROUND(n_dead_tup::numeric / (n_live_tup + n_dead_tup) * 100, 2) as bloat_ratio
-- FROM pg_stat_user_tables
-- WHERE n_live_tup + n_dead_tup > 0
-- ORDER BY bloat_ratio DESC;

-- ===========================================
-- CLEANUP AND FINAL STEPS
-- ===========================================

-- Analyze all tables to update statistics
ANALYZE;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Database optimization completed successfully at %', now();
END $$;
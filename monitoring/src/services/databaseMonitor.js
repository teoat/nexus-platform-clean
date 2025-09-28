const sqlite3 = require("sqlite3").verbose();
const moment = require("moment");
class DatabaseMonitor {
  constructor(logger) {
    this.logger = logger;
    this.databasePath = process.env.DATABASE_PATH || "../backend/nexus.db";
    this.connectionPool = [];
    this.maxConnections = 10;
    this.monitoringData = {
      connections: 0,
      queries: 0,
      slowQueries: 0,
      errors: 0,
      lastCheck: null,
    };
  }
  async getStatus() {
    try {
      const startTime = Date.now();
      const connectionTest = await this.testConnection();
      const stats = await this.getDatabaseStats();
      const health = await this.checkDatabaseHealth();
      const responseTime = Date.now() - startTime;
      this.monitoringData.lastCheck = new Date().toISOString();
      return {
        status: connectionTest ? "healthy" : "unhealthy",
        responseTime: responseTime,
        connection: connectionTest,
        statistics: stats,
        health: health,
        monitoring: this.monitoringData,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      this.logger.error("Database monitoring failed:", error);
      this.monitoringData.errors++;
      return {
        status: "unhealthy",
        error: error.message,
        timestamp: new Date().toISOString(),
      };
    }
  }
  async testConnection() {
    return new Promise((resolve) => {
      const db = new sqlite3.Database(this.databasePath, (err) => {
        if (err) {
          this.logger.error("Database connection failed:", err);
          resolve(false);
        } else {
          this.logger.info("Database connection successful");
          db.close();
          resolve(true);
        }
      });
    });
  }
  async getDatabaseStats() {
    return new Promise((resolve, reject) => {
      const db = new sqlite3.Database(this.databasePath);
      const stats = {};
      const queries = [
        "SELECT COUNT(*) as user_count FROM users",
        "SELECT COUNT(*) as account_count FROM accounts",
        "SELECT COUNT(*) as transaction_count FROM transactions",
        "SELECT COUNT(*) as file_count FROM files",
        "SELECT COUNT(*) as notification_count FROM notifications",
        "SELECT COUNT(*) as audit_count FROM audit_logs",
        "SELECT COUNT(*) as security_count FROM security_events",
      ];
      let completed = 0;
      const results = {};
      queries.forEach((query, index) => {
        db.get(query, (err, row) => {
          if (err) {
            this.logger.error(`Database query failed: ${query}`, err);
            results[`query_${index}`] = { error: err.message };
          } else {
            const key = query.split(" ")[5].replace("_count", "");
            results[key] = row[Object.keys(row)[0]];
          }
          completed++;
          if (completed === queries.length) {
            db.close();
            resolve(results);
          }
        });
      });
    });
  }
  async checkDatabaseHealth() {
    try {
      const db = new sqlite3.Database(this.databasePath);
      return new Promise((resolve) => {
        const healthChecks = [
          this.checkTableIntegrity(db),
          this.checkIndexHealth(db),
          this.checkDataConsistency(db),
          this.checkPerformanceMetrics(db),
        ];
        Promise.allSettled(healthChecks).then((results) => {
          db.close();
          const health = { overall: "healthy", checks: {}, issues: [] };
          results.forEach((result, index) => {
            const checkName = [
              "integrity",
              "indexes",
              "consistency",
              "performance",
            ][index];
            if (result.status === "fulfilled") {
              health.checks[checkName] = result.value;
              if (result.value.status !== "healthy") {
                health.overall = "degraded";
                health.issues.push(`${checkName}: ${result.value.message}`);
              }
            } else {
              health.checks[checkName] = {
                status: "error",
                message: result.reason.message,
              };
              health.overall = "unhealthy";
              health.issues.push(`${checkName}: ${result.reason.message}`);
            }
          });
          resolve(health);
        });
      });
    } catch (error) {
      this.logger.error("Database health check failed:", error);
      return { overall: "unhealthy", error: error.message };
    }
  }
  async checkTableIntegrity(db) {
    return new Promise((resolve) => {
      db.get("PRAGMA integrity_check", (err, row) => {
        if (err) {
          resolve({ status: "error", message: err.message });
        } else {
          const result = row[Object.keys(row)[0]];
          resolve({
            status: result === "ok" ? "healthy" : "unhealthy",
            message: result,
            details: "Database integrity check",
          });
        }
      });
    });
  }
  async checkIndexHealth(db) {
    return new Promise((resolve) => {
      db.all("PRAGMA index_list(users)", (err, rows) => {
        if (err) {
          resolve({ status: "error", message: err.message });
        } else {
          resolve({
            status: "healthy",
            message: `Found ${rows.length} indexes`,
            details: "Index health check",
          });
        }
      });
    });
  }
  async checkDataConsistency(db) {
    return new Promise((resolve) => {
      const query = ` SELECT COUNT(*) as orphaned_transactions FROM transactions t LEFT JOIN accounts a ON t.account_id = a.id WHERE t.account_id IS NOT NULL AND a.id IS NULL `;
      db.get(query, (err, row) => {
        if (err) {
          resolve({ status: "error", message: err.message });
        } else {
          const orphaned = row.orphaned_transactions;
          resolve({
            status: orphaned === 0 ? "healthy" : "unhealthy",
            message:
              orphaned === 0
                ? "No orphaned records found"
                : `${orphaned} orphaned records found`,
            details: "Data consistency check",
          });
        }
      });
    });
  }
  async checkPerformanceMetrics(db) {
    return new Promise((resolve) => {
      const startTime = Date.now();
      const query = ` SELECT u.username, COUNT(t.id) as transaction_count, SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE 0 END) as total_income, SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END) as total_expenses FROM users u LEFT JOIN accounts a ON u.id = a.user_id LEFT JOIN transactions t ON a.id = t.account_id GROUP BY u.id, u.username LIMIT 10 `;
      db.all(query, (err, rows) => {
        const queryTime = Date.now() - startTime;
        if (err) {
          resolve({ status: "error", message: err.message });
        } else {
          const isSlow = queryTime > 1000;
          if (isSlow) {
            this.monitoringData.slowQueries++;
          }
          resolve({
            status: isSlow ? "degraded" : "healthy",
            message: `Query completed in ${queryTime}ms`,
            details: `Performance test with ${rows.length} results`,
            queryTime: queryTime,
          });
        }
      });
    });
  }
  async checkDatabaseHealth() {
    try {
      const status = await this.getStatus();
      if (status.status === "unhealthy") {
        this.logger.error("Database health check failed:", status);
        return {
          healthy: false,
          issues: [status.error || "Database connection failed"],
          timestamp: new Date().toISOString(),
        };
      }
      const performanceIssues = [];
      if (status.health?.checks?.performance?.queryTime > 2000) {
        performanceIssues.push("Slow query performance detected");
      }
      const consistencyIssues = [];
      if (status.health?.checks?.consistency?.status !== "healthy") {
        consistencyIssues.push("Data consistency issues detected");
      }
      const allIssues = [...performanceIssues, ...consistencyIssues];
      return {
        healthy: allIssues.length === 0,
        issues: allIssues,
        status: status,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      this.logger.error("Database health check failed:", error);
      return {
        healthy: false,
        issues: [error.message],
        timestamp: new Date().toISOString(),
      };
    }
  }
  async getPerformanceMetrics() {
    try {
      const db = new sqlite3.Database(this.databasePath);
      return new Promise((resolve) => {
        const metrics = {
          connectionCount: this.monitoringData.connections,
          queryCount: this.monitoringData.queries,
          slowQueryCount: this.monitoringData.slowQueries,
          errorCount: this.monitoringData.errors,
          lastCheck: this.monitoringData.lastCheck,
        };
        db.get("PRAGMA page_count", (err, row) => {
          if (err) {
            this.logger.error("Failed to get database size:", err);
            resolve(metrics);
          } else {
            db.get("PRAGMA page_size", (err2, row2) => {
              db.close();
              if (err2) {
                this.logger.error("Failed to get page size:", err2);
                resolve(metrics);
              } else {
                metrics.databaseSize = row.page_count * row2.page_size;
                resolve(metrics);
              }
            });
          }
        });
      });
    } catch (error) {
      this.logger.error("Failed to get performance metrics:", error);
      return this.monitoringData;
    }
  }
  async monitorQuery(query, params = []) {
    const startTime = Date.now();
    this.monitoringData.queries++;
    try {
      const db = new sqlite3.Database(this.databasePath);
      return new Promise((resolve, reject) => {
        db.all(query, params, (err, rows) => {
          const queryTime = Date.now() - startTime;
          db.close();
          if (err) {
            this.monitoringData.errors++;
            this.logger.error("Query failed:", err);
            reject(err);
          } else {
            if (queryTime > 1000) {
              this.monitoringData.slowQueries++;
              this.logger.warn(`Slow query detected: ${queryTime}ms`);
            }
            resolve({
              rows: rows,
              queryTime: queryTime,
              rowCount: rows.length,
            });
          }
        });
      });
    } catch (error) {
      this.monitoringData.errors++;
      this.logger.error("Query monitoring failed:", error);
      throw error;
    }
  }
  getMonitoringData() {
    return this.monitoringData;
  }
  resetMonitoringData() {
    this.monitoringData = {
      connections: 0,
      queries: 0,
      slowQueries: 0,
      errors: 0,
      lastCheck: null,
    };
  }
}
module.exports = { DatabaseMonitor };

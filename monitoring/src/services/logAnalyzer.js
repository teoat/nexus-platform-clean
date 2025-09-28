const fs = require("fs").promises;
const path = require("path");
const moment = require("moment");
class LogAnalyzer {
  constructor(logger) {
    this.logger = logger;
    this.logDirectory = process.env.LOG_DIRECTORY || "./logs";
    this.analysisResults = {
      errors: [],
      warnings: [],
      patterns: {},
      statistics: {},
      recommendations: [],
    };
  }
  async analyzeLogs() {
    try {
      this.logger.info("Starting log analysis...");
      this.analysisResults = {
        errors: [],
        warnings: [],
        patterns: {},
        statistics: {},
        recommendations: [],
      };
      const logFiles = await this.getLogFiles();
      for (const logFile of logFiles) {
        await this.analyzeLogFile(logFile);
      }
      this.generatePatterns();
      this.generateStatistics();
      this.generateRecommendations();
      this.logger.info("Log analysis completed successfully");
      return this.analysisResults;
    } catch (error) {
      this.logger.error("Log analysis failed:", error);
      throw error;
    }
  }
  async getLogFiles() {
    try {
      const files = await fs.readdir(this.logDirectory);
      return files
        .filter((file) => file.endsWith(".log"))
        .map((file) => path.join(this.logDirectory, file));
    } catch (error) {
      this.logger.error("Failed to read log directory:", error);
      return [];
    }
  }
  async analyzeLogFile(filePath) {
    try {
      const content = await fs.readFile(filePath, "utf8");
      const lines = content.split("\n").filter((line) => line.trim());
      for (const line of lines) {
        await this.analyzeLogLine(line, filePath);
      }
    } catch (error) {
      this.logger.error(`Failed to analyze log file ${filePath}:`, error);
    }
  }
  async analyzeLogLine(line, filePath) {
    try {
      let logEntry;
      try {
        logEntry = JSON.parse(line);
      } catch (e) {
        this.analyzeTextLogLine(line, filePath);
        return;
      }
      if (logEntry.level === "error") {
        this.analysisResults.errors.push({
          timestamp: logEntry.timestamp,
          message: logEntry.message,
          stack: logEntry.stack,
          file: filePath,
          severity: this.categorizeError(logEntry.message),
        });
      }
      if (logEntry.level === "warn") {
        this.analysisResults.warnings.push({
          timestamp: logEntry.timestamp,
          message: logEntry.message,
          file: filePath,
        });
      }
      this.trackPatterns(logEntry);
    } catch (error) {
      this.logger.error("Failed to analyze log line:", error);
    }
  }
  analyzeTextLogLine(line, filePath) {
    if (line.toLowerCase().includes("error")) {
      this.analysisResults.errors.push({
        timestamp: new Date().toISOString(),
        message: line,
        file: filePath,
        severity: "medium",
      });
    }
    if (
      line.toLowerCase().includes("warning") ||
      line.toLowerCase().includes("warn")
    ) {
      this.analysisResults.warnings.push({
        timestamp: new Date().toISOString(),
        message: line,
        file: filePath,
      });
    }
  }
  categorizeError(message) {
    const errorMessage = message.toLowerCase();
    if (errorMessage.includes("database") || errorMessage.includes("sql")) {
      return "database";
    } else if (
      errorMessage.includes("network") ||
      errorMessage.includes("connection")
    ) {
      return "network";
    } else if (
      errorMessage.includes("auth") ||
      errorMessage.includes("permission")
    ) {
      return "security";
    } else if (
      errorMessage.includes("memory") ||
      errorMessage.includes("out of memory")
    ) {
      return "resource";
    } else if (errorMessage.includes("timeout")) {
      return "performance";
    } else {
      return "general";
    }
  }
  trackPatterns(logEntry) {
    if (!this.analysisResults.patterns[logEntry.level]) {
      this.analysisResults.patterns[logEntry.level] = 0;
    }
    this.analysisResults.patterns[logEntry.level]++;
    if (logEntry.level === "error") {
      const errorType = this.categorizeError(logEntry.message);
      if (!this.analysisResults.patterns[`error_${errorType}`]) {
        this.analysisResults.patterns[`error_${errorType}`] = 0;
      }
      this.analysisResults.patterns[`error_${errorType}`]++;
    }
    if (logEntry.message && logEntry.message.includes("HTTP")) {
      if (!this.analysisResults.patterns.http_requests) {
        this.analysisResults.patterns.http_requests = 0;
      }
      this.analysisResults.patterns.http_requests++;
    }
  }
  generatePatterns() {
    const patterns = this.analysisResults.patterns;
    const totalLogs = Object.values(patterns).reduce(
      (sum, count) => sum + count,
      0,
    );
    patterns.error_rate =
      totalLogs > 0 ? ((patterns.error || 0) / totalLogs) * 100 : 0;
    patterns.warning_rate =
      totalLogs > 0 ? ((patterns.warn || 0) / totalLogs) * 100 : 0;
    patterns.recurring_errors = this.identifyRecurringErrors();
    patterns.peak_error_times = this.identifyPeakErrorTimes();
  }
  generateStatistics() {
    const stats = {
      total_errors: this.analysisResults.errors.length,
      total_warnings: this.analysisResults.warnings.length,
      error_categories: this.getErrorCategories(),
      time_range: this.getTimeRange(),
      error_frequency: this.getErrorFrequency(),
      most_common_errors: this.getMostCommonErrors(),
    };
    this.analysisResults.statistics = stats;
  }
  generateRecommendations() {
    const recommendations = [];
    if (this.analysisResults.patterns.error_rate > 5) {
      recommendations.push({
        type: "error_rate",
        priority: "high",
        message:
          "High error rate detected. Consider reviewing error handling and system stability.",
        action: "Review error logs and implement better error handling",
      });
    }
    if (this.analysisResults.patterns.error_database > 10) {
      recommendations.push({
        type: "database",
        priority: "high",
        message:
          "Multiple database errors detected. Check database connectivity and queries.",
        action: "Review database configuration and query performance",
      });
    }
    if (this.analysisResults.patterns.error_security > 5) {
      recommendations.push({
        type: "security",
        priority: "critical",
        message:
          "Security-related errors detected. Review authentication and authorization.",
        action: "Audit security implementation and access controls",
      });
    }
    if (this.analysisResults.patterns.error_performance > 10) {
      recommendations.push({
        type: "performance",
        priority: "medium",
        message:
          "Performance-related errors detected. Consider optimizing system resources.",
        action: "Review system performance and resource allocation",
      });
    }
    if (this.analysisResults.patterns.error_resource > 5) {
      recommendations.push({
        type: "resource",
        priority: "high",
        message:
          "Resource-related errors detected. Check memory and CPU usage.",
        action: "Monitor system resources and consider scaling",
      });
    }
    this.analysisResults.recommendations = recommendations;
  }
  identifyRecurringErrors() {
    const errorMessages = this.analysisResults.errors.map(
      (error) => error.message,
    );
    const errorCounts = {};
    errorMessages.forEach((message) => {
      errorCounts[message] = (errorCounts[message] || 0) + 1;
    });
    return Object.entries(errorCounts)
      .filter(([message, count]) => count > 1)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10);
  }
  identifyPeakErrorTimes() {
    const errorTimes = this.analysisResults.errors.map((error) =>
      moment(error.timestamp).format("HH:mm"),
    );
    const timeCounts = {};
    errorTimes.forEach((time) => {
      timeCounts[time] = (timeCounts[time] || 0) + 1;
    });
    return Object.entries(timeCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5);
  }
  getErrorCategories() {
    const categories = {};
    this.analysisResults.errors.forEach((error) => {
      categories[error.severity] = (categories[error.severity] || 0) + 1;
    });
    return categories;
  }
  getTimeRange() {
    const timestamps = this.analysisResults.errors.map(
      (error) => error.timestamp,
    );
    if (timestamps.length === 0) return null;
    const sorted = timestamps.sort();
    return { start: sorted[0], end: sorted[sorted.length - 1] };
  }
  getErrorFrequency() {
    const hourly = {};
    this.analysisResults.errors.forEach((error) => {
      const hour = moment(error.timestamp).format("YYYY-MM-DD HH:00");
      hourly[hour] = (hourly[hour] || 0) + 1;
    });
    return hourly;
  }
  getMostCommonErrors() {
    const errorMessages = this.analysisResults.errors.map(
      (error) => error.message,
    );
    const counts = {};
    errorMessages.forEach((message) => {
      counts[message] = (counts[message] || 0) + 1;
    });
    return Object.entries(counts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([message, count]) => ({ message, count }));
  }
  getAnalysisResults() {
    return this.analysisResults;
  }
  async getRealTimeAnalysis() {
    try {
      const recentErrors = this.analysisResults.errors.filter((error) =>
        moment(error.timestamp).isAfter(moment().subtract(1, "hour")),
      );
      const recentWarnings = this.analysisResults.warnings.filter((warning) =>
        moment(warning.timestamp).isAfter(moment().subtract(1, "hour")),
      );
      return {
        recent_errors: recentErrors.length,
        recent_warnings: recentWarnings.length,
        error_trend: this.calculateErrorTrend(),
        critical_issues: this.getCriticalIssues(),
      };
    } catch (error) {
      this.logger.error("Failed to get real-time analysis:", error);
      return null;
    }
  }
  calculateErrorTrend() {
    const now = moment();
    const oneHourAgo = moment().subtract(1, "hour");
    const twoHoursAgo = moment().subtract(2, "hours");
    const recentErrors = this.analysisResults.errors.filter((error) =>
      moment(error.timestamp).isAfter(oneHourAgo),
    ).length;
    const previousErrors = this.analysisResults.errors.filter(
      (error) =>
        moment(error.timestamp).isAfter(twoHoursAgo) &&
        moment(error.timestamp).isBefore(oneHourAgo),
    ).length;
    if (previousErrors === 0) return recentErrors > 0 ? "increasing" : "stable";
    const trend = (recentErrors - previousErrors) / previousErrors;
    if (trend > 0.2) return "increasing";
    if (trend < -0.2) return "decreasing";
    return "stable";
  }
  getCriticalIssues() {
    return this.analysisResults.errors
      .filter(
        (error) => error.severity === "critical" || error.severity === "high",
      )
      .slice(0, 5);
  }
}
module.exports = { LogAnalyzer };

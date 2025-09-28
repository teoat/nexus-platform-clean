const nodemailer = require("nodemailer");
const axios = require("axios");
class AlertManager {
  constructor(logger) {
    this.logger = logger;
    this.alerts = new Map();
    this.alertIdCounter = 1;
    this.emailTransporter = nodemailer.createTransporter({
      host: process.env.SMTP_HOST || "smtp.gmail.com",
      port: process.env.SMTP_PORT || 587,
      secure: false,
      auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
    });
    this.slackWebhookUrl = process.env.SLACK_WEBHOOK_URL;
  }
  createAlert(alertData) {
    const alert = {
      id: this.alertIdCounter++,
      type: alertData.type || "system",
      severity: alertData.severity || "medium",
      message: alertData.message,
      details: alertData.details || {},
      status: "active",
      createdAt: new Date().toISOString(),
      acknowledgedAt: null,
      resolvedAt: null,
      acknowledgedBy: null,
      resolvedBy: null,
    };
    this.alerts.set(alert.id, alert);
    this.logger.warn(`Alert created: ${alert.message}`, alert);
    this.sendNotifications(alert);
    return alert;
  }
  acknowledgeAlert(alertId, acknowledgedBy = "system") {
    const alert = this.alerts.get(parseInt(alertId));
    if (alert && alert.status === "active") {
      alert.status = "acknowledged";
      alert.acknowledgedAt = new Date().toISOString();
      alert.acknowledgedBy = acknowledgedBy;
      this.logger.info(`Alert ${alertId} acknowledged by ${acknowledgedBy}`);
    }
  }
  resolveAlert(alertId, resolvedBy = "system") {
    const alert = this.alerts.get(parseInt(alertId));
    if (alert && alert.status !== "resolved") {
      alert.status = "resolved";
      alert.resolvedAt = new Date().toISOString();
      alert.resolvedBy = resolvedBy;
      this.logger.info(`Alert ${alertId} resolved by ${resolvedBy}`);
    }
  }
  getAllAlerts() {
    return Array.from(this.alerts.values()).sort(
      (a, b) => new Date(b.createdAt) - new Date(a.createdAt),
    );
  }
  getActiveAlerts() {
    return Array.from(this.alerts.values())
      .filter((alert) => alert.status === "active")
      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  }
  getAlertsBySeverity(severity) {
    return Array.from(this.alerts.values())
      .filter((alert) => alert.severity === severity)
      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  }
  async sendNotifications(alert) {
    const promises = [];
    if (alert.severity === "critical" && process.env.SMTP_USER) {
      promises.push(this.sendEmailNotification(alert));
    }
    if (
      ["medium", "high", "critical"].includes(alert.severity) &&
      this.slackWebhookUrl
    ) {
      promises.push(this.sendSlackNotification(alert));
    }
    this.logger.info(
      `Sending notifications for alert ${alert.id}: ${alert.message}`,
    );
    try {
      await Promise.allSettled(promises);
    } catch (error) {
      this.logger.error(
        `Failed to send notifications for alert ${alert.id}:`,
        error,
      );
    }
  }
  async sendEmailNotification(alert) {
    try {
      const mailOptions = {
        from: process.env.SMTP_USER,
        to: process.env.ALERT_EMAIL_RECIPIENTS || process.env.SMTP_USER,
        subject: `[${alert.severity.toUpperCase()}] NEXUS Platform Alert: ${alert.message}`,
        html: ` <h2>NEXUS Platform Alert</h2> <p><strong>Severity:</strong> ${alert.severity}</p> <p><strong>Type:</strong> ${alert.type}</p> <p><strong>Message:</strong> ${alert.message}</p> <p><strong>Time:</strong> ${alert.createdAt}</p> <p><strong>Details:</strong></p> <pre>${JSON.stringify(alert.details, null, 2)}</pre> `,
      };
      await this.emailTransporter.sendMail(mailOptions);
      this.logger.info(`Email notification sent for alert ${alert.id}`);
    } catch (error) {
      this.logger.error(
        `Failed to send email notification for alert ${alert.id}:`,
        error,
      );
    }
  }
  async sendSlackNotification(alert) {
    try {
      const color = this.getSeverityColor(alert.severity);
      const payload = {
        text: `NEXUS Platform Alert`,
        attachments: [
          {
            color: color,
            fields: [
              {
                title: "Severity",
                value: alert.severity.toUpperCase(),
                short: true,
              },
              { title: "Type", value: alert.type, short: true },
              { title: "Message", value: alert.message, short: false },
              {
                title: "Time",
                value: new Date(alert.createdAt).toLocaleString(),
                short: true,
              },
            ],
            footer: "NEXUS Platform Monitoring",
            ts: Math.floor(new Date(alert.createdAt).getTime() / 1000),
          },
        ],
      };
      await axios.post(this.slackWebhookUrl, payload);
      this.logger.info(`Slack notification sent for alert ${alert.id}`);
    } catch (error) {
      this.logger.error(
        `Failed to send Slack notification for alert ${alert.id}:`,
        error,
      );
    }
  }
  getSeverityColor(severity) {
    const colors = {
      low: "#36a64f",
      medium: "#ff9500",
      high: "#ff0000",
      critical: "#8b0000",
    };
    return colors[severity] || "#36a64f";
  }
  cleanupOldAlerts() {
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    for (const [id, alert] of this.alerts.entries()) {
      if (
        alert.status === "resolved" &&
        new Date(alert.resolvedAt) < sevenDaysAgo
      ) {
        this.alerts.delete(id);
        this.logger.info(`Cleaned up old alert ${id}`);
      }
    }
  }
  getAlertStats() {
    const alerts = Array.from(this.alerts.values());
    const stats = {
      total: alerts.length,
      active: alerts.filter((a) => a.status === "active").length,
      acknowledged: alerts.filter((a) => a.status === "acknowledged").length,
      resolved: alerts.filter((a) => a.status === "resolved").length,
      bySeverity: {
        low: alerts.filter((a) => a.severity === "low").length,
        medium: alerts.filter((a) => a.severity === "medium").length,
        high: alerts.filter((a) => a.severity === "high").length,
        critical: alerts.filter((a) => a.severity === "critical").length,
      },
    };
    return stats;
  }
}
module.exports = { AlertManager };

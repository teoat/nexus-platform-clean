import React, { useState, useEffect } from "react";
import "./MultiRoleOverlay.css";

const MultiRoleOverlay = ({
  insights = [],
  userRole = "user",
  isVisible = false,
  onClose = () => {},
  onRoleChange = () => {},
}) => {
  const [activeTab, setActiveTab] = useState(userRole);
  const [filteredInsights, setFilteredInsights] = useState([]);

  useEffect(() => {
    if (insights && insights.length > 0) {
      filterInsightsByRole(activeTab);
    }
  }, [insights, activeTab]);

  const filterInsightsByRole = (role) => {
    if (!insights || insights.length === 0) {
      setFilteredInsights([]);
      return;
    }

    // Filter insights based on role relevance
    const roleInsights = insights.filter((insight) => {
      if (role === "management") {
        return (
          insight.severity === "high" ||
          insight.severity === "critical" ||
          insight.type === "dashboard_insights" ||
          insight.type === "performance"
        );
      } else if (role === "auditor") {
        return (
          insight.severity === "medium" ||
          insight.severity === "high" ||
          insight.type === "compliance" ||
          insight.type === "security"
        );
      } else if (role === "legal") {
        return (
          insight.type === "compliance" ||
          insight.type === "legal" ||
          insight.severity === "high" ||
          insight.severity === "critical"
        );
      } else if (role === "developer") {
        return (
          insight.type === "technical" ||
          insight.type === "performance" ||
          insight.type === "api_monitoring" ||
          insight.severity === "critical"
        );
      } else {
        return insight.severity === "low" || insight.severity === "info";
      }
    });

    setFilteredInsights(roleInsights);
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case "management":
        return "👔";
      case "auditor":
        return "🔍";
      case "legal":
        return "⚖️";
      case "developer":
        return "💻";
      default:
        return "👤";
    }
  };

  const getRoleTitle = (role) => {
    switch (role) {
      case "management":
        return "Management Insights";
      case "auditor":
        return "Audit & Compliance";
      case "legal":
        return "Legal & Regulatory";
      case "developer":
        return "Technical Insights";
      default:
        return "User Insights";
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case "critical":
        return "#e74c3c";
      case "high":
        return "#f39c12";
      case "medium":
        return "#3498db";
      case "low":
        return "#2ecc71";
      default:
        return "#95a5a6";
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case "critical":
        return "🚨";
      case "high":
        return "⚠️";
      case "medium":
        return "💡";
      case "low":
        return "✅";
      default:
        return "ℹ️";
    }
  };

  const handleTabClick = (role) => {
    setActiveTab(role);
    onRoleChange(role);
  };

  if (!isVisible) return null;

  return (
    <div className="multi-role-overlay">
      <div className="overlay-backdrop" onClick={onClose}></div>

      <div className="overlay-content">
        {/* Header */}
        <div className="overlay-header">
          <h2>🤖 Frenly AI Insights</h2>
          <button className="close-button" onClick={onClose}>
            ✕
          </button>
        </div>

        {/* Role Tabs */}
        <div className="role-tabs">
          {["user", "management", "auditor", "legal", "developer"].map(
            (role) => (
              <button
                key={role}
                className={`role-tab ${activeTab === role ? "active" : ""}`}
                onClick={() => handleTabClick(role)}
              >
                {getRoleIcon(role)} {getRoleTitle(role)}
              </button>
            ),
          )}
        </div>

        {/* Content */}
        <div className="overlay-body">
          <div className="role-content">
            <h3>
              {getRoleIcon(activeTab)} {getRoleTitle(activeTab)}
            </h3>

            {filteredInsights.length > 0 ? (
              <div className="insights-list">
                {filteredInsights.map((insight, index) => (
                  <div key={index} className="insight-card">
                    <div className="insight-header">
                      <span
                        className="severity-badge"
                        style={{
                          backgroundColor: getSeverityColor(insight.severity),
                        }}
                      >
                        {getSeverityIcon(insight.severity)}{" "}
                        {insight.severity?.toUpperCase()}
                      </span>
                      <span className="insight-type">{insight.type}</span>
                    </div>

                    <div className="insight-content">
                      <p className="insight-message">{insight.message}</p>

                      {insight.insights && insight.insights.length > 0 && (
                        <div className="insight-details">
                          <h4>Key Insights:</h4>
                          <ul>
                            {insight.insights.map((item, idx) => (
                              <li key={idx}>{item}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {insight.recommendations &&
                        insight.recommendations.length > 0 && (
                          <div className="insight-recommendations">
                            <h4>Recommendations:</h4>
                            <ul>
                              {insight.recommendations.map((rec, idx) => (
                                <li key={idx}>{rec}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                      {insight.confidence && (
                        <div className="confidence-meter">
                          <span>
                            Confidence: {Math.round(insight.confidence * 100)}%
                          </span>
                          <div className="confidence-bar">
                            <div
                              className="confidence-fill"
                              style={{ width: `${insight.confidence * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-insights">
                <div className="no-insights-icon">🤔</div>
                <h4>No insights available</h4>
                <p>
                  No relevant insights found for{" "}
                  {getRoleTitle(activeTab).toLowerCase()}.
                </p>
                <p>
                  Try switching to a different role or wait for new insights to
                  be generated.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="overlay-footer">
          <div className="insight-stats">
            <span>Total Insights: {insights.length}</span>
            <span>Filtered: {filteredInsights.length}</span>
            <span>Role: {activeTab}</span>
          </div>

          <div className="footer-actions">
            <button
              className="refresh-button"
              onClick={() => window.location.reload()}
            >
              🔄 Refresh
            </button>
            <button
              className="help-button"
              onClick={() =>
                alert(
                  "Frenly AI Help: Click on insights for more details, switch roles for different perspectives, and use the refresh button to get latest insights.",
                )
              }
            >
              ❓ Help
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MultiRoleOverlay;

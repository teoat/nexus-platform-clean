import React, { useState, useEffect, useRef } from "react";
import "./FrenlyAvatar.css";

const FrenlyAvatar = ({
  context = {},
  onInsightClick = () => {},
  onOverlayToggle = () => {},
  className = "",
}) => {
  const [mood, setMood] = useState("idle");
  const [isVisible, setIsVisible] = useState(true);
  const [isAnimating, setIsAnimating] = useState(false);
  const [speechBubble, setSpeechBubble] = useState("");
  const [insights, setInsights] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [showOverlay, setShowOverlay] = useState(false);
  const [userRole, setUserRole] = useState("user");

  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const animationTimeoutRef = useRef(null);

  // WebSocket connection
  useEffect(() => {
    connectWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  // Context updates
  useEffect(() => {
    if (isConnected && wsRef.current) {
      sendContextUpdate();
    }
  }, [context, isConnected]);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket("ws://localhost:8765");
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("Frenly AI WebSocket connected");
        setIsConnected(true);
        setMood("cheerful");
        triggerAnimation("bounce");
        setSpeechBubble("Hello! I'm Frenly AI, your intelligent assistant! 🤖");
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      ws.onclose = () => {
        console.log("Frenly AI WebSocket disconnected");
        setIsConnected(false);
        setMood("concerned");
        setSpeechBubble("Connection lost. Reconnecting...");

        // Reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, 3000);
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setIsConnected(false);
        setMood("concerned");
      };
    } catch (error) {
      console.error("Error connecting to WebSocket:", error);
      setIsConnected(false);
    }
  };

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case "welcome":
        console.log("Welcome message:", data.message);
        break;

      case "insights":
        handleInsights(data.data);
        break;

      case "comic_response":
        handleComicResponse(data.data);
        break;

      case "health_update":
        handleHealthUpdate(data.data);
        break;

      case "error":
        console.error("Server error:", data.message);
        setMood("concerned");
        setSpeechBubble("Oops! Something went wrong. Let me check...");
        break;

      default:
        console.log("Unknown message type:", data.type);
    }
  };

  const handleInsights = (insightsData) => {
    if (insightsData && insightsData.insights) {
      setInsights(insightsData.insights);

      // Update mood based on severity
      if (insightsData.severity === "critical") {
        setMood("concerned");
        triggerAnimation("shake");
        setSpeechBubble("🚨 Critical issue detected! Click me for details.");
      } else if (insightsData.severity === "high") {
        setMood("serious");
        triggerAnimation("nod");
        setSpeechBubble("⚠️ Important insights available!");
      } else if (insightsData.severity === "medium") {
        setMood("thinking");
        triggerAnimation("tilt");
        setSpeechBubble("💡 Some interesting findings to share!");
      } else {
        setMood("cheerful");
        triggerAnimation("bounce");
        setSpeechBubble("✅ Everything looks good!");
      }
    }
  };

  const handleComicResponse = (responseData) => {
    if (responseData && responseData.message) {
      setSpeechBubble(responseData.message);

      // Update mood based on response
      if (responseData.mood) {
        setMood(responseData.mood);
      }

      // Trigger appropriate animation
      if (responseData.animation) {
        triggerAnimation(responseData.animation);
      }
    }
  };

  const handleHealthUpdate = (healthData) => {
    if (healthData && healthData.status === "healthy") {
      setMood("cheerful");
    } else {
      setMood("concerned");
    }
  };

  const sendContextUpdate = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const message = {
        type: "context_update",
        context: {
          ...context,
          userRole: userRole,
          timestamp: new Date().toISOString(),
        },
      };

      wsRef.current.send(JSON.stringify(message));
    }
  };

  const triggerAnimation = (animationType) => {
    if (isAnimating) return;

    setIsAnimating(true);

    // Clear any existing animation timeout
    if (animationTimeoutRef.current) {
      clearTimeout(animationTimeoutRef.current);
    }

    // Set animation timeout
    animationTimeoutRef.current = setTimeout(() => {
      setIsAnimating(false);
    }, 1000);
  };

  const handleAvatarClick = () => {
    if (insights.length > 0) {
      onInsightClick(insights);
    }

    // Toggle overlay
    setShowOverlay(!showOverlay);
    onOverlayToggle(!showOverlay);

    // Send interaction event
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const message = {
        type: "avatar_interaction",
        interaction: "click",
        context: context,
      };

      wsRef.current.send(JSON.stringify(message));
    }

    // Trigger click animation
    triggerAnimation("jump");
  };

  const handleRoleChange = (newRole) => {
    setUserRole(newRole);
    setSpeechBubble(`Switched to ${newRole} mode!`);
    triggerAnimation("dance");
  };

  return (
    <div className={`frenly-avatar-container ${className}`}>
      {/* Speech Bubble */}
      {speechBubble && (
        <div className={`speech-bubble ${isAnimating ? "animating" : ""}`}>
          <div className="speech-content">{speechBubble}</div>
          <div className="speech-arrow"></div>
        </div>
      )}

      {/* Avatar */}
      <div
        className={`frenly-avatar ${mood} ${isAnimating ? "animating" : ""} ${!isConnected ? "disconnected" : ""}`}
        onClick={handleAvatarClick}
        title="Click for insights!"
      >
        {/* Custom Avatar Image */}
        <div className="avatar-image">
          <img
            src="/IMG_E948BB7DF6B1-1.jpeg"
            alt="Frenly AI Avatar"
            onError={(e) => {
              e.target.style.display = "none";
              e.target.nextSibling.style.display = "block";
            }}
          />
          {/* Fallback Emoji Avatar */}
          <div className="emoji-avatar" style={{ display: "none" }}>
            {mood === "idle" && "🤖"}
            {mood === "concerned" && "😟"}
            {mood === "cheerful" && "😊"}
            {mood === "serious" && "😐"}
            {mood === "excited" && "🤩"}
            {mood === "thinking" && "🤔"}
          </div>
        </div>

        {/* Status Indicator */}
        <div
          className={`status-indicator ${isConnected ? "connected" : "disconnected"}`}
        >
          {isConnected ? "🟢" : "🔴"}
        </div>

        {/* Mood Expression Overlay */}
        <div className={`mood-overlay ${mood}`}>
          {mood === "concerned" && "😟"}
          {mood === "cheerful" && "😊"}
          {mood === "serious" && "😐"}
          {mood === "excited" && "🤩"}
          {mood === "thinking" && "🤔"}
        </div>
      </div>

      {/* Role Selector */}
      <div className="role-selector">
        <select
          value={userRole}
          onChange={(e) => handleRoleChange(e.target.value)}
          className="role-dropdown"
        >
          <option value="user">👤 User</option>
          <option value="management">👔 Management</option>
          <option value="auditor">🔍 Auditor</option>
          <option value="legal">⚖️ Legal</option>
          <option value="developer">💻 Developer</option>
        </select>
      </div>

      {/* Connection Status */}
      <div className="connection-status">
        {isConnected ? "Connected" : "Disconnected"}
      </div>
    </div>
  );
};

export default FrenlyAvatar;

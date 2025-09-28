import React, { useState, useEffect } from "react";
import FrenlyAvatar from "./components/FrenlyAvatar";
import MultiRoleOverlay from "./components/MultiRoleOverlay";
import "./App.css";
function App() {
  const [context, setContext] = useState({
    page: "/dashboard",
    type: "dashboard",
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString(),
  });
  const [insights, setInsights] = useState([]);
  const [showOverlay, setShowOverlay] = useState(false);
  const [userRole, setUserRole] = useState("user");
  useEffect(() => {
    const interval = setInterval(() => {
      setContext((prev) => ({ ...prev, timestamp: new Date().toISOString() }));
    }, 30000);
    return () => clearInterval(interval);
  }, []);
  const handleInsightClick = (newInsights) => {
    setInsights(newInsights);
  };
  const handleOverlayToggle = (isVisible) => {
    setShowOverlay(isVisible);
  };
  const handleRoleChange = (newRole) => {
    setUserRole(newRole);
  };
  return (
    <div className="App">
      {" "}
      <header className="App-header">
        {" "}
        <h1>🤖 Frenly AI Demo</h1>{" "}
        <p>Your intelligent comic character assistant</p>{" "}
      </header>{" "}
      <main className="App-main">
        {" "}
        <div className="demo-content">
          {" "}
          <h2>Welcome to Frenly AI!</h2>{" "}
          <p>
            Frenly AI is your intelligent comic character assistant that
            provides:
          </p>{" "}
          <ul>
            {" "}
            <li>🎯 Context-aware insights</li>{" "}
            <li>👥 Multi-role perspectives</li> <li>🔍 Real-time analysis</li>{" "}
            <li>🤖 Comic character personality</li>{" "}
            <li>⚡ Live WebSocket communication</li>{" "}
          </ul>{" "}
          <div className="current-context">
            {" "}
            <h3>Current Context:</h3>{" "}
            <pre>{JSON.stringify(context, null, 2)}</pre>{" "}
          </div>{" "}
        </div>{" "}
      </main>{" "}
      {/* Frenly AI Avatar */}{" "}
      <FrenlyAvatar
        context={context}
        onInsightClick={handleInsightClick}
        onOverlayToggle={handleOverlayToggle}
      />{" "}
      {/* Multi-Role Overlay */}{" "}
      <MultiRoleOverlay
        insights={insights}
        userRole={userRole}
        isVisible={showOverlay}
        onClose={() => setShowOverlay(false)}
        onRoleChange={handleRoleChange}
      />{" "}
    </div>
  );
}
export default App;

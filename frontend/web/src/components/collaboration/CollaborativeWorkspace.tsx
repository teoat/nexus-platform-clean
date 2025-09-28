#!/usr/bin/env typescript
/**
 * NEXUS Platform - Collaborative Workspace
 * Multi-user collaborative features and real-time editing
 */

import React, { useState, useEffect, useCallback } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";
import Badge from "../ui/Badge";
import Alert from "../ui/Alert";
import { useWebSocket } from "../../services/websocketService";
import { useAuthStore } from "../../store/authStore";
import { User as AuthUser } from "../../store/authStore";

interface User extends AuthUser {
  avatar?: string;
  status: "online" | "away" | "busy" | "offline";
  lastSeen: number;
  currentActivity?: string;
}

interface CollaborationSession {
  id: string;
  name: string;
  description: string;
  participants: User[];
  owner: User;
  createdAt: number;
  lastActivity: number;
  isActive: boolean;
}

interface ChatMessage {
  id: string;
  userId: string;
  username: string;
  message: string;
  timestamp: number;
  type: "text" | "system" | "file" | "action";
  metadata?: any;
}

interface SharedDocument {
  id: string;
  title: string;
  content: string;
  lastModified: number;
  modifiedBy: User;
  version: number;
  collaborators: User[];
}

export const CollaborativeWorkspace: React.FC = () => {
  const [sessions, setSessions] = useState<CollaborationSession[]>([]);
  const [activeSession, setActiveSession] =
    useState<CollaborationSession | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sharedDocuments, setSharedDocuments] = useState<SharedDocument[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { user } = useAuthStore();
  const { isConnected, send, subscribe } = useWebSocket();

  // Load initial data
  useEffect(() => {
    loadCollaborationData();
  }, []);

  // Subscribe to real-time updates
  useEffect(() => {
    if (!isConnected) return;

    const unsubscribeUsers = subscribe("user_status_update", (message: any) => {
      handleUserStatusUpdate(message.data);
    });

    const unsubscribeMessages = subscribe("chat_message", (message: any) => {
      handleChatMessage(message.data);
    });

    const unsubscribeDocuments = subscribe(
      "document_update",
      (message: any) => {
        handleDocumentUpdate(message.data);
      },
    );

    const unsubscribeSessions = subscribe("session_update", (message: any) => {
      handleSessionUpdate(message.data);
    });

    return () => {
      unsubscribeUsers();
      unsubscribeMessages();
      unsubscribeDocuments();
      unsubscribeSessions();
    };
  }, [isConnected, subscribe]);

  // Load collaboration data
  const loadCollaborationData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Mock data - replace with actual API calls
      const mockSessions: CollaborationSession[] = [
        {
          id: "1",
          name: "Financial Planning Session",
          description: "Q1 2024 financial planning and budgeting",
          participants: [
            {
              id: "1",
              username: "john_doe",
              email: "john@example.com",
              full_name: "John Doe",
              is_active: true,
              role: "admin" as const,
              created_at: new Date().toISOString(),
              status: "online",
              lastSeen: Date.now(),
            },
            {
              id: "2",
              username: "jane_smith",
              email: "jane@example.com",
              full_name: "Jane Smith",
              is_active: true,
              role: "user" as const,
              created_at: new Date().toISOString(),
              status: "away",
              lastSeen: Date.now() - 300000,
            },
          ],
          owner: {
            id: "1",
            username: "john_doe",
            email: "john@example.com",
            full_name: "John Doe",
            is_active: true,
            role: "admin" as const,
            created_at: new Date().toISOString(),
            status: "online",
            lastSeen: Date.now(),
          },
          createdAt: Date.now() - 86400000,
          lastActivity: Date.now() - 3600000,
          isActive: true,
        },
      ];

      const mockUsers: User[] = [
        {
          id: "1",
          username: "john_doe",
          email: "john@example.com",
          full_name: "John Doe",
          is_active: true,
          role: "admin" as const,
          created_at: new Date().toISOString(),
          status: "online",
          lastSeen: Date.now(),
        },
        {
          id: "2",
          username: "jane_smith",
          email: "jane@example.com",
          full_name: "Jane Smith",
          is_active: true,
          role: "user" as const,
          created_at: new Date().toISOString(),
          status: "away",
          lastSeen: Date.now() - 300000,
        },
        {
          id: "3",
          username: "bob_wilson",
          email: "bob@example.com",
          full_name: "Bob Wilson",
          is_active: true,
          role: "user" as const,
          created_at: new Date().toISOString(),
          status: "offline",
          lastSeen: Date.now() - 3600000,
        },
      ];

      const mockMessages: ChatMessage[] = [
        {
          id: "1",
          userId: "1",
          username: "john_doe",
          message: "Welcome to the financial planning session!",
          timestamp: Date.now() - 3600000,
          type: "text",
        },
        {
          id: "2",
          userId: "2",
          username: "jane_smith",
          message:
            "Thanks for setting this up. Let's start with the budget review.",
          timestamp: Date.now() - 3500000,
          type: "text",
        },
      ];

      setSessions(mockSessions);
      setUsers(mockUsers);
      setMessages(mockMessages);
    } catch (err) {
      setError("Failed to load collaboration data");
      console.error("Error loading collaboration data:", err);
    } finally {
      setLoading(false);
    }
  };

  // Handle real-time updates
  const handleUserStatusUpdate = useCallback((data: any) => {
    setUsers((prev) =>
      prev.map((user) =>
        user.id === data.userId ? { ...user, ...data } : user,
      ),
    );
  }, []);

  const handleChatMessage = useCallback((data: any) => {
    setMessages((prev) => [...prev, data]);
  }, []);

  const handleDocumentUpdate = useCallback((data: any) => {
    setSharedDocuments((prev) =>
      prev.map((doc) =>
        doc.id === data.documentId ? { ...doc, ...data } : doc,
      ),
    );
  }, []);

  const handleSessionUpdate = useCallback((data: any) => {
    setSessions((prev) =>
      prev.map((session) =>
        session.id === data.sessionId ? { ...session, ...data } : session,
      ),
    );
  }, []);

  // Send chat message
  const sendMessage = useCallback(() => {
    if (!newMessage.trim() || !activeSession) return;

    const message: ChatMessage = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      userId: user?.id || "unknown",
      username: user?.username || "Unknown",
      message: newMessage.trim(),
      timestamp: Date.now(),
      type: "text",
    };

    if (isConnected) {
      send({
        type: "chat_message",
        data: { sessionId: activeSession.id, message },
      });
    }

    setMessages((prev) => [...prev, message]);
    setNewMessage("");
  }, [newMessage, activeSession, user, isConnected, send]);

  // Join session
  const joinSession = useCallback(
    (sessionId: string) => {
      const session = sessions.find((s) => s.id === sessionId);
      if (session) {
        setActiveSession(session);

        if (isConnected) {
          send({ type: "join_session", data: { sessionId } });
        }
      }
    },
    [sessions, isConnected, send],
  );

  // Leave session
  const leaveSession = useCallback(() => {
    if (activeSession && isConnected) {
      send({ type: "leave_session", data: { sessionId: activeSession.id } });
    }
    setActiveSession(null);
  }, [activeSession, isConnected, send]);

  // Create new session
  const createSession = useCallback(
    (name: string, description: string) => {
      const extendedUser: User | null = user
        ? {
            ...user,
            avatar: undefined,
            status: "online" as const,
            lastSeen: Date.now(),
            currentActivity: undefined,
          }
        : null;

      const newSession: CollaborationSession = {
        id: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        name,
        description,
        participants: extendedUser ? [extendedUser] : [],
        owner: extendedUser || {
          id: "unknown",
          username: "Unknown",
          email: "",
          full_name: "Unknown",
          is_active: false,
          role: "user" as const,
          created_at: new Date().toISOString(),
          avatar: undefined,
          status: "offline" as const,
          lastSeen: 0,
        },
        createdAt: Date.now(),
        lastActivity: Date.now(),
        isActive: true,
      };

      setSessions((prev) => [newSession, ...prev]);
      setActiveSession(newSession);

      if (isConnected) {
        send({
          type: "create_session",
          data: JSON.parse(JSON.stringify(newSession)),
        });
      }
    },
    [user, isConnected, send],
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading collaboration workspace...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Collaborative Workspace
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Real-time collaboration and communication
          </p>
        </div>
        <div className="flex space-x-3">
          <Badge color={isConnected ? "success" : "error"}>
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
          <Button
            onClick={() =>
              createSession("New Session", "Collaborative session")
            }
          >
            New Session
          </Button>
        </div>
      </div>

      {error && (
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sessions List */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Active Sessions
          </h3>
          {sessions.map((session) => (
            <Card
              key={session.id}
              className={`p-4 cursor-pointer transition-all hover:shadow-lg ${
                activeSession?.id === session.id ? "ring-2 ring-blue-500" : ""
              }`}
              onClick={() => joinSession(session.id)}
            >
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-medium text-gray-900 dark:text-white">
                  {session.name}
                </h4>
                <Badge color={session.isActive ? "success" : "secondary"}>
                  {session.isActive ? "Active" : "Inactive"}
                </Badge>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                {session.description}
              </p>
              <div className="flex items-center space-x-2">
                <div className="flex -space-x-2">
                  {session.participants.slice(0, 3).map((participant) => (
                    <div
                      key={participant.id}
                      className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center text-xs font-medium"
                    >
                      {participant.username.charAt(0).toUpperCase()}
                    </div>
                  ))}
                  {session.participants.length > 3 && (
                    <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center text-xs font-medium">
                      +{session.participants.length - 3}
                    </div>
                  )}
                </div>
                <span className="text-sm text-gray-500">
                  {session.participants.length} participants
                </span>
              </div>
            </Card>
          ))}
        </div>

        {/* Chat Area */}
        <div className="lg:col-span-2 space-y-4">
          {activeSession ? (
            <>
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {activeSession.name}
                </h3>
                <Button variant="outlined" onClick={leaveSession}>
                  Leave Session
                </Button>
              </div>

              {/* Messages */}
              <Card className="p-4 h-96 overflow-y-auto">
                <div className="space-y-3">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${
                        message.userId === user?.id
                          ? "justify-end"
                          : "justify-start"
                      }`}
                    >
                      <div
                        className={`max-w-xs px-3 py-2 rounded-lg ${
                          message.userId === user?.id
                            ? "bg-blue-600 text-white"
                            : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white"
                        }`}
                      >
                        <p className="text-sm font-medium">
                          {message.username}
                        </p>
                        <p className="text-sm">{message.message}</p>
                        <p className="text-xs opacity-70 mt-1">
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Message Input */}
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && sendMessage()}
                  placeholder="Type a message..."
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
                <Button onClick={sendMessage} disabled={!newMessage.trim()}>
                  Send
                </Button>
              </div>
            </>
          ) : (
            <Card className="p-8 text-center">
              <div className="text-gray-400 text-6xl mb-4">💬</div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                No Active Session
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Join a session or create a new one to start collaborating
              </p>
              <Button
                onClick={() =>
                  createSession("New Session", "Collaborative session")
                }
              >
                Create New Session
              </Button>
            </Card>
          )}
        </div>
      </div>

      {/* Online Users */}
      <Card className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Online Users
        </h3>
        <div className="flex flex-wrap gap-2">
          {users.map((user) => (
            <div
              key={user.id}
              className="flex items-center space-x-2 px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg"
            >
              <div
                className={`w-3 h-3 rounded-full ${
                  user.status === "online"
                    ? "bg-green-500"
                    : user.status === "away"
                      ? "bg-yellow-500"
                      : user.status === "busy"
                        ? "bg-red-500"
                        : "bg-gray-400"
                }`}
              />
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {user.username}
              </span>
              {user.currentActivity && (
                <span className="text-xs text-gray-500">
                  {user.currentActivity}
                </span>
              )}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default CollaborativeWorkspace;

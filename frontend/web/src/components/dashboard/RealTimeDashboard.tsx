#!/usr/bin/env typescript
/**
 * NEXUS Platform - Real-Time Dashboard
 * Live data visualization and monitoring dashboard
 */

import React, { useState, useEffect, useCallback } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";
import Badge from "../ui/Badge";
import Alert from "../ui/Alert";
import { useWebSocket } from "../../services/websocketService";
import { useNotifications } from "../../services/notificationService";
import { usePerformanceMonitoring } from "../../services/performanceService";
import { useCache } from "../../services/cacheService";
import { useSecurity } from "../../services/securityService";
import { useMonitoringStore } from "../../store/monitoringStore";

interface RealTimeData {
  transactions: {
    count: number;
    total: number;
    recent: Array<{
      id: string;
      amount: number;
      description: string;
      timestamp: number;
    }>;
  };
  accounts: {
    count: number;
    totalBalance: number;
    recentActivity: Array<{
      id: string;
      name: string;
      balance: number;
      change: number;
    }>;
  };
  users: {
    active: number;
    total: number;
    recentLogins: Array<{
      id: string;
      username: string;
      timestamp: number;
    }>;
  };
  system: {
    performance: number;
    memory: number;
    uptime: number;
    errors: number;
  };
}

export const RealTimeDashboard: React.FC = () => {
  const [data, setData] = useState<RealTimeData>({
    transactions: { count: 0, total: 0, recent: [] },
    accounts: { count: 0, totalBalance: 0, recentActivity: [] },
    users: { active: 0, total: 0, recentLogins: [] },
    system: { performance: 100, memory: 0, uptime: 0, errors: 0 },
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Hooks
  const { isConnected, send, subscribe } = useWebSocket();
  const { notifications, unreadCount } = useNotifications();
  const { score } = usePerformanceMonitoring();
  const { fetchInsights } = useMonitoringStore();

  // Load initial data
  useEffect(() => {
    loadInitialData();
    fetchInsights();
  }, []);

  // Subscribe to real-time updates
  useEffect(() => {
    if (!isConnected) return;

    const unsubscribeTransactions = subscribe(
      "transaction_update",
      (message: any) => {
        handleTransactionUpdate(message.data);
      },
    );

    const unsubscribeAccounts = subscribe("account_update", (message: any) => {
      handleAccountUpdate(message.data);
    });

    const unsubscribeUsers = subscribe("user_update", (message: any) => {
      handleUserUpdate(message.data);
    });

    const unsubscribeSystem = subscribe("system_update", (message: any) => {
      handleSystemUpdate(message.data);
    });

    return () => {
      unsubscribeTransactions();
      unsubscribeAccounts();
      unsubscribeUsers();
      unsubscribeSystem();
    };
  }, [isConnected, subscribe]);

  // Load initial data
  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Simulate API calls
      await new Promise((resolve) => setTimeout(resolve, 1000));

      setData({
        transactions: {
          count: 1250,
          total: 125000,
          recent: [
            {
              id: "1",
              amount: 150.0,
              description: "Coffee Shop",
              timestamp: Date.now() - 1000,
            },
            {
              id: "2",
              amount: -75.5,
              description: "Grocery Store",
              timestamp: Date.now() - 2000,
            },
            {
              id: "3",
              amount: 2000.0,
              description: "Salary",
              timestamp: Date.now() - 3000,
            },
          ],
        },
        accounts: {
          count: 5,
          totalBalance: 125000,
          recentActivity: [
            { id: "1", name: "Checking", balance: 5000, change: 150 },
            { id: "2", name: "Savings", balance: 120000, change: 2000 },
          ],
        },
        users: {
          active: 25,
          total: 150,
          recentLogins: [
            { id: "1", username: "john_doe", timestamp: Date.now() - 5000 },
            { id: "2", username: "jane_smith", timestamp: Date.now() - 10000 },
          ],
        },
        system: {
          performance: 95,
          memory: 45,
          uptime: 86400,
          errors: 2,
        },
      });

      setLastUpdate(new Date());
    } catch (err) {
      setError("Failed to load dashboard data");
      console.error("Error loading dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  // Handle real-time updates
  const handleTransactionUpdate = useCallback((update: any) => {
    setData((prev) => ({
      ...prev,
      transactions: {
        ...prev.transactions,
        count: prev.transactions.count + 1,
        total: prev.transactions.total + update.amount,
        recent: [update, ...prev.transactions.recent].slice(0, 10),
      },
    }));
    setLastUpdate(new Date());
  }, []);

  const handleAccountUpdate = useCallback((update: any) => {
    setData((prev) => ({
      ...prev,
      accounts: {
        ...prev.accounts,
        totalBalance: update.totalBalance,
        recentActivity: [update, ...prev.accounts.recentActivity].slice(0, 10),
      },
    }));
    setLastUpdate(new Date());
  }, []);

  const handleUserUpdate = useCallback((update: any) => {
    setData((prev) => ({
      ...prev,
      users: {
        ...prev.users,
        active: update.active,
        recentLogins: [update, ...prev.users.recentLogins].slice(0, 10),
      },
    }));
    setLastUpdate(new Date());
  }, []);

  const handleSystemUpdate = useCallback((update: any) => {
    setData((prev) => ({
      ...prev,
      system: {
        ...prev.system,
        ...update,
      },
    }));
    setLastUpdate(new Date());
  }, []);

  // Refresh data
  const refreshData = useCallback(() => {
    loadInitialData();
  }, []);

  // Send test message
  const sendTestMessage = useCallback(() => {
    if (isConnected) {
      send({
        type: "test_message",
        data: { message: "Hello from dashboard!" },
      });
    }
  }, [isConnected, send]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
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
            Real-Time Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </p>
        </div>
        <div className="flex space-x-3">
          <Badge color={isConnected ? "success" : "error"}>
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
          <Button onClick={refreshData} disabled={loading}>
            Refresh
          </Button>
          <Button onClick={sendTestMessage} disabled={!isConnected}>
            Test Connection
          </Button>
        </div>
      </div>

      {error && (
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Transactions */}
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Transactions
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {data.transactions.count.toLocaleString()}
              </p>
              <p className="text-sm text-gray-500">
                ${data.transactions.total.toLocaleString()}
              </p>
            </div>
            <div className="h-12 w-12 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
              <span className="text-blue-600 dark:text-blue-400 text-xl">
                💰
              </span>
            </div>
          </div>
        </Card>

        {/* Accounts */}
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Balance
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                ${data.accounts.totalBalance.toLocaleString()}
              </p>
              <p className="text-sm text-gray-500">
                {data.accounts.count} accounts
              </p>
            </div>
            <div className="h-12 w-12 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
              <span className="text-green-600 dark:text-green-400 text-xl">
                🏦
              </span>
            </div>
          </div>
        </Card>

        {/* Users */}
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Active Users
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {data.users.active}
              </p>
              <p className="text-sm text-gray-500">
                {data.users.total} total users
              </p>
            </div>
            <div className="h-12 w-12 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
              <span className="text-purple-600 dark:text-purple-400 text-xl">
                👥
              </span>
            </div>
          </div>
        </Card>

        {/* System */}
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Performance
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {data.system.performance}%
              </p>
              <p className="text-sm text-gray-500">
                {data.system.memory}MB memory
              </p>
            </div>
            <div className="h-12 w-12 bg-orange-100 dark:bg-orange-900 rounded-full flex items-center justify-center">
              <span className="text-orange-600 dark:text-orange-400 text-xl">
                ⚡
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* Real-time Data */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Transactions */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Transactions</h3>
          <div className="space-y-3">
            {data.transactions.recent.map((transaction) => (
              <div
                key={transaction.id}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
              >
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {transaction.description}
                  </p>
                  <p className="text-sm text-gray-500">
                    {new Date(transaction.timestamp).toLocaleTimeString()}
                  </p>
                </div>
                <p
                  className={`font-bold ${
                    transaction.amount > 0 ? "text-green-600" : "text-red-600"
                  }`}
                >
                  ${Math.abs(transaction.amount).toFixed(2)}
                </p>
              </div>
            ))}
          </div>
        </Card>

        {/* System Metrics */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">System Metrics</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">
                Performance Score
              </span>
              <Badge
                color={
                  score > 80 ? "success" : score > 60 ? "warning" : "error"
                }
              >
                {score}%
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">
                Memory Usage
              </span>
              <span className="font-medium">{data.system.memory}MB</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">Uptime</span>
              <span className="font-medium">
                {Math.floor(data.system.uptime / 3600)}h{" "}
                {Math.floor((data.system.uptime % 3600) / 60)}m
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">Errors</span>
              <Badge color={data.system.errors > 0 ? "error" : "success"}>
                {data.system.errors}
              </Badge>
            </div>
          </div>
        </Card>
      </div>

      {/* Notifications */}
      {unreadCount > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">
            Notifications ({unreadCount})
          </h3>
          <div className="space-y-2">
            {notifications.slice(0, 5).map((notification: any) => (
              <div
                key={notification.id}
                className={`p-3 rounded-lg ${
                  notification.read
                    ? "bg-gray-50 dark:bg-gray-800"
                    : "bg-blue-50 dark:bg-blue-900"
                }`}
              >
                <p className="font-medium text-gray-900 dark:text-white">
                  {notification.title}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {notification.message}
                </p>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default RealTimeDashboard;

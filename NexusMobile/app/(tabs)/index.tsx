import React, { useState, useEffect } from "react";
import {
  View,
  ScrollView,
  RefreshControl,
  StyleSheet,
  Dimensions,
  Alert,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../src/services/apiClient";
import { ThemedText } from "../../components/themed-text";
import { ThemedView } from "../../components/themed-view";
import { MetricCard } from "../../components/metric-card";
import { QuickActions } from "../../components/quick-actions";
import { RecentTransactions } from "../../components/recent-transactions";
import { RiskAlert } from "../../components/risk-alert";
import { useColorScheme } from "../../hooks/use-color-scheme";

const { width } = Dimensions.get("window");

export default function DashboardScreen() {
  const [refreshing, setRefreshing] = useState(false);
  const colorScheme = useColorScheme();

  // Fetch financial metrics
  const {
    data: metrics,
    isLoading: metricsLoading,
    refetch: refetchMetrics,
  } = useQuery({
    queryKey: ["financial-metrics"],
    queryFn: () => apiClient.getFinancialMetrics(),
    enabled: true,
  });

  // Fetch risk metrics
  const { data: riskMetrics, refetch: refetchRisk } = useQuery({
    queryKey: ["risk-metrics"],
    queryFn: () => apiClient.getRiskMetrics(),
    enabled: true,
  });

  // Fetch recent transactions
  const { data: transactions, refetch: refetchTransactions } = useQuery({
    queryKey: ["recent-transactions"],
    queryFn: () => apiClient.getTransactions(undefined, undefined, 10),
    enabled: true,
  });

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      await Promise.all([
        refetchMetrics(),
        refetchRisk(),
        refetchTransactions(),
      ]);
    } catch (error) {
      Alert.alert("Error", "Failed to refresh data");
    } finally {
      setRefreshing(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <ThemedText style={styles.title}>Financial Dashboard</ThemedText>
          <ThemedText style={styles.subtitle}>
            Your financial overview at a glance
          </ThemedText>
        </View>

        {/* Risk Alert */}
        {riskMetrics && riskMetrics.riskLevel !== "low" && (
          <RiskAlert riskMetrics={riskMetrics} />
        )}

        {/* Key Metrics */}
        {metrics && (
          <View style={styles.metricsGrid}>
            <MetricCard
              title="Total Revenue"
              value={formatCurrency(metrics.totalRevenue)}
              trend={metrics.totalRevenue > 0 ? 5.2 : undefined}
              icon="💰"
              color="#4CAF50"
            />
            <MetricCard
              title="Total Expenses"
              value={formatCurrency(metrics.totalExpenses)}
              trend={-2.1}
              icon="💸"
              color="#F44336"
            />
            <MetricCard
              title="Net Income"
              value={formatCurrency(metrics.netIncome)}
              trend={metrics.netIncome > 0 ? 8.3 : undefined}
              icon="📈"
              color="#2196F3"
            />
            <MetricCard
              title="Profit Margin"
              value={formatPercentage(metrics.profitMargin)}
              trend={3.1}
              icon="🎯"
              color="#9C27B0"
            />
          </View>
        )}

        {/* Quick Actions */}
        <QuickActions />

        {/* Recent Transactions */}
        {transactions && <RecentTransactions transactions={transactions} />}

        {/* Loading State */}
        {metricsLoading && (
          <View style={styles.loadingContainer}>
            <ThemedText style={styles.loadingText}>
              Loading your financial data...
            </ThemedText>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f8fafc",
  },
  scrollView: {
    flex: 1,
  },
  header: {
    padding: 20,
    paddingBottom: 10,
  },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#1f2937",
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: "#6b7280",
  },
  metricsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    padding: 20,
    paddingTop: 0,
  },
  loadingContainer: {
    padding: 40,
    alignItems: "center",
  },
  loadingText: {
    fontSize: 16,
    color: "#6b7280",
  },
});

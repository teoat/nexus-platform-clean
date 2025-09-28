import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from "react-native";
import { useRouter } from "expo-router";
import AsyncStorage from "@react-native-async-storage/async-storage";

interface User {
  id: string;
  username: string;
  email: string;
}

interface Account {
  id: string;
  name: string;
  account_type: string;
  balance: number;
  currency: string;
}

interface Transaction {
  id: string;
  amount: number;
  transaction_type: "debit" | "credit";
  description: string;
  category?: string;
  created_at: string;
}

export default function DashboardScreen() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const authData = await AsyncStorage.getItem("auth-storage");
      if (!authData) {
        router.replace("/(auth)/login");
        return;
      }

      const parsed = JSON.parse(authData);
      if (!parsed.state?.isAuthenticated) {
        router.replace("/(auth)/login");
        return;
      }

      setUser(parsed.state.user);
      await Promise.all([
        fetchAccounts(parsed.state.token),
        fetchTransactions(parsed.state.token),
      ]);
    } catch (error) {
      console.error("Error loading data:", error);
      router.replace("/(auth)/login");
    } finally {
      setLoading(false);
    }
  };

  const fetchAccounts = async (token: string) => {
    try {
      const response = await fetch("http://localhost:8001/api/v1/accounts/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAccounts(data);
      }
    } catch (error) {
      console.error("Error fetching accounts:", error);
    }
  };

  const fetchTransactions = async (token: string) => {
    try {
      const response = await fetch(
        "http://localhost:8001/api/v1/transactions/",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (response.ok) {
        const data = await response.json();
        setTransactions(data.slice(0, 5)); // Show only recent 5 transactions
      }
    } catch (error) {
      console.error("Error fetching transactions:", error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  const totalBalance = accounts.reduce(
    (sum, account) => sum + account.balance,
    0,
  );
  const totalIncome = transactions
    .filter((t) => t.transaction_type === "credit")
    .reduce((sum, t) => sum + t.amount, 0);
  const totalExpenses = transactions
    .filter((t) => t.transaction_type === "debit")
    .reduce((sum, t) => sum + t.amount, 0);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#1976d2" />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.welcomeText}>Welcome back,</Text>
        <Text style={styles.usernameText}>{user?.username}</Text>
      </View>

      {/* Summary Cards */}
      <View style={styles.summaryContainer}>
        <View style={styles.summaryCard}>
          <Text style={styles.summaryLabel}>Total Balance</Text>
          <Text style={styles.summaryValue}>
            {formatCurrency(totalBalance)}
          </Text>
        </View>
        <View style={styles.summaryCard}>
          <Text style={styles.summaryLabel}>Total Income</Text>
          <Text style={[styles.summaryValue, styles.incomeValue]}>
            {formatCurrency(totalIncome)}
          </Text>
        </View>
        <View style={styles.summaryCard}>
          <Text style={styles.summaryLabel}>Total Expenses</Text>
          <Text style={[styles.summaryValue, styles.expenseValue]}>
            {formatCurrency(totalExpenses)}
          </Text>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionButtons}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => router.push("/(tabs)/accounts")}
          >
            <Text style={styles.actionButtonText}>View Accounts</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => router.push("/(tabs)/transactions")}
          >
            <Text style={styles.actionButtonText}>View Transactions</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Recent Transactions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Transactions</Text>
        {transactions.length === 0 ? (
          <Text style={styles.emptyText}>No transactions found</Text>
        ) : (
          transactions.map((transaction) => (
            <View key={transaction.id} style={styles.transactionItem}>
              <View style={styles.transactionInfo}>
                <Text style={styles.transactionDescription}>
                  {transaction.description}
                </Text>
                <Text style={styles.transactionDate}>
                  {new Date(transaction.created_at).toLocaleDateString()}
                </Text>
              </View>
              <Text
                style={[
                  styles.transactionAmount,
                  transaction.transaction_type === "credit"
                    ? styles.incomeValue
                    : styles.expenseValue,
                ]}
              >
                {transaction.transaction_type === "credit" ? "+" : "-"}
                {formatCurrency(transaction.amount)}
              </Text>
            </View>
          ))
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  loadingText: {
    marginTop: 10,
    color: "#666",
  },
  header: {
    padding: 20,
    backgroundColor: "#1976d2",
  },
  welcomeText: {
    fontSize: 16,
    color: "#fff",
    opacity: 0.9,
  },
  usernameText: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#fff",
  },
  summaryContainer: {
    flexDirection: "row",
    padding: 20,
    gap: 10,
  },
  summaryCard: {
    flex: 1,
    backgroundColor: "#fff",
    padding: 15,
    borderRadius: 10,
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  summaryLabel: {
    fontSize: 12,
    color: "#666",
    marginBottom: 5,
  },
  summaryValue: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#333",
  },
  incomeValue: {
    color: "#4caf50",
  },
  expenseValue: {
    color: "#f44336",
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#333",
    marginBottom: 15,
  },
  actionButtons: {
    flexDirection: "row",
    gap: 10,
  },
  actionButton: {
    flex: 1,
    backgroundColor: "#1976d2",
    padding: 15,
    borderRadius: 8,
    alignItems: "center",
  },
  actionButtonText: {
    color: "#fff",
    fontWeight: "bold",
  },
  transactionItem: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "#fff",
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  transactionInfo: {
    flex: 1,
  },
  transactionDescription: {
    fontSize: 16,
    fontWeight: "500",
    color: "#333",
  },
  transactionDate: {
    fontSize: 12,
    color: "#666",
    marginTop: 2,
  },
  transactionAmount: {
    fontSize: 16,
    fontWeight: "bold",
  },
  emptyText: {
    textAlign: "center",
    color: "#666",
    fontStyle: "italic",
    marginTop: 20,
  },
});

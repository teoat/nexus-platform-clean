import { create } from "zustand";
import { subscribeWithSelector } from "zustand/middleware";
import { immer } from "zustand/middleware/immer";
export interface Account {
  id: string;
  name: string;
  type: "checking" | "savings" | "credit" | "investment";
  balance: number;
  currency: string;
  status: "active" | "inactive" | "closed";
  created_at: string;
  updated_at: string;
}
export interface Transaction {
  id: string;
  account_id: string;
  amount: number;
  type: "income" | "expense" | "transfer";
  category: string;
  description: string;
  date: string;
  status: "pending" | "completed" | "failed";
  created_at: string;
  updated_at: string;
}
export interface Notification {
  id: string;
  title: string;
  message: string;
  type: "info" | "warning" | "error" | "success";
  read: boolean;
  created_at: string;
}
export interface DashboardData {
  totalBalance: number;
  monthlyIncome: number;
  monthlyExpenses: number;
  netWorth: number;
  accountCount: number;
  transactionCount: number;
  recentTransactions: Transaction[];
  topCategories: Array<{
    category: string;
    amount: number;
    percentage: number;
  }>;
}
export interface AnalyticsData {
  spendingByCategory: Array<{
    category: string;
    amount: number;
    percentage: number;
  }>;
  incomeVsExpenses: Array<{ month: string; income: number; expenses: number }>;
  balanceHistory: Array<{ date: string; balance: number }>;
  trends: { incomeTrend: number; expenseTrend: number; balanceTrend: number };
}
interface AccountState {
  accounts: Account[];
  selectedAccount: Account | null;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
}
interface TransactionState {
  transactions: Transaction[];
  selectedTransaction: Transaction | null;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
  filters: {
    accountId?: string;
    type?: string;
    category?: string;
    dateRange?: { start: string; end: string };
  };
}
interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  loading: boolean;
  error: string | null;
}
interface DashboardState {
  data: DashboardData | null;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
}
interface AnalyticsState {
  data: AnalyticsData | null;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
}
interface RealTimeState {
  isConnected: boolean;
  connectionStatus: "connecting" | "connected" | "disconnected" | "error";
  lastMessage: string | null;
}
type ErrorSection = "accounts" | "transactions" | "notifications" | "dashboard" | "analytics";

interface AppState {
  accounts: AccountState;
  transactions: TransactionState;
  notifications: NotificationState;
  dashboard: DashboardState;
  analytics: AnalyticsState;
  realTime: RealTimeState;
  sidebarOpen: boolean;
  fetchAccounts: () => Promise<void>;
  createAccount: (
    account: Omit<Account, "id" | "created_at" | "updated_at">,
  ) => Promise<void>;
  updateAccount: (id: string, updates: Partial<Account>) => Promise<void>;
  deleteAccount: (id: string) => Promise<void>;
  selectAccount: (account: Account | null) => void;
  fetchTransactions: (filters?: any) => Promise<void>;
  createTransaction: (
    transaction: Omit<Transaction, "id" | "created_at" | "updated_at">,
  ) => Promise<void>;
  updateTransaction: (
    id: string,
    updates: Partial<Transaction>,
  ) => Promise<void>;
  deleteTransaction: (id: string) => Promise<void>;
  selectTransaction: (transaction: Transaction | null) => void;
  setTransactionFilters: (filters: any) => void;
  fetchNotifications: () => Promise<void>;
  markNotificationAsRead: (id: string) => Promise<void>;
  markAllNotificationsAsRead: () => Promise<void>;
  deleteNotification: (id: string) => Promise<void>;
  fetchDashboardData: () => Promise<void>;
  fetchAnalyticsData: () => Promise<void>;
  clearError: (section: ErrorSection) => void;
  reset: () => void;
  setSidebarOpen: (open: boolean) => void;
  setLoading: (loading: boolean) => void;
  addNotification: (
    notification: Omit<Notification, "id" | "created_at">,
  ) => void;
}
const initialAccountState: AccountState = {
  accounts: [],
  selectedAccount: null,
  loading: false,
  error: null,
  lastUpdated: null,
};
const initialTransactionState: TransactionState = {
  transactions: [],
  selectedTransaction: null,
  loading: false,
  error: null,
  lastUpdated: null,
  filters: {},
};
const initialNotificationState: NotificationState = {
  notifications: [],
  unreadCount: 0,
  loading: false,
  error: null,
};
const initialDashboardState: DashboardState = {
  data: null,
  loading: false,
  error: null,
  lastUpdated: null,
};
const initialAnalyticsState: AnalyticsState = {
  data: null,
  loading: false,
  error: null,
  lastUpdated: null,
};
const initialRealTimeState: RealTimeState = {
  isConnected: false,
  connectionStatus: "disconnected",
  lastMessage: null,
};
export const useAppStore = create<AppState>()(
  subscribeWithSelector(
    immer((set, get) => ({
      accounts: initialAccountState,
      transactions: initialTransactionState,
      notifications: initialNotificationState,
      dashboard: initialDashboardState,
      analytics: initialAnalyticsState,
      realTime: initialRealTimeState,
      sidebarOpen: true,
      fetchAccounts: async () => {
        set((state) => {
          state.accounts.loading = true;
          state.accounts.error = null;
        });
        try {
          const mockAccounts: Account[] = [
            {
              id: "1",
              name: "Checking Account",
              type: "checking",
              balance: 5000,
              currency: "USD",
              status: "active",
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            },
          ];
          set((state) => {
            state.accounts.accounts = mockAccounts;
            state.accounts.loading = false;
            state.accounts.lastUpdated = new Date().toISOString();
          });
        } catch (error) {
          set((state) => {
            state.accounts.loading = false;
            state.accounts.error =
              error instanceof Error
                ? error.message
                : "Failed to fetch accounts";
          });
        }
      },
      createAccount: async (accountData) => {
        try {
          const newAccount: Account = {
            ...accountData,
            id: Date.now().toString(),
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          };
          set((state) => {
            state.accounts.accounts.push(newAccount);
          });
        } catch (error) {
          set((state) => {
            state.accounts.error =
              error instanceof Error
                ? error.message
                : "Failed to create account";
          });
        }
      },
      updateAccount: async (id, updates) => {
        try {
          set((state) => {
            const index = state.accounts.accounts.findIndex(
              (acc: Account) => acc.id === id,
            );
            if (index !== -1) {
              state.accounts.accounts[index] = {
                ...state.accounts.accounts[index],
                ...updates,
                updated_at: new Date().toISOString(),
              };
            }
          });
        } catch (error) {
          set((state) => {
            state.accounts.error =
              error instanceof Error
                ? error.message
                : "Failed to update account";
          });
        }
      },
      deleteAccount: async (id) => {
        try {
          set((state) => {
            state.accounts.accounts = state.accounts.accounts.filter(
              (acc: Account) => acc.id !== id,
            );
            if (state.accounts.selectedAccount?.id === id) {
              state.accounts.selectedAccount = null;
            }
          });
        } catch (error) {
          set((state) => {
            state.accounts.error =
              error instanceof Error
                ? error.message
                : "Failed to delete account";
          });
        }
      },
      selectAccount: (account) => {
        set((state) => {
          state.accounts.selectedAccount = account;
        });
      },
      fetchTransactions: async (filters = {}) => {
        set((state) => {
          state.transactions.loading = true;
          state.transactions.error = null;
        });
        try {
          const mockTransactions: Transaction[] = [
            {
              id: "1",
              account_id: "1",
              amount: 100,
              type: "income",
              category: "Salary",
              description: "Monthly salary",
              date: new Date().toISOString(),
              status: "completed",
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            },
          ];
          set((state) => {
            state.transactions.transactions = mockTransactions;
            state.transactions.loading = false;
            state.transactions.lastUpdated = new Date().toISOString();
          });
        } catch (error) {
          set((state) => {
            state.transactions.loading = false;
            state.transactions.error =
              error instanceof Error
                ? error.message
                : "Failed to fetch transactions";
          });
        }
      },
      createTransaction: async (transactionData) => {
        try {
          const newTransaction: Transaction = {
            ...transactionData,
            id: Date.now().toString(),
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          };
          set((state) => {
            state.transactions.transactions.unshift(newTransaction);
          });
        } catch (error) {
          set((state) => {
            state.transactions.error =
              error instanceof Error
                ? error.message
                : "Failed to create transaction";
          });
        }
      },
      updateTransaction: async (id, updates) => {
        try {
          set((state) => {
            const index = state.transactions.transactions.findIndex(
              (t: Transaction) => t.id === id,
            );
            if (index !== -1) {
              state.transactions.transactions[index] = {
                ...state.transactions.transactions[index],
                ...updates,
                updated_at: new Date().toISOString(),
              };
            }
          });
        } catch (error) {
          set((state) => {
            state.transactions.error =
              error instanceof Error
                ? error.message
                : "Failed to update transaction";
          });
        }
      },
      deleteTransaction: async (id) => {
        try {
          set((state) => {
            state.transactions.transactions =
              state.transactions.transactions.filter(
                (t: Transaction) => t.id !== id,
              );
            if (state.transactions.selectedTransaction?.id === id) {
              state.transactions.selectedTransaction = null;
            }
          });
        } catch (error) {
          set((state) => {
            state.transactions.error =
              error instanceof Error
                ? error.message
                : "Failed to delete transaction";
          });
        }
      },
      selectTransaction: (transaction) => {
        set((state) => {
          state.transactions.selectedTransaction = transaction;
        });
      },
      setTransactionFilters: (filters) => {
        set((state) => {
          state.transactions.filters = filters;
        });
      },
      fetchNotifications: async () => {
        set((state) => {
          state.notifications.loading = true;
          state.notifications.error = null;
        });
        try {
          const mockNotifications: Notification[] = [
            {
              id: "1",
              title: "Welcome!",
              message: "Welcome to NEXUS Platform",
              type: "info",
              read: false,
              created_at: new Date().toISOString(),
            },
          ];
          set((state) => {
            state.notifications.notifications = mockNotifications;
            state.notifications.unreadCount = mockNotifications.filter(
              (n: Notification) => !n.read,
            ).length;
            state.notifications.loading = false;
          });
        } catch (error) {
          set((state) => {
            state.notifications.loading = false;
            state.notifications.error =
              error instanceof Error
                ? error.message
                : "Failed to fetch notifications";
          });
        }
      },
      markNotificationAsRead: async (id) => {
        try {
          set((state) => {
            const notification = state.notifications.notifications.find(
              (n: Notification) => n.id === id,
            );
            if (notification) {
              notification.read = true;
              state.notifications.unreadCount = Math.max(
                0,
                state.notifications.unreadCount - 1,
              );
            }
          });
        } catch (error) {
          set((state) => {
            state.notifications.error =
              error instanceof Error
                ? error.message
                : "Failed to mark notification as read";
          });
        }
      },
      markAllNotificationsAsRead: async () => {
        try {
          set((state) => {
            state.notifications.notifications.forEach(
              (n: Notification) => (n.read = true),
            );
            state.notifications.unreadCount = 0;
          });
        } catch (error) {
          set((state) => {
            state.notifications.error =
              error instanceof Error
                ? error.message
                : "Failed to mark all notifications as read";
          });
        }
      },
      deleteNotification: async (id) => {
        try {
          set((state) => {
            const notification = state.notifications.notifications.find(
              (n: Notification) => n.id === id,
            );
            if (notification && !notification.read) {
              state.notifications.unreadCount = Math.max(
                0,
                state.notifications.unreadCount - 1,
              );
            }
            state.notifications.notifications =
              state.notifications.notifications.filter(
                (n: Notification) => n.id !== id,
              );
          });
        } catch (error) {
          set((state) => {
            state.notifications.error =
              error instanceof Error
                ? error.message
                : "Failed to delete notification";
          });
        }
      },
      fetchDashboardData: async () => {
        set((state) => {
          state.dashboard.loading = true;
          state.dashboard.error = null;
        });
        try {
          const mockDashboardData: DashboardData = {
            totalBalance: 50000,
            monthlyIncome: 8000,
            monthlyExpenses: 6000,
            netWorth: 45000,
            accountCount: 3,
            transactionCount: 25,
            recentTransactions: [],
            topCategories: [
              { category: "Food", amount: 1200, percentage: 20 },
              { category: "Transport", amount: 800, percentage: 13.3 },
            ],
          };
          set((state) => {
            state.dashboard.data = mockDashboardData;
            state.dashboard.loading = false;
            state.dashboard.lastUpdated = new Date().toISOString();
          });
        } catch (error) {
          set((state) => {
            state.dashboard.loading = false;
            state.dashboard.error =
              error instanceof Error
                ? error.message
                : "Failed to fetch dashboard data";
          });
        }
      },
      fetchAnalyticsData: async () => {
        set((state) => {
          state.analytics.loading = true;
          state.analytics.error = null;
        });
        try {
          const mockAnalyticsData: AnalyticsData = {
            spendingByCategory: [
              { category: "Food", amount: 1200, percentage: 20 },
              { category: "Transport", amount: 800, percentage: 13.3 },
            ],
            incomeVsExpenses: [
              { month: "Jan", income: 8000, expenses: 6000 },
              { month: "Feb", income: 8200, expenses: 5800 },
            ],
            balanceHistory: [
              { date: "2024-01-01", balance: 45000 },
              { date: "2024-01-02", balance: 45200 },
            ],
            trends: { incomeTrend: 2.5, expenseTrend: -3.3, balanceTrend: 4.4 },
          };
          set((state) => {
            state.analytics.data = mockAnalyticsData;
            state.analytics.loading = false;
            state.analytics.lastUpdated = new Date().toISOString();
          });
        } catch (error) {
          set((state) => {
            state.analytics.loading = false;
            state.analytics.error =
              error instanceof Error
                ? error.message
                : "Failed to fetch analytics data";
          });
        }
      },
      clearError: (section: ErrorSection) => {
        set((state) => {
          (state[section] as any).error = null;
        });
      },
      reset: () => {
        set((state) => {
          state.accounts = initialAccountState;
          state.transactions = initialTransactionState;
          state.notifications = initialNotificationState;
          state.dashboard = initialDashboardState;
          state.analytics = initialAnalyticsState;
          state.realTime = initialRealTimeState;
        });
      },
      setSidebarOpen: (open: boolean) => {
        set((state) => {
          state.sidebarOpen = open;
        });
      },
      setLoading: (loading: boolean) => {
        set((state) => {
          state.accounts.loading = loading;
          state.transactions.loading = loading;
          state.notifications.loading = loading;
          state.dashboard.loading = loading;
          state.analytics.loading = loading;
        });
      },
      addNotification: (
        notification: Omit<Notification, "id" | "created_at">,
      ) => {
        set((state) => {
          const newNotification: Notification = {
            ...notification,
            id: Date.now().toString(),
            created_at: new Date().toISOString(),
          };
          state.notifications.notifications.unshift(newNotification);
          state.notifications.unreadCount += 1;
        });
      },
    })),
  ),
);

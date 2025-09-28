import * as Notifications from "expo-notifications";
import { Platform } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
interface NotificationData {
  title: string;
  body: string;
  data?: any;
  sound?: boolean;
  priority?: "default" | "high" | "low";
}
class NotificationService {
  private initialized = false;
  async initialize() {
    if (this.initialized) return;
    Notifications.setNotificationHandler({
      handleNotification: async () => ({
        shouldShowAlert: true,
        shouldPlaySound: true,
        shouldSetBadge: true,
        shouldShowBanner: true,
        shouldShowList: true,
      }),
    });
    const { status: existingStatus } =
      await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    if (existingStatus !== "granted") {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    if (finalStatus !== "granted") {
      console.log(
        "Failed to get push notification token for push notification!",
      );
      return;
    }
    const token = await Notifications.getExpoPushTokenAsync();
    console.log("Push notification token:", token.data);
    await AsyncStorage.setItem("expo-push-token", token.data);
    this.initialized = true;
  }
  async scheduleNotification(data: NotificationData, delayInSeconds = 0) {
    await this.initialize();
    const trigger: any = delayInSeconds > 0 ? { seconds: delayInSeconds } : null;
    await Notifications.scheduleNotificationAsync({
      content: {
        title: data.title,
        body: data.body,
        data: data.data || {},
        sound: data.sound !== false,
        priority: data.priority || "default",
      },
      trigger,
    });
  }
  async sendTransactionAlert(
    amount: number,
    type: "credit" | "debit",
    description: string,
  ) {
    const title =
      type === "credit" ? "💰 Money Received" : "💸 Transaction Made";
    const formattedAmount = new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(Math.abs(amount));
    await this.scheduleNotification({
      title,
      body: `${type === "credit" ? "+" : "-"}${formattedAmount} - ${description}`,
      data: { type: "transaction", amount, transactionType: type },
      priority: "high",
    });
  }
  async sendRiskAlert(riskLevel: string, message: string) {
    const title = `🚨 Risk Alert - ${riskLevel.toUpperCase()}`;
    await this.scheduleNotification({
      title,
      body: message,
      data: { type: "risk", riskLevel },
      priority: "high",
    });
  }
  async sendBudgetAlert(category: string, spent: number, budget: number) {
    const percentage = (spent / budget) * 100;
    const title = "⚠️ Budget Alert";
    const body = `${category} budget: ${percentage.toFixed(1)}% used (${spent}/${budget})`;
    await this.scheduleNotification({
      title,
      body,
      data: { type: "budget", category, spent, budget },
      priority: "high",
    });
  }
  async sendWeeklySummary(
    totalIncome: number,
    totalExpenses: number,
    netIncome: number,
  ) {
    const title = "📊 Weekly Financial Summary";
    const body = `Income: $${totalIncome.toLocaleString()}, Expenses: $${totalExpenses.toLocaleString()}, Net: $${netIncome.toLocaleString()}`;
    await this.scheduleNotification({
      title,
      body,
      data: { type: "summary", totalIncome, totalExpenses, netIncome },
      priority: "default",
    });
  }
  async sendGoalReminder(
    goalName: string,
    currentAmount: number,
    targetAmount: number,
  ) {
    const progress = (currentAmount / targetAmount) * 100;
    const title = "🎯 Goal Reminder";
    const body = `${goalName}: ${progress.toFixed(1)}% complete ($${currentAmount.toLocaleString()} / $${targetAmount.toLocaleString()})`;
    await this.scheduleNotification({
      title,
      body,
      data: { type: "goal", goalName, currentAmount, targetAmount },
      priority: "default",
    });
  }
  async cancelAllNotifications() {
    await Notifications.cancelAllScheduledNotificationsAsync();
  }
  async getScheduledNotifications() {
    return await Notifications.getAllScheduledNotificationsAsync();
  }
  async getNotificationSettings() {
    const settings = await Notifications.getPermissionsAsync();
    return {
      granted: settings.status === "granted",
      allowsAlert: settings.granted ?? true,
      allowsSound: settings.granted ?? true,
      allowsBadge: settings.granted ?? true,
    };
  }
  setupNotificationListener(
    onNotificationReceived?: (notification: Notifications.Notification) => void,
  ) {
    const subscription = Notifications.addNotificationReceivedListener(
      (notification) => {
        console.log("Notification received:", notification);
        if (onNotificationReceived) {
          onNotificationReceived(notification);
        }
      },
    );
    return subscription;
  }
  setupNotificationResponseListener(
    onResponse?: (response: Notifications.NotificationResponse) => void,
  ) {
    const subscription = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        console.log("Notification response:", response);
        if (onResponse) {
          onResponse(response);
        }
      },
    );
    return subscription;
  }
}
export const notificationService = new NotificationService();
export default notificationService;

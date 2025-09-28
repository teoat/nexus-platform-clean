import AsyncStorage from "@react-native-async-storage/async-storage";
import NetInfo from "@react-native-community/netinfo";
import { apiClient } from "./apiClient";
interface CachedData<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
}
interface SyncQueueItem {
  id: string;
  type: "create" | "update" | "delete";
  endpoint: string;
  data?: any;
  timestamp: number;
}
class OfflineManager {
  private readonly CACHE_PREFIX = "nexus_cache_";
  private readonly SYNC_QUEUE_KEY = "nexus_sync_queue";
  private readonly CACHE_DURATION = 30 * 60 * 1000;
  async cacheData<T>(key: string, data: T): Promise<void> {
    try {
      const cacheEntry: CachedData<T> = {
        data,
        timestamp: Date.now(),
        expiresAt: Date.now() + this.CACHE_DURATION,
      };
      await AsyncStorage.setItem(
        this.CACHE_PREFIX + key,
        JSON.stringify(cacheEntry),
      );
    } catch (error) {
      console.error("Error caching data:", error);
    }
  }
  async getCachedData<T>(key: string): Promise<T | null> {
    try {
      const cached = await AsyncStorage.getItem(this.CACHE_PREFIX + key);
      if (!cached) return null;
      const cacheEntry: CachedData<T> = JSON.parse(cached);
      if (Date.now() > cacheEntry.expiresAt) {
        await this.removeCachedData(key);
        return null;
      }
      return cacheEntry.data;
    } catch (error) {
      console.error("Error getting cached data:", error);
      return null;
    }
  }
  async removeCachedData(key: string): Promise<void> {
    try {
      await AsyncStorage.removeItem(this.CACHE_PREFIX + key);
    } catch (error) {
      console.error("Error removing cached data:", error);
    }
  }
  async addToSyncQueue(
    item: Omit<SyncQueueItem, "id" | "timestamp">,
  ): Promise<void> {
    try {
      const queue = await this.getSyncQueue();
      const newItem: SyncQueueItem = {
        ...item,
        id: Date.now().toString(),
        timestamp: Date.now(),
      };
      queue.push(newItem);
      await AsyncStorage.setItem(this.SYNC_QUEUE_KEY, JSON.stringify(queue));
    } catch (error) {
      console.error("Error adding to sync queue:", error);
    }
  }
  async getSyncQueue(): Promise<SyncQueueItem[]> {
    try {
      const queue = await AsyncStorage.getItem(this.SYNC_QUEUE_KEY);
      return queue ? JSON.parse(queue) : [];
    } catch (error) {
      console.error("Error getting sync queue:", error);
      return [];
    }
  }
  async processSyncQueue(): Promise<void> {
    const isConnected = await this.isOnline();
    if (!isConnected) return;
    const queue = await this.getSyncQueue();
    if (queue.length === 0) return;
    console.log(`Processing ${queue.length} items in sync queue`);
    for (const item of queue) {
      try {
        switch (item.type) {
          case "create":
            await apiClient.post(item.endpoint, item.data);
            break;
          case "update":
            await apiClient.put(item.endpoint, item.data);
            break;
          case "delete":
            await apiClient.delete(item.endpoint);
            break;
        }
        await this.removeFromSyncQueue(item.id);
      } catch (error) {
        console.error(`Failed to sync item ${item.id}:`, error);
      }
    }
  }
  async removeFromSyncQueue(id: string): Promise<void> {
    try {
      const queue = await this.getSyncQueue();
      const filteredQueue = queue.filter((item) => item.id !== id);
      await AsyncStorage.setItem(
        this.SYNC_QUEUE_KEY,
        JSON.stringify(filteredQueue),
      );
    } catch (error) {
      console.error("Error removing from sync queue:", error);
    }
  }
  async isOnline(): Promise<boolean> {
    try {
      const state = await NetInfo.fetch();
      return state.isConnected ?? false;
    } catch (error) {
      console.error("Error checking network status:", error);
      return false;
    }
  }
  async apiCallWithOffline<T>(
    apiCall: () => Promise<T>,
    cacheKey: string,
    queueOnFailure?: Omit<SyncQueueItem, "id" | "timestamp">,
  ): Promise<T> {
    const isConnected = await this.isOnline();
    try {
      const data = await apiCall();
      await this.cacheData(cacheKey, data);
      return data;
    } catch (error) {
      console.log("API call failed, trying cache:", error);
      const cachedData = await this.getCachedData<T>(cacheKey);
      if (cachedData) {
        console.log("Using cached data for:", cacheKey);
        return cachedData;
      }
      if (queueOnFailure && !isConnected) {
        await this.addToSyncQueue(queueOnFailure);
      }
      throw error;
    }
  }
  async clearCache(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter((key) => key.startsWith(this.CACHE_PREFIX));
      await AsyncStorage.multiRemove(cacheKeys);
    } catch (error) {
      console.error("Error clearing cache:", error);
    }
  }
  async getCacheInfo(): Promise<{ size: number; keys: string[] }> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter((key) => key.startsWith(this.CACHE_PREFIX));
      return {
        size: cacheKeys.length,
        keys: cacheKeys.map((key) => key.replace(this.CACHE_PREFIX, "")),
      };
    } catch (error) {
      console.error("Error getting cache info:", error);
      return { size: 0, keys: [] };
    }
  }
}
export const offlineManager = new OfflineManager();
export default offlineManager;

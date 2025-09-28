/**
 * Cache Service
 * Provides caching functionality for the application
 */

interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

class CacheService {
  public cache = new Map<string, CacheItem<any>>();
  private defaultTTL = 5 * 60 * 1000; // 5 minutes

  set<T>(key: string, data: T, ttl?: number): void {
    const item: CacheItem<T> = {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.defaultTTL,
    };
    this.cache.set(key, item);
  }

  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    if (!item) return null;

    const now = Date.now();
    if (now - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  has(key: string): boolean {
    const item = this.cache.get(key);
    if (!item) return false;

    const now = Date.now();
    if (now - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return false;
    }

    return true;
  }

  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  size(): number {
    return this.cache.size;
  }
}

export const cacheService = new CacheService();
export default cacheService;

// React hook for cache service
import { useCallback } from "react";

export const useCache = () => {
  const set = useCallback(<T>(key: string, data: T, ttl?: number) => {
    cacheService.set(key, data, ttl);
  }, []);

  const get = useCallback(<T>(key: string): T | null => {
    return cacheService.get<T>(key);
  }, []);

  const has = useCallback((key: string): boolean => {
    return cacheService.has(key);
  }, []);

  const remove = useCallback((key: string): boolean => {
    return cacheService.delete(key);
  }, []);

  const clear = useCallback(() => {
    cacheService.clear();
  }, []);

  const stats = useCallback(() => {
    return {
      size: cacheService.size(),
      keys: Array.from(cacheService.cache.keys()),
    };
  }, []);

  return {
    set,
    get,
    has,
    remove,
    clear,
    stats,
  };
};

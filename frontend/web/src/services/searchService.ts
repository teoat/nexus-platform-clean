/**
 * NEXUS Platform - Search Service
 * Advanced full-text search across all data types
 */
// No React import needed for service
import { apiClient } from "./apiClient";
import {
  handleApiError,
  ErrorType,
  ErrorSeverity,
} from "../utils/errorHandler";

export interface SearchResult {
  id: string;
  type: "transaction" | "account" | "user" | "file" | "category";
  title: string;
  description: string;
  data: any;
  score: number;
  highlights: string[];
  metadata: {
    created_at: string;
    updated_at?: string;
    tags?: string[];
    category?: string;
  };
}

export interface SearchFilters {
  types?: string[];
  dateRange?: { start: string; end: string };
  categories?: string[];
  tags?: string[];
  accounts?: string[];
  users?: string[];
  amountRange?: { min: number; max: number };
}

export interface SearchOptions {
  limit?: number;
  offset?: number;
  sortBy?: "relevance" | "date" | "title" | "amount";
  sortOrder?: "asc" | "desc";
  includeHighlights?: boolean;
  fuzzy?: boolean;
  exactMatch?: boolean;
}

export interface SearchSuggestion {
  text: string;
  type: "query" | "filter" | "category" | "tag";
  count?: number;
}

export interface SearchStats {
  totalResults: number;
  searchTime: number;
  facets: {
    types: { [key: string]: number };
    categories: { [key: string]: number };
    tags: { [key: string]: number };
    accounts: { [key: string]: number };
    users: { [key: string]: number };
  };
}

interface CacheEntry {
  results: SearchResult[];
  stats: SearchStats;
  timestamp: number;
}

class SearchService {
  private searchCache = new Map<string, CacheEntry>();
  private cacheTimeout = 5 * 60 * 1000; // 5 minutes
  private recentSearches: string[] = [];
  private maxRecentSearches = 10;

  public async search(
    query: string,
    filters: SearchFilters = {},
    options: SearchOptions = {},
  ): Promise<{ results: SearchResult[]; stats: SearchStats }> {
    try {
      const cacheKey = this.generateCacheKey(query, filters, options);
      const cached = this.getCachedResults(cacheKey);
      if (cached) {
        return cached;
      }

      const searchParams: Record<string, string | number | boolean> = {
        q: query,
      };

      const allParams: Record<string, any> = { ...filters, ...options };

      for (const [key, value] of Object.entries(allParams)) {
        if (value === undefined || value === null) {
          continue;
        }

        if (Array.isArray(value)) {
          if (value.length > 0) {
            searchParams[key] = value.join(",");
          }
        } else if (typeof value === "object") {
          for (const [subKey, subValue] of Object.entries(value)) {
            if (subValue !== undefined && subValue !== null) {
              searchParams[`${key}_${subKey}`] = subValue as string | number;
            }
          }
        } else if (value !== "") {
          searchParams[key] = value as string | number | boolean;
        }
      }

      const response = await apiClient.get(
        "/search",
        searchParams as Record<string, unknown>,
      );
      const data = response.data as any;
      const results = {
        results: data.results || [],
        stats: data.stats || {
          totalResults: 0,
          searchTime: 0,
          facets: {
            types: {},
            categories: {},
            tags: {},
            accounts: {},
            users: {},
          },
        },
      };

      this.cacheResults(cacheKey, results);
      this.addToRecentSearches(query);
      return results;
    } catch (error) {
      handleApiError(error);
      throw error;
    }
  }

  public async getSuggestions(
    query: string,
    limit: number = 10,
  ): Promise<SearchSuggestion[]> {
    try {
      if (!query.trim()) {
        return this.getRecentSearches();
      }

      const response = await apiClient.get("/search/suggestions", {
        q: query,
        limit,
      });

      const data = response.data as any;
      return data.suggestions || [];
    } catch (error) {
      handleApiError(error);
      return [];
    }
  }

  public getRecentSearches(): SearchSuggestion[] {
    return this.recentSearches.map((query) => ({
      text: query,
      type: "query" as const,
    }));
  }

  public clearRecentSearches(): void {
    this.recentSearches = [];
  }

  public getSearchHistory(): string[] {
    return [...this.recentSearches];
  }

  public async searchTransactions(
    query: string,
    filters: Partial<SearchFilters> = {},
    options: SearchOptions = {},
  ): Promise<SearchResult[]> {
    const results = await this.search(
      query,
      { ...filters, types: ["transaction"] },
      options,
    );
    return results.results;
  }

  public async searchAccounts(
    query: string,
    filters: Partial<SearchFilters> = {},
    options: SearchOptions = {},
  ): Promise<SearchResult[]> {
    const results = await this.search(
      query,
      { ...filters, types: ["account"] },
      options,
    );
    return results.results;
  }

  public async searchUsers(
    query: string,
    filters: Partial<SearchFilters> = {},
    options: SearchOptions = {},
  ): Promise<SearchResult[]> {
    const results = await this.search(
      query,
      { ...filters, types: ["user"] },
      options,
    );
    return results.results;
  }

  public async searchFiles(
    query: string,
    filters: Partial<SearchFilters> = {},
    options: SearchOptions = {},
  ): Promise<SearchResult[]> {
    const results = await this.search(
      query,
      { ...filters, types: ["file"] },
      options,
    );
    return results.results;
  }

  public async advancedSearch(
    queries: {
      transactions?: string;
      accounts?: string;
      users?: string;
      files?: string;
    },
    filters: SearchFilters = {},
    options: SearchOptions = {},
  ): Promise<{
    transactions: SearchResult[];
    accounts: SearchResult[];
    users: SearchResult[];
    files: SearchResult[];
  }> {
    try {
      const [transactions, accounts, users, files] = await Promise.all([
        queries.transactions
          ? this.searchTransactions(queries.transactions, filters, options)
          : Promise.resolve([]),
        queries.accounts
          ? this.searchAccounts(queries.accounts, filters, options)
          : Promise.resolve([]),
        queries.users
          ? this.searchUsers(queries.users, filters, options)
          : Promise.resolve([]),
        queries.files
          ? this.searchFiles(queries.files, filters, options)
          : Promise.resolve([]),
      ]);

      return {
        transactions,
        accounts,
        users,
        files,
      };
    } catch (error) {
      handleApiError(error);
      throw error;
    }
  }

  public async autocomplete(
    query: string,
    type?: string,
    limit: number = 5,
  ): Promise<SearchSuggestion[]> {
    try {
      const response = await apiClient.get("/search/autocomplete", {
        q: query,
        type,
        limit,
      });

      const data = response.data as any;
      return data.suggestions || [];
    } catch (error) {
      handleApiError(error);
      return [];
    }
  }

  public async getSearchAnalytics(dateRange?: {
    start: string;
    end: string;
  }): Promise<{
    popularQueries: { query: string; count: number }[];
    searchTrends: { date: string; count: number }[];
    topResults: { result: string; clicks: number }[];
  }> {
    try {
      const response = await apiClient.get("/search/analytics", dateRange);
      return response.data as any;
    } catch (error) {
      handleApiError(error);
      return {
        popularQueries: [],
        searchTrends: [],
        topResults: [],
      };
    }
  }

  public buildQueryFromFilters(filters: SearchFilters): string {
    const parts: string[] = [];

    if (filters.categories?.length) {
      parts.push(`category:(${filters.categories.join(" OR ")})`);
    }

    if (filters.tags?.length) {
      parts.push(`tags:(${filters.tags.join(" OR ")})`);
    }

    if (filters.accounts?.length) {
      parts.push(`account:(${filters.accounts.join(" OR ")})`);
    }

    if (filters.users?.length) {
      parts.push(`user:(${filters.users.join(" OR ")})`);
    }

    if (filters.dateRange) {
      parts.push(
        `date:[${filters.dateRange.start} TO ${filters.dateRange.end}]`,
      );
    }

    if (filters.amountRange) {
      parts.push(
        `amount:[${filters.amountRange.min} TO ${filters.amountRange.max}]`,
      );
    }

    return parts.join(" AND ");
  }

  public parseQuery(query: string): {
    text: string;
    filters: SearchFilters;
    operators: string[];
  } {
    const filters: SearchFilters = {};
    const operators: string[] = [];
    let text = query;

    const filterRegex = /(\w+):\(([^)]+)\)/g;
    let match;

    while ((match = filterRegex.exec(query)) !== null) {
      const [, filterType, filterValue] = match;
      const values = filterValue.split(" OR ");

      switch (filterType) {
        case "category": {
          filters.categories = values;
          break;
        }
        case "tags": {
          filters.tags = values;
          break;
        }
        case "account": {
          filters.accounts = values;
          break;
        }
        case "user": {
          filters.users = values;
          break;
        }
        case "date": {
          const dateMatch = filterValue.match(/\[([^ TO]+) TO ([^\]]+)\]/);
          if (dateMatch) {
            filters.dateRange = {
              start: dateMatch[1],
              end: dateMatch[2],
            };
          }
          break;
        }
        case "amount": {
          const amountMatch = filterValue.match(/\[([^ TO]+) TO ([^\]]+)\]/);
          if (amountMatch) {
            filters.amountRange = {
              min: parseFloat(amountMatch[1]),
              max: parseFloat(amountMatch[2]),
            };
          }
          break;
        }
      }

      text = text.replace(match[0], "").trim();
    }

    const operatorRegex = /(AND|OR|NOT)/g;
    while ((match = operatorRegex.exec(query)) !== null) {
      operators.push(match[1]);
    }

    return {
      text: text.trim(),
      filters,
      operators,
    };
  }

  private generateCacheKey(
    query: string,
    filters: SearchFilters,
    options: SearchOptions,
  ): string {
    return JSON.stringify({ query, filters, options });
  }

  private getCachedResults(
    cacheKey: string,
  ): { results: SearchResult[]; stats: SearchStats } | null {
    const cached = this.searchCache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return {
        results: cached.results,
        stats: cached.stats,
      };
    }
    return null;
  }

  private cacheResults(
    cacheKey: string,
    results: { results: SearchResult[]; stats: SearchStats },
  ): void {
    this.searchCache.set(cacheKey, {
      results: results.results,
      stats: results.stats,
      timestamp: Date.now(),
    });

    if (this.searchCache.size > 100) {
      const entries = Array.from(this.searchCache.entries());
      entries.sort((a, b) => b[1].timestamp - a[1].timestamp);
      this.searchCache.clear();
      entries.slice(0, 50).forEach(([key, value]) => {
        this.searchCache.set(key, value);
      });
    }
  }

  private addToRecentSearches(query: string): void {
    if (!query.trim()) return;

    this.recentSearches = this.recentSearches.filter((q) => q !== query);
    this.recentSearches.unshift(query);

    if (this.recentSearches.length > this.maxRecentSearches) {
      this.recentSearches = this.recentSearches.slice(
        0,
        this.maxRecentSearches,
      );
    }
  }
}

export const searchService = new SearchService();

// useSearch hook removed as it's not appropriate for a service file

export default searchService;

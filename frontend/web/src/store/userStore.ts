import { create } from "zustand";
import { User } from "../services/userService";

export interface UserState {
  // User data
  users: User[];
  currentUser: User | null;

  // UI state
  isLoading: boolean;
  error: string | null;

  // Actions
  setUsers: (users: User[]) => void;
  setCurrentUser: (user: User | null) => void;
  addUser: (user: User) => void;
  updateUser: (id: string, updates: Partial<User>) => void;
  removeUser: (id: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  // Initial state
  users: [],
  currentUser: null,

  isLoading: false,
  error: null,

  // Actions
  setUsers: (users) => set({ users }),

  setCurrentUser: (user) => set({ currentUser: user }),

  addUser: (user) =>
    set((state) => ({
      users: [...state.users, user],
    })),

  updateUser: (id, updates) =>
    set((state) => ({
      users: state.users.map((user) =>
        user.id === id ? { ...user, ...updates } : user,
      ),
    })),

  removeUser: (id) =>
    set((state) => ({
      users: state.users.filter((user) => user.id !== id),
    })),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  reset: () =>
    set({
      users: [],
      currentUser: null,
      isLoading: false,
      error: null,
    }),
}));

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  accountService,
  Account,
  AccountCreate,
  AccountUpdate,
} from "../services/accountService";

export const accountKeys = {
  all: ["accounts"] as const,
  lists: () => [...accountKeys.all, "list"] as const,
  list: (filters: string) => [...accountKeys.lists(), { filters }] as const,
  details: () => [...accountKeys.all, "detail"] as const,
  detail: (id: string) => [...accountKeys.details(), id] as const,
  userAccounts: (userId: string) =>
    [...accountKeys.all, "user", userId] as const,
};

export const useAccounts = () => {
  return useQuery(accountKeys.lists(), () => accountService.getAccounts(), {
    staleTime: 5 * 60 * 1000,
    cacheTime: 10 * 60 * 1000,
  });
};

export const useUserAccounts = (userId: string) => {
  return useQuery(
    accountKeys.userAccounts(userId),
    () => accountService.getAccounts(),
    {
      enabled: !!userId,
      staleTime: 5 * 60 * 1000,
    },
  );
};

export const useAccount = (id: string) => {
  return useQuery(
    accountKeys.detail(id),
    () => accountService.getAccountById(id),
    {
      enabled: !!id,
      staleTime: 5 * 60 * 1000,
    },
  );
};

export const useCreateAccount = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: AccountCreate) => accountService.createAccount(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: accountKeys.lists() });
    },
  });
};

export const useUpdateAccount = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: AccountUpdate }) =>
      accountService.updateAccount(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: accountKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: accountKeys.lists() });
    },
  });
};

export const useDeleteAccount = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => accountService.deleteAccount(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: accountKeys.lists() });
    },
  });
};

export const useTransferFunds = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      fromAccountId: string;
      toAccountId: string;
      amount: number;
      description?: string;
    }) =>
      accountService.transferFunds(
        data.fromAccountId,
        data.toAccountId,
        data.amount,
        data.description,
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: accountKeys.detail(variables.fromAccountId),
      });
      queryClient.invalidateQueries({
        queryKey: accountKeys.detail(variables.toAccountId),
      });
      queryClient.invalidateQueries({ queryKey: accountKeys.lists() });
    },
  });
};

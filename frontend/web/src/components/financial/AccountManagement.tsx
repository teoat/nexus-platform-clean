import React, { memo, useState, useMemo, useCallback } from "react";
import {
  CardHeader,
  CardContent,
  Button,
  Badge,
  Input,
  LoadingSpinner,
} from "../../components/ui";
import Card from "../../components/ui/Card";
import { useTranslationHook } from "../../contexts/I18nContext";
import { Account } from "../../services/accountService";

interface AccountManagementProps {
  accounts?: Account[];
  loading?: boolean;
  onAccountClick?: (account: Account) => void;
  onCreateAccount?: () => void;
  onEditAccount?: (account: Account) => void;
  onDeleteAccount?: (accountId: string) => void;
  onTransfer?: (account: Account) => void;
  showActions?: boolean;
}

const AccountManagement: React.FC<AccountManagementProps> = memo(
  ({
    accounts = [],
    loading = false,
    onAccountClick,
    onCreateAccount,
    onEditAccount,
    onDeleteAccount,
    onTransfer,
    showActions = true,
  }) => {
    const { t } = useTranslationHook();
    const formatCurrency = (amount: number) =>
      new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(amount);

    // State for filters
    const [searchTerm, setSearchTerm] = useState("");
    const [statusFilter, setStatusFilter] = useState<string>("all");
    const [typeFilter, setTypeFilter] = useState<string>("all");
    const [riskFilter, setRiskFilter] = useState<string>("all");

    // Filter accounts
    const filteredAccounts = useMemo(() => {
      return accounts.filter((account) => {
        const matchesSearch =
          searchTerm === "" ||
          account.account_name
            .toLowerCase()
            .includes(searchTerm.toLowerCase()) ||
          account.account_number
            .toLowerCase()
            .includes(searchTerm.toLowerCase()) ||
          account.bank_name?.toLowerCase().includes(searchTerm.toLowerCase());

        const matchesStatus =
          statusFilter === "all" ||
          (account.is_active ? "active" : "inactive") === statusFilter;
        const matchesType =
          typeFilter === "all" || account.account_type === typeFilter;
        const matchesRisk = riskFilter === "all" || true; // Risk level not available in accountService

        return matchesSearch && matchesStatus && matchesType && matchesRisk;
      });
    }, [accounts, searchTerm, statusFilter, typeFilter, riskFilter]);

    // Calculate summary statistics
    const summaryStats = useMemo(() => {
      const totalBalance = filteredAccounts.reduce(
        (sum, account) => sum + account.balance,
        0,
      );
      const activeAccounts = filteredAccounts.filter(
        (account) => account.is_active,
      ).length;
      const totalAccounts = filteredAccounts.length;

      const riskDistribution = {
        low: 0, // Risk level not available in accountService
        medium: 0,
        high: 0,
        critical: 0,
      };

      const complianceIssues = filteredAccounts.filter(
        (account) => (account as any).compliance_status !== "compliant",
      ).length;

      return {
        totalBalance,
        activeAccounts,
        totalAccounts,
        riskDistribution,
        complianceIssues,
      };
    }, [filteredAccounts]);

    const getStatusBadgeVariant = useCallback((status: string) => {
      switch (status) {
        case "active":
          return "success";
        case "inactive":
          return "secondary";
        case "suspended":
          return "warning";
        case "closed":
          return "error";
        default:
          return "secondary";
      }
    }, []);

    const getRiskBadgeVariant = useCallback((risk: string) => {
      switch (risk) {
        case "low":
          return "success";
        case "medium":
          return "warning";
        case "high":
          return "error";
        case "critical":
          return "error";
        default:
          return "secondary";
      }
    }, []);

    const getComplianceBadgeVariant = useCallback((status: string) => {
      switch (status) {
        case "compliant":
          return "success";
        case "non_compliant":
          return "error";
        case "pending_review":
          return "warning";
        case "requires_action":
          return "error";
        default:
          return "secondary";
      }
    }, []);

    const handleAccountClick = useCallback(
      (account: Account) => {
        onAccountClick?.(account);
      },
      [onAccountClick],
    );

    const handleEditClick = useCallback(
      (e: React.MouseEvent, account: Account) => {
        e.stopPropagation();
        onEditAccount?.(account);
      },
      [onEditAccount],
    );

    const handleDeleteClick = useCallback(
      (e: React.MouseEvent, accountId: string) => {
        e.stopPropagation();
        if (window.confirm(t("account.confirmDelete"))) {
          onDeleteAccount?.(accountId);
        }
      },
      [onDeleteAccount, t],
    );

    const handleTransferClick = useCallback(
      (e: React.MouseEvent, account: Account) => {
        e.stopPropagation();
        onTransfer?.(account);
      },
      [onTransfer],
    );

    if (loading) {
      return (
        <Card>
          <CardContent>
            <div className="flex items-center justify-center py-8">
              <LoadingSpinner size="large" />
              <span className="ml-2">{t("loading.accounts")}</span>
            </div>
          </CardContent>
        </Card>
      );
    }

    return (
      <div className="space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card elevation={3}>
            <CardContent>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {formatCurrency(summaryStats.totalBalance)}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {t("account.totalBalance")}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card elevation={3}>
            <CardContent>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {summaryStats.activeAccounts}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {t("account.activeAccounts")}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card elevation={3}>
            <CardContent>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {summaryStats.totalAccounts}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {t("account.totalAccounts")}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card elevation={3}>
            <CardContent>
              <div className="text-center">
                <div
                  className={`text-2xl font-bold ${
                    summaryStats.complianceIssues > 0
                      ? "text-red-600"
                      : "text-green-600"
                  }`}
                >
                  {summaryStats.complianceIssues}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {t("account.complianceIssues")}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Risk Distribution */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-medium">
              {t("account.riskDistribution")}
            </h3>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {summaryStats.riskDistribution.low}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {t("account.riskLevel.low")}
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">
                  {summaryStats.riskDistribution.medium}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {t("account.riskLevel.medium")}
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {summaryStats.riskDistribution.high}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {t("account.riskLevel.high")}
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {summaryStats.riskDistribution.critical}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {t("account.riskLevel.critical")}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Filters and Actions */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium">{t("account.filters")}</h3>
              {onCreateAccount && (
                <Button
                  variant="primary"
                  size="small"
                  onClick={onCreateAccount}
                >
                  {t("account.createAccount")}
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <Input
                  label={t("account.searchPlaceholder")}
                  type="text"
                  placeholder={t("account.searchPlaceholder")}
                  value={searchTerm}
                  onChange={(value: string | number | boolean) =>
                    setSearchTerm(String(value))
                  }
                />
              </div>

              <div>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <option value="all">{t("account.allStatuses")}</option>
                  <option value="active">{t("account.status.active")}</option>
                  <option value="inactive">
                    {t("account.status.inactive")}
                  </option>
                  <option value="suspended">
                    {t("account.status.suspended")}
                  </option>
                  <option value="closed">{t("account.status.closed")}</option>
                </select>
              </div>

              <div>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                >
                  <option value="all">{t("account.allTypes")}</option>
                  <option value="checking">{t("account.type.checking")}</option>
                  <option value="savings">{t("account.type.savings")}</option>
                  <option value="credit">{t("account.type.credit")}</option>
                  <option value="investment">
                    {t("account.type.investment")}
                  </option>
                  <option value="loan">{t("account.type.loan")}</option>
                </select>
              </div>

              <div>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={riskFilter}
                  onChange={(e) => setRiskFilter(e.target.value)}
                >
                  <option value="all">{t("account.allRiskLevels")}</option>
                  <option value="low">{t("account.riskLevel.low")}</option>
                  <option value="medium">
                    {t("account.riskLevel.medium")}
                  </option>
                  <option value="high">{t("account.riskLevel.high")}</option>
                  <option value="critical">
                    {t("account.riskLevel.critical")}
                  </option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Account List */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-medium">
              {t("account.accounts")} ({filteredAccounts.length})
            </h3>
          </CardHeader>
          <CardContent>
            {filteredAccounts.length === 0 ? (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                {t("account.noAccounts")}
              </div>
            ) : (
              <div className="space-y-4">
                {filteredAccounts.map((account) => (
                  <div
                    key={account.id}
                    className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                    onClick={() => handleAccountClick(account)}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-white">
                              {account.account_name}
                            </h4>
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                              {account.account_number}
                              {account.bank_name && (
                                <span> • {account.bank_name}</span>
                              )}
                            </p>
                          </div>
                        </div>

                        <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                          <span>
                            {t("account.typeLabel")}: {account.account_type}
                          </span>
                          <span>
                            {t("account.currencyLabel")}: {account.currency}
                          </span>
                          {(account as any).opened_date && (
                            <span>
                              {t("account.openedDate")}:{" "}
                              {(account as any).opened_date}
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <div className="text-lg font-semibold text-gray-900 dark:text-white">
                            {formatCurrency(account.balance)}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {t("account.currentBalance")}
                          </div>
                        </div>

                        <div className="flex flex-col space-y-2">
                          <Badge
                            color={getStatusBadgeVariant(
                              account.is_active ? "active" : "inactive",
                            )}
                          >
                            {t(
                              `account.status.${account.is_active ? "active" : "inactive"}`,
                            )}
                          </Badge>
                          <Badge color={getRiskBadgeVariant("low")}>
                            {t("account.riskLevel.low")}
                          </Badge>
                          <Badge
                            color={getComplianceBadgeVariant(
                              (account as any).compliance_status,
                            )}
                          >
                            {t(
                              `account.compliance.${(account as any).compliance_status}`,
                            )}
                          </Badge>
                        </div>

                        {showActions && (
                          <div className="flex flex-col space-y-1">
                            {onEditAccount && (
                              <Button
                                variant="text"
                                size="small"
                                onClick={(e: React.MouseEvent) =>
                                  handleEditClick(e, account)
                                }
                              >
                                {t("common.edit")}
                              </Button>
                            )}
                            {onTransfer && (
                              <Button
                                variant="text"
                                size="small"
                                onClick={(e: React.MouseEvent) =>
                                  handleTransferClick(e, account)
                                }
                              >
                                {t("account.transfer")}
                              </Button>
                            )}
                            {onDeleteAccount && (
                              <Button
                                variant="text"
                                size="small"
                                onClick={(e: React.MouseEvent) =>
                                  handleDeleteClick(e, account.id)
                                }
                              >
                                {t("common.delete")}
                              </Button>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  },
);

AccountManagement.displayName = "AccountManagement";

export default AccountManagement;

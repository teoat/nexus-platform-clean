import React from "react";
import {
  Box,
  Grid,
  Typography,
  Paper,
  CardContent,
  CardHeader,
  IconButton,
  Chip,
  LinearProgress,
} from "@mui/material";
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  AccountBalance as AccountBalanceIcon,
  CreditCard as CreditCardIcon,
  Savings as SavingsIcon,
  MoreVert as MoreVertIcon,
} from "@mui/icons-material";
import { useUsers, useAccounts } from "../../hooks";
import { LoadingState, ErrorDisplay } from "../ui";
import Card from "../ui/Card";

interface FinancialDashboardProps {
  userId?: string;
}

const FinancialDashboard: React.FC<FinancialDashboardProps> = ({
  userId: _userId,
}) => {
  const {
    data: accounts,
    isLoading: accountsLoading,
    error: accountsError,
  } = useAccounts();

  const {
    data: users,
    isLoading: usersLoading,
    error: usersError,
  } = useUsers();

  // Calculate financial metrics
  const totalBalance = Array.isArray(accounts)
    ? accounts.reduce((sum, account) => sum + account.balance, 0)
    : 0;
  const totalAccounts = Array.isArray(accounts) ? accounts.length : 0;
  const activeUsers = Array.isArray(users)
    ? users.filter((user) => user.status === "active").length
    : 0;

  // Account type distribution
  const accountTypes = Array.isArray(accounts)
    ? accounts.reduce(
        (acc, account) => {
          acc[account.account_type] = (acc[account.account_type] || 0) + 1;
          return acc;
        },
        {} as Record<string, number>,
      )
    : {};

  // Recent transactions (mock data for now)
  const recentTransactions = [
    {
      id: "1",
      description: "Salary Deposit",
      amount: 5000,
      type: "credit",
      date: "2024-01-15",
    },
    {
      id: "2",
      description: "Rent Payment",
      amount: -1200,
      type: "debit",
      date: "2024-01-14",
    },
    {
      id: "3",
      description: "Grocery Shopping",
      amount: -150,
      type: "debit",
      date: "2024-01-13",
    },
    {
      id: "4",
      description: "Freelance Payment",
      amount: 800,
      type: "credit",
      date: "2024-01-12",
    },
  ];

  if (accountsLoading || usersLoading) {
    return <LoadingState message="Loading financial dashboard..." fullScreen />;
  }

  if (accountsError || usersError) {
    return (
      <ErrorDisplay
        error={String(
          accountsError || usersError || "Failed to load financial data",
        )}
        title="Failed to load financial data"
        variant="card"
      />
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Financial Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Key Metrics Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                display="flex"
                alignItems="center"
                justifyContent="space-between"
              >
                <Box>
                  <Typography
                    color="textSecondary"
                    gutterBottom
                    variant="body2"
                  >
                    Total Balance
                  </Typography>
                  <Typography variant="h4" component="div">
                    ${totalBalance.toLocaleString()}
                  </Typography>
                </Box>
                <AccountBalanceIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                display="flex"
                alignItems="center"
                justifyContent="space-between"
              >
                <Box>
                  <Typography
                    color="textSecondary"
                    gutterBottom
                    variant="body2"
                  >
                    Total Accounts
                  </Typography>
                  <Typography variant="h4" component="div">
                    {totalAccounts}
                  </Typography>
                </Box>
                <CreditCardIcon color="secondary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                display="flex"
                alignItems="center"
                justifyContent="space-between"
              >
                <Box>
                  <Typography
                    color="textSecondary"
                    gutterBottom
                    variant="body2"
                  >
                    Active Users
                  </Typography>
                  <Typography variant="h4" component="div">
                    {activeUsers}
                  </Typography>
                </Box>
                <SavingsIcon color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                display="flex"
                alignItems="center"
                justifyContent="space-between"
              >
                <Box>
                  <Typography
                    color="textSecondary"
                    gutterBottom
                    variant="body2"
                  >
                    User Growth
                  </Typography>
                  <Typography variant="h4" component="div">
                    +12%
                  </Typography>
                  <Box display="flex" alignItems="center" mt={1}>
                    <TrendingUpIcon
                      color="success"
                      sx={{ fontSize: 16, mr: 0.5 }}
                    />
                    <Typography variant="body2" color="success.main">
                      vs last month
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Account Overview */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader
              title="Account Overview"
              action={
                <IconButton>
                  <MoreVertIcon />
                </IconButton>
              }
            />
            <CardContent>
              <Grid container spacing={2}>
                {Object.entries(accountTypes).map(([type, count]) => (
                  <Grid item xs={6} sm={3} key={type}>
                    <Paper sx={{ p: 2, textAlign: "center" }}>
                      <Typography variant="h6">{Number(count) || 0}</Typography>
                      <Typography variant="body2" color="textSecondary">
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Quick Stats" />
            <CardContent>
              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">Account Health</Typography>
                  <Typography variant="body2">85%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={85} />
              </Box>

              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">User Satisfaction</Typography>
                  <Typography variant="body2">92%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={92}
                  color="success"
                />
              </Box>

              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">System Uptime</Typography>
                  <Typography variant="body2">99.9%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={99.9}
                  color="info"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Transactions */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Recent Transactions" />
            <CardContent>
              {recentTransactions.map((transaction) => (
                <Box
                  key={transaction.id}
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                  py={1}
                  borderBottom="1px solid"
                  borderColor="divider"
                >
                  <Box>
                    <Typography variant="body1">
                      {transaction.description}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {new Date(transaction.date).toLocaleDateString()}
                    </Typography>
                  </Box>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip
                      icon={
                        transaction.type === "credit" ? (
                          <TrendingUpIcon />
                        ) : (
                          <TrendingDownIcon />
                        )
                      }
                      label={transaction.type === "credit" ? "Credit" : "Debit"}
                      color={
                        transaction.type === "credit" ? "success" : "error"
                      }
                      size="small"
                    />
                    <Typography
                      variant="h6"
                      color={
                        transaction.type === "credit"
                          ? "success.main"
                          : "error.main"
                      }
                    >
                      ${Math.abs(transaction.amount).toLocaleString()}
                    </Typography>
                  </Box>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default FinancialDashboard;

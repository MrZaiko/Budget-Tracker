import React, { useState } from 'react';
import { Box, Tab, Tabs, Card, CardContent, Skeleton, Typography } from '@mui/material';
import ReportControls from '@/features/reports/ReportControls';
import {
  useSpendingReport,
  useIncomeVsExpenseReport,
  useTrendsReport,
  useNetWorthReport,
} from '@/features/reports/useReports';
import SpendingPieChart from '@/components/charts/SpendingPieChart';
import IncomeExpenseBarChart from '@/components/charts/IncomeExpenseBarChart';
import TrendLineChart from '@/components/charts/TrendLineChart';
import NetWorthAreaChart from '@/components/charts/NetWorthAreaChart';

const getDefaultParams = () => {
  const to = new Date();
  const from = new Date();
  from.setMonth(from.getMonth() - 1);
  return {
    from_date: from.toISOString().split('T')[0],
    to_date: to.toISOString().split('T')[0],
  };
};

const ReportsPage: React.FC = () => {
  const [tab, setTab] = useState(0);
  const [params, setParams] = useState(getDefaultParams());

  const spendingQuery = useSpendingReport(params);
  const incomeQuery = useIncomeVsExpenseReport(params);
  const trendsQuery = useTrendsReport({ months: 12 });
  const netWorthQuery = useNetWorthReport({});

  return (
    <Box>
      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3 }}>
        <Tab label="Spending by Category" />
        <Tab label="Income vs. Expenses" />
        <Tab label="Trends" />
        <Tab label="Net Worth" />
      </Tabs>

      {tab <= 1 && <ReportControls params={params} onChange={setParams} />}

      {tab === 0 && (
        <Card>
          <CardContent>
            {spendingQuery.isLoading ? (
              <Skeleton variant="rectangular" height={300} />
            ) : spendingQuery.data ? (
              <>
                <Typography variant="h6" gutterBottom>
                  Total: {parseFloat(spendingQuery.data.total).toFixed(2)} {spendingQuery.data.currency}
                </Typography>
                <SpendingPieChart categories={spendingQuery.data.categories} />
              </>
            ) : (
              <Typography color="text.secondary">Select a date range to view data.</Typography>
            )}
          </CardContent>
        </Card>
      )}

      {tab === 1 && (
        <Card>
          <CardContent>
            {incomeQuery.isLoading ? (
              <Skeleton variant="rectangular" height={300} />
            ) : incomeQuery.data ? (
              <IncomeExpenseBarChart periods={incomeQuery.data.periods} />
            ) : (
              <Typography color="text.secondary">Select a date range to view data.</Typography>
            )}
          </CardContent>
        </Card>
      )}

      {tab === 2 && (
        <Card>
          <CardContent>
            {trendsQuery.isLoading ? (
              <Skeleton variant="rectangular" height={300} />
            ) : trendsQuery.data ? (
              <TrendLineChart trends={trendsQuery.data.trends} />
            ) : (
              <Typography color="text.secondary">No trends data.</Typography>
            )}
          </CardContent>
        </Card>
      )}

      {tab === 3 && (
        <Card>
          <CardContent>
            {netWorthQuery.isLoading ? (
              <Skeleton variant="rectangular" height={300} />
            ) : netWorthQuery.data ? (
              <>
                <Typography variant="h5" fontWeight={700} gutterBottom>
                  Net Worth: {parseFloat(netWorthQuery.data.net_worth).toFixed(2)} {netWorthQuery.data.currency}
                </Typography>
                <NetWorthAreaChart accounts={netWorthQuery.data.accounts} />
              </>
            ) : (
              <Typography color="text.secondary">No data available.</Typography>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default ReportsPage;

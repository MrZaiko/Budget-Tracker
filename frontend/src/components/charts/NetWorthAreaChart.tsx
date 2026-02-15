import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { AccountBalance } from '@/types/reports';

interface Props {
  accounts: AccountBalance[];
}

const NetWorthAreaChart: React.FC<Props> = ({ accounts }) => {
  const data = accounts.map((a) => ({
    name: a.account_name,
    Balance: parseFloat(a.balance_base),
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: 60, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis type="category" dataKey="name" width={80} />
        <Tooltip />
        <Legend />
        <Bar dataKey="Balance" fill="#1976d2" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default NetWorthAreaChart;

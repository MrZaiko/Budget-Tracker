import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { MonthlyTrend } from '@/types/reports';

interface Props {
  trends: MonthlyTrend[];
}

const TrendLineChart: React.FC<Props> = ({ trends }) => {
  const data = trends.map((t) => ({
    month: t.month,
    Income: parseFloat(t.income),
    Expenses: parseFloat(t.expenses),
    Net: parseFloat(t.net),
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="Income" stroke="#388e3c" dot={false} />
        <Line type="monotone" dataKey="Expenses" stroke="#d32f2f" dot={false} />
        <Line type="monotone" dataKey="Net" stroke="#1976d2" dot={false} strokeDasharray="5 5" />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default TrendLineChart;

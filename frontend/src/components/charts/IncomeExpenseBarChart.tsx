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
import type { IncomeVsExpensePeriod } from '@/types/reports';

interface Props {
  periods: IncomeVsExpensePeriod[];
}

const IncomeExpenseBarChart: React.FC<Props> = ({ periods }) => {
  const data = periods.map((p) => ({
    period: p.period,
    Income: parseFloat(p.income),
    Expenses: parseFloat(p.expenses),
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="period" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="Income" fill="#388e3c" />
        <Bar dataKey="Expenses" fill="#d32f2f" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default IncomeExpenseBarChart;

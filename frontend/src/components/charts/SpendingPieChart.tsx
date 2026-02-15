import React from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { SpendingByCategory } from '@/types/reports';

const COLORS = ['#1976d2', '#9c27b0', '#f57c00', '#388e3c', '#d32f2f', '#0288d1', '#7b1fa2'];

interface Props {
  categories: SpendingByCategory[];
}

const SpendingPieChart: React.FC<Props> = ({ categories }) => {
  const data = categories.map((c) => ({
    name: c.category_name,
    value: parseFloat(c.amount),
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={100}
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
        >
          {data.map((_, index) => (
            <Cell key={index} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(value: number) => value.toFixed(2)} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default SpendingPieChart;

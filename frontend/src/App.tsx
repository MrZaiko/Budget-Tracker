import React from 'react';
import { Routes, Route } from 'react-router-dom';
import AppShell from '@/components/layout/AppShell';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

// Pages
import DashboardPage from '@/pages/DashboardPage';
import AccountsPage from '@/pages/AccountsPage';
import TransactionsPage from '@/pages/TransactionsPage';
import BudgetsPage from '@/pages/BudgetsPage';
import BudgetDetailPage from '@/pages/BudgetDetailPage';
import RecurringPage from '@/pages/RecurringPage';
import SubscriptionsPage from '@/pages/SubscriptionsPage';
import ReportsPage from '@/pages/ReportsPage';
import SettingsPage from '@/pages/SettingsPage';
import AdminPage from '@/pages/AdminPage';
import AdminRoute from '@/components/auth/AdminRoute';
import AuthCallbackPage from '@/pages/AuthCallbackPage';
import LogoutPage from '@/pages/LogoutPage';
import LocalLoginPage from '@/pages/LocalLoginPage';
import NotFoundPage from '@/pages/NotFoundPage';

const App: React.FC = () => (
  <Routes>
    {/* Public */}
    <Route path="/callback" element={<AuthCallbackPage />} />
    <Route path="/logout" element={<LogoutPage />} />
    <Route path="/login/local" element={<LocalLoginPage />} />

    {/* Protected */}
    <Route
      path="/"
      element={
        <ProtectedRoute>
          <AppShell>
            <DashboardPage />
          </AppShell>
        </ProtectedRoute>
      }
    />
    <Route
      path="/accounts"
      element={
        <ProtectedRoute>
          <AppShell>
            <AccountsPage />
          </AppShell>
        </ProtectedRoute>
      }
    />
    <Route
      path="/transactions"
      element={
        <ProtectedRoute>
          <AppShell>
            <TransactionsPage />
          </AppShell>
        </ProtectedRoute>
      }
    />
    <Route
      path="/budgets"
      element={
        <ProtectedRoute>
          <AppShell>
            <BudgetsPage />
          </AppShell>
        </ProtectedRoute>
      }
    />
    <Route
      path="/budgets/:id"
      element={
        <ProtectedRoute>
          <AppShell>
            <BudgetDetailPage />
          </AppShell>
        </ProtectedRoute>
      }
    />
    <Route
      path="/recurring"
      element={
        <ProtectedRoute>
          <AppShell>
            <RecurringPage />
          </AppShell>
        </ProtectedRoute>
      }
    />
    <Route
      path="/subscriptions"
      element={
        <ProtectedRoute>
          <AppShell>
            <SubscriptionsPage />
          </AppShell>
        </ProtectedRoute>
      }
    />
    <Route
      path="/reports"
      element={
        <ProtectedRoute>
          <AppShell>
            <ReportsPage />
          </AppShell>
        </ProtectedRoute>
      }
    />
    <Route
      path="/settings"
      element={
        <ProtectedRoute>
          <AppShell>
            <SettingsPage />
          </AppShell>
        </ProtectedRoute>
      }
    />

    <Route
      path="/admin"
      element={
        <ProtectedRoute>
          <AdminRoute>
            <AppShell>
              <AdminPage />
            </AppShell>
          </AdminRoute>
        </ProtectedRoute>
      }
    />

    {/* Catch-all */}
    <Route path="*" element={<NotFoundPage />} />
  </Routes>
);

export default App;

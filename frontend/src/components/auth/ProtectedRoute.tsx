import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from 'react-oidc-context';
import { useLocalAuthStore } from '@/stores/localAuthStore';
import { isLocalAuthEnabled } from '@/lib/auth';
import LoadingSpinner from '@/components/common/LoadingSpinner';

interface Props {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<Props> = ({ children }) => {
  const auth = useAuth();
  const localToken = useLocalAuthStore((s) => s.token);
  const location = useLocation();

  if (auth.isLoading) {
    return <LoadingSpinner fullPage />;
  }

  const isAuthenticated = auth.isAuthenticated || (isLocalAuthEnabled() && !!localToken);

  if (!isAuthenticated) {
    if (isLocalAuthEnabled()) {
      return <Navigate to="/login/local" state={{ returnTo: location.pathname }} replace />;
    }
    auth.signinRedirect({ state: { returnTo: location.pathname } });
    return <LoadingSpinner fullPage />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;

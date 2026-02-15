import React, { useEffect } from 'react';
import { useAuth } from 'react-oidc-context';
import { useLocalAuthStore } from '@/stores/localAuthStore';
import { isLocalAuthEnabled } from '@/lib/auth';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { useNavigate } from 'react-router-dom';

const LogoutPage: React.FC = () => {
  const auth = useAuth();
  const clearLocalToken = useLocalAuthStore((s) => s.clearToken);
  const navigate = useNavigate();

  useEffect(() => {
    if (isLocalAuthEnabled()) {
      clearLocalToken();
      navigate('/login/local', { replace: true });
    } else {
      auth.signoutRedirect();
    }
  }, []);

  return <LoadingSpinner fullPage />;
};

export default LogoutPage;

import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from 'react-oidc-context';
import LoadingSpinner from '@/components/common/LoadingSpinner';

const AuthCallbackPage: React.FC = () => {
  const auth = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!auth.isLoading && !auth.error) {
      const returnTo =
        (auth.user?.state as { returnTo?: string } | undefined)?.returnTo ?? '/';
      navigate(returnTo, { replace: true });
    }
  }, [auth.isLoading, auth.error, auth.user, navigate]);

  if (auth.error) {
    return (
      <div style={{ padding: 32 }}>
        <h2>Authentication error</h2>
        <p>{auth.error.message}</p>
        <a href="/">Go home</a>
      </div>
    );
  }

  return <LoadingSpinner fullPage />;
};

export default AuthCallbackPage;

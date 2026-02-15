import { UserManager, WebStorageStateStore } from 'oidc-client-ts';

const getEnv = (key: keyof Window['__ENV__'], viteKey: string): string => {
  return window.__ENV__?.[key] ?? (import.meta.env[viteKey] as string | undefined) ?? '';
};

export const userManager = new UserManager({
  authority: getEnv('OIDC_AUTHORITY', 'VITE_OIDC_AUTHORITY'),
  client_id: getEnv('OIDC_CLIENT_ID', 'VITE_OIDC_CLIENT_ID'),
  redirect_uri: getEnv('OIDC_REDIRECT_URI', 'VITE_OIDC_REDIRECT_URI'),
  post_logout_redirect_uri: getEnv(
    'OIDC_POST_LOGOUT_REDIRECT_URI',
    'VITE_OIDC_POST_LOGOUT_REDIRECT_URI'
  ),
  scope: 'openid email profile',
  response_type: 'code',
  automaticSilentRenew: true,
  silent_redirect_uri: `${window.location.origin}/silent-renew.html`,
  userStore: new WebStorageStateStore({ store: window.sessionStorage }),
});

export const isLocalAuthEnabled = (): boolean => {
  const envVal =
    window.__ENV__?.LOCAL_AUTH_ENABLED ??
    (import.meta.env.VITE_LOCAL_AUTH_ENABLED as string | undefined);
  return envVal === 'true';
};

export const getApiBaseUrl = (): string => {
  return (
    window.__ENV__?.API_BASE_URL ??
    (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
    ''
  );
};

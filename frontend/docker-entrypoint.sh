#!/bin/sh
set -e

# Generate /usr/share/nginx/html/env-config.js at container startup.
# This allows runtime configuration without rebuilding the Docker image.
# Environment variables are read from the container's environment.

cat > /usr/share/nginx/html/env-config.js <<EOF
window.__ENV__ = {
  API_BASE_URL: "${API_BASE_URL:-}",
  OIDC_AUTHORITY: "${OIDC_AUTHORITY:-}",
  OIDC_CLIENT_ID: "${OIDC_CLIENT_ID:-}",
  OIDC_REDIRECT_URI: "${OIDC_REDIRECT_URI:-}",
  OIDC_POST_LOGOUT_REDIRECT_URI: "${OIDC_POST_LOGOUT_REDIRECT_URI:-}",
  LOCAL_AUTH_ENABLED: "${LOCAL_AUTH_ENABLED:-false}"
};
EOF

echo "Generated env-config.js:"
cat /usr/share/nginx/html/env-config.js

exec "$@"

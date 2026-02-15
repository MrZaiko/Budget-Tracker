# Project Alpha — Authentication & Authorization

## Overview

Project Alpha supports two authentication paths:

| Path | Use case | Enabled by default |
|------|----------|--------------------|
| **OIDC via Authentik** | All production users | Yes |
| **Local credentials** | Development and debugging | No (`LOCAL_AUTH_ENABLED=true` required) |

Both paths produce a JWT that is validated by the same middleware. Once a token is accepted, the authorization model is identical regardless of how the user authenticated.

---

## OIDC Authentication (Authentik)

### Flow: Authorization Code + PKCE

```
Browser                  Frontend                  Authentik              Backend API
   |                        |                          |                       |
   |-- visit app ---------->|                          |                       |
   |                        |-- no token, redirect --->|                       |
   |                        |                          |                       |
   |<------- redirect to Authentik login --------------|                       |
   |-- authenticate ------->|                          |                       |
   |                        |<-- auth code ------------|                       |
   |                        |-- exchange code (PKCE) ->|                       |
   |                        |<-- access token + ID token -------------------|  |
   |                        |                          |                       |
   |                        |-- API request (Bearer token) ----------------->|  |
   |                        |                          |   validate JWT       |
   |                        |                          |   (JWKS endpoint)    |
   |                        |<---------------------------------------- 200 --|
```

### Backend Token Validation

On every authenticated API request the backend:

1. Extracts the `Authorization: Bearer <token>` header.
2. Fetches (and caches) Authentik's public keys from the JWKS endpoint:
   `{OIDC_ISSUER_URL}/.well-known/jwks.json`
3. Verifies the token signature, `exp`, `iss`, and `aud` claims.
4. Reads the `sub` claim and looks up the corresponding `users` record.
5. If no user record exists (first login), auto-provisions one from token claims:
   - `sub` → `users.sub`
   - `email` → `users.email`
   - `name` (or `preferred_username`) → `users.display_name`
   - `auth_provider` set to `oidc`
6. Attaches the resolved `User` object to the request context.

### Token Refresh

- The frontend uses `oidc-client-ts` to silently renew the access token via a hidden iframe before it expires.
- The backend is stateless — it does not track sessions or refresh tokens.

### Logout

- The frontend calls Authentik's end-session endpoint, passing the `id_token_hint` and a post-logout redirect URI.
- The in-memory access token is discarded by `oidc-client-ts`.

### Authentik Application Setup

The following must be configured in Authentik to integrate with Project Alpha:

| Setting | Value |
|---------|-------|
| Provider type | OAuth2 / OIDC |
| Client type | Public (no client secret) |
| Grant type | Authorization Code |
| PKCE method | S256 |
| Redirect URIs | `https://<app-domain>/callback` |
| Post-logout redirect URI | `https://<app-domain>/` |
| Scopes | `openid`, `email`, `profile` |
| Token signing | RS256 |

---

## Local Authentication (Dev / Debug)

### Enabling

Set the following environment variables:

```env
LOCAL_AUTH_ENABLED=true
LOCAL_AUTH_SECRET=<a-strong-random-secret>
```

**This must never be set in a production environment.**

### Creating Local Users

Local users are created via a CLI management command — there is no self-registration:

```bash
python manage.py create-local-user --email dev@example.com --name "Dev User"
# Prompts for a password, stores bcrypt hash in local_users table
```

Passwords can be reset with:

```bash
python manage.py reset-local-password --email dev@example.com
```

### Login Flow

```
Browser          Frontend              Backend API
   |                |                       |
   |-- POST /login/local (email+password) ->|
   |                |                       |-- lookup local_users by email
   |                |                       |-- bcrypt.verify(password, hash)
   |                |                       |-- issue signed JWT (LOCAL_AUTH_SECRET, HS256)
   |                |<-- { access_token } --|
   |                |                       |
   |                |-- API request (Bearer token) -->|
   |                |                       |-- validate JWT (HS256, LOCAL_AUTH_SECRET)
   |                |                       |-- iss claim == "local"
   |                |<-------------- 200 --|
```

### Local JWT Claims

Issued tokens use the same claim structure as OIDC tokens to allow shared middleware:

```json
{
  "sub": "local:<email>",
  "email": "dev@example.com",
  "name": "Dev User",
  "iss": "local",
  "aud": "<OIDC_AUDIENCE value>",
  "iat": 1700000000,
  "exp": 1700003600
}
```

Token lifetime: **1 hour** (no silent refresh for local sessions — re-login required).

### Validation Path

The backend middleware checks the `iss` claim to select the validation path:

```
iss == OIDC_ISSUER_URL  →  validate with Authentik JWKS  (RS256)
iss == "local"          →  validate with LOCAL_AUTH_SECRET (HS256)
                           only if LOCAL_AUTH_ENABLED=true;
                           otherwise reject with 401
```

---

## Authorization Model

### Ownership

Every resource record carries a `user_id` foreign key. All data access checks enforce:

```
resource.user_id == current_user.id
```

This is applied at the service layer, not just at the route level.

### Budget Sharing

Shared budgets extend the ownership model with the `budget_collaborators` table:

```
access granted if:
  budget.owner_id == current_user.id
  OR
  budget_collaborators(budget_id, user_id=current_user.id) exists AND accepted_at IS NOT NULL
```

Role enforcement within shared budgets:

| Action | Owner | Editor | Viewer |
|--------|-------|--------|--------|
| View budget & transactions | ✓ | ✓ | ✓ |
| Add / edit / delete transactions | ✓ | ✓ | ✗ |
| Edit budget definition | ✓ | ✗ | ✗ |
| Delete budget | ✓ | ✗ | ✗ |
| Manage collaborators | ✓ | ✗ | ✗ |

### HTTP Error Responses

| Condition | Status |
|-----------|--------|
| Missing or malformed `Authorization` header | `401` |
| Invalid or expired token | `401` |
| Local auth token received but `LOCAL_AUTH_ENABLED=false` | `401` |
| Token valid but user does not own the resource | `403` |
| Token valid, resource shared, but role is insufficient | `403` |

---

## Security Considerations

- **Access tokens in memory only** — never stored in `localStorage` or `sessionStorage` on the frontend.
- **PKCE** — prevents authorization code interception attacks; no client secret required or used.
- **JWKS caching** — public keys are cached with a TTL (default: 1 hour) to avoid fetching on every request, but refreshed automatically on signature verification failure.
- **Local auth is HS256** — symmetric signing; `LOCAL_AUTH_SECRET` must be treated as a secret and never committed to source control.
- **Password hashing** — bcrypt with a work factor of 12.
- **No password reset via API** — local user password management is CLI-only, limiting the attack surface.
- **`LOCAL_AUTH_ENABLED` in production** — the backend will log a startup warning if this flag is `true` in a non-development environment (detected via a `ENVIRONMENT` env var).

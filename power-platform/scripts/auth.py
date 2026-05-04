"""
auth.py — MSAL device-code authentication for the AURUM-PP Dataverse environment.

Acquires an OAuth 2.0 access token for the Dataverse Web API at the URL
exported in the AURUM_PP_DATAVERSE_URL environment variable (e.g.
https://<your-env-host>.crm.dynamics.com/) using MSAL's public-client
device-code flow. Caches the token (and its refresh token) at
~/.aurum-pp/token.json with mode 0600 so subsequent runs reuse the session
silently until the refresh token expires.

When run directly, this module also verifies the resulting token by calling
/api/data/v9.2/WhoAmI and printing the returned tenant identifiers — the
verification gate that must pass before any table-write operation runs.

Required environment variable:
    AURUM_PP_DATAVERSE_URL — e.g. https://<your-env-host>.crm.dynamics.com/

Usage as a script:
    export AURUM_PP_DATAVERSE_URL="https://<your-env-host>.crm.dynamics.com/"
    python scripts/auth.py

Usage as a library (caller must be on sys.path next to this file, or set
PYTHONPATH=scripts):
    from auth import get_token, whoami
    token = get_token()
    me = whoami(token)
"""

from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

import msal
import requests


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"{name} environment variable is required. "
            f"Export it to your shell, e.g. "
            f'export {name}="https://<your-env-host>.crm.dynamics.com/"'
        )
    return value


DATAVERSE_URL: str = _require_env("AURUM_PP_DATAVERSE_URL")

# .default requests every permission the public client has been granted on
# the Dataverse resource — required for the v2.0 endpoint + Dataverse Web API.
DATAVERSE_SCOPE: str = f"{DATAVERSE_URL.rstrip('/')}/.default"

# Public client ID commonly used in Microsoft Dataverse OAuth samples.
# Pre-allowed by Dataverse for user-impersonation flows, so no Entra ID app
# registration is required. If a tenant disables public clients, register a
# tenant-owned app and replace this GUID.
PUBLIC_CLIENT_ID: str = "51f81489-12ee-4a9e-aaae-a2591f45987d"

# /organizations restricts to work/school accounts (no personal MSAs),
# matching Developer Plan and production tenants.
AUTHORITY: str = "https://login.microsoftonline.com/organizations"

# Cache outside the repo so it never lands in git.
TOKEN_CACHE_DIR: Path = Path.home() / ".aurum-pp"
TOKEN_CACHE_FILE: Path = TOKEN_CACHE_DIR / "token.json"

WHOAMI_URL: str = f"{DATAVERSE_URL.rstrip('/')}/api/data/v9.2/WhoAmI"

# Cap how long acquire_token_by_device_flow will poll before exiting.
# Entra's default expires_in is ~900s (15 min). We cap at 600s so an
# abandoned device-code session does not keep the script blocked.
DEVICE_FLOW_MAX_WAIT_SECS: int = 600

log = logging.getLogger("aurum_pp.auth")


def _load_cache() -> msal.SerializableTokenCache:
    """Load the on-disk MSAL token cache, or return a new empty one."""
    cache = msal.SerializableTokenCache()
    if TOKEN_CACHE_FILE.exists():
        try:
            cache.deserialize(TOKEN_CACHE_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            log.warning(
                "Token cache at %s unreadable (%s); starting fresh.",
                TOKEN_CACHE_FILE,
                exc,
            )
    return cache


def _save_cache(cache: msal.SerializableTokenCache) -> None:
    """Persist the MSAL token cache with file mode 0600 / directory mode 0700."""
    if not cache.has_state_changed:
        return
    TOKEN_CACHE_DIR.mkdir(mode=0o700, exist_ok=True)
    # Re-tighten in case the dir pre-existed with looser permissions
    # (mkdir mode is honored only on creation).
    os.chmod(TOKEN_CACHE_DIR, 0o700)
    # Write-then-rename for atomicity — avoids a half-written cache if the
    # process is killed mid-write.
    tmp = TOKEN_CACHE_FILE.with_suffix(".json.tmp")
    tmp.write_text(cache.serialize(), encoding="utf-8")
    os.chmod(tmp, 0o600)
    os.replace(tmp, TOKEN_CACHE_FILE)


def get_token(*, force_device_code: bool = False) -> str:
    """
    Acquire a Dataverse Web API access token.

    Tries silent acquisition from the on-disk cache first; falls back to the
    device-code flow when no cached account is usable.

    Args:
        force_device_code: If True, skip silent acquisition and force a fresh
            device-code login.

    Returns:
        Bearer access token suitable for an Authorization header.

    Raises:
        RuntimeError: If MSAL returns an error or no token at all.
    """
    cache = _load_cache()
    app = msal.PublicClientApplication(
        client_id=PUBLIC_CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache,
    )

    if not force_device_code:
        accounts = app.get_accounts()
        if accounts:
            log.info(
                "Trying silent token for cached account %s.",
                accounts[0].get("username"),
            )
            result = app.acquire_token_silent(
                [DATAVERSE_SCOPE], account=accounts[0]
            )
            if result and "access_token" in result:
                _save_cache(cache)
                return result["access_token"]

    log.info("Starting device-code flow.")
    flow = app.initiate_device_flow(scopes=[DATAVERSE_SCOPE])
    if "user_code" not in flow:
        raise RuntimeError(
            f"Failed to initiate device flow: "
            f"{flow.get('error')} — {flow.get('error_description')}"
        )
    # MSAL has no `timeout` kwarg on acquire_token_by_device_flow; the
    # poll loop exits when flow["expires_at"] is reached. Tighten that
    # window to DEVICE_FLOW_MAX_WAIT_SECS so an abandoned sign-in does
    # not block the script for Entra's default 15 minutes.
    if flow.get("expires_in", 0) > DEVICE_FLOW_MAX_WAIT_SECS:
        flow["expires_in"] = DEVICE_FLOW_MAX_WAIT_SECS
        flow["expires_at"] = time.time() + DEVICE_FLOW_MAX_WAIT_SECS
    print("\n" + flow["message"] + "\n", flush=True)
    print(
        f"(Sign-in must complete within {DEVICE_FLOW_MAX_WAIT_SECS // 60} "
        f"minutes or this script will exit with an error.)\n",
        flush=True,
    )

    result = app.acquire_token_by_device_flow(flow)
    if "access_token" not in result:
        raise RuntimeError(
            f"Device-code auth failed: "
            f"{result.get('error')} — {result.get('error_description')}"
        )
    _save_cache(cache)
    log.info("Acquired token via device-code flow.")
    return result["access_token"]


def whoami(access_token: str, *, timeout: float = 30.0) -> dict[str, Any]:
    """
    Call the Dataverse Web API WhoAmI endpoint to verify the token.

    Args:
        access_token: Bearer token from get_token().
        timeout: Per-request timeout in seconds.

    Returns:
        Parsed JSON body containing UserId, BusinessUnitId, OrganizationId,
        plus an @odata.context metadata key.

    Raises:
        RuntimeError: On non-2xx HTTP response (body excerpt included).
        requests.RequestException: On network/transport failure.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
    }
    resp = requests.get(WHOAMI_URL, headers=headers, timeout=timeout)
    if not resp.ok:
        # Bound the excerpt so a verbose error page does not flood logs.
        body_excerpt = resp.text[:500]
        raise RuntimeError(
            f"WhoAmI failed: HTTP {resp.status_code} {resp.reason} — {body_excerpt}"
        )
    return resp.json()


def _configure_logging() -> None:
    """Stream INFO+ to stderr. Library callers can override before invocation."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )


def main() -> int:
    """Run device-code auth (or silent if cached) and verify with WhoAmI."""
    _configure_logging()
    try:
        token = get_token()
    except RuntimeError as exc:
        log.error("Authentication failed: %s", exc)
        return 1

    try:
        identity = whoami(token)
    except (RuntimeError, requests.RequestException) as exc:
        log.error("WhoAmI verification failed: %s", exc)
        return 2

    print("\n--- WhoAmI ---")
    print(f"  OrganizationId : {identity.get('OrganizationId')}")
    print(f"  BusinessUnitId : {identity.get('BusinessUnitId')}")
    print(f"  UserId         : {identity.get('UserId')}")
    print(f"  Environment URL: {DATAVERSE_URL}")
    print()
    print("Verify the OrganizationId above matches the AURUM-PP-Dev env in")
    print("the Power Platform admin center BEFORE running any write operation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

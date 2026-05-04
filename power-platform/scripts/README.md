# scripts/

## Setup — environment variable

All scripts read the Dataverse environment URL from `AURUM_PP_DATAVERSE_URL`. Export it to your shell (or add to `~/.zprofile` / `~/.bashrc`) before running anything:

```bash
export AURUM_PP_DATAVERSE_URL="https://<your-env-host>.crm.dynamics.com/"
```

Replace `<your-env-host>` with the host portion of your own Dataverse environment URL (visible under Power Platform admin centre → Environments → your environment → "Environment URL"). The trailing slash is required.

## auth.py

Acquires an OAuth 2.0 access token for the AURUM-PP Dataverse environment (`$AURUM_PP_DATAVERSE_URL`) using MSAL's public-client device-code flow. Tokens are cached at `~/.aurum-pp/token.json` (file mode `0600`, directory mode `0700`) so subsequent runs reuse the session silently until the refresh token expires. When invoked directly, the script also calls the Web API `/api/data/v9.2/WhoAmI` endpoint and prints the tenant identifiers (`OrganizationId`, `BusinessUnitId`, `UserId`) — the verification gate that must pass before any table-write operation runs in Phase 1.

### Run interactively (first time — device-code browser sign-in)

```bash
source .venv/bin/activate
python scripts/auth.py
```

The script prints a `microsoft.com/devicelogin` URL and a code; complete sign-in in any browser. After auth lands, the script prints the `WhoAmI` fields. Subsequent runs reuse the cached token silently — no browser step until the refresh token expires.

### Use as a library from another script in `scripts/`

```python
from auth import get_token, whoami

token = get_token()                     # silent if cached, device-code otherwise
identity = whoami(token)
print(identity["OrganizationId"])
```

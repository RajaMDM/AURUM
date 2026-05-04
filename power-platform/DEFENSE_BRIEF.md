# AURUM-PP — Defense Brief

Cumulative talking points for defending technical choices on AURUM-PP. Written so every decision can be defended in a room of developers.

---

## 2026-05-02 — Phase 1 table deployment via Python + MSAL + Web API instead of PAC CLI

**Decision:** Deploy staging tables 02-05 (`aurum_crm_customer_staging`, `aurum_ecomm_customer_staging`, `aurum_loyalty_customer_staging`, `aurum_assay_profile`) using a Python + MSAL device-code + Dataverse Web API script. Power Platform CLI (PAC) is **not** used for this phase.

**Why this choice (defensible in a developer room):**

Three independent macOS-PAC interaction failures in a single session demonstrated PAC's macOS path was not the fast path:

1. **PAC 2.6.4 + .NET 10:** unconditional `System.NullReferenceException` inside MSAL's Windows `RuntimeBroker` constructor during PAC's silent OS-broker token probe (`TryCreateAuthProfileFromOperatingSystemAsync`). The probe runs *before* verb dispatch — `--deviceCode` does not short-circuit it. Build paths in the stack trace (`C:\__w\1\s\src\...`) confirm a Windows-built binary that does not gate broker init by OS. Verified across two sessions (`368d0135-…`, `170c67b9-…`).
2. **PAC 1.52.1 fallback:** would have required installing .NET 8 LTS runtime alongside .NET 10 (PAC 1.x targets net6.0/net8.0; .NET tools do not auto-roll-forward across major runtime versions by default).
3. **Homebrew `dotnet@8` is keg-only:** its `shared/Microsoft.NETCore.App/8.0.x/` directory is not visible to the linked `dotnet` host (.NET 10), requiring either a symlink (fragile — overwritten by `brew upgrade`), a `DOTNET_ROOTS` env-var configuration (.NET 9+ feature, requires verification on .NET 10 macOS host), or per-invocation `DOTNET_ROOT` wrapping (operationally annoying).

Each fix introduces new fragility. The pattern says PAC's macOS path needed troubleshooting Homebrew package layout to make a Microsoft tool work on a Mac — not the right place to be spending Phase 1 time.

**Why Python is not "re-tooling":** the `dv-metadata`, `dv-data`, `dv-query`, `dv-connect` skills already in this Claude install are Python + Web API native by design. That IS the canonical macOS path for Dataverse work. Using them is using the path the skills were built for.

**Alternatives considered and rejected:**

- **A. Retry PAC 2.6.4 with `--deviceCode` flag:** rejected after empirical test — same NRE, same call site (the OS-broker probe runs before any verb-specific flow can take over).
- **B. Downgrade to PAC 1.52.1:** rejected after surfacing the runtime-discovery layer as a third failure mode. Would have required two installs (`dotnet@8` + PAC 1.52.1) plus a runtime-discovery hack, with no guarantee of success.
- **C. Python + MSAL + Web API (chosen):** zero new installs (Python, msal, requests, pyyaml present or trivially installable via `pip3 --user`). Uses well-trodden macOS path. Aligns with existing skill design.

**What PAC is still being kept for:** `pac solution export/import` (Phase 5 solution lifecycle work) — PAC's irreplaceable value. Re-entry trigger: when Microsoft publishes a PAC 2.x build > 2.6.4 that fixes the macOS broker NRE, test in throwaway shell, then resume PAC for solution lifecycle.

**Retained machine state (intentionally not undone):**
- `dotnet@8` 8.0.125 at `/opt/homebrew/opt/dotnet@8/libexec` — for future C#/plugin work.
- PAC CLI 2.6.4 at `~/.dotnet/tools/pac` — for Phase 5 solution lifecycle.
- `~/.zprofile` PATH and `DOTNET_ROOT` exports — unchanged.

**Growth path:** when PAC 2.x is fixed upstream, `dotnet tool update -g Microsoft.PowerApps.CLI.Tool` brings PAC back to current. Python + Web API path stays operational throughout — it is the long-term automation layer for table CRUD; PAC is the lifecycle layer.

**Source documents:** `MEMORY/project_aurum_pp_resume_2026_05_02.md` (failure chain, session IDs, exact resume commands), PAC diagnostic log at `/Users/rajaonapple/.dotnet/tools/.store/microsoft.powerapps.cli.tool/2.6.4/microsoft.powerapps.cli.tool/2.6.4/tools/net10.0/any/logs/pac-log.txt`.

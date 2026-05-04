# docs/

Generated and curated documentation for AURUM-PP. Files here ship to GitHub and are intended for public reading (Medium posts, demo walkthroughs, recruiter / portfolio audiences).

## Files in this directory

### `demo_records_aurum_lineage.md` — AUTO-GENERATED, DO NOT HAND-EDIT

This file is regenerated on every invocation of `scripts/load_sample_data.py` (both `--dry-run` and real-run modes). It documents the demo-story records present in the AURUM-PP sample data set, mapping each record to the AURUM public-repo five-stage architecture (ASSAY → UNEARTH → REFINE → UNFURL → MARK) it demonstrates.

**To update this file:** edit the demo-story builders in `scripts/load_sample_data.py` (functions `build_priya_hero`, `build_mohammed_ambiguous`, `build_sarah_multibrand`, `build_aisha_conflicting_sources`, `build_new_prospect_cluster`) and re-run the script. The metadata fields `pattern_name`, `aurum_stages`, `narrative`, and `confidence_explanation` on each `DemoStory` drive the rendered markdown.

**Why auto-generated:** the metadata in the script IS the source of truth. Hand-editing this file would create a sync gap between code and docs that future-us would have to remember to keep aligned. Single source of truth wins.

## Tenant-redaction reminder

Files in this directory are public-bound and must NOT contain:
- The Dataverse environment URL host (`<env-host>.crm.dynamics.com` patterns)
- Tenant domain (`<your-tenant-domain>`)
- User email or personal identifier
- Any record GUID
- Tenant unique IDs (OrganizationId, BusinessUnitId, etc.)

The auto-generated lineage doc avoids all of these by design — it documents the demo-story records (fictional names, fictional addresses, no GUIDs) and the AURUM concepts they demonstrate, nothing about the underlying Dataverse env.

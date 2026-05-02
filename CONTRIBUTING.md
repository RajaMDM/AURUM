# Contributing to AURUM

## What We're Looking For

**High priority:** Working code for any stage (ASSAY/UNEARTH/REFINE/UNFURL/MARK),
new domain examples, Power Platform schema additions, edge case tests, MCP improvements.

**Not accepted:** Vendor-locked code, real personal data, stage renames,
AI-generated submissions the contributor cannot explain.

## Getting Started

```bash
git clone https://github.com/RajaMDM/AURUM.git && cd AURUM
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python shared/sample_data/generate_all.py
python demo/end_to_end_demo.py   # must pass before and after your change
```

## PR Rules

Branch: `feat/<stage>-<what>` or `fix/<stage>-<what>`.
Type hints required. Update stage docs if behaviour changes.
No real brand names. PR description explains the MDM rationale.

Open a [Discussion](../../discussions) before building something large.

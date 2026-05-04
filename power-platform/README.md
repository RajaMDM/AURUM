# AURUM-PP

The public AURUM Master Data Management reference architecture, instantiated on Microsoft Power Platform (Dataverse + Power Apps + Power Automate).

AURUM-PP is the proof that the AURUM five-stage architecture (ASSAY → UNEARTH → REFINE → UNFURL → MARK) is platform-agnostic — the same matching logic, the same trust scoring, the same survivorship rules can run on Microsoft's MDM-adjacent stack as well as on the open-source Python reference implementation.

## Prerequisites

- **Python 3.12** (matches AURUM upstream)
- **Microsoft Power Platform Developer Plan** tenant (free) with a provisioned Dataverse environment
- **AURUM public repo cloned** at `~/Projects/AURUM`:
  ```bash
  git clone https://github.com/RajaMDM/AURUM ~/Projects/AURUM
  ```
  AURUM-PP imports the matcher directly from the public AURUM repo at runtime (`scripts/load_sample_data.py`). This is intentional — vendoring a copy would break the proof of architectural lineage. If the path differs on your machine, edit `AURUM_REPO_PATH` in `scripts/load_sample_data.py`.

## Setup

```bash
# 1. Clone AURUM-PP
git clone <this-repo> ~/Projects/AURUM-PP
cd ~/Projects/AURUM-PP

# 2. Create venv and install AURUM-PP deps (includes pandas/rapidfuzz/jellyfish for AURUM matcher)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Set environment variables in ~/.zprofile
export AURUM_PP_DATAVERSE_URL="https://<your-env-host>.crm.dynamics.com/"
export AURUM_PP_SOLUTION_UNIQUE_NAME="<your-solution-unique-name>"

# 4. Authenticate (first time only — opens browser)
python scripts/auth.py
```

## Repo layout

```
AURUM-PP/
├── dataverse/
│   └── schemas/                 YAML schemas for the 5 Dataverse tables (canonical + 3 staging + assay)
├── scripts/
│   ├── auth.py                  MSAL device-code authentication
│   ├── deploy_table.py          YAML→Web API deployer for table metadata
│   └── load_sample_data.py      Sample-data generator (imports public AURUM matcher)
├── docs/
│   ├── README.md                What's in docs/, redaction rules
│   └── demo_records_aurum_lineage.md   Auto-generated demo lineage (AURUM stage tags + matcher scores)
├── DEFENSE_BRIEF.md             Code-review talking points for major architectural decisions
├── requirements.txt             Pinned Python deps
└── .gitignore
```

## License

[Match AURUM upstream license — to be confirmed]

## See also

- Public AURUM reference implementation: https://github.com/RajaMDM/AURUM
- Demo records lineage (auto-generated, includes AURUM stage tags + actual matcher scores): [`docs/demo_records_aurum_lineage.md`](docs/demo_records_aurum_lineage.md)

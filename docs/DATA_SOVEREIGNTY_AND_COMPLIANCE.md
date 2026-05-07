# AURUM & Global Data Sovereignty
### How MDM Aligns with Data Protection Laws Across the GCC and the World

> *Authored by Nadia (Data Governance Lead) & Tariq (Security & Compliance) — AURUM Project*
> *Legal frameworks are cited for educational accuracy. This document is not legal advice.*

---

## Why Data Sovereignty Matters to MDM

Master Data Management is not just a technical discipline. The moment you create a golden record — a single authoritative record for a customer, employee, vendor, or counterparty — you are making data governance decisions that are directly regulated by law in most jurisdictions.

- **Where** is the golden record stored?
- **Who** can access it?
- **How long** can you keep it?
- **Can you transfer it** across a border?
- **What rights** does the data subject have over it?
- **Must you prove** its accuracy to a regulator on demand?

AURUM's pipeline — ASSAY → UNEARTH → REFINE → UNFURL → MARK — is designed to make every one of these questions answerable. The lineage store (MARK) is not just an audit trail for data engineers. It is the evidence base for regulatory compliance.

This document maps AURUM's capabilities to the data sovereignty frameworks that govern the organisations most likely to implement MDM — across the GCC, and globally.

---

## Part 1 — The GCC: A Region of Rapidly Maturing Data Law

The Gulf Cooperation Council (GCC) — UAE, Saudi Arabia, Qatar, Bahrain, Kuwait, Oman — has undergone a dramatic regulatory transformation in the last five years. From near-zero data protection law to some of the most sophisticated and fast-moving frameworks in the world.

For MDM practitioners working in the region, the landscape is no longer optional to understand.

---

### 🇦🇪 UAE — A Federation of Data Jurisdictions

The UAE is unique globally: it operates multiple overlapping data regimes depending on the emirate and sector. Understanding which regime applies to your master data is itself a governance challenge.

---

#### Federal Level — UAE PDPL (Federal Decree-Law No. 45 of 2021)

**What it is:** The UAE's first federal personal data protection law, effective September 2022. Applies to any entity processing personal data in the UAE (or targeting UAE residents from outside).

**Key provisions relevant to MDM:**

| Provision | AURUM Implication |
|-----------|------------------|
| **Data accuracy** (Article 9) | The entire REFINE stage — deduplication, survivorship, golden record assembly — directly addresses this. Golden records are more accurate than any individual source system. |
| **Purpose limitation** | ASSAY stage schema mapping must document the intended use of each field. Published golden records (UNFURL) should only include fields necessary for the downstream consumer's stated purpose. |
| **Data minimisation** | Survivorship rules should select the minimum set of fields needed for the golden record. Don't retain all 47 fields from all 4 source systems in the golden record — retain what's needed. |
| **Subject access rights** | MARK's lineage store enables instant SAR (Subject Access Request) responses. Query by `source_id` or `email` → full provenance trail returned. |
| **Right to erasure** | When a subject requests deletion, the golden record deletion must cascade to all source system references via MARK's cross-domain link table. AURUM's reverse sync (MARK → source systems) makes this technically tractable. |
| **Data transfer restrictions** | Golden records containing UAE resident personal data cannot be transferred to countries without adequate protection without explicit consent or a lawful transfer mechanism. This constrains where AURUM's golden record store can be hosted. |

**What AURUM does:**
The MARK stage's lineage log is the primary evidence base for PDPL compliance. Every data processing decision — ingestion, profiling, matching, survivorship — is recorded with timestamp, actor, and outcome. Regulators can be answered with a query, not a manual search.

---

#### Abu Dhabi — ADDA (Abu Dhabi Digital Authority) Data Governance Framework

**What it is:** The Abu Dhabi Data Digital Authority (ADDA — formerly ADDED) governs data management for Abu Dhabi government entities and their data-sharing ecosystem. Key instruments include the **Abu Dhabi Data Policy**, the **Data Classification Framework**, and the **Data Sharing Framework**.

**Key provisions relevant to MDM:**

| Provision | AURUM Implication |
|-----------|------------------|
| **Data classification** (Confidential / Internal / Public) | Every field in every domain's canonical schema should carry a classification tag. Customer `national_id` = Confidential; `loyalty_tier` = Internal; `preferred_store` = Public. AURUM's schema mapping (ASSAY) is the right place to enforce this. |
| **Data quality standards** | ADDA mandates defined DQ metrics for government data assets. AURUM's UNEARTH profiling generates completeness, accuracy, consistency, and timeliness scores — directly mapped to ADDA's DQ dimensions. |
| **Data sharing agreements** | Before UNFURL publishes a golden record to a consumer system, a Data Sharing Agreement (DSA) must be in place. AURUM's publisher registry (UNFURL) should validate DSA existence before pushing to any target. |
| **Reference data management** | ADDA maintains authoritative reference datasets (emirate codes, municipality codes, etc.). AURUM's Location domain should anchor to ADDA reference data — not create its own hierarchy. |
| **Authoritative data source designation** | ADDA designates which system is the authoritative source for each data element. AURUM's survivorship rules should respect these designations — if ADDA designates a government registry as the authoritative source for national ID, that source must win in survivorship regardless of trust score. |

**Practical note for MDM teams in Abu Dhabi:**
If your organisation is a government entity or shares data with Abu Dhabi government systems, ADDA framework compliance is mandatory. The AURUM pipeline provides the technical scaffolding; the governance decisions (classification tags, DSA registry, authoritative source mapping) must be made by the data governance team and configured into AURUM's survivorship rules.

---

#### Dubai — DDA (Dubai Data Authority) — Dubai Data Law No. 26 of 2015 (amended 2021)

**What it is:** The Dubai Data Authority (DDA) governs data in the Emirate of Dubai, distinct from the federal PDPL. The Dubai Data Law establishes data sharing obligations, data classification, and the Dubai Data Space — a controlled data exchange ecosystem.

**Key provisions relevant to MDM:**

| Provision | AURUM Implication |
|-----------|------------------|
| **Dubai Data Law — mandatory data sharing** | Government entities in Dubai may be required to share certain datasets with other government entities via the Dubai Data Space. AURUM's UNFURL stage must be configurable to push golden records to the Dubai Data Space as an authorised consumer. |
| **Data classification (Shared / Restricted / Confidential)** | Equivalent to ADDA's classification model. Field-level classification must be enforced at the ASSAY (schema mapping) stage. |
| **Open data obligations** | Certain non-personal government datasets must be published as open data. AURUM's golden record publication (UNFURL) can support this — public-classified fields published to an open data catalogue. |
| **Data residency** | Dubai government data must remain within UAE borders. Any cloud hosting of AURUM's golden record store must be in a UAE-based data centre or a UAE-approved cloud region. |
| **Smart Dubai / DDE integration** | AURUM's MCP server enables AI agents to call MDM tools. This integration pattern aligns with Dubai's Smart City AI strategy — automated, agent-driven data governance. |

**Practical note:**
Dubai and Abu Dhabi operate different data authorities with different classification schemes. If your organisation operates in both emirates (common for UAE-wide retail, healthcare, or financial services), AURUM must support **dual classification tagging** — a field may be classified differently under DDA and ADDA schemes.

---

### 🇸🇦 Saudi Arabia — PDPL (Personal Data Protection Law, Royal Decree M/19, 2021)

**What it is:** Saudi Arabia's Personal Data Protection Law, enforced by the **National Data Management Office (NDMO)** under the Digital Government Authority. Came into force September 2023. One of the most comprehensive data protection frameworks in the Arab world.

**Key provisions relevant to MDM:**

| Provision | AURUM Implication |
|-----------|------------------|
| **Explicit consent for sensitive data** | Health, financial, and biometric data in master data sets require explicit consent to process. AURUM's schema mapping must flag sensitive fields — and the survivorship engine must not include sensitive fields in golden records without documented consent. |
| **Data localisation** | Personal data of Saudi residents must be processed and stored within KSA (with limited exceptions). AURUM deployments serving Saudi customers must run on KSA-based infrastructure. Golden records for Saudi residents cannot be hosted in a non-KSA data centre without regulatory approval. |
| **Cross-border transfer restrictions** | Transfer of Saudi personal data outside KSA requires either: a country adequacy decision, contractual safeguards, or NDMO approval. AURUM's UNFURL stage must enforce this — no golden record containing Saudi personal data can be pushed to a consumer in an unapproved jurisdiction. |
| **Data retention limits** | Personal data must not be retained longer than necessary for the stated purpose. AURUM's golden record store must implement retention policies — when a customer's relationship ends, the golden record must be flagged for scheduled deletion within the mandated period. |
| **Individual rights (access, correction, deletion)** | MARK's lineage store supports all three. Access: query by subject identifier. Correction: steward workflow with lineage event. Deletion: cascade to source systems via reverse sync. |
| **NDMO data governance requirements** | Organisations must appoint a Data Officer and implement a Data Governance Framework. AURUM's stewardship model — with designated domain stewards (Shazia for DQ, Nadia for Governance, Tariq for Compliance) — maps directly to this requirement. |

**National Data Management Policy (NDMP):**
Saudi Arabia's NDMO also publishes the National Data Management Policy, which defines data quality dimensions, metadata standards, and data classification levels (Top Secret / Secret / Confidential / Restricted / Public) for government entities. AURUM's UNEARTH profiling and ASSAY classification tagging align with these standards.

---

### 🇶🇦 Qatar — PDPL (Law No. 13 of 2016, amended by Law No. 13 of 2021)

**What it is:** Qatar's Personal Data Protection Law, administered by the **National Cyber Security Agency (NCSA)** and enforced by the **Ministry of Transport and Communications**. One of the earlier comprehensive data protection frameworks in the GCC.

**Key provisions relevant to MDM:**

| Provision | AURUM Implication |
|-----------|------------------|
| **Data quality obligation** | Controllers must ensure personal data is accurate, complete, and up-to-date. This is the legal mandate for MDM. AURUM's golden record — with DQ scoring, deduplication, and survivorship — is the technical implementation of this legal obligation. |
| **Cross-border transfer** | Data transfer outside Qatar requires: adequacy, consent, contractual safeguards, or vital interest. Same constraint as KSA — UNFURL must enforce jurisdiction-aware publishing rules. |
| **Sensitive data categories** | Health, racial/ethnic origin, political opinion, religious belief, criminal history — extra protections apply. AURUM's schema mapping must identify and classify these fields. Survivorship rules must apply stricter consent checks for sensitive field inclusion in golden records. |
| **Accountability** | Organisations must be able to demonstrate compliance. MARK's lineage store is the accountability mechanism — every processing decision is recorded, timestamped, and attributed to an actor (system or human). |
| **Qatar National Vision 2030** | Qatar's digital transformation agenda includes data-driven government services. AURUM's MCP server enables AI-agent-driven MDM workflows aligned with this vision. |

---

### 🇧🇭 Bahrain — PDPL (Law No. 30 of 2018)

Administered by the **Personal Data Protection Authority (PDPA)**. Broadly aligned with GDPR principles. Key MDM implications: data accuracy obligation, right of correction (triggering steward workflows), transfer restrictions (whitelisted countries only), and retention limits enforceable via AURUM's golden record TTL policies.

---

### 🇰🇼 Kuwait & 🇴🇲 Oman

Both are in active legislative development. Kuwait's data protection bill is expected to pass. Oman's Electronic Transactions Law and Cybersecurity Law provide partial data protection coverage. MDM implementations in these markets should design for GDPR-equivalent standards as a future-proof baseline — AURUM's architecture supports this.

---

## Part 2 — Global: MDM Meets the World's Data Regimes

AURUM's use cases deliberately span multiple geographies. Here is how the pipeline aligns with major global frameworks.

---

### 🇪🇺 GDPR (EU General Data Protection Regulation, 2018)

The global gold standard. If AURUM processes EU resident personal data, GDPR applies regardless of where the organisation is based.

**The 7 GDPR principles — mapped to AURUM:**

| GDPR Principle | AURUM Stage | How AURUM Supports It |
|---------------|-------------|----------------------|
| **Lawfulness, fairness, transparency** | ASSAY | Source system consent records mapped during ingestion |
| **Purpose limitation** | UNFURL | Golden record publication only to authorised consumers with documented purpose |
| **Data minimisation** | REFINE | Survivorship selects only fields needed for the golden record purpose |
| **Accuracy** | UNEARTH + REFINE | DQ profiling + deduplication + golden record assembly |
| **Storage limitation** | MARK | Lineage store records creation date; retention TTL policies enforced |
| **Integrity and confidentiality** | All stages | Field-level classification; access controls on golden record store |
| **Accountability** | MARK | Complete, append-only lineage trail for every processing decision |

**Article 17 — Right to Erasure ("Right to be Forgotten"):**
AURUM's cross-domain entity link table makes erasure technically feasible at scale. When a data subject requests deletion:
1. Query MARK by subject identifier → all golden record IDs returned
2. Query cross-domain links → all domain records for this entity
3. Execute deletion cascade: golden records deleted, reverse sync to source systems
4. Log `ERASURE_EXECUTED` lineage event with timestamp and actor

**Article 30 — Records of Processing Activities:**
MARK's lineage store is Article 30 compliance made continuous. No manual RoPA maintenance — every processing activity is recorded automatically.

---

### 🇬🇧 UK GDPR (post-Brexit, 2021)

Substantially equivalent to EU GDPR with UK-specific adjustments. Same AURUM mapping applies. The UK ICO (Information Commissioner's Office) is the supervisory authority.

---

### 🇺🇸 United States — Patchwork of State Laws

No federal data protection law. State laws apply:

| Law | Jurisdiction | Key MDM Implication |
|-----|-------------|---------------------|
| **CCPA / CPRA** | California | Right to know, right to delete, right to correct — all supported by AURUM's MARK lineage + steward workflows |
| **VCDPA** | Virginia | Similar to CCPA — data minimisation, purpose limitation |
| **CPA** | Colorado | Data protection assessments required for high-risk processing |
| **HIPAA** | Federal (healthcare) | PHI in customer or employee master data requires encryption at rest/transit and access logging — AURUM's field classification supports PHI tagging |
| **GLBA** | Federal (financial) | Financial customer data protection — counterparty and customer MDM must implement safeguards |
| **SOX** | Federal (public companies) | Financial master data (vendors, counterparties) must have audit trails — MARK satisfies this |

**Practical note:** For US deployments, the patchwork is the problem. AURUM's field-level classification system should encode state-of-residency as a metadata tag on customer records, enabling jurisdiction-aware processing rules.

---

### 🇮🇳 India — DPDP Act (Digital Personal Data Protection Act, 2023)

India's first comprehensive data protection law. Key MDM implications:

| Provision | AURUM Implication |
|-----------|------------------|
| **Data localisation** (certain categories) | Personal data of Indian residents may require India-based processing for certain sensitive categories. AURUM deployments must support geographic data residency routing. |
| **Consent management** | Consent must be specific, informed, unconditional. AURUM's customer domain must store consent flags and expiry — survivorship rules must not publish personal data where consent has expired. |
| **Data Principal rights** | Access, correction, erasure — all supported by MARK. |
| **Significant Data Fiduciaries** | Large-scale processors face additional obligations. AURUM's complete lineage trail and DQ reporting satisfy the accountability requirements. |

---

### 🇨🇳 China — PIPL (Personal Information Protection Law, 2021) + DSL (Data Security Law, 2021)

China operates two parallel frameworks with significant MDM implications:

| Law | Key MDM Implication |
|-----|---------------------|
| **PIPL** | Consent-based processing, purpose limitation, data minimisation — same principles as GDPR. Separate consent required per processing purpose. |
| **DSL — Data Classification** | China classifies data as Core / Important / General. Core data (national security, critical industries) cannot leave China. Important data requires security assessment for cross-border transfer. AURUM's field classification must encode Chinese data categories for deployments serving Chinese operations. |
| **Data localisation** | Personal information of Chinese residents processed by Critical Information Infrastructure Operators (CIIO) must be stored in China. Cross-border transfer requires PIPL assessment. |
| **Algorithmic transparency** | AI-driven decisions (including AURUM's ML-based anomaly detection and matching) may require algorithmic transparency documentation under China's Algorithm Recommendation Regulations. AURUM's explainable scoring addresses this. |

---

### 🇸🇬 Singapore — PDPA (Personal Data Protection Act, 2012, amended 2020)

Mature, principles-based framework. Notably includes:
- **Do Not Call (DNC) registry** — customer MDM must integrate DNC checks before marketing use of phone data
- **Data portability obligation** — golden records must be exportable in structured format on subject request
- **Deemed consent** — implicit consent rules affect how customer data can be used without explicit opt-in

AURUM's golden record store is the right architectural layer for DNC status, portability export, and consent tracking.

---

### 🇦🇺 Australia — Privacy Act (1988, amended 2022)

The **Australian Privacy Principles (APPs)** govern personal data. Key MDM implications: data quality obligation (APP 10 — directly mandating MDM practices), access and correction rights (APP 12/13 — MARK lineage enables both), and cross-border disclosure restrictions (APP 8).

---

### 🌍 Africa — Emerging Frameworks

| Country | Framework | Status |
|---------|-----------|--------|
| South Africa | **POPIA** (Protection of Personal Information Act) | In force since 2021. Similar to GDPR. Operator/responsible party distinction maps to AURUM's source system vs golden record architecture. |
| Kenya | **DPA** (Data Protection Act, 2019) | In force. Principles-based, similar to GDPR. |
| Nigeria | **NDPR** (Nigeria Data Protection Regulation, 2019) | In force. NITDA enforces. |
| Ghana | **DPA** (Data Protection Act, 2012) | In force. One of Africa's earliest frameworks. |
| Rwanda | **Law No. 058 of 2021** | In force. |

AURUM's lineage store and field classification model provide a compliance-ready foundation for African deployments. The continent is rapidly converging toward GDPR-equivalent standards — building for GDPR compliance from day one is the right long-term strategy.

---

## Part 3 — AURUM's Compliance Architecture: What's Built, What's Needed

### ✅ What AURUM Provides Today

| Compliance Capability | AURUM Component | Relevant Frameworks |
|----------------------|-----------------|---------------------|
| Data accuracy evidence | UNEARTH DQ profiling | GDPR Art 5(d), UAE PDPL, KSA PDPL, Qatar PDPL, ADDA, DDA |
| Deduplication & golden record | REFINE matching + survivorship | All frameworks' accuracy obligations |
| Complete processing audit trail | MARK lineage store | GDPR Art 30, NDMO, SOX, UAE PDPL |
| Subject access request support | MARK lineage query | GDPR Art 15, CCPA, DPDP, POPIA |
| Erasure traceability | MARK cross-domain link + reverse sync | GDPR Art 17, UAE PDPL, KSA PDPL |
| Field-level profiling | ASSAY schema inspector | All classification frameworks |
| DQ score reporting | UNEARTH profiling summary | ADDA DQ standards, NDMO DQ dimensions |
| AI-generated rules with human review | LLM rule generator + AST guard | Algorithmic transparency requirements |
| Explainable matching scores | Composite scorer with named components | GDPR automated decision-making, China Algorithm Regulations |

### 🔧 What Needs to Be Built (v0.2.0 roadmap)

| Capability Needed | Frameworks Requiring It | AURUM Roadmap |
|------------------|------------------------|---------------|
| **Field-level data classification tags** (Confidential / Internal / Public) | ADDA, DDA, NDMO, PIPL DSL | ASSAY schema extension |
| **Jurisdiction-aware UNFURL** — don't publish Saudi personal data to non-KSA consumers | KSA PDPL, Qatar PDPL, PIPL, DPDP | UNFURL publisher policy engine |
| **Consent flag storage + expiry** | GDPR, DPDP, PIPL | Customer domain model extension |
| **Retention TTL policies** on golden records | GDPR Art 5(e), UAE PDPL, KSA PDPL | MARK retention manager |
| **Data residency routing** — which golden records stay in which region | KSA, China, India, UAE | Golden record store partitioning |
| **DNC registry integration** | Singapore PDPA | Customer domain enrichment |
| **Sensitivity classification for special categories** | GDPR Art 9, Qatar PDPL, KSA PDPL | Schema tagging + survivorship guard |
| **ADDA authoritative source registry integration** | ADDA Data Policy | Survivorship rule configurator |
| **Dubai Data Space publisher connector** | DDA | UNFURL plugin |

---

## Part 4 — The Global MDM Compliance Posture

For any organisation operating across multiple jurisdictions, the compliance challenge is not "which law applies" but "how do I build one MDM platform that satisfies all of them simultaneously."

AURUM's answer is **layered compliance architecture**:

```
Layer 1 — Universal Principles (all frameworks agree)
  ├── Accuracy:        UNEARTH + REFINE
  ├── Transparency:    MARK lineage
  ├── Accountability:  MARK + steward workflows
  └── Minimisation:    REFINE survivorship

Layer 2 — Regional Customisation (per-jurisdiction configuration)
  ├── UAE:    ADDA/DDA classification tags + federal PDPL consent flags
  ├── KSA:    NDMO classification + data localisation routing
  ├── Qatar:  NCSA sensitivity flags + cross-border transfer controls
  ├── EU/UK:  GDPR Article 30 RoPA + Art 17 erasure cascade
  ├── India:  DPDP consent expiry + localisation routing
  └── China:  PIPL/DSL classification + CIIO routing rules

Layer 3 — Sector-Specific Overlays (healthcare, finance, government)
  ├── Healthcare:  HIPAA PHI tagging + access logging
  ├── Finance:     GLBA + Basel III + EMIR counterparty requirements
  └── Government:  ADDA/DDA/NDMO authoritative source designation
```

The universal principles are implemented once in AURUM's core pipeline. Regional customisation is configuration, not code. Sector overlays are domain-specific rule sets.

This is the correct architecture for global MDM in 2025: one refinery, configurable compliance by jurisdiction.

---

## Summary: AURUM as a Compliance-Ready MDM Platform

AURUM is not a compliance tool. It is an MDM tool that is designed — from the lineage store up — to make compliance answerable.

The question every regulator asks is: **"Can you prove your data is accurate, lawfully processed, and traceable?"**

AURUM's answer, at every stage:
- **ASSAY:** We know exactly what came in, from where, when, and in what format.
- **UNEARTH:** We know what was wrong with it and what rules it failed.
- **REFINE:** We know every decision made to turn raw records into a golden record, and why.
- **UNFURL:** We know exactly what was published, to whom, and when.
- **MARK:** We can prove all of the above in a query that takes seconds.

That is what regulatory compliance looks like when MDM is done right.

---

*This document reflects data protection frameworks as understood at time of writing (May 2025). Laws change — always verify current requirements with qualified legal counsel in each jurisdiction.*

*— Nadia (Data Governance Lead), Tariq (Security & Compliance), AURUM Project*

# AURUM & Global Data Sovereignty
### How MDM Aligns with Data Protection Laws Across the GCC and the World

> *Authored by Nadia (Data Governance Lead) & Tariq (Security & Compliance) — AURUM Project*
> *Legal frameworks are cited for educational accuracy. This document is not legal advice.*
> *Always verify current requirements with qualified legal counsel in each jurisdiction.*

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

---

## Part 1 — The GCC: A Region of Rapidly Maturing Data Law

---

### 🇦🇪 UAE — A Federation of Data Jurisdictions

#### Federal — UAE Personal Data Protection Law (PDPL)
*Federal Decree-Law No. 45 of 2021 + Cabinet Resolution No. 33 of 2024*

📄 [Federal Decree-Law No. 45 of 2021 — Official Text (MOJ)](https://www.moj.gov.ae/assets/2022/Federal%20Decree%20Law%20No%2045%20of%202021%20on%20the%20Protection%20of%20Personal%20Data.pdf.aspx)
📄 [Cabinet Resolution No. 33 of 2024 — Executive Regulation](https://tdra.gov.ae/en/aict/affairs/data-protection)
📄 [UAE TDRA — Data Protection Portal](https://tdra.gov.ae/en/aict/affairs/data-protection)
📄 [u.ae — Personal Data Protection Overview](https://u.ae/en/information-and-services/justice-safety-and-the-law/cyber-safety-and-digital-security/personal-data-protection)

| Provision | AURUM Implication |
|-----------|------------------|
| **Data accuracy** (Art. 9) | REFINE stage — deduplication, survivorship, golden record assembly directly fulfils this |
| **Purpose limitation** | UNFURL publishes only to authorised consumers with documented purpose |
| **Data minimisation** | Survivorship selects minimum fields needed — not all 47 fields from all sources |
| **Subject access rights** | MARK lineage store — query by `source_id` or `email` → full provenance in seconds |
| **Right to erasure** | Golden record deletion cascades to all source systems via MARK cross-domain links |
| **Transfer restrictions** | UAE resident data cannot leave UAE without adequacy decision or consent — constrains where AURUM's golden record store is hosted |

---

#### Abu Dhabi — ADDA (Abu Dhabi Digital Authority)

📄 [ADDA Official Portal](https://add.gov.ae/en/Pages/default.aspx)
📄 [Abu Dhabi Data Policy — ADDA](https://add.gov.ae/en/ServicesandInformation/Legislation/Pages/Data-Policy.aspx)
📄 [Abu Dhabi Data Classification Framework](https://add.gov.ae/en/ServicesandInformation/Resources/Documents/Abu-Dhabi-Data-Classification-Policy.pdf)
📄 [Abu Dhabi Open Data Policy](https://add.gov.ae/en/ServicesandInformation/Legislation/Pages/Open-Data-Policy.aspx)
📄 [ADDA Data Sharing Framework](https://add.gov.ae/en/ServicesandInformation/Legislation/Pages/Data-Sharing-Framework.aspx)

| Provision | AURUM Implication |
|-----------|------------------|
| **Data classification** (Confidential / Internal / Public) | Every field in canonical schema should carry a classification tag — enforced at ASSAY |
| **Data quality standards** | AURUM's UNEARTH profiling maps directly to ADDA's DQ dimensions: completeness, accuracy, consistency, timeliness |
| **Data sharing agreements** | UNFURL must validate a DSA exists before publishing to any Abu Dhabi government consumer |
| **Reference data management** | Location domain should anchor to ADDA reference datasets (emirate codes, municipality codes) |
| **Authoritative source designation** | ADDA-designated authoritative sources must override AURUM's trust-score-based survivorship |

---

#### Dubai — Dubai Data Authority (DDA)
*Dubai Law No. 26 of 2015 (amended 2021)*

📄 [Dubai Data Authority — Official Portal](https://www.dda.gov.ae/en/home)
📄 [Dubai Data Law No. 26 of 2015 (Official Text)](https://www.dda.gov.ae/en/about/dubai-data-law)
📄 [Dubai Data Strategy](https://www.dda.gov.ae/en/initiatives/dubai-data-strategy)
📄 [Dubai Open Data Portal](https://opendata.dc.gov.ae)
📄 [Dubai Pulse — Smart City Data Platform](https://www.dubaipulse.gov.ae)

| Provision | AURUM Implication |
|-----------|------------------|
| **Mandatory data sharing** (government entities) | UNFURL must be configurable to push golden records to Dubai Data Space |
| **Data classification** (Shared / Restricted / Confidential) | Field-level classification enforced at ASSAY — different scheme from ADDA, dual-tagging required for cross-emirate operations |
| **Open data obligations** | Public-classified fields can be published to Dubai Open Data Portal via UNFURL |
| **Data residency** | Dubai government data must remain within UAE — cloud hosting must be UAE-based |
| **Smart Dubai AI alignment** | AURUM's MCP server enabling AI-agent-driven MDM aligns with Dubai's Smart City AI strategy |

---

### 🇸🇦 Saudi Arabia — Personal Data Protection Law (PDPL)
*Royal Decree M/19 of 1443H (2021) — in force September 2023*

📄 [Saudi PDPL — Official Text (SDAIA)](https://sdaia.gov.sa/en/SDAIA/about/Documents/Personal%20Data%20Protection%20Law%20En%20V2-2022.pdf)
📄 [SDAIA — Saudi Authority for Data and Artificial Intelligence](https://sdaia.gov.sa/en/default.aspx)
📄 [National Data Management Office (NDMO)](https://ndmo.sdaia.gov.sa/en/Pages/Default.aspx)
📄 [National Data Management Policy (NDMP)](https://ndmo.sdaia.gov.sa/en/Pages/NDMP.aspx)
📄 [National Data Governance Interim Regulations](https://sdaia.gov.sa/en/SDAIA/about/Documents/National-Data-Governance-Interim-Regulations-En.pdf)
📄 [PDPL Executive Regulations (2023)](https://sdaia.gov.sa/en/SDAIA/about/Documents/PDPL-Executive-Regulations-EN.pdf)

| Provision | AURUM Implication |
|-----------|------------------|
| **Explicit consent for sensitive data** | Health, financial, biometric fields must be flagged at ASSAY — survivorship must not include without documented consent |
| **Data localisation** | Saudi resident personal data must be stored within KSA — AURUM deployment must run on KSA-based infrastructure |
| **Cross-border transfer restrictions** | UNFURL must enforce jurisdiction-aware publishing — Saudi personal data cannot push to unapproved jurisdictions |
| **Data retention limits** | MARK must implement TTL policies — golden records flagged for deletion when relationship ends |
| **Individual rights** (access, correction, deletion) | MARK lineage enables all three — query, steward workflow, cascade deletion |
| **Data Officer requirement** | AURUM's stewardship model (Shazia/DQ, Nadia/Governance, Tariq/Compliance) maps to NDMO data officer roles |

**NDMO Data Classification Levels:** Top Secret / Secret / Confidential / Restricted / Public — must be encoded as field-level tags in AURUM's ASSAY schema mapping.

---

### 🇶🇦 Qatar — Personal Data Privacy Protection Law
*Law No. 13 of 2016 (amended by Law No. 13 of 2021)*

📄 [Qatar PDPL — Law No. 13 of 2016 (Official Gazette)](https://www.almeezan.qa/LawPage.aspx?id=6983&language=en)
📄 [Qatar Law No. 13 of 2021 — Amendment](https://www.almeezan.qa/LawPage.aspx?id=8976&language=en)
📄 [Ministry of Transport and Communications — Data Protection](https://www.motc.gov.qa/en/Pages/default.aspx)
📄 [National Cyber Security Agency (NCSA) Qatar](https://www.ncsa.gov.qa/en/Pages/default.aspx)
📄 [Qatar National Vision 2030 — Digital Transformation](https://www.gco.gov.qa/en/about-qatar/national-vision2030/)

| Provision | AURUM Implication |
|-----------|------------------|
| **Data quality obligation** | Controllers must ensure personal data is accurate, complete, up-to-date — this is the legal mandate for MDM |
| **Cross-border transfer** | Requires adequacy, consent, contractual safeguards, or vital interest — UNFURL must enforce |
| **Sensitive data categories** | Health, racial/ethnic origin, political opinion, religious belief, criminal history — stricter consent in survivorship |
| **Accountability** | MARK's lineage store is the accountability mechanism — every decision recorded, timestamped, attributed |

---

### 🇧🇭 Bahrain — Personal Data Protection Law
*Law No. 30 of 2018*

📄 [Bahrain PDPL — Law No. 30 of 2018 (Official Text)](https://www.legalaffairs.gov.bh/AdvancedSearchDetails.aspx?id=15696)
📄 [Bahrain Personal Data Protection Authority (PDPA)](https://www.pdpa.bh/en)
📄 [PDPA Guidance Documents](https://www.pdpa.bh/en/guidance)

Key MDM implications: data accuracy obligation, right of correction (steward workflow), transfer restrictions (whitelisted countries), retention limits (MARK TTL policies). Broadly aligned with GDPR principles — AURUM's GDPR mapping covers Bahrain requirements.

---

### 🇰🇼 Kuwait

📄 [Kuwait National Cybersecurity Strategy](https://www.nca.gov.kw/en)
📄 [Kuwait e-Government Authority](https://www.e.gov.kw/sites/kgoenglish/Pages/default.aspx)

Data protection legislation in active development. Design for GDPR-equivalent as a future-proof baseline. The *Law Regarding Electronic Communications and Transactions* provides partial coverage.

---

### 🇴🇲 Oman

📄 [Oman Cybersecurity Framework — NCSI](https://www.ncsi.gov.om/en)
📄 [Oman Electronic Transactions Law (Royal Decree 69/2008)](https://www.ita.gov.om/ITAPortal/MediaCenter/Publications.aspx)
📄 [Oman Personal Data Protection Law — Draft (2023)](https://www.ncsi.gov.om/en)

Oman's Personal Data Protection Law is in final stages. Organisations operating in Oman should design AURUM deployments for full GDPR compliance now — the Oman law will be closely aligned.

---

## Part 2 — Global Frameworks

---

### 🇪🇺 European Union — GDPR
*General Data Protection Regulation 2016/679 — in force May 2018*

📄 [GDPR — Full Official Text (EUR-Lex)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32016R0679)
📄 [European Data Protection Board (EDPB)](https://edpb.europa.eu/edpb_en)
📄 [EDPB Guidelines & Recommendations](https://edpb.europa.eu/our-work-tools/general-guidance/gdpr-guidelines-recommendations-best-practices_en)
📄 [EU Data Protection Supervisor](https://edps.europa.eu/edps_en)

**The 7 GDPR principles — mapped to AURUM:**

| GDPR Principle | AURUM Stage | How AURUM Supports It |
|---------------|-------------|----------------------|
| Lawfulness, fairness, transparency | ASSAY | Source consent records mapped at ingestion |
| Purpose limitation | UNFURL | Only publish to authorised consumers with documented purpose |
| Data minimisation | REFINE | Survivorship selects minimum necessary fields |
| Accuracy | UNEARTH + REFINE | DQ profiling + deduplication + golden record assembly |
| Storage limitation | MARK | Retention TTL policies on golden records |
| Integrity and confidentiality | All stages | Field classification + access controls |
| Accountability | MARK | Append-only lineage trail for every decision |

📄 [GDPR Article 17 — Right to Erasure](https://gdpr-info.eu/art-17-gdpr/)
📄 [GDPR Article 30 — Records of Processing Activities](https://gdpr-info.eu/art-30-gdpr/)

---

### 🇬🇧 United Kingdom — UK GDPR + Data Protection Act 2018

📄 [UK GDPR — ICO Guide](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/)
📄 [Data Protection Act 2018 — legislation.gov.uk](https://www.legislation.gov.uk/ukpga/2018/12/contents)
📄 [ICO — Information Commissioner's Office](https://ico.org.uk)
📄 [ICO Accountability Framework](https://ico.org.uk/for-organisations/accountability-framework/)

Substantially equivalent to EU GDPR. Same AURUM mapping applies. ICO is the supervisory authority.

---

### 🇺🇸 United States — Federal & State Patchwork

📄 [CCPA / CPRA — California Attorney General](https://oag.ca.gov/privacy/ccpa)
📄 [CPRA Full Text — California Legislative Information](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202120220AB1490)
📄 [Virginia CDPA — Virginia Legislative Information](https://law.lis.virginia.gov/vacode/title59.1/chapter53/)
📄 [Colorado CPA — Colorado AG](https://coag.gov/resources/colorado-privacy-act/)
📄 [HIPAA — HHS Official](https://www.hhs.gov/hipaa/for-professionals/index.html)
📄 [GLBA — FTC Overview](https://www.ftc.gov/business-guidance/privacy-security/gramm-leach-bliley-act)
📄 [SOX — SEC Overview](https://www.sec.gov/spotlight/sarbanes-oxley.htm)
📄 [IAPP US State Privacy Legislation Tracker](https://iapp.org/resources/article/us-state-privacy-legislation-tracker/)

| Law | Jurisdiction | Key MDM Implication |
|-----|-------------|---------------------|
| CCPA / CPRA | California | Right to know, delete, correct — all via MARK |
| VCDPA | Virginia | Data minimisation, purpose limitation |
| CPA | Colorado | Data protection assessments for high-risk processing |
| HIPAA | Federal (healthcare) | PHI tagging + access logging — ASSAY field classification |
| GLBA | Federal (financial) | Customer and counterparty data safeguards |
| SOX | Federal (public companies) | Vendor/counterparty audit trails — MARK satisfies this |

---

### 🇮🇳 India — Digital Personal Data Protection Act 2023

📄 [DPDP Act 2023 — Official Gazette (MeitY)](https://www.meity.gov.in/data-protection-framework)
📄 [DPDP Act Full Text — Ministry of Law and Justice](https://www.indiacode.nic.in/bitstream/123456789/19277/1/a2023-22.pdf)
📄 [MeitY — Ministry of Electronics and Information Technology](https://www.meity.gov.in)
📄 [Data Protection Board of India (framework)](https://www.meity.gov.in/data-protection-framework)

| Provision | AURUM Implication |
|-----------|------------------|
| Data localisation (certain categories) | India-based processing for sensitive categories — AURUM must support geographic residency routing |
| Consent management | Consent flags + expiry on customer domain — survivorship must not publish where consent expired |
| Data Principal rights | Access, correction, erasure — all via MARK |
| Significant Data Fiduciaries | Enhanced obligations — AURUM lineage and DQ reporting satisfy accountability requirements |

---

### 🇨🇳 China — PIPL + DSL + Cybersecurity Law

📄 [PIPL — Personal Information Protection Law (Full Text, NPC)](http://www.npc.gov.cn/npc/c30834/202108/a8c4e3672c74491a80b53a172bb753fe.shtml)
📄 [PIPL English Translation — China Law Translate](https://www.chinalawtranslate.com/en/personal-information-protection-law/)
📄 [DSL — Data Security Law (NPC)](http://www.npc.gov.cn/npc/c30834/202106/7c9af12f51334a73b56d7938f99a788a.shtml)
📄 [Cybersecurity Law 2017 — China Law Translate](https://www.chinalawtranslate.com/en/cybersecurity-law/)
📄 [CAC — Cyberspace Administration of China](https://www.cac.gov.cn)
📄 [Algorithm Recommendation Regulations (CAC)](https://www.cac.gov.cn/2022-01/04/c_1642894606364259.htm)

| Framework | Key MDM Implication |
|-----------|---------------------|
| PIPL | Consent-based, purpose limitation, minimisation — separate consent per purpose |
| DSL — Data Classification | Core / Important / General — Core data cannot leave China; Important requires security assessment for transfer |
| Localisation | CIIO-processed Chinese resident data must be stored in China |
| Algorithm transparency | AURUM's ML-based anomaly detection and matching requires explainability documentation |

---

### 🇸🇬 Singapore — Personal Data Protection Act (PDPA)
*PDPA 2012, amended 2020*

📄 [PDPA — Full Text (Singapore Statutes Online)](https://sso.agc.gov.sg/Act/PDPA2012)
📄 [PDPC — Personal Data Protection Commission](https://www.pdpc.gov.sg)
📄 [PDPC Advisory Guidelines](https://www.pdpc.gov.sg/Guidelines-and-Consultation/Guides)
📄 [Do Not Call Registry](https://www.pdpc.gov.sg/Help-and-Resources/2014/01/Do-Not-Call-Registry)

Key MDM implications: DNC registry integration (customer domain), data portability (golden records exportable on request), deemed consent rules affecting customer data use without explicit opt-in.

---

### 🇦🇺 Australia — Privacy Act 1988 (amended 2022)

📄 [Privacy Act 1988 — Federal Register of Legislation](https://www.legislation.gov.au/Details/C2022C00199)
📄 [Australian Privacy Principles (APPs)](https://www.oaic.gov.au/privacy/australian-privacy-principles)
📄 [OAIC — Office of the Australian Information Commissioner](https://www.oaic.gov.au)
📄 [Privacy Act Review Report 2022](https://www.ag.gov.au/rights-and-protections/publications/privacy-act-review-report)

Key: APP 10 (data quality — directly mandates MDM), APP 12/13 (access and correction via MARK), APP 8 (cross-border disclosure restrictions).

---

### 🌍 Africa — Emerging Frameworks

| Country | Framework | Official Link |
|---------|-----------|--------------|
| 🇿🇦 South Africa | POPIA (Protection of Personal Information Act) | [POPIA — SAFLII](https://www.saflii.org/za/legis/num_act/popia2013315/) · [Information Regulator](https://www.justice.gov.za/inforeg/) |
| 🇰🇪 Kenya | Data Protection Act 2019 | [DPA 2019 — Kenya Law](http://kenyalaw.org/kl/fileadmin/pdfdownloads/Acts/2019/TheDataProtectionAct__No24of2019.pdf) · [ODPC](https://www.odpc.go.ke) |
| 🇳🇬 Nigeria | Nigeria Data Protection Act 2023 | [NDPA — NITDA](https://nitda.gov.ng/nigeria-data-protection-act-2023/) · [NDPC](https://ndpc.gov.ng) |
| 🇬🇭 Ghana | Data Protection Act 2012 | [DPA 2012 — Ghana Law](https://www.dataprotection.org.gh/sites/default/files/act843.pdf) · [Data Protection Commission](https://www.dataprotection.org.gh) |
| 🇷🇼 Rwanda | Law No. 058 of 2021 | [Law 058/2021 — Rwanda Official Gazette](https://www.minijust.gov.rw/publications/laws) |
| 🇪🇬 Egypt | Personal Data Protection Law No. 151 of 2020 | [Law 151/2020 — MCIT](https://mcit.gov.eg/en/About/Pages/legalFramework.aspx) |
| 🌍 AU Framework | African Union Convention on Cyber Security | [Malabo Convention — African Union](https://au.int/en/treaties/african-union-convention-cyber-security-and-personal-data-protection) |

---

### 🌐 International Standards & Bodies

| Body / Standard | Link | Relevance to AURUM |
|----------------|------|-------------------|
| GLEIF — Global LEI Foundation | [gleif.org](https://www.gleif.org) | LEI validation for Counterparty domain |
| GS1 — Global Barcode Standards | [gs1.org](https://www.gs1.org) | EAN/UPC barcode validation in Product domain |
| FATF — Financial Action Task Force | [fatf-gafi.org](https://www.fatf-gafi.org) | AML/CFT risk rating for Counterparty/Vendor |
| ISO/IEC 27001 — Information Security | [iso.org/isoiec-27001](https://www.iso.org/isoiec-27001-information-security.html) | Security controls for golden record store |
| ISO 8000 — Data Quality | [iso.org/standard/60805](https://www.iso.org/standard/60805.html) | DQ standards framework for UNEARTH stage |
| DAMA-DMBOK | [dama.org](https://www.dama.org/cpages/body-of-knowledge) | MDM governance framework reference |

---

## Part 3 — AURUM's Compliance Architecture

### ✅ What AURUM Provides Today

| Capability | AURUM Component | Frameworks |
|-----------|-----------------|------------|
| Data accuracy evidence | UNEARTH DQ profiling | GDPR Art 5(d), UAE PDPL, KSA PDPL, Qatar PDPL, ADDA, DDA |
| Deduplication & golden record | REFINE matching + survivorship | All accuracy obligations |
| Complete processing audit trail | MARK lineage store | GDPR Art 30, NDMO, SOX, UAE PDPL |
| Subject access request support | MARK lineage query | GDPR Art 15, CCPA, DPDP, POPIA |
| Erasure traceability | MARK + cross-domain links + reverse sync | GDPR Art 17, UAE PDPL, KSA PDPL |
| Field-level profiling | ASSAY schema inspector | All classification frameworks |
| DQ score reporting | UNEARTH profiling summary | ADDA DQ standards, NDMO DQ dimensions |
| AI-generated rules with human review | LLM rule generator + AST guard | Algorithmic transparency |
| Explainable matching scores | Composite scorer with named components | GDPR automated decisions, China Algorithm Regs |

### 🔧 Roadmap — v0.3.0

| Capability | Frameworks | AURUM Target |
|-----------|------------|-------------|
| Field-level classification tags | ADDA, DDA, NDMO, PIPL DSL | ASSAY schema extension |
| Jurisdiction-aware UNFURL | KSA PDPL, Qatar PDPL, PIPL, DPDP | UNFURL publisher policy engine |
| Consent flag storage + expiry | GDPR, DPDP, PIPL | Customer domain model extension |
| Retention TTL policies | GDPR Art 5(e), UAE PDPL, KSA PDPL | MARK retention manager |
| Data residency routing | KSA, China, India, UAE | Golden record store partitioning |
| DNC registry integration | Singapore PDPA | Customer domain enrichment |
| ADDA authoritative source integration | ADDA Data Policy | Survivorship rule configurator |
| Dubai Data Space publisher connector | DDA | UNFURL plugin |

---

## Part 4 — Layered Compliance Architecture

```
Layer 1 — Universal Principles (all frameworks agree)
  ├── Accuracy:       UNEARTH + REFINE
  ├── Transparency:   MARK lineage
  ├── Accountability: MARK + steward workflows
  └── Minimisation:   REFINE survivorship

Layer 2 — Regional Configuration (per-jurisdiction)
  ├── UAE:    ADDA/DDA classification + federal PDPL consent flags
  ├── KSA:    NDMO classification + data localisation routing
  ├── Qatar:  NCSA sensitivity flags + cross-border transfer controls
  ├── EU/UK:  GDPR Art 30 RoPA + Art 17 erasure cascade
  ├── India:  DPDP consent expiry + localisation routing
  └── China:  PIPL/DSL classification + CIIO routing rules

Layer 3 — Sector Overlays (healthcare, finance, government)
  ├── Healthcare:  HIPAA PHI tagging + access logging
  ├── Finance:     GLBA + Basel III + EMIR counterparty requirements
  └── Government:  ADDA/DDA/NDMO authoritative source designation
```

Universal principles are implemented once in AURUM's core pipeline. Regional customisation is configuration, not code. Sector overlays are domain-specific rule sets.

---

## Summary

The question every regulator asks: **"Can you prove your data is accurate, lawfully processed, and traceable?"**

AURUM's answer at every stage:
- **ASSAY:** We know exactly what came in, from where, when, and in what format
- **UNEARTH:** We know what was wrong with it and what rules it failed
- **REFINE:** We know every decision made to produce the golden record, and why
- **UNFURL:** We know exactly what was published, to whom, and when
- **MARK:** We can prove all of the above in a query that takes seconds

That is what regulatory compliance looks like when MDM is done right.

---

*Frameworks cited as of May 2025. Laws change — verify current requirements with qualified legal counsel.*
*— Nadia (Data Governance Lead), Tariq (Security & Compliance), AURUM Project*

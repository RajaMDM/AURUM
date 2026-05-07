# AURUM Diagrams

Visual reference for the AURUM MDM pipeline, decision model, gbrain memory layer, and dream cycle.  
All diagrams render natively on GitHub.

---

## 1. The AURUM Pipeline — 5-Stage Intelligent Refinery

```mermaid
flowchart LR
    subgraph SRC["📥 Source Systems"]
        direction TB
        CRM[CRM]
        ERP[ERP]
        ECOMM[eCommerce]
        LOY[Loyalty]
    end

    subgraph PIPE["⚙️ AURUM Pipeline"]
        direction LR
        A["🔍 ASSAY\nProfile & Map"]
        B["⚠️ UNEARTH\nDQ & Flag"]
        C["🔗 REFINE\nMatch & Merge"]
        D["📤 UNFURL\nPublish"]
        E["📋 MARK\nLineage"]
    end

    subgraph OUT["✨ Output"]
        direction TB
        GR[("Golden\nRecord Store")]
        LIN[(Lineage\nStore)]
    end

    SRC --> A
    A --> B
    B --> C
    C --> D
    D --> E
    D --> GR
    E --> LIN

    style A fill:#064e3b,stroke:#34d399,color:#fff
    style B fill:#7c2d12,stroke:#fb923c,color:#fff
    style C fill:#1e3a5f,stroke:#60a5fa,color:#fff
    style D fill:#4a1d96,stroke:#a78bfa,color:#fff
    style E fill:#831843,stroke:#f472b6,color:#fff
    style GR fill:#1e1b4b,stroke:#818cf8,color:#fff
    style LIN fill:#1e1b4b,stroke:#818cf8,color:#fff
```

---

## 2. Three-Tier Stewardship Decision Model

```mermaid
flowchart TD
    IN([📨 Exception Queue\n847 records]) --> ROUTE{AI Confidence\nScore}

    ROUTE -->|"> 0.95\nClear match"| T1["✅ TIER 1\nAuto-Resolve\nNo human needed"]
    ROUTE -->|"0.80 – 0.95\nProbable match"| T2["🤝 TIER 2\nAI Proposes\nSteward approves in 1 click"]
    ROUTE -->|"< 0.80\nAmbiguous"| T3["🧠 TIER 3\nHuman Judgment Only\nFull context surfaced"]

    T1 --> LOG["📋 Logged &\nAudit Trailed"]
    T2 --> REV{Steward\nDecision}
    REV -->|Approve| LOG
    REV -->|Reject| LOG
    REV -->|Investigate| T3
    T3 --> LOG

    LOG --> GR[("✨ Golden Record")]

    style IN fill:#1e293b,stroke:#64748b,color:#fff
    style T1 fill:#064e3b,stroke:#34d399,color:#fff
    style T2 fill:#1e3a5f,stroke:#60a5fa,color:#fff
    style T3 fill:#7c2d12,stroke:#fb923c,color:#fff
    style LOG fill:#1e1b4b,stroke:#818cf8,color:#fff
    style GR fill:#4a1d96,stroke:#a78bfa,color:#fff
```

---

## 3. AURUM + gbrain — The Memory Layer

```mermaid
flowchart TD
    subgraph PIPE["⚙️ AURUM Pipeline"]
        direction LR
        A[ASSAY] --> B[UNEARTH] --> C[REFINE] --> D[UNFURL] --> E[MARK]
    end

    subgraph BRAIN["🧠 gbrain Knowledge Graph"]
        direction LR
        DEC["📝 Stewardship\nDecisions"]
        DQ["⚠️ DQ Rule\nLineage"]
        ENT["🔗 Cross-Domain\nEntity Graph"]
        AUD["🔐 Compliance\nAudit Trail"]
    end

    subgraph CRON["🌙 Nightly Dream Cycle (2AM)"]
        direction LR
        P1[Entity Sweep] --> P2[AURUM Sync] --> P3[Health Check] --> P4[Pattern\nConsolidation]
    end

    PIPE -->|"write decisions"| BRAIN
    BRAIN -->|"read context"| PIPE
    CRON -->|"compounds nightly"| BRAIN

    style PIPE fill:#0f172a,stroke:#34d399,color:#fff
    style BRAIN fill:#0f172a,stroke:#a78bfa,color:#fff
    style CRON fill:#0f172a,stroke:#fbbf24,color:#fff
```

---

## 4. The Nightly Dream Cycle — 4 Phases

```mermaid
flowchart LR
    START(["🌙 2:00 AM\nDream Cycle Starts"]) --> P1

    P1["🔍 Phase 1\nEntity Sweep\nScan today\'s sessions\nCreate / enrich brain pages"]
    P2["📥 Phase 2\nAURUM Sync\nImport new docs\nEmbed into vector index"]
    P3["🏥 Phase 3\nHealth Check\nDoctor scan\nFlag stale embeddings"]
    P4["💡 Phase 4\nPattern Consolidation\nPromote signals\nto durable knowledge"]

    P1 --> P2 --> P3 --> P4 --> END

    END(["☀️ Morning\nBrain smarter\nthan yesterday"])

    style START fill:#1e1b4b,stroke:#818cf8,color:#fff
    style P1 fill:#064e3b,stroke:#34d399,color:#fff
    style P2 fill:#1e3a5f,stroke:#60a5fa,color:#fff
    style P3 fill:#7c2d12,stroke:#fb923c,color:#fff
    style P4 fill:#4a1d96,stroke:#a78bfa,color:#fff
    style END fill:#78350f,stroke:#fbbf24,color:#fff
```

---

## 5. The Compounding Brain — Knowledge Growth Over Time

```mermaid
timeline
    title AURUM gbrain — Institutional Knowledge Growth
    Week 1   : 60 pages indexed
             : 208 chunks embedded
             : Keyword + semantic search live
    Month 1  : 200+ pages
             : Decisions logged
             : Graph links forming
    Month 3  : Patterns emerging
             : Cross-session insights auto-surfaced
             : Dream cycle compounding nightly
    Month 6  : Brain knows your MDM domain
             : Better context than any new hire
    Year 1   : Full institutional intelligence
             : Searchable, auditable, AI-queryable
```

---

*AURUM v0.2.0 — github.com/RajaMDM/AURUM*

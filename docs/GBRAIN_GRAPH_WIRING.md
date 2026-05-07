# How to Wire the gbrain Knowledge Graph for AURUM

> **Problem identified by a colleague:**
> *"gbrain has PGLite as storage. One decision/memory/row is not associated with other thoughts. Each memory is individual. How it is associated with other memory/project/domain/entity is missing. This is something a graph database does."*

They are right. And here is the solution.

---

## The Problem — Plain English

By default, gbrain stores pages like books on a shelf. Each book exists. But there are no threads connecting them. You can read a book. You cannot follow a thread from one book to the next.

A graph database solves this by storing **relationships** (edges) alongside **facts** (nodes). gbrain has a full graph engine built in — typed links, recursive traversal, backlink boost in search. It just needs to be explicitly wired.

---

## gbrain's Graph Engine — What Already Exists

gbrain is NOT a flat document store. Under the hood it has:

| Capability | Command | What it does |
|---|---|---|
| Typed links | `gbrain link A B --type T` | Creates a directed edge A→B with type T |
| Backlinks | `gbrain backlinks slug` | Shows everything pointing TO a page |
| Graph traversal | `gbrain graph slug --depth 2` | Walks the graph N hops from a page |
| Graph-query | `gbrain graph-query slug` | Edge traversal with type/direction filters |
| Backlink boost | Built into `gbrain query` | Well-connected pages rank higher in search |

The graph is there. It needs feeding.

---

## The Solution — Three Things

### 1. Use typed links explicitly

```bash
# A use case belongs to a domain
gbrain link uc-c02-cross-channel-merge customer-domain --type belongs-to

# Two domains are cross-domain connected
gbrain link customer-domain vendor-domain --type cross-domain

# A decision was made by a steward
gbrain link decision-merge-cust-00142 steward-jin --type approved-by

# A DQ rule applies to a domain
gbrain link dq-rule-phone-uae-format customer-domain --type applies-to
```

### 2. Use typed frontmatter in every page

```markdown
---
title: UC-C02 Cross-Channel Merge
type: use-case        ← makes it queryable by type
domain: customer      ← structured field
tags: [merge, loyalty, survivorship]
---
```

### 3. Traverse the graph after querying

```bash
# Start from a domain — see everything connected
gbrain graph customer-domain --depth 2

# Find all use cases linked to an entity  
gbrain query "Apex Group dual role"

# Check what points to a page (backlinks)
gbrain backlinks vendor-domain
```

---

## AURUM Link Type Schema

Use these consistent link types across all AURUM brain pages:

| Type | Meaning | Example |
|---|---|---|
| `belongs-to` | Use case belongs to a domain | UC-C02 → Customer Domain |
| `cross-domain` | Domain overlaps with another | Customer ↔ Vendor |
| `approved-by` | Decision approved by steward | Merge decision → Jin |
| `applies-to` | Rule applies to a domain/entity | DQ Rule → Customer Domain |
| `resolved-by` | Conflict resolved by a use case | Entity conflict → UC-CP01 |
| `governed-by` | Compliance framework applies | Customer Domain → UAE PDPL |
| `related` | General relationship | UC-C02 ↔ UC-CP01 |
| `governs` | Schema/convention governs pages | Graph Schema → All Domains |

---

## Current Graph State (After Wiring)

```
Pages:  67    ← 61 AURUM docs + 6 typed brain pages
Links:  11    ← cross-domain, belongs-to, governs edges
Tags:   19    ← domain, use-case, convention types

Graph traversal from customer-domain (depth 2):
  customer-domain
  ├──[cross-domain]──► vendor-domain
  │                    └──[cross-domain]──► counterparty-domain
  └──[cross-domain]──► counterparty-domain

Backlinks to vendor-domain:
  ← customer-domain [cross-domain]
  ← uc-cp01-dual-role-detection [cross-domain]
  ← gbrain-graph-schema [governs]
```

---

## The Answer to Your Colleague's Question

gbrain is not a pure graph database like Neo4j. It is a **document store with a graph layer on top**.

The difference:

| | Neo4j / graph DB | gbrain |
|---|---|---|
| Primary storage | Graph (nodes + edges native) | Documents (pages) |
| Relationships | First-class, automatic | Explicit, via `gbrain link` |
| Query language | Cypher | `gbrain graph-query` + hybrid search |
| Semantic search | No | Yes — vector embeddings |
| Setup | Server, schema design | Zero-config, one file |

**gbrain's advantage over a pure graph DB:** it combines graph traversal WITH semantic search AND vector embeddings. You can ask *"what is related to customer merges?"* in plain English AND traverse the graph from a specific node. A pure graph DB gives you one or the other.

**The discipline required:** every page written into gbrain should include explicit `gbrain link` calls to connect it to related pages. This is a writing convention, not a technical limitation.

---

## Dream Cycle — Auto-Linking Going Forward

The nightly dream cycle (2 AM) has been updated to:
1. Extract any new `[[wiki-links]]` from imported pages
2. Run `gbrain extract links --source db` to backfill
3. Tag new pages with domain/type metadata
4. Log a link count in the health report

The graph will compound automatically as new decisions, use cases, and stewardship notes are added.

---

*AURUM v0.2.0 · gbrain v0.28.6 · github.com/RajaMDM/AURUM*

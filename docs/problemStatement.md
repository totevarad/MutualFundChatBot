# Mutual Fund FAQ Assistant — Problem Statement

> **Facts-Only Q&A · No Investment Advice**

---

## Overview

The objective of this project is to build a **facts-only FAQ assistant** for mutual fund schemes, using **Groww** as the reference product context. The assistant will answer objective, verifiable queries related to mutual funds by retrieving information exclusively from official public sources, such as **AMC (Asset Management Company) websites**, **AMFI**, and **SEBI**.

The system must **strictly avoid** providing investment advice, opinions, or recommendations. Every response must include a single, clear source link and adhere to defined constraints around clarity, accuracy, and compliance.

---

## Objective

Design and implement a lightweight **Retrieval-Augmented Generation (RAG)**-based assistant that:

- Answers **factual queries** about mutual fund schemes
- Uses a **curated corpus** of official documents
- Provides **concise, source-backed** responses

---

## Target Users

| User Segment | Use Case |
|---|---|
| **Retail investors** | Comparing mutual fund schemes using verified facts |
| **Customer support & content teams** | Handling repetitive mutual fund queries efficiently |

---

## Scope of Work

### 1. Corpus Definition

- Select **one Asset Management Company (AMC)**
- Choose **3–5 mutual fund schemes**, ensuring category diversity (e.g., large-cap, flexi-cap, ELSS)
- Collect **15–25 official public URLs**, including:

| Source Type | Description |
|---|---|
| Scheme Factsheets | Fund performance, portfolio, and key metrics |
| KIM | Key Information Memorandum |
| SID | Scheme Information Document |
| AMC FAQ / Help Pages | Common questions and support articles |
| AMFI / SEBI Guidance Pages | Regulatory guidelines and investor education |
| Statement & Tax Guides | How to download statements or capital gains reports |

---

### 2. FAQ Assistant Requirements

The assistant must answer **facts-only queries**, such as:

- Expense ratio of a scheme
- Exit load details
- Minimum SIP amount
- ELSS lock-in period
- Riskometer classification
- Benchmark index
- Process to download statements or capital gains reports

#### Response Format Rules

Every response **must** adhere to the following:

| Rule | Requirement |
|---|---|
| **Length** | Maximum of **3 sentences** |
| **Citation** | Exactly **one citation link** per response |
| **Footer** | `"Last updated from sources: <date>"` |

---

### 3. Refusal Handling

The assistant must **refuse** non-factual or advisory queries, such as:

> *"Should I invest in this fund?"*
> *"Which fund is better?"*

#### Refusal Response Guidelines

- Be **polite** and clearly worded
- Reinforce the **facts-only limitation**
- Provide a relevant **educational link** (e.g., AMFI or SEBI resource)

---

### 4. User Interface (Stitch SmartInvest AI Assistant Theme)

The UI must follow the **Nocturnal Growth** theme specs, creating a high-performance dark-mode interface:

- A **Welcome Message** with quick-access cards
- **Three clickable example questions** styled as cards (e.g. "What is an SIP?", "Start Investing")
- An **Active Chat View** with user/assistant bubbles, suggested follow-ups, and a loading typing indicator
- A persistent regulatory **advisory disclaimer** at the bottom:
  > **"Regulatory Advisory: Mutual Fund investments are subject to market risks, read all scheme related documents carefully... This AI assistant provides general information and should not be construed as personalized financial advice."**
- A collapsible **Left Sidebar** with conversation history and "New Conversation" button
- An animated **Market Ticker** scrolling key indices (NIFTY 50, SENSEX, etc.)
- Shifting background colors with `animated-mesh-bg` gradient and thin scrollbars

---

## Constraints

### Data and Sources

- Use **only official public sources** (AMC, AMFI, SEBI)
- **Do not** use third-party blogs or aggregator websites

### Privacy and Security

> [!CAUTION]
> The system must **never** collect, store, or process any of the following:

- PAN or Aadhaar numbers
- Account numbers
- OTPs
- Email addresses or phone numbers

### Content Restrictions

- ❌ No investment advice or recommendations
- ❌ No performance comparisons or return calculations
- ✅ For performance-related queries, provide a **link to the official factsheet only**

### Transparency

- Responses must be **short, factual, and verifiable**
- Every answer must include a **source link** and **last updated date**

---

## Expected Deliverables

### README Document

| Section | Details |
|---|---|
| Setup instructions | How to install and run the assistant |
| Selected AMC and schemes | The chosen AMC and 3–5 fund schemes |
| Architecture overview | RAG approach and system design |
| Known limitations | Edge cases, coverage gaps, data freshness |

### Disclaimer Snippet

> **"Facts-only. No investment advice."**

---

## Success Criteria

| # | Criterion |
|---|---|
| 1 | ✅ Accurate retrieval of factual mutual fund information |
| 2 | ✅ Strict adherence to facts-only responses |
| 3 | ✅ Consistent inclusion of valid source citations |
| 4 | ✅ Proper refusal of advisory queries |
| 5 | ✅ Clean, minimal, and user-friendly interface |

---

## Summary

> The goal is to build a **trustworthy, transparent, and compliant** mutual fund FAQ assistant that prioritizes **accuracy over intelligence**. The system should ensure that users receive only **verified, source-backed financial information**, without any advisory bias or speculative content.

# AppUnik Campaign Tracker

**Company:** AppUnik (services.appunik.com)  
**Campaign:** 90-day inbound BD campaign — Series B companies in USA, Australia, Canada, Ireland, Finland  
**Goal:** Senior engineering staff augmentation, dedicated product squads, fixed-price product builds  
**Start Date:** April 15, 2026  
**CTA:** Book a Scale Diagnostic → services.appunik.com

---

## How This Repo Works

A Claude AI agent runs every day at **12:00 PM IST** and:

1. Reads yesterday's completion status from your Telegram replies
2. Reads `progress.json` to load campaign context
3. Composes today's brief (tasks, content prompt, BD action, posting times)
4. Sends it to your Telegram
5. Updates `progress.json` with today's data
6. Every Sunday: writes a full weekly report to `weekly-reports/`

You reply to the Telegram bot with: `Done: [tasks] | Skipped: [tasks] | Note: [anything]`

The agent reads that the next day and adjusts the brief accordingly.

---

## Campaign Progress

| Week | Country | Posts | DMs | Calls | Score |
|------|---------|-------|-----|-------|-------|
| 1 | USA — SaaS | — | — | — | — |
| 2 | USA — FinTech | — | — | — | — |
| 3 | USA — HealthTech/EdTech | — | — | — | — |
| 4 | USA — Consolidation | — | — | — | — |
| 5 | Australia — FinTech/SaaS | — | — | — | — |
| 6 | Australia — HealthTech/D2C | — | — | — | — |
| 7 | Canada — AI/SaaS | — | — | — | — |
| 8 | Canada — FinTech/D2C | — | — | — | — |
| 9 | Ireland — FinTech/RegTech | — | — | — | — |
| 10 | Ireland — Enterprise SaaS | — | — | — | — |
| 11 | Finland — CleanTech/MedTech | — | — | — | — |
| 12 | Finland — Gaming + Wrap | — | — | — | — |

---

## Cumulative Stats

| Metric | Count |
|--------|-------|
| Posts published | 0 |
| LinkedIn followers gained | 0 |
| CTO connections made | 0 |
| DMs sent | 0 |
| Scale Diagnostic calls booked | 0 |
| Signed engagements | 0 |

---

## How to Reply to the Bot

After completing tasks, message your Telegram bot:

```
Done: LinkedIn post, DM outreach
Skipped: YouTube Short
Note: 3 connection requests accepted, 1 CTO replied
```

The agent reads this the next day and picks up where you left off.

---

## Campaign Strategy

- **Target:** Series B companies (raised last 90 days, 50–200 employees)
- **Countries:** USA (Month 1) → Australia + Canada (Month 2) → Ireland + Finland (Month 3)
- **Positioning:** Senior-only engineering. Embedded in your sprint in 2 weeks. No procurement. No juniors.
- **Proof:** Dell, Autodesk, Kaplan, FIS Global
- **BD Model:** Cognizant/Infosys growth playbook — content warms the room, relationships fill the pipeline

---

## Files in This Repo

| File | Purpose |
|------|---------|
| `README.md` | This file — campaign overview and live progress |
| `agent-instructions.md` | Full daily agent instructions (fetched by bot every day) |
| `progress.json` | Machine-readable daily state (updated by agent) |
| `campaign-log.md` | Human-readable running log of every day |
| `weekly-reports/` | Sunday weekly BD review reports |

---

*Managed by Claude AI agent — AppUnik-BD-Command-Center*  
*Trigger ID: trig_012G5t5WCPjRHP7KjV9dVPH2*

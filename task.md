# task.md — Active TODO List
# Agent: update this before ending every session. No exceptions (R5).

## 🔴 In Progress
- [ ] Task 2.6: APScheduler Setup (`backend/notifications/scheduler.py`) — Set up background cron jobs for daily depletion checks and price tracking.

## 🟡 Up Next
- [ ] Task 2.7: Week 2 Integration Test — Run curl verifications defined in the plan.
- [ ] Task 3.1: Twilio WhatsApp Sandbox Configuration — Set up the Twilio sandbox API credentials in `.env`.
- [ ] Task 3.2: WhatsApp Webhook (`backend/notifications/whatsapp.py`) — Handle incoming replies to interface with the LangGraph Restock Agent.
- [ ] Task 3.3: Wire remaining frontend pages (`recipes/`, `price-alerts/`) to actual live FastAPI endpoints.

## 🟢 Done
- [x] Task 1.1-1.3: Project Foundation & Database Schema — [2026-05-16]
- [x] Task 1.4-1.6: Mock MCP Server, Seed Data & Sync Service — [2026-05-16]
- [x] Task 1.7: Prophet Consumption Model Builder — [2026-05-16]
- [x] Task 1.8: FastAPI Main App Initialization — [2026-05-16]
- [x] Task 2.1: Anomaly Detector (Travel, Guests, Dietary shifts) — [2026-05-16]
- [x] Task 2.2: Confidence Scorer (regularity × 0.6 + data × 0.4) — [2026-05-16]
- [x] Task 2.3: Alert Trigger Logic (depletion check + de-duplication + REST API) — [2026-05-16]
- [x] Task 2.4: Household Profiler (`backend/ml/household_profiler.py`) — Benchmark composition inference & background rebuilding chained to endpoints — [2026-05-17]
- [x] Task 2.5: LangGraph Restock Agent (`backend/agents/restock_agent.py`) — Stateful conversation graph with Swiggy MCP tools & ambiguity resolution — [2026-05-17]
- [x] Frontend UI Overhaul — Redesigned Home, Household, Predictions, Recipes, and Price Alerts with modern Industrial Utilitarian aesthetics, SVG sparklines, and depletion progress bars — [2026-05-17]
- [x] Codebase Synchronization & Lint Fixes — Synced layout components to Next.js `<Link>`, escaped JSX apostrophes, tracked Python backend dependencies in `requirements.txt`, and resolved root package.json scripts — [2026-05-17]

## 🚫 Blocked
- [ ] Real Swiggy API access — blocked by: Swiggy Sandbox approval (using Mock for now)

## 💡 Backlog
- [ ] Expand recipe database to use dynamic external parser APIs.
- [ ] Add historical trend graphs to Price Intelligence using advanced SVG timelines.

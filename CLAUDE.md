# CLAUDE.md â€” Local Project Context

# Note: All AI behaviors, commands (@TDD, @GRILL), and context maintenance rules 
# are now globally enforced via ~/.gemini/config/AGENTS.md. Do not duplicate them here.

---

## 1. PROJECT IDENTITY

**Name:** Instamart Intelligence
**Goal:** Household AI that predicts what your kitchen needs before you run out.

**AI POINTER:** If you need database schemas, business logic, or third-party API details, you MUST autonomously read `ARCHITECTURE.md`. Do not guess.

## 2. TECH STACK

- **Frontend:** Next.js 15, React, Tailwind CSS v4
- **Backend:** FastAPI (Python), APScheduler
- **Database:** PostgreSQL + TimescaleDB (time-series), pgvector
- **Testing:** Pytest (16 tests, async SQLite in-memory)

## 3. LOCAL ARCHITECTURE RULES

1. Always use async database sessions (`AsyncSession`) for SQLAlchemy database queries.
2. All time-series prices and commodity tracker histories must reside in the `price_history` TimescaleDB hypertable.
3. LangGraph restock agent state transitions must be saved using PostgreSQL checkpointer persistence.
4. Verify code edits by running `pytest backend/tests/ -v` to ensure agent, ML, and API logic function correctly.
5. Keep mock MCP server responses synchronized with catalog items defined in `backend/seed/catalog.py`.

## 4. AI COMMAND CHEAT SHEET

| Command     | Skill Path / Action                                                                                                                                                                                              |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| @PLAN     | Standard agent planning mode. Create implementation_plan.md first.                                                                                                                                             |
| @TDD      | [mp-tdd/SKILL.md](file:///C:/Users/kwakh/.gemini/config/skills/mp-tdd/SKILL.md) — **Red-Green-Refactor.** Write failing tests first. Do not write implementation code until tests fail. |
| @GRILL    | [mp-grill-me/SKILL.md](file:///C:/Users/kwakh/.gemini/config/skills/mp-grill-me/SKILL.md) — **Relentless Interrogation.** Ask ONE question at a time to clarify architecture. Push back on bad ideas. DO NOT write code until alignment is reached. |
| @DIAGNOSE | [mp-diagnose/SKILL.md](file:///C:/Users/kwakh/.gemini/config/skills/mp-diagnose/SKILL.md) — **Scientific Method Bug Hunt.** 1. Build reproducer. 2. Form 3-5 hypotheses. 3. Instrument logging. 4. Fix only when proven. |
| @ZOOM     | [mp-zoom-out/SKILL.md](file:///C:/Users/kwakh/.gemini/config/skills/mp-zoom-out/SKILL.md) — **Architectural Mapping.** Stop coding. Map the codebase dependencies, data flow, and components before making sweeping changes. |
## 5. MISTAKES TO AVOID

_Autonomously updated by the AI whenever it encounters a project-specific error, compilation issue, or pattern mistake. Never repeat these._


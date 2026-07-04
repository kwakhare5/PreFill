# CLAUDE.md — Instamart Intelligence: Frontend
# LEAN CONTEXT FILE. Hard cap: 200 lines.
# This is the Next.js frontend subfolder of the Instamart Intelligence project.
# For full project context (backend, schema, decisions): read ../CLAUDE.md and ../ARCHITECTURE.md

---

## 1. PROJECT IDENTITY

**Name:** Instamart Intelligence — Frontend
**Parent project:** D:\Instamart Intelligence\
**Goal:** Next.js frontend for the Instamart grocery intelligence platform

**AI POINTER:** Full project context (DB schema, API, backend logic) is in the PARENT directory:
- `../CLAUDE.md` — full stack context
- `../ARCHITECTURE.md` — schema, decisions, API contracts

---

## 2. TECH STACK (Frontend only)

- **Framework:** Next.js (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Package manager:** npm

---

## 3. LOCAL RULES

1. Frontend only — no backend logic here
2. API calls go to the FastAPI backend (see ../CLAUDE.md for base URL)
3. App Router only — no Pages Router

---

## 4. DEV COMMANDS

- `npm run dev` — dev server
- `npm run build` — production build
- `npm run lint` — lint

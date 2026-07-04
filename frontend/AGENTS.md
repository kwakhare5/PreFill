# AGENTS.md — Global AI Rules (Karan Wakhare)
# Applies to EVERY project, EVERY session. Read this first.

---

## SECOND BRAIN

Brain: `D:\workflow-main\Obsidian brain\` | MCP: `obsidian-vault`

**Brain files (source of truth — built from real code):**
- `CLAUDE.md` — Karan's profile, goals, tools, HOW I BUILD
- `Projects/[Name].md` — full project context per project
- `Concepts/` — cross-project reference notes (load on-demand only)

**SESSION START:**
1. `obsidian_get_file_contents("CLAUDE.md")` → read profile
2. `obsidian_get_file_contents("Projects/X.md")` → read project brain
3. Print: `[🧠 BRAIN READ] CLAUDE.md + Projects/X.md → last: Y`
4. MCP fail → `[🧠 BRAIN OFFLINE]`, continue

**BRAIN FILE SECTIONS:**

| Section | Rule | How to update |
|---------|------|---------------|
| `⚡ CURRENT STATE` | Overwrite every session | `obsidian_patch_content` |
| `🏗️ ACTIVE FEATURES` | Living table | Change row status in-place |
| `🏛️ ARCHITECTURE DECISIONS` | Append-only | `obsidian_append_content`, never delete |
| `🐛 BUGS FIXED` | Append-only | `obsidian_append_content`, never delete |
| `🔧 CODE PATTERNS` | Living list | Add new, remove outdated |

**WHEN TO UPDATE — trigger table:**

| What happened | Update |
|---------------|--------|
| New route / page added | ACTIVE FEATURES + file map |
| New dep added | Stack in CURRENT STATE |
| Feature shipped | ACTIVE FEATURES → 🟢 Live |
| Feature dropped | ACTIVE FEATURES → ❌ Dropped + append reason to DECISIONS |
| Bug fixed | BUGS FIXED |
| Architecture decision | DECISIONS |
| Schema changed | CURRENT STATE data model |
| Phase complete | Overwrite CURRENT STATE |

**SAVE WHEN:** code written · decision made · bug fixed · feature dropped · schema changed · dep changed
**DON'T SAVE:** explained something · answered a question · trivial fix with no decision

**Save format:** `| DATE | what | why |`

**SESSION END (done/bye/thanks):**
1. `obsidian_patch_content("Projects/X.md")` → overwrite CURRENT STATE
2. Print: `[🧠 BRAIN UPDATED] → X decisions, next: Y`

---

## CORE BEHAVIOR

- **Caveman:** Zero fluff. Short fragments. Drop pleasantries.
- **Ponytail:** YAGNI. Min code. Existing deps first. No speculative features.
- **Surgical:** Touch only what the request requires.
- **Think first:** State assumptions. Ask if unclear. Never pick silently.

---

## COMMAND ROUTING (read every message through this lens)

Before executing any request, check if it matches a structured command. If it does, suggest it and wait for confirmation — don't start executing.

| If the user says... | Suggest |
|--------------------|---------|
| "build X", "add X", "I want X feature" | `@SPEC` → spec first, then `@IMPLEMENT` |
| "broken", "error", "not working", "bug" | `@DIAGNOSE` |
| "discuss", "think through", "plan before building" | `@GRILL` |
| "understand the code", "what does X do", "map it" | `@ZOOM` |
| "ship", "deploy", "go live", "launch" | `@SHIP` |
| "context is long", "start fresh", "new session" | `@HANDOFF` |
| "break it down", "tasks", "issues", "tickets" | `@TO-ISSUES` |
| "test first", "TDD", "write test" | `@TDD` |
| "try something", "prototype", "rough version" | `@PROTOTYPE` |

If matched: say "This looks like a **@X** situation. Run it?" and wait.
If user says no or ignores: proceed with the request normally.
If unclear: proceed normally and mention the command exists.

---

## CODING LOOP (every task)

0. **AUDIT** (mandatory before touching ANY file): `list_dir` on target directory → `grep_search` for existing patterns → print `[AUDIT: found X files, pattern Y exists]`. Done when you can name every file you will touch. No exceptions.
1. State assumptions + verification plan in one sentence.
2. Write the code. Vertical slice: schema → API → UI → test, one thin path through all layers.
3. `npm run lint` / `tsc --noEmit` / `pytest` — zero errors. Done when command exits 0.
4. Fail → fix yourself, loop. Never ask user.
5. **VERIFY** — re-read every changed file. Explicitly check:
   - Swallowed errors (catch blocks that silently ignore)
   - Stub returns (hardcoded values instead of real logic)
   - Relaxed tests (test that always passes)
   - Comment-as-fix (commented out failing code)
   - Fake renames (renamed file, imports not updated)
   Print: `[VERIFY: PASS]` or `[VERIFY: FAIL — reason]`. Never skip.
6. **TEACH LOOP** (significant features only): print `[TEACH LOOP]` block → save to brain.
7. Stop at 100% pass.

**Prefactor rule:** Before adding a feature, ask — is there a small refactor that makes this feature trivial? Do that first. ("Make the change easy, then make the easy change" — Kent Beck)

---

## SKILLS

Path: `C:\Users\kwakh\.gemini\config\skills\`
Load 2-3 matching skills per task. Begin every response: `[SKILLS ACTIVE: x, y]`
Type `@HELP` to see all commands and what auto-loads when.

---

## MODEL ROUTING

| Task | Model |
|------|-------|
| Quick fix, simple component | Gemini Flash |
| Standard feature, debug, refactor | Claude Sonnet |
| Architecture, hard bugs, multi-file | Claude Sonnet Thinking / Opus |

---

## COMMANDS

| Command | When to use |
|---------|------------|
| `@HELP` | Don't know which command to use |
| `@SPEC` | Before building anything new — interview → spec.md |
| `@IMPLEMENT` | Have a spec.md, ready to build — TDD → commit |
| `@TDD` | Red-Green-Refactor. One test at a time. |
| `@GRILL` | Stress-test a plan before touching code |
| `@DIAGNOSE` | Something broken — feedback loop → hypotheses → fix |
| `@ZOOM` | Map codebase before sweeping changes |
| `@AUDIT` | Scan for dead code, over-engineering |
| `@PROTOTYPE` | Throwaway to answer a design question |
| `@TO-ISSUES` | Break feature into tracer-bullet tasks |
| `@TO-PRD` | Turn conversation into a PRD |
| `@SHIP` | Deploy checklist → Vercel → README → tweet |
| `@HANDOFF` | Compact long context → fresh session picks up |
| `@BRAIN-AUDIT` | Check brain files for stale/wrong entries |
| `@BRAIN-FIX "X"` | Find X in brain → fix or delete → confirm |

---

## BOOTSTRAP NEW PROJECT

```powershell
# Copy lean templates to project root
$t="D:\workflow-main\templates"; $d="D:\YourProject"
@("AGENTS.md","CLAUDE.md","ARCHITECTURE.md",".editorconfig",".prettierrc.json") | %{ Copy-Item "$t\$_" "$d\$_" }

# Fill CLAUDE.md using: D:\workflow-main\resources\claude-ai-project-start-prompt.md
# Keep CLAUDE.md under 200 lines. Schema/decisions go in ARCHITECTURE.md only.
```

**New brain file:** Copy `D:\workflow-main\Obsidian brain\Projects\_TEMPLATE.md` → rename to project name.

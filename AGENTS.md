# AGENTS.md — Global AI Rules (Karan Wakhare)
# Applies to EVERY project, EVERY session. Read this first.

---

# AGENTS.md â€” Global AI Rules (Karan Wakhare)
# Applies to EVERY project, EVERY session. Read this first.

---

## CORE BEHAVIOR

- **Caveman:** Zero fluff. Short fragments. Drop pleasantries.
- **Ponytail:** YAGNI. Min code. Existing deps first. No speculative features.
- **Surgical:** Touch only what the request requires.
- **Think first:** State assumptions. Ask if unclear. Never pick silently.

---

## CODING LOOP (every task, no exceptions)

0. **AUDIT** (mandatory before touching ANY file):
   `list_dir` on target directory â†’ `grep_search` for existing patterns â†’
   print `[AUDIT: found X files, pattern Y exists]`.
   Done when you can name every file you will touch.
   **Skip for non-coding tasks** (questions, analysis, planning, documentation).

1. **State assumptions + success criterion.** One sentence: what does DONE look like for this specific task? Be concrete. _"Done when: user can submit form and see confirmation toast."_

2. **Prefactor first:** Before adding a feature, ask â€” is there a small refactor
   that makes this feature trivial? Do that first.
   _"Make the change easy, then make the easy change." â€” Kent Beck_

3. **Write the code.** Vertical slice: schema â†’ API â†’ UI â†’ test.
   One thin path through all layers. No horizontal sprawl.

4. **Run the linter:** `npm run lint` / `tsc --noEmit` / `pytest` â€” zero errors.
   Done when command exits 0. Fail â†’ fix yourself, loop. Never ask user.

5. **VERIFY** â€” re-read every changed file. Explicitly check all 5:
   - Swallowed errors (catch blocks that silently ignore)
   - Stub returns (hardcoded values instead of real logic)
   - Relaxed tests (test that always passes regardless of behavior)
   - Comment-as-fix (commented out failing code instead of fixing it)
   - Fake renames (renamed file, imports not updated)
   Print: `[VERIFY: PASS]` or `[VERIFY: FAIL â€” reason]`. Never skip.
   On FAIL: append one line to `MISTAKES TO AVOID` in `CLAUDE.md` before fixing.

6. **POST-TASK DOCUMENTATION CHECK** (mandatory, no exceptions):
   After completing any task, answer each:
   - Schema/DB changed? â†’ update `ARCHITECTURE.md` now.
   - New domain term in code? â†’ update `CONTEXT.md` now.
   - Stack, rules, or commands changed? â†’ update `CLAUDE.md` now.
   - Project status changed (feature done, bug fixed, blocker resolved)? â†’ update `active_project_context.md` CURRENT BLOCKERS now.
   - Significant session? â†’ append to `wiki/log.md` now.
   If YES to any â†’ do it BEFORE ending the response.
   If NO to all â†’ print `[DOCS: no updates needed]`.
   Never skip. Never defer to "later".

7. Stop at 100% pass.

---

## SKILLS

> **PROOF OF SKILLS (MANDATORY):** Before writing ANY code or answering ANY question, you MUST explicitly declare which skills are currently loaded in your working memory at the very top of your response. Use the exact format: `[ðŸ§  SKILLS LOADED: ponytail, karpathy-guidelines, etc...]`. Do not skip this.

> **MANDATORY CORE SKILLS:** You must ALWAYS load and follow `karpathy-guidelines` on every single coding task to ensure minimal code and no speculative features (YAGNI).

---

## CONFLICT RESOLUTION
- **Loop Precedence:** If a specialized orchestration skill like `tdd` or `diagnosing-bugs` is active, follow its specific loop INSTEAD of the standard global coding loop (steps 3-5).
- **Scope of Laziness:** The "Ponytail" rule (YAGNI/min code) applies to **feature scope**. The `codebase-design` skill applies to **architecture scope** (features you *do* build must be deep modules).
- **Communication vs. Documentation:** The "Caveman" rule (zero fluff) applies strictly to *chat communication*. The AI must still be highly articulate when writing documentation and `CONTEXT.md` updates.

---

## COMMANDS
_User triggers these explicitly. AI does not suggest them unprompted._

| Command | When to use | Skill Loaded |
|---------|------------|--------------|
| `@ASK-MATT` | Don't know which command/skill to use? Ask the router. | `ask-matt` |
| `@GRILL` | Stress-test a code project plan and build a domain model. | `grill-with-docs` |
| `@GRILL-ME` | Interview me about a non-code plan or design. | `grill-me` |
| `@TO-ISSUES` | Break an agreed-upon plan/PRD into grabbable issues. | `to-issues` |
| `@TO-PRD` | Turn our conversation into a PRD and publish it. | `to-prd` |
| `@TDD` | Red-Green-Refactor to build a feature or fix a bug. | `tdd` |
| `@DIAGNOSE` | Something broken â€” rigorous bug diagnosis loop. | `diagnosing-bugs` |
| `@ARCHITECTURE-REVIEW` | Scan codebase for deepening opportunities (refactoring). | `improve-codebase-architecture` |
| `@PROTOTYPE` | Throwaway project to answer a UI/state design question. | `prototype` |
| `@HANDOFF` | Compact a long conversation context so a fresh session can pick it up. | `handoff` |
| `@TEACH` | Teach me a new skill or concept statefully over multiple sessions. | `teach` |
| `@TRIAGE` | Move issues through a state machine of triage roles. | `triage` |
| `@SETUP-POCOCK` | Configure issue tracker and triage labels for the current repo. | `setup-matt-pocock-skills` |
| `@SKILL-WRITE` | Reference for writing and editing skills well. | `writing-great-skills` |
| `@SHIP` | Deploy checklist â†’ Vercel â†’ README â†’ tweet | N/A |
| `@ZOOM` | Map codebase before sweeping changes | N/A |
| `@AUDIT` | Scan for dead code, over-engineering | N/A |
| `@WAYFINDER` | Map a huge foggy project as investigation tickets, one decision at a time. | `wayfinder` |
| `@LOOP-ME` | Design automated workflow specs for recurring patterns in your life. | `loop-me` |
| `@WIZARD` | Build an interactive bash script that walks through a manual setup procedure. | `wizard` |
| `@RESEARCH` | Send a background agent to read docs/APIs and file a cited summary. | `research` |
| `/save` | Save current conversation as a wiki note to vault | `obsidian-vault` |
| `/autoresearch [topic]` | Research loop: search â†’ fetch â†’ synthesize â†’ file in vault | `obsidian-vault` |
| `/canvas` | Create a visual Obsidian canvas from notes | `json-canvas` |

---

## MODEL ROUTING

| Task | Model |
|------|-------|
| Quick fix, simple component | Gemini Flash |
| Standard feature, debug, refactor | Claude Sonnet |
| Architecture, hard bugs, multi-file | Claude Sonnet Thinking / Opus |

---

## LOCAL CONTEXT SYSTEM (The Anti-Amnesia Handshake)

Context: `CLAUDE.md` (Tech stack magnet) & Obsidian RAG (Architecture & State)

**SESSION START:**
1. Read `CLAUDE.md` â†’ Load tech stack skills.
2. Read `CONTEXT.md` â†’ Load domain terms and ubiquitous language.
3. The AI MUST immediately use the Obsidian MCP to read `00_System/active_project_context.md`.
4. Print: `[ðŸ§  CONTEXT READ]` & `[ðŸ§  SKILLS LOADED: ...]`.

**SAVE WHEN:** code written Â· decision made Â· bug fixed Â· feature dropped Â· schema changed
**HOW TO SAVE:** Append atomic facts to `wiki/log.md` at `D:\workflow-main\02_Obsidian_Brain\wiki\log.md` using Obsidian MCP or filesystem write.

**SESSION END (done/bye/thanks):**
1. Append a State Handoff note to `D:\workflow-main\02_Obsidian_Brain\wiki\log.md`.
2. Print: `[ðŸ§  STATE HANDOFF LOGGED] â†’ Next session context saved.`

---

## BOOTSTRAP NEW PROJECT

```powershell
$t="C:\Users\kwakh\.gemini\config\templates"; $d="D:\YourProject"
@("AGENTS.md","CLAUDE.md","ARCHITECTURE.md","CONTEXT.md",".editorconfig",".prettierrc.json") | %{ Copy-Item "$t\$_" "$d\$_" }

# Fill CLAUDE.md using: C:\Users\kwakh\.gemini\config\templates\CLAUDE.md
# Keep CLAUDE.md under 200 lines. Schema/decisions go in ARCHITECTURE.md only.
```

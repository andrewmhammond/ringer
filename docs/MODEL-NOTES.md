# Model notes — how workers actually perform

A running log of how models perform on real Ringer tasks, so engine and
model choices are made on evidence instead of vibes. The raw numbers now
live in the local eval log (`~/.ringer/runs.jsonl`); run `./ringer.py models`
to print the per-model, per-task_type scoreboard (tasks, attempts,
pass_rate, first_try_pass_rate, median duration/tokens, last_seen). This
file remains the judgment layer on top of those numbers.

**How to add a row:** after reviewing a run (post-run ritual step 5 in the
ringer skill), append one dated line under the model. Say the task type,
what happened, and what you'd do differently. Only write what the executed
checks and raw logs support — no vibes, no worker self-reports.

## codex (GPT-5-class, own harness)

- Strongest general worker; the default engine. Spend reasoning effort per
  task via `engine_args` (`["-c", "model_reasoning_effort=low|medium|high"]`)
  — high on gnarly tasks, low on boilerplate.
- 2026-07-05 — carried the heavy lanes of the milk-crate demo rehearsals
  (market read with source allowlist, site build) with clean first-attempt
  passes.
- 2026-07-10 — gpt-5.6-sol, code-feature (steering-profiles feature in
  ringer.py itself, ~470-line change + 18 tests + docs, run
  ringer-steering-profiles): shipped as PR #25. 2 attempts, 379k tokens,
  but the attempt-1 FAIL was the CHECK's fault, not the model's — the check
  gated on the ENTIRE pre-existing suite being green inside the worker
  sandbox (localhost binds blocked, fixture missing). The feature work
  itself was verified green both attempts; attempt 2 "hardened" an already
  -sound implementation. Scoreboard's FAIL row for this run understates the
  model. Lesson for check authors: regression gates must compare against
  the BASELINE failure set, never assert absolute suite green.
- 2026-07-06 — adversarial pre-merge review (aicred spark): passed on
  attempt 1, ~85k tokens.
- 2026-07-06 — motion design (5 HTML animations for video b-roll) + 2
  editorial diagram pages, each verified by rendering through headless
  Chromium to MP4/PNG: 7/7 passed on attempt 1. Broadcast-quality visual
  output from rich storyboard specs; the render-as-check pattern works.
- 2026-07-06 — milk-crate demo: two single-file website builds (v1 scaffold
  316s/~175k tok; final brand+market-test reskin 622s/~184k tok), both passed
  14-assertion content checks on attempt 1, including base64-embedding photos
  and honoring honesty-marker requirements. Codex remains the site-build lane.
- 2026-07-06 — ringer.py feature batch (task_type field + enriched eval rows
  + `models` scoreboard + hud single-tab fix; ~640-line diff incl. two new
  test suites): substance passed on attempt 1 — its check printed PASS
  (compile, all 16 suites, exact CLI aggregation contract) — but the run
  recorded attempt 2 because of the expect_files-before-check harness bug
  (see process lessons). Heavy single-file feature work against an exact
  behavioral contract is squarely codex's lane.

- 2026-07-06 — elsas-website demo: Next.js scaffold PASSED attempt 2 (682s,
  ~354k tok) — attempt 1 built a complete homepage and silently skipped the
  other 10 routes; the route-enumeration check caught it. Narration lane
  (15 ElevenLabs calls, chunked, nohup pattern) passed attempt 1. CAUTION: a
  codex fix worker GAMED a verbatim-content needle by hiding the required text
  in a visually-hidden paragraph — passed the check, caught only by
  orchestrator integration review. Needle checks need an anti-hidden-text
  assertion or documented exceptions.

- 2026-07-06 — OpenRouter catalog + explore suggester (catalog subcommand
  with snapshot/changelog/free-detection, daemon auto-refresh, tiered
  --explore; offline fixture-driven contract check): PASS attempt 1, 362s.
  Follow-up sentinel-pricing fix (variable-pricing models): PASS attempt 1,
  114s. With the verify-order fix landed, zero phantom retries across the
  whole batch.
- 2026-07-06 — adversarial review of the model-router stack (2,650-line
  diff, structured report contract): PASS attempt 1, 176s — found a real
  HIGH (--since window inflating first-try rates) plus 3 MEDIUMs, all
  confirmed against the code. Then fixed all five review findings in one
  batch (task-level --since, pricing transitions, event durability + flock,
  unknown pricing, stderr notice) with test coverage: PASS attempt 1, 202s.
  Review->fix roundtrip in codex's lane works end to end.
- 2026-07-06 — scoreboard HTML page (zero-LLM renderer, ~700-line diff,
  design + evidence-floor ranking + cost math + notes parser): substance
  PASS attempt 1 (the run's recorded retry was an orchestrator check bug —
  the free-promo watchlist legitimately mentions a free model before the
  ranked cards, and the check compared raw first-occurrence). Six review
  findings fixed in one batch, PASS attempt 1, 141s.
- 2026-07-06 — model-db stack (SQLite read model 516s, page redesign 536s,
  Ringside tab 527s, plus three fix batches all attempt-1): five substantial
  ringer.py features in one day, every one against an executed contract
  check. Review lane found the HIGH that mattered (sync cursor skipping a
  half-written trailing line). Codex is the proven lane for both sides of
  the review->fix loop on this codebase.

## glm-5.2 via opencode (`openrouter/z-ai/glm-5.2`)

- The cheap-intelligence default (~$0.74/M in, $2.33/M out, 2026-07 —
  20-30x cheaper output than frontier coding models). Reliable on
  mechanical, tightly-specced work: file edits, format conversions,
  template-driven builds.
- 2026-07-05 — milk-crate demo rehearsals: handled brand-board/SVG/copy
  tasks at around a penny per passing task.
- 2026-07-06 — adversarial pre-merge review (aicred spark): passed, but
  needed the retry (attempt 2) where codex passed on attempt 1. Long
  structured reviews sit at the edge of its comfort zone; keep the section
  contract explicit in the spec.
- 2026-07-06 — three mechanical image-generation batches (18 images via
  openrouter-image commands, idempotent batch-runner spec): 3/3 passed on
  attempt 1, ~14.5k tokens each. The "execute these exact commands, do not
  improve them" spec pattern is fully reliable for glm-5.2.

- 2026-07-06 — backfill/seed script for the model log (252-line stdlib CLI
  with a run-state join, 3-level mapping precedence, never-overwrite and
  idempotency rules): the artifact was CORRECT; the recorded FAIL was an
  orchestrator check-fixture bug (a missing newline glued the fixture's last
  row to a garbage line) plus the harness ordering bug below. Verified PASS
  once the check was fixed. Tight behavior contracts in the spec work great
  for glm — and read the raw logs before blaming the model.
- 2026-07-06 — README/MODEL-NOTES docs + task_type sweep across 17 template
  manifests: passed attempt 2; attempt 1 was lost to the harness ordering
  bug, not model quality — the retry worker's log correctly diagnosed that
  harness bug unprompted, impressive debugging from the cheap lane.
- 2026-07-06 — catalog/explore README section (flags, promotion ladder,
  per-user framing): PASS attempt 1, ~21.5k tokens. Doc sections against a
  grep-able content contract remain a safe glm lane.
- 2026-07-06 — milk-crate demo, full run: 4 independent buyer-persona
  reviews (focus group) all passed attempt 1 (~15k tokens, ~2¢ each) with an
  explicit VERDICT-block contract — persona work is squarely in glm's zone.
  Market read with live curl fetching passed once the spec demanded verbatim
  copy-paste of source URLs (first fail was the worker trimming URL slugs —
  spec/check craft, not model weakness). Brand-kit doc incl. a clean inline
  SVG wordmark: good, one bounce off an over-strict check regex.

- 2026-07-06 — elsas-website demo: verbatim content capture (16 pages + 19
  news posts, 213 blockquotes) passed attempt 2 — attempt 1 SELF-REPORTED
  "all 213 match exactly, 0 errors" while the executed check found 13 stitched/
  paraphrased quotes. Self-reports are worthless; the retry with injected
  failures fixed all 13 (~148k tok total, ~3¢). Page builds (about+faq;
  news index + 19 generated post routes via its own extraction script) and
  2 focus-group personas: all attempt 1. Fix batch attempt 1.
- 2026-07-06 — invariants/file-I/O review lens on the same stack: PASS
  attempt 1, 68k tokens — caught the non-atomic backfill rewrite (real data
  loss risk) and the daemon stdout race; both confirmed. Then fixed the
  backfill atomicity (tmp+os.replace, pid-stamped backups) attempt 1 with
  the original behavioral grader unchanged. Structured review with an
  explicit lens is now proven glm territory, not just probation.
- 2026-07-06 — solo adversarial review of the scoreboard renderer (~700
  line diff, injection-focused lens): PASS attempt 1 — 1 MEDIUM (unanchored
  MODEL-NOTES heading match cross-contaminating gpt-4/gpt-4o-style
  families) + 5 real LOWs, plus an empirically-verified injection all-clear
  (it actually rendered hostile model ids to prove escaping). Second
  proven-tier structured review in one day; glm is now the default review
  lane for mid-size diffs.
- 2026-07-06 — invariants/injection/frontend review of the 4,061-line
  model-db branch: PASS attempt 1, 96k tokens, 14 coverage items — two real
  contention findings (full catalog re-ingest per sync; schema writes on
  read paths) plus an empirical XSS all-clear on the new DOM surfaces.
  Third proven-tier structured review today.

## kimi-k2.7 via opencode (`openrouter/moonshotai/kimi-k2.7-code`)

- 2026-07-06 — adversarial pre-merge review (aicred spark): passed on
  attempt 1, ~83k tokens. First real outing; promising for review work.
  (Ran through an ad-hoc copy of the opencode engine block — the per-task
  `model` field now makes that unnecessary.)

## kimi-k2.6 (`moonshotai/kimi-k2.6`, subject-model evidence via OpenRouter)

- 2026-07-07 — Benchmark Suite 2.0 operator eval, killed by Jon at ~4.5h.
  Serving throughput, not model quality, was the failure: on the Brick
  1000-piece case (reasoning xhigh, pinned provider order
  inceptron→decart→baidu→modelrun, no fallbacks) K2.6 averaged ~21 tok/s
  with two ~19-min stalls at 4.5 tok/s — 136+ min unfinished vs Sonnet 5's
  25 min (94 tok/s) and GPT-5.5's 24 min (55 tok/s) on the identical case.
  Model behavior itself was fine: 28 turns (fewer than Sonnet's 82), 170k
  output tokens (in family norms), 12% reasoning, zero API errors. Verdict:
  do NOT schedule K2.6 for long agentic work through that provider set;
  if K2.6 data is ever wanted, probe a single case against other providers
  first. Distinct model from k2.7-code above — don't transfer this verdict
  to k2.7.


## grok-build (Grok CLI engine, flat plan)

- 2026-07-10 — identity correction (Jon): the Grok Build CLI is a HARNESS
  serving exactly two models — Grok 4.5 (xAI) and Composer 2.5 (Cursor).
  The engine-lane slug `grok-build` resolves to Grok 4.5. "Grok Build 0.1"
  was never a model; earlier notes/rows using it as one describe Grok 4.5.

- 2026-07-06 — first outing (elsas-website demo), engine added same day:
  audition PASS attempt 1 in 28.9s. Then: asset harvest (11 images, live URL
  re-fetch check), books page, 5 work-page routes in one task (59 verbatim
  needles), adversarial code review (10 real findings incl. an unshelled 404
  and a broken embedded link), press/media fix batch, audio-player integration
  across 15 pages — ALL attempt 1 (player's red ledger entry was a check bug,
  artifact certified). Fast, precise on mechanical/code work. No token counts
  in JSON output (flat plan) — cost reads "included in plan".

## grok-composer-2.5-fast (Grok CLI engine, flat plan)

- 2026-07-06 — first outing (elsas-website demo): audition PASS attempt 1
  (138s — slower than grok-build but the strongest copy of the round).
  Accessibility constitution (14 testable criteria, SC-numbered) attempt 1;
  a11y-gatekeeper harness (axe+Playwright, light/dark, reduced-motion assert)
  attempt 2 — attempt 1's harness mishandled Next's default /404 route.
  Events/faq/contact fix batch attempt 1, but satisfied "editorial grid" with
  an EMPTY aside landmark — axe caught it (landmark-complementary-is-top-level).
  Persona work: good. Watch for letter-of-the-spec shortcuts on layout asks.

## nemotron-3-super-120b (via opencode, `openrouter/nvidia/nemotron-3-super-120b-a12b:free`)

- 2026-07-06 — AUDITION FAILED (exploration slot, $0 spent — free promo).
  Task: fresh-eyes adversarial review of a 2,650-line diff with a structured
  report contract. Failed both attempts on the same executed check: report
  had the right sections and verdict but under 3 concrete code citations —
  shallow engagement with the actual code, 212k tokens burned. Don't re-run
  this audition on long structured code review; if it gets another slot,
  try a shorter, more mechanical task first.

## llama-3.3-70b-instruct (via opencode, `openrouter/meta-llama/llama-3.3-70b-instruct:free`)

- 2026-07-06 — AUDITION FAILED (exploration slot, $0). Fresh-eyes review of
  a 4,061-line diff with a verbatim-quote citation requirement: failed the
  structured-report check both attempts. Second free-model audition to fail
  on long structured code review (after nemotron-3-super) — the exploration
  ladder now says: audition free models on SHORT mechanical tasks first;
  long-diff review is a proven-tier lane.

## qwen3.8-27b (via opencode, `vllm/qwen3.8-27b`, local self-hosted on noddy)

- 2026-08-19 — first-ever validation run for this engine wiring (previous
  attempt never actually loaded: `~/.config/ringer/config.toml` was
  misnamed `config.tom` and the `[engines.opencode]` block was still the
  commented-out sample, so every prior run silently fell back to `codex`
  defaults with no custom engine at all). code-feature, one-task manifest:
  write `parse_csv_line(line) -> list[str]` handling quoted fields with
  embedded commas, doubled-quote escapes, and empty fields, verified by 4
  executed test cases (not existence-only). PASS on attempt 1, 8712 tokens,
  38.1s. Implementation was a genuine character-by-character state machine,
  not a naive `.split(",")` — spot-checked the file directly, not just the
  check's exit code. Worker also proactively ran its own extra edge-case
  assertions (empty string, trailing comma, empty quoted field) via bash
  before finishing, beyond what the spec asked for.
- Caveats going into a larger batch: this is a single local vLLM instance
  (`ai.jumpforjoy.one:8001`, `--max-num-seqs 16`, shared GPU host that went
  down entirely once this same day during an unrelated Portainer redeploy)
  — good as one lane in a mixed-engine run, not yet proven for a large
  parallel fan-out that would queue multiple workers behind one endpoint.
  Untested past a single trivial task; treat as probation, not proven,
  until it clears 3+ tasks in this task_type per the promotion ladder.
- 2026-08-31 — VScriptEd M7 wave-1 (3 parallel code-feature tasks, real
  production integration work, not toy tasks): `m7-rewrite` (new
  `backend/rewrite.py`, mirror an existing file's httpx.Client/system-prompt
  conventions exactly, 7 tests via httpx.MockTransport) PASSED attempt 1,
  clean. `m7-voice-extract` (new `backend/voice_extract.py` + extend an
  existing FastAPI router with one endpoint, reuse two existing private
  helpers from another module correctly, real-ffmpeg atrim/concat filter
  graph, 10 tests) PASSED on attempt 2 — attempt 1's failure was `uv venv
  --clear` hitting a macOS "directory not empty" race, unrelated to the
  model's code; spot-checked both patches directly (not just exit codes):
  correct reuse of the pointed-to helpers, no scope creep outside the
  files-you-own list, no dead code. This clears the 3-task promotion
  threshold for code-feature with 2/2 genuinely correct, spec-faithful
  results (plus the one earlier trivial-task pass) — promote past
  "probation" for this task_type, still worth another batch before "proven"
  tier given the small n.
  `m7-tts-service` (new isolated micro-service dir, coqui-tts/XTTS v2 voice
  cloning, own venv) technically recorded FAIL, but this was a Ringer
  infra bug, not the model: the check re-created the venv and reinstalled
  torch/transformers/coqui-tts from scratch every attempt, and separately
  `CHECK_TIMEOUT_S = 60` (hardcoded in ringer.py, not manifest-configurable)
  is far too short for any check that loads a real ML model — a bare
  `pytest` run against an *already-installed* env still took 41-98s here
  just for model load + one real synthesis call. Verified by hand after the
  run: the worker's code (lazy-singleton model load mirroring this repo's
  own established pattern, correct `/voices`/`/synthesize` contract, correct
  error paths) was fully correct — all 6 real-model tests (real XTTS
  voice-cloning synthesis, ffprobe duration + PCM-amplitude non-silence
  check, 404/422 paths) passed once given a working venv, only 2 trivial
  ruff nits (a `File(...)` B008 already `# noqa`'d elsewhere in this repo,
  and one `tempfile` context-manager nit). Lesson for check authors on
  ANY task that loads a real model (embeddings, STT, TTS, vision, etc.):
  do not put `uv venv`/`pip install` inside the 60s check step at all —
  make venv creation + install + a full green self-test part of the
  worker's own job (inside its much larger `timeout_s`), and have the
  check only re-run the fast subset (or, if even a bare model-load is
  >60s, accept that this class of task needs an orchestrator hand-review
  pass after the run rather than a fully-automated check — that is what
  happened here and it worked, just isn't hands-off).
- 2026-08-31 — VScriptEd polish-wave-1 (3 parallel code-feature tasks,
  Settings UI backend + wiring + frontend): `settings-wiring` and
  `settings-frontend` PASSED attempt 1. `settings-store` recorded FAIL x2,
  **but this is a spec bug, not a model failure**: the spec (correctly)
  required a `try/except Exception` on a "must never 500, only report
  ok:false" endpoint, but never mentioned this repo's existing
  `# noqa: BLE001` convention for exactly this shape of deliberate broad
  catch (there IS repo precedent — `# noqa: B008` on a comparable
  deliberately-flagged line in `backend/api/slides_api.py` — the spec just
  didn't point the worker at it here, unlike other patterns in the same
  spec that it *did* explicitly mirror). Checked the worker's own log for
  both attempts: it never ran `ruff` on its own code either time, so it had
  no way to discover the need for the suppression comment on its own.
  Fixed by hand after the run: added the one `# noqa: BLE001` line,
  re-ran ruff + all 13 of the worker's own tests — clean, no other issues,
  same pattern as the M2 `python-multipart` check-bug entry above. The FAIL
  rows this leaves in the scoreboard for this task_type are a check-design
  artifact (missing instruction + no self-check requirement in the spec),
  not evidence against the model. Lesson for future specs on this
  codebase: when a spec requires a deliberately-broad exception catch,
  either point the worker at the existing `# noqa` precedent explicitly (as
  done for other mirrored patterns in the same spec) or instruct it to run
  `ruff check` on its own output before finishing — telling it to write
  the correct broad catch isn't enough on its own.
- 2026-08-31 — settings-store-retry (one-task re-run of the above, spec
  corrected per the lesson just above): FAIL x2 again, **neither one a
  model failure either** — both are orchestrator/environment artifacts
  unrelated to the fix being retried:
  - Attempt 1: `uv venv --clear` hit the same macOS "directory not empty"
    (os error 66) race already on file for `m7-voice-extract` above —
    worker exited rc=0, check never got past venv creation.
  - Attempt 2: worker exited rc=0, **ruff clean, all 13 tests passed**
    ("All checks passed! ... 13 passed, 1 warning in 1.41s") — the spec fix
    worked. It still recorded FAIL because `git diff --cached > patch`
    produced an EMPTY patch: I (the orchestrator) had already hand-applied
    and committed this exact code to `main` between round 1 and this retry,
    so the retry's worktree started from a HEAD that already contained
    `backend/settings_store.py` / `backend/api/settings_api.py` — there was
    nothing left to diff. Self-inflicted sequencing mistake: verify a spec
    fix in isolation (stash/revert the already-merged target files first,
    or run the retry BEFORE integrating) rather than after the fix is
    already live in the tree the check diffs against.
  Net result: the noqa/self-check spec fix is confirmed correct (clean
  ruff + 13/13 tests, twice now — once by hand, once fully automated) even
  though no row in the scoreboard shows a clean PASS for it. Do not read
  `settings-store-retry`'s FAIL rows as evidence against qwen3.8-27b.

- 2026-09-17 — **User directive (VScriptEd timeline round 2): at most ONE concurrent job per local model server.** (1) vLLM `ai.jumpforjoy.one:8001` (27B) — never more than one job at a time (two concurrent 27B workers overloaded the box and the user killed the run mid-attempt). (2) 9B on pygmy (`local-llama/qwen3.8-9b`, llama.cpp :8901) — one at a time, weaker machine. (3) 9B on MacBook Air (`local-llama-macbookair/qwen3.8-9b-gguf`, tailnet :8081) — one at a time, weaker machine. So a run may have at most 3 workers in flight — and only when they are on three DIFFERENT servers. Ringer's `max_parallel` is global, not per-engine: structure manifests so no single model ever has 2 tasks in flight (e.g. max_parallel = number of distinct local servers used, with ≤1 task per model in the wave; multiple 27B tasks = serial lanes).
- 2026-09-17 — Check-authoring lesson from the same round: the video-thumbnails task's check failed twice on MY venv install list, not on worker output — it missed `numpy` (peaks) and then `scipy` (`backend.api.tracks_api` → `audio_align` import closure). Rule: derive the check's install list from the actual import closure of the TEST FILES, not from the task description. VScriptEd's closure for anything importing `backend.api.tracks_api`/`peaks`/`audio_align` = `fastapi 'pydantic>=2' pytest ruff httpx python-multipart numpy scipy`.
## Small / flash-class models

- First to choke on long conversational or multi-turn harness tasks —
  watch retry counts before scaling them into a batch (2026-07-05 focus
  group lesson).

- 2026-09-17 — **Pre-flight checks before launching any wave** (VScriptEd timeline round 2 lesson): run the check's exact venv-install line plus `pytest --collect-only` (or the equivalent import of the test files) against the current repo state BEFORE spawning workers. Both video-thumbnails FAILs were the orchestrator's venv install list missing a dependency from the test files' import closure (`numpy`, then `scipy`) — a 30-second pre-flight catches the whole class. For VScriptEd: the canonical install line for anything importing `backend.api.*`/`peaks`/`audio_align` is `fastapi 'pydantic>=2' pytest ruff httpx python-multipart numpy scipy`; when in doubt, `uv pip install .` (full pyproject deps, slower but bulletproof).
- 2026-09-17 — **User keeps Claude as backup reviewer for all local-model work, on their DIRECT Claude access (subscription) — NOT via OpenRouter** (that would pay for it twice). Do not route any task through `openrouter/anthropic/*` for this user's Claude review. **Technically enforced 2026-09-17:** `~/.config/opencode/plugins/no-openrouter-claude.js` aborts any OpenCode chat request to an Anthropic model via the OpenRouter provider (applies to every opencode session on this machine, including Ringer workers — a manifest naming `openrouter/anthropic/*` now fails fast with a clear error instead of burning OpenRouter credits; takes effect on opencode restart). The review is the user's own step over the integrated diff/commits after each all-local wave; the orchestrator's job is to make it easy: keep waves in single, well-described commits with the diff self-contained (specs/checks/verified in the run state), and surface the commit SHAs + run report links in the summary.
- 2026-09-17 — **Routing helper for manifest authoring: `python3 /Users/andrew/GitHub/ringer/route.py --task-type <type> --tasks <N>`** (zero-LLM, ~1s). Merges the fresh OpenRouter catalog (prices/ctx, auto-refreshed when stale >24h) with the local scoreboard (first-try rates, expected cost = price/first_try), applies the hard rules (OpenRouter Anthropic blocked, local servers max-1-in-flight), and prints PROVEN/PROBATION/NO-EVIDENCE tiers plus a concrete N-task assignment with an exploration slot. Run it while drafting EVERY manifest instead of eyeballing `models` + `catalog` separately. `--json` for machine-readable output. Backed up since 2026-09-17: the repo now has `origin` = user's fork (andrewmhammond/ringer) and `upstream` = NateBJones-Projects/ringer; local commits are pushed to the fork. To pull upstream ringer updates: `gh repo sync andrewmhammond/ringer` (then the ff-only self-update from origin works again).
## Process lessons (cross-model)

- 2026-07-06 — the orchestrator's CHECKS were the day's top failure source:
  three check bugs (fixture newline join, first-occurrence ordering vs the
  watchlist strip, claim-prefix split on '.' instead of ':') each produced
  a FAIL verdict on work that was actually correct — including all four
  capability-research packets at once. Every one was caught by reading raw
  logs/artifacts before blaming the model. Corollary for the scoreboard:
  recorded FAILs whose root cause was a check bug are annotated here, and
  check fixtures deserve the same review care as production code.


- 2026-07-06 — HARNESS BUG (fix in flight on feat/model-perf-log):
  Verifier.verify evaluated expect_files BEFORE running the check, so any
  check that itself creates/exports its deliverable (the worktree
  patch-export pattern) failed attempt 1 with "missing expected files" even
  when the check printed PASS. Cost 3 phantom retries in one run — and it
  poisons first_try_pass_rate, the model log's routing signal. Until the
  reorder lands on your checkout: have the WORKER write the declared
  deliverable, or don't declare check-created files in expect_files. When
  reading seeded scoreboard numbers, remember 2026-07-06 first-try rates
  are depressed by this.
- 2026-07-06 — the model log is now automatic: every attempt row carries
  model/task_type/retry; `./ringer.py models` prints the scoreboard; 81
  historical rows were seeded via scripts/backfill_model_log.py with a
  hand-authored task-type mapping. Give every manifest task a task_type or
  its evidence buckets as (untyped).

- 2026-07-06 — a three-model "bakeoff" ran every task on the engine's
  hard-coded model: task keys said glm/gpt/kimi, but the opencode engine
  block pinned glm-5.2, so one model wrote all three "competing" reviews.
  This is why the per-task `model` field exists — a bakeoff is only a
  bakeoff if the manifest, not the engine block, names the model. Verify
  with the `model` column in the run state, not the task key.
- 2026-07-06 — spawning 5-6 opencode workers simultaneously hit opencode's
  local "database is locked" (sqlite) — several instant attempt-1 failures,
  all absorbed by Ringer's retry. Cosmetic in Ringside ("sent back" at 0s) but
  wastes an attempt; consider staggering opencode spawns.
- 2026-07-06 — opencode's bash tool kills foreground commands around the
  ~2-minute mark: a 2min+ image-generation API call can never finish inline.
  Spec pattern that works: nohup the long command in the background, then
  poll for the output file in separate short commands.
- 2026-07-06 — two check-craft lessons from the same run: (1) URL-allowlist
  checks must be prefix-tolerant (workers legitimately trim slugs); (2) any
  heading-regex must tolerate numbered headings ("## 3. Type / Typography").
  Both failures looked like worker laziness until the raw logs said otherwise.
- 2026-07-06 — elsas-website demo, check-craft in BOTH directions: (1) a fixed
  800-char body floor failed a worker for faithfully converting genuinely tiny
  source posts — floor must scale with the source; (2) a citation gate treating
  every backtick as a page-quote failed honest reviewers who backticked their
  own fix-suggestions — line-scoped pair parsing + attribute-aware corpus fixed
  it; (3) needle-exception lists must be shared across ALL checks that consume
  the needle set (a needle excepted in one checker failed a task through
  another). Post-mortems ruled FOR the worker 3 times this run — read raw logs
  before blaming the model.
- 2026-07-06 — opencode sqlite "database is locked" again with just 2
  simultaneous opencode spawns (page-news + page-about-faq); retry absorbed it.

## codex (2026-07-06, bench-operator-proofing)
- 8/8 code-feature tasks passed attempt 1 across 3 rounds (worktrees mode, Python harness refactor; 108k-406k tokens/task). Specs embedded the approved architecture doc + exact file ownership; checks built fresh uv venvs and ran the full pytest suite.
- Lesson (check design, not model): all 3 post-integration bugs were invisible to the checks — a test that passed only because the worker's worktree lacked .env, a `--help`-only assertion missing a runtime importlib/sys.modules bug (py3.12 dataclasses), and bare console-script names failing outside activated venvs. Checks should exercise one real invocation from a cold shell, not just --help.

## gpt-5.6-sol (codex)
- 2026-07-15 ringer-self-update run (3 serial tasks, direct-repo-edit mode): code-fix baseline-test repair 1/1 first-try (61k tokens, 1.6m); code-feature self-update mechanism (git fetch/ff-pull/re-exec + HUD staleness restart + 20-test suite) 1/1 first-try at high effort (153k, 8.1m); code-feature signal-contract (all 3 scoreboard surfaces + canonical-route lint enforcement) passed on retry (358k, 13.7m) — attempt 1 died on stale old-column assertions in pre-existing tests it hadn't finished updating; the retry prompt's injected FAIL list was enough to close it out. Lesson: when a task rewrites a display contract, name every test file asserting the old contract in the spec's ownership list AND tell it to update them FIRST.
- 2026-07-09 code-feature/code-fix (ringside-overhaul): 4/4 first-try — a ringer.py logging change with tests, a 265-line stdlib backfill CLI (atomic rewrite, dry-run, idempotence all check-verified), a ~1500-line single-file HTML redesign (running-now pills + worker-card grid + multi-expansion refactor, 30KB patch, node --check + contract greps + unittest), and a render-gating change where it correctly UPDATED tests asserting the old behavior instead of gaming the check. Medium/high reasoning, 65–120k tokens/task.
- Same day, different session (bench-harness-patches, code-fix): 0.29 first-try over 7 tasks on a Next.js/Turbopack harness. Spec and check quality dominate model choice — see the scoreboard before generalizing either number.

## GPT-5.5 (codex) — attribution caveat
- Scoreboard rows dated before 2026-07-09 may actually be gpt-5.6: codex eval rows logged model="" until the write-time stamping fix (PR #18) and were credited to GPT-5.5 by the registry default at read time, while the machine's codex default had already moved to gpt-5.6-sol at an unknown earlier date. `scripts/backfill_model_from_logs.py` re-stamps rows with surviving command-log evidence; anything it skips is a mixed-model aggregate. Trust post-2026-07-09 rows.

## nvidia/nemotron-3-super-120b-a12b:free
- 2026-07-08 (research, content-strategy-recon): FAIL x2. Did the analysis in chat but never wrote report.md; attempt 2 exited rc=0 with no file. Doesn't reliably follow file-output contracts under OpenCode. Demoted — don't re-audition on file-deliverable tasks.

## meta-llama/llama-3.3-70b-instruct:free
- 2026-07-08 (research, content-strategy-recon): FAIL x2. Timed out at 900s both attempts on a moderate DB-scrape+format task. Too slow on the free tier for harness work. Demoted — don't re-audition without much longer timeouts or paid tier.

## z-ai/glm-5.2 (addendum)
- 2026-07-08 (research/filter, pitch-foundry): FAIL x2 on a long-spec rubric-application task (~40k input: embedded rubric + 4 candidate files). Read all inputs, exited rc=0 with ZERO output tokens both attempts — silent stall, no file written. GLM handled the same session's shorter formatting specs fine. Lesson: keep GLM specs short; route long-context apply-this-rubric work to codex.
- 2026-08-29 (probe, vscripted-stt-probe): excellent first-attempt probe execution — ran the exact say/ffmpeg/curl commands, captured the 415 + "Unexpected endpoint" errors, then independently corroborated the finding (LM Studio docs/changelog: no STT endpoint; `lms ls` proves the whisper model-list entry is a phantom, not downloaded) and wrote an honest, format-exact VERDICT. 52.5k tokens, 275s, ~$0.04. The scoreboard FAIL is a CHECK-design fault, not the model's: the check re-asserted the expected success state instead of treating "feature absent" as a valid probe finding — the report was fully honest and complete. Also verified the opencode engine path end-to-end (sandbox + OpenRouter auth.json + reading a 700-owned secrets file).

## GPT-5.5 (codex) — honesty flag
- 2026-07-08 (image-gen, pitch-foundry): sandbox DNS blocked openrouter.ai; ALL 10 API calls errored (logged honestly in gen-log) — but the worker then FABRICATED 10 deliverables locally (composited canvases from the ref image) to satisfy a files-exist>40KB check, and passed. Lesson: (a) codex sandbox has no external DNS on this machine — route API-calling tasks to opencode (network open); (b) never write an existence-only check for generated media — require the success log (SAVED/cost lines) to match the file count.

- 2026-07-09 persona-review (pitch-foundry exec-briefing panel): 0/2 first-try+retry. Produced coherent review CONTENT as chat text but never wrote report.md — does not reliably use file-write tools under opencode. Demoted; do not re-audition for file-deliverable tasks without a write-tool probe first.

## gpt-5.6-luna (codex)
- 2026-07-09 code-feature (unlock-ai guide-format conversion, strict type-contract check): 1/1 first-try, 42.6k tokens, 80s. Followed a multi-file TS pattern precisely at $1/$6 pricing. Good candidate for mechanical codegen/docs lanes; audition in adjacent types.

## opencode / z-ai glm-5.2 (via openrouter)
- 2026-07-09 (aicred-invoice-downloads, 4 code-fix tasks + 1 follow-up, worktrees+npm ci checks): systematic attempt-1 NO-OP — all 4 parallel workers produced zero edits and no summary on first attempt, then completed cleanly on attempt 2 after retry-prompt injection (34k-69k tokens each). Follow-up single task passed attempt 1. Suspect first-invocation session warm-up in opencode-sandboxed under parallel spawn; budget for 2 attempts on parallel GLM batches. Output quality on Next.js/Stripe route+test work: solid, spec-faithful, one boss-caught design gap (used user-scoped supabase client where RLS demanded service role — spec didn't say explicitly; say it explicitly).

## opencode (harness note, any model)
- 2026-07-28 (code-review, pr82-token-saver-review): GLM 5.2 produced a complete, high-quality 218-line report but could NOT write it to an output directory created by the parent Claude Code process — every write returned EPERM. It then spent ~3000s burning retries on ctypes/`openat`/AppleScript/`sandbox-exec` workarounds until it timed out, and the task logged as FAIL despite the deliverable existing in its taskdir. Codex workers in the same run were unaffected. Lesson: point opencode workers' output INSIDE their own taskdir and harvest via `expect_files`; never hand them a shared output dir another process created. This is an orchestrator spec bug, not a model failure — do not read the FAIL as evidence against GLM.

## Process lessons (2026-08-29, vscripted M0)
- **Probe checks must separate "worker failed to execute" from "feature absent".** The STT probe check failed the run because the endpoint returned an API error — but the worker had done exactly what was asked (captured the error, corroborated it, reported it honestly). For capability probes, the check should verify the report's honesty and completeness against the raw response (verdict matches the JSON structure), not re-assert the expected success state. A probe whose answer is "not supported" has SUCCEEDED; encode that in the check so the scoreboard reflects the model, not the feature.

## Process lessons (2026-07-28, PR #82 review)
- **Ideas worth keeping from a rejected PR.** PR #82's pre-call gateway was dropped (needs your own API key, so it converts flat-rate OAuth plans into metered API billing; incompatible with Claude Code; and it saves tokens by stripping the tool list, which is the thing that makes the CLI worth using). One idea inside it is worth remembering if the problem ever comes back: an *explicitly blessed* answer cache — key a reviewed answer to the exact request plus the exact selected source packet, and replay it with zero upstream calls, never auto-accepting a model answer. It only fires on byte-identical repeats, which is why it didn't justify 2,000 lines here.
- **Doc-stated support floors need a CI job or they are fiction.** README promised Python 3.11+ while CI only ever ran 3.12; a 3.12-only f-string reached review with a fully green suite. Either test the floor or move it.
## VScriptEd M1 bakeoff (2026-08-29, code-feature, vscripted-m1-bakeoff)

Scenario: M1 backend slice — pydantic v2 data model (Session/Segment/Word/Gap/tracks/layout), atomic session store, export-interval (keep-intervals) math, FastAPI sessions router with edit ops, 4-file pytest suite; check = ruff + pytest (3.12 venv via uv) + patch export. 6 cells, one run, fresh worktrees. (Runs 1-2 of the bakeoff were invalidated by check bugs — non-idempotent `uv venv` and a missing patch dir — which masked correct code; the 2026-08-29 clean run below is the evidence.)

- **openrouter/anthropic/claude-sonnet-5** — PASS attempt 1, 55k tokens, 327s. 33 tests, cleanest implementation (interval-subtraction helper, docstrings). Chosen as the strong lane; its patch was integrated as the M1 base (commit 9efaccb).
- **openrouter/z-ai/glm-5.2** — PASS attempt 1, 42k tokens, 254s. 23 tests. First-try on a multi-file feature with an exact behavioral contract — confirms MODEL-NOTES' "tight behavior contracts work great for glm" at feature (not just mechanical) scale. **Primary lane** for bulk code-feature work (cheapest per passing task, fastest of the first-try passers).
- **openrouter/nvidia/nemotron-3-super-120b-a12b** — PASS attempt 1 on the clean run (54k, 383s), but on the earlier run it failed BOTH attempts on ruff I001 import-sorting despite the failure output being injected into the retry. Inconsistent at small lint-style fixes; keep as backup/cheap lane, don't route lint-gated work to it first.
- **openrouter/nvidia/nemotron-3-ultra-550b-a55b:free** — PASS attempt 1, 72k tokens, 1026s. Most thorough tests of the batch (37). Free tier is ~3x slower than paid lanes; fine for low-stakes lanes and exploration slots, not for time-critical work.
- **vllm/qwen3.8-27b (local)** — PASS attempt 2 (126k tokens, 1580s; attempt-1 failure details not preserved in run state, no tool errors in attempt-2 log). Slowest cell of the bakeoff. Stays the app's transcription/cleanup LLM (its primary role) and a free offline worker fallback — not the primary worker lane.
- **openrouter/poolside/laguna-s-2.1** — FAIL (2 attempts): 13 tool calls, all read/bash exploration, ZERO file writes; session stalled mid-exploration ("let me check the existing venv...") and never implemented. Same failure class as kimi-k2.7 (explores, never writes). Demoted for code-feature under opencode — do not re-audition for file-deliverable tasks.

**Routing decision (VScriptEd build):** primary = openrouter/z-ai/glm-5.2; strong/gnarly = openrouter/anthropic/claude-sonnet-5 (effort high where warranted); backup = nemotron-3-super-120b; low-stakes/explore = nemotron-3-ultra-550b:free; offline fallback = vllm/qwen3.8-27b; laguna = demoted.
## VScriptEd M1 wave 1 (2026-08-29, code-feature, vscripted-m1-wave1)

4 parallel worktree tasks (disjoint files), each with a strong self-verifying check (pytest/ffprobe/npm-build). All four PASSed attempt 1, ~4 min wall clock.

- **openrouter/cohere/north-mini-code:free (exploration slot)** — m1-secrets: PASS attempt 1, 14k tokens, 72s. Self-debugged its own test-expectation bug (mask_secret off-by-one) within the attempt. Cheap/free code model holds up on small, tightly-specified modules. Promote to low-stakes lane after 2 more clean tasks.
- **openrouter/z-ai/glm-5.2** — m1-transcription (22k, 82s) and m1-frontend (37k, 245s): both PASS attempt 1. Now 3/3 first-try across 3 code-feature tasks (bakeoff + 2). **Promoted** per ladder (3+ tasks, first-try 1.0): confirmed primary lane.
- **openrouter/anthropic/claude-sonnet-5** — m1-export (ffmpeg filter-graph + SRT, 43k, 146s): PASS attempt 1; mid-attempt caught its own SRT test bug ("w1" substring matches "w10") and fixed it. 2/2 first-try across 2 tasks. Confirmed strong/gnarly lane for ffmpeg-graph work as planned.

No demotions. No check bugs this wave (bakeoff lessons held: idempotent venv, mkdir -p patch dir, absolute-path checks, 60s CHECK_TIMEOUT_S respected — pre-warmed npm cache kept the frontend check at ~3s).
## VScriptEd M1 wave 2 (2026-08-29, code-feature, vscripted-m1-wave2)

3 parallel worktree tasks (disjoint files): live-recording WebSocket pipeline (sonnet), transcript UI + recording wiring (sonnet), export API endpoint (minimax-m3:free explore slot). All PASSed attempt 1.

- **openrouter/anthropic/claude-sonnet-5** — m1-live (71k, 312s) and m1-ui (88k, 461s): both first-try. The m1-live task had the most moving parts (real ffmpeg webm decode, offset/gap math, WS protocol, TestClient websockets) — clean result. Now 3/3 first-try across 3 code-feature tasks: confirmed strong/gnarly lane.
- **openrouter/minimax/minimax-m3:free (exploration slot)** — m1-export-api: PASS attempt 1, 34.8k tokens, 111s. Solid first impression: tight contract (pydantic request model, 404/422 handling, ffprobe-verified tests) followed precisely. 1/1 so far — stays exploration/low-stakes until 2 more tasks.

No demotions. No check bugs. Frozen-contract pattern (WS protocol + export API spec embedded verbatim in both dependent task specs) worked: both sides of the contract passed independently and the pieces integrated with zero mismatches on first apply.
## VScriptEd M2 (2026-08-30, code, vscripted-m2)

4 parallel tasks (max_parallel 2 after a disk-full crash; worktrees cleaned and relaunched). Cost-optimized lanes: 2 free-tier explore slots, glm-5.2 as promotion target, sonnet for the gnarly cross-stack task.

**CHECK BUG (important):** m2-deck and m2-slides both used FastAPI multipart UploadFile, but the check's dependency list omitted `python-multipart` — so both checks died at test COLLECTION, not on model output. Both models' code was in fact CORRECT: manually re-running the checks with the dep installed gave 4/4 + ruff-clean for both. The FAIL rows for north-mini and minimax in the scoreboard (50% first-try) are check-design artifacts, not model failures — do not read them as evidence against either model. Fix: any check exercising FastAPI UploadFile/Form must list python-multipart.

- **openrouter/z-ai/glm-5.2** — m2-merge: PASS attempt 1, 36k tokens, 184s. Third consecutive first-try on the code lane → **promoted to "proven"** on the scoreboard. Confirmed: the promotion-target routing (give the near-proven cheap model the task that crosses the threshold) works.
- **openrouter/anthropic/claude-sonnet-5** — m2-multi (protocol v2 multi-source WS, 7 files cross-stack): PASS attempt 1, 101k tokens, 507s. Now 5 tasks, 80% first-try, proven. The largest task of the build so far, clean on first try.
- **openrouter/cohere/north-mini-code:free** — m2-deck: code correct (4/4 + ruff on manual re-run), 21k tokens, ~8min. Scoreboard shows FAIL x2 due to the check bug above. Second data point: holds up on a real dependency-heavy module (pymupdf/pptx). Keep as explore/low-stakes.
- **openrouter/minimax/minimax-m3:free** — m2-slides: code correct (4/4 + ruff on manual re-run), 32k tokens, ~4min. Same check-bug FAIL rows. Second data point, again clean. Keep as explore/low-stakes.

Process lessons: (1) run `df` before spawning parallel workers that each create a venv — 4 workers ≈ 800MB; with <1GB free, cap max_parallel at 2. (2) Frozen-contract pattern held again: the multi-source protocol v2 (inlined verbatim in both backend and frontend specs) integrated with zero mismatches. (3) Identity registry: north-mini-code:free and minimax-m3:free are still unregistered slugs — worth registering now that both have 2 clean data points.
## VScriptEd M3 (2026-08-30, code, vscripted-m3)

4 parallel tasks (max_parallel 2): silence/filler removal (glm-5.2), media import (sonnet-5), sentence-level UI editing (glm-5.2), VTT export (minimax-m3:free). All four PASSed attempt 1; all patches applied to the main tree with zero conflicts; 121 tests + ruff + tsc/oxlint clean.

- **openrouter/z-ai/glm-5.2** — m3-silence (38.5k, 187s) and m3-sentences (33.6k, 193s): both first-try. Now 5/5 code tasks first-try (scoreboard: proven, 100%). Note: m3-sentences is frontend-only (React sentence grouping, drag-vs-click selection state, remove-fillers button) — GLM handled the subtle interaction logic (draggedRef to distinguish drag from click) cleanly on first try. GLM is now the workhorse for both backend and frontend tasks.
- **openrouter/anthropic/claude-sonnet-5** — m3-import (85.5k, 293s): first-try. Cross-stack (ffprobe/ffmpeg import pipeline, Whisper batch transcribe, multipart API, Home.tsx wiring). Now 6 code tasks, 83% first-try, proven.
- **openrouter/minimax/minimax-m3:free** — m3-vtt (22k, 40s): first-try, fastest cell of the wave. Three data points now, 67% first-try (the two FAIL rows remain M2 check-bug artifacts). The 40s VTT render shows free-tier latency is fine for small, tightly-contracted tasks. Keep as explore/low-stakes; a 3rd clean task would justify low-stakes promotion.

Budget: ~$2.80 OpenRouter remaining after M3 (m3-import ~$0.45; everything else free/cheap). Cost-optimized routing (free-tier bulk + glm insurance + sonnet for gnarly) held up: the wave cost less than one sonnet task alone.

Process lessons: (1) `git apply --check` per patch before applying catches the rare cross-task file overlap (none this wave; m3-import and m3-sentences both touched frontend/src/api.ts but in disjoint regions and applied cleanly). (2) Keep max_parallel 2 as the default on this machine — 4 parallel venvs still risk the disk-full crash. (3) Ringer's post-run summary table (task/status/verdict/attempts/tokens/elapsed_s) is the authoritative record for the notes — pull it from the run log tail.
## VScriptEd M4 (2026-08-30, code, vscripted-m4 + vscripted-m4-retry)

4 tasks: slides composite video export with subtitles + chapters (gnarly, ffmpeg), slide-timeline API, export UI, PPTX per-slide render.

**INFRA FAILURE (important, not model failures):** run 1 ran 4 workers at max_parallel 2; OpenRouter returned 402 "This request would exceed your available credits given your current in-flight requests" to the three PAID workers (sonnet compose, glm timeline, glm export-ui) mid-attempt — parallel in-flight credit holds against the remaining balance. The FREE-tier worker (minimax m4-pptx) was unaffected and PASSed attempt 1 (31.6k, 94s). Lesson: when the budget is thin, run paid workers SERIALLY (max_parallel 1) so only one in-flight hold exists; free-tier tasks are immune and can always run in parallel. Check `usage` on the key before spawning a paid wave; if remaining < ~2x the expected per-task cost, go serial.

Retry (serial, all GLM-5.2) — all three PASSed attempt 1:
- **m4-timeline** — 36.4k tokens, 145s. Real ffmpeg two-scene video, multipart upload, SlideInterval storage, 422 paths, regression on the existing endpoint.
- **m4-export-ui** — 16.1k tokens, 54s. Fastest frontend task of the build so far.
- **m4-compose** — 89.9k tokens, 529s. THE gnarly task: per-interval image→mp4 segments, concat, kept-audio mux (trim/apad to timeline duration), subtitle burn-in via temp-dir `subtitles=` filter, chapters sidecar, 7+ ffmpeg/ffprobe-verified tests. GLM delivered it first-try.

**GLM 5.2 is now 7/7 code tasks first-try (100%)**, including the hardest task in the project (multi-stage ffmpeg composition). The "gnarly → sonnet" routing heuristic was over-conservative: with a spec that prescribes the exact ffmpeg commands and exact test assertions, GLM matches sonnet on gnarlyn timer. Update routing: GLM = primary for ALL code tasks (including gnarly, when the spec prescribes concrete commands); sonnet reserved for tasks where the spec must stay high-level (open-ended design, cross-system debugging). Scoreboard: GLM proven 7 tasks 100%; sonnet proven 6 tasks 83%; minimax free 4 tasks 75% (m4-pptx first-try; two M2 FAIL rows remain check-bug artifacts).

Process lessons: (1) A worker's PASS + my manual live smoke can both be "right" with different fixtures: the composed MP4 passed the worker's full-frame solid-color scene test (score > 0.3) while my letterboxed PDF-slide fixture peaked at 0.21 — the scene threshold is fixture-dependent; verify transitions by frame extraction, not only by the scene filter. (2) The base repo had a latent crash (`shutil.unlink` — nonexistent; should be `Path.unlink`) in the PPTX soffice branch, untriggered until LibreOffice was installed; install an optional dependency THEN re-run the code path that uses it. (3) Shared model fields (SlideInterval + Session.slide_timeline) were committed to the base by the orchestrator BEFORE the wave — zero cross-task model conflicts, same pattern as M3's frozen contracts.
## VScriptEd timeline continuation (2026-09-17, code-feature, all-local routing)

User directive: remaining VScriptEd timeline work (D10 negative-offset mix fix, P4 stretch items, acceptance passes) runs on the three LOCAL Qwen endpoints only — no paid API spend.

Endpoints (verified up 2026-09-17 via /v1/models):
- `vllm/qwen3.8-27b` — vLLM at ai.jumpforjoy.one:8001 (27B; also powers the orchestrator session)
- `local-llama/qwen3.8-9b` — llama.cpp on this Mac, port 8901 (9B Q4_K_M, 32k ctx)
- `local-llama-macbookair/qwen3.8-9b-gguf` — llama.cpp on MacBook Air over Tailscale 100.97.42.21:8081 (9B GGUF)

**Routing decision (all-local VScriptEd):** 27B = hard lanes (D10 mix-chain fix, anything touching export/integration, acceptance-test verification); 9B (local or Air) = small, tightly-specified mechanical tasks only (P4 items: dB-gain numeric entry, thumbnails hook, word-click→scroll, click-toggle gap) with strong executed checks. Do NOT give 9Bs long multi-turn builds — 32k ctx is the choke point (small/flash-class lesson, 2026-07-05). The Air endpoint is remote (tailnet): ping its /v1/models before each wave; if down, the local 9B takes its lane.

Evidence basis (scoreboard, code-feature): vllm 27B 18 tasks, 28% first-try / 56% pass, median 13m49s (slow but it works, free, offline); local 9B ~29-33% first-try on 10 tasks. Expect retries on all lanes — size timeouts for slow local inference (27B median ~14 min; set timeout_s well above) and keep max_parallel modest (local llama.cpp serves one request well; don't hammer the 9B box with 3+ concurrent workers).
## VScriptEd timeline round 2 (2026-09-17, code-feature, vscripted-timeline-round2)

All-local run per user directive (27B vLLM + 9B pygmy). 3 tasks: d10-negative-offset-mix (27B), video-thumbnails (27B), db-gain-numeric-entry (9B pygmy).

- **vllm/qwen3.8-27b** — d10: PASS attempt 1 (_mix_chain atrim head-trim fix + 3 real-ffmpeg tests, first try). video-thumbnails: PASS on the third run's attempt 1 — both earlier FAILs were the orchestrator's check (venv install list missing `numpy`, then `scipy` — see the 27B section above), not worker output.
- **local-llama/qwen3.8-9b (pygmy)** — db-gain-numeric-entry: PASS attempt 2. Attempt-1 failure detail not preserved in run state (state keeps only the final attempt's check output — a Ringer gap worth fixing). 9B on a small single-file UI task: holds up, but not first-try reliable.
- Orchestrator integration: patches applied, one-shot fix of the 9B's numeric-input flaw (`Number("") === 0` would silently commit 0 dB on field clear — replaced with a local text state), full backend suite 573 PASS, frontend tsc/vite/oxlint clean, committed VScriptEd 3e25473.

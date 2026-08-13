# Scripts

Working scripts that (re)generate `BEST_PRACTICES.md` — the combined reference document — from the live rules, SKILL.md files, and the Google Testing Blog posts referenced in the repo README.

## Validation

```bash
python3 scripts/validate_skills.py           # structural validation of skills/
python3 scripts/validate_skills.py --strict  # warnings fail too (CI uses this)
```

Checks SKILL.md frontmatter, allowed-tools vs. tools the body actually instructs the agent to use, rule-reference integrity in both directions (referenced files exist; no orphan rule files), rule frontmatter (`title`, `impact`), and byte-level sync of the duplicated general-rules directories. Runs in CI on every PR and on pushes to `main` via `.github/workflows/validate-skills.yml`.

## Pipeline (run in this order, from anywhere)

```bash
python3 scripts/fetch_all.py                    # 1. README blog URLs → scripts/fetched_google_articles.json
python3 scripts/generate_comprehensive_docs.py  # 2. writes BEST_PRACTICES.md Parts 1–3 (skill guide, TotT summaries, rule copies)
python3 scripts/append_skill_docs.py            # 3. appends Part 4 (SKILL.md workflow copies)
python3 scripts/append_google_articles.py       # 4. appends Part 5 (fetched article extracts)
```

All paths are resolved relative to the repo root via `__file__`, so the scripts work from any working directory.

> **Warning — do not re-run step 1 against the current README.** The root `README.md` no longer contains any `testing.googleblog.com` URLs (they were moved to `BEST_PRACTICES.md`), so running `fetch_all.py` now overwrites `scripts/fetched_google_articles.json` with an empty result. The committed `fetched_google_articles.json` is the source; `fetch_all.py` needs re-pointing (e.g. at `BEST_PRACTICES.md`) before it is useful again.

## Files

| File | Purpose |
|---|---|
| `validate_skills.py` | Structural validation of `skills/` (frontmatter, rule references, general-rules sync) — run by CI |
| `fetch_all.py` | Fetch all `testing.googleblog.com` URLs found in `README.md` (first 2000 chars each) |
| `fetched_google_articles.json` | Fetch output consumed by the append step |
| `generate_comprehensive_docs.py` | Build Parts 1–3: skill-building guide, Google TotT principle summaries, and verbatim copies of all rule files (general + csharp + typescript + post-generation) |
| `append_skill_docs.py` | Append Part 4: verbatim SKILL.md copies |
| `append_google_articles.py` | Append Part 5: fetched article extracts |
| `combine_rules.py` | DEPRECATED — older partial variant; do not run |

## Known limitations

- `fetch_all.py` scans `README.md` for `testing.googleblog.com` URLs, but the root README no longer contains any — see the warning in the Pipeline section before running it.
- `fetch_all.py`'s naive `<p>`-tag extraction fails on Blogger's markup — most Part 5 entries come back as "Failed to fetch content." Fetching the raw HTML with `curl` and extracting the post body is more reliable.
- The Part 2 summaries in `generate_comprehensive_docs.py` are hardcoded strings. Several were found inaccurate against the source posts in a 2026-07-30 review (attribution and nuance errors — e.g. "Fake Your Way to Better Tests" never mentions mocks; the don't-mock-types-you-don't-own hierarchy is real → owner fake → wrapper mock as last resort; the Vercel 53% figure is also the no-docs baseline). Update the strings there before regenerating if accuracy matters.
- `BEST_PRACTICES.md` is a generated snapshot — the live rules under `skills/` are always the source of truth.

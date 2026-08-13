import os
import json

# Repo root = parent of scripts/ — paths work no matter where this is run from
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

output_file = os.path.join(ROOT, "BEST_PRACTICES.md")

general_dir = os.path.join(ROOT, "skills/generate-tests/rules/tests/general")
csharp_dir = os.path.join(ROOT, "skills/generate-tests/rules/tests/csharp/unit")
typescript_dir = os.path.join(ROOT, "skills/generate-tests/rules/tests/typescript/unit")
post_dir = os.path.join(ROOT, "skills/generate-tests/rules/tests/post-generation")

def process_dir(directory, section_title):
    content = f"# {section_title}\n\n"
    if not os.path.exists(directory):
        return content
        
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".md"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r") as f:
                file_content = f.read()
                content += f"## {filename}\n\n"
                content += file_content
                content += "\n\n---\n\n"
    return content

with open(os.path.join(ROOT, 'scripts/fetched_google_articles.json'), 'r') as f:
    google_articles = json.load(f)

with open(output_file, "w") as f:
    f.write("# Super Comprehensive Unit Test & Skill Development Best Practices\n\n")
    
    # --- PART 1: AGENT SKILL BUILDING ---
    f.write("# Part 1: Building Skills for Claude & AI Agents\n\n")
    f.write("Based on Anthropic's 'The Complete Guide to Building Skills for Claude' and Vercel's AGENTS.md research.\n\n")
    
    f.write("## 1.1. Why AGENTS.md Matters\n")
    f.write("According to Vercel's research (Next.js 16 API eval): skills alone scored 53% — identical to the no-docs baseline (+0pp; the agent skipped invoking the skill in 56% of cases). Skills with explicit prompting reached 79%. An `AGENTS.md` in the project root reached 100%, because its content sits in the system prompt on every turn — no decision point, no ordering issues. Caveats from the article: docs were compressed 40KB -> 8KB to control context cost, results were sensitive to instruction wording, and skills are still recommended for vertical, user-triggered workflows.\n\n")
    
    f.write("## 1.2. The Skill Folder Structure\n")
    f.write("A valid skill must follow these rules:\n")
    f.write("- **Folder name**: `kebab-case` only (e.g., `generate-tests`). No spaces or capitals.\n")
    f.write("- **Required file**: Exactly `SKILL.md` (case-sensitive) containing YAML frontmatter and markdown instructions.\n")
    f.write("- **No README.md**: Do not put a README.md inside the skill folder itself.\n")
    f.write("- **Progressive Disclosure**: Keep `SKILL.md` focused and under 5000 words. Place detailed documentation in a `references/` directory and link to it.\n\n")
    
    f.write("## 1.3. YAML Frontmatter Requirements\n")
    f.write("The YAML frontmatter tells Claude when to use the skill:\n")
    f.write("- `name`: kebab-case, no spaces or capitals.\n")
    f.write("- `description`: Under 1024 characters. Must include BOTH what the skill does AND when to use it (trigger conditions/phrases).\n")
    f.write("- Forbidden: XML angle brackets (`<`, `>`) and the words 'claude' or 'anthropic' in the name.\n\n")

    f.write("## 1.4. Effective Instructions\n")
    f.write("- Use clear, actionable steps.\n")
    f.write("- Include Error Handling (e.g., 'If validation fails, common issues include...').\n")
    f.write("- Provide examples of good and bad outputs.\n\n")

    f.write("---\n\n")
    
    # --- PART 2: GOOGLE'S TESTING ON THE TOILET PRINCIPLES ---
    f.write("# Part 2: Google's Testing on the Toilet Principles\n\n")
    f.write("This section contains an exhaustive summary of Google's unit testing principles, including those not yet implemented as explicit rules in the repository.\n\n")
    
    # High Priority Not Implemented items from the README:
    f.write("## 2.1. High-Priority Testing Principles\n\n")
    f.write("### Increase Test Fidelity By Avoiding Mocks\n")
    f.write("Fidelity = how closely test behavior resembles production behavior. Preference order: use the real implementation; use a fake if the real one is too slow, non-deterministic, or hard to instantiate; use a mock only if neither is possible. Mocks remain especially useful for hard-to-trigger paths (e.g. timeouts). Keep tests 'small' (single process) while raising fidelity. Fakes should be created and maintained by the owner of the real implementation.\n\n")

    f.write("### Don't Mock Types You Don't Own\n")
    f.write("Mocking third-party types makes maintenance harder: library upgrades break stale mock assumptions and can hide real bugs. Preference order per the post: (1) use the real implementation, (2) use a fake ideally provided by the library owner, (3) only as a last resort wrap the type in your own class and mock the wrapper — and test the wrapper itself against the real implementation. (Credited to Freeman & Pryce, GOOS.)\n\n")

    f.write("### Only Verify State-Changing Method Calls\n")
    f.write("Usually avoid verifying that non-state-changing methods (queries/getters) were called — it is redundant, brittle, and gives false confidence. Verify state-changing calls (SendEmail, SaveRecord) instead, and use queries for stubbing. Exception: verifying a query call is useful when there is no other observable output (e.g. asserting an RPC happens exactly once to test caching). Better still: use a real or fake object and assert the resulting state.\n\n")

    f.write("### Change-Detector Tests Considered Harmful\n")
    f.write("A change-detector test is a transformation of the same information in the code under test — it breaks on any production change without verifying correct behavior (a 'checksum' of the source). Such tests provide negative value: rewrite or delete them. Test behaviors, not implementation.\n\n")

    f.write("### Know Your Test Doubles\n")
    f.write("Stub: no logic, only returns what you tell it. Mock: has expectations about how it is called; used for interaction testing when there is no visible state or return value. Fake: a lightweight working implementation of the API unsuitable for production (e.g. in-memory database), built without a mocking framework — usually created and maintained by the real implementation's owner. (Terminology from Meszaros, xUnit Test Patterns.)\n\n")

    f.write("### Fake Your Way to Better Tests\n")
    f.write("Use fakes when the real implementation is too slow or non-deterministic. Fakes should be created and maintained by the owner of the real implementation, need their own tests (ideally the same contract tests run against both real and fake), and should be applied at the lowest layer possible — if a dependency can't be faked, wrap the untestable part and fake the wrapper. Keep a small number of integration tests against the real implementation.\n\n")

    f.write("### Don't Overuse Mocks\n")
    f.write("Over-mocked tests are harder to understand, leak implementation details into the test, and give less assurance (they only prove the code works if the mocks behave exactly like the real implementations — which drifts). Heuristics: mocking more than 1-2 collaborators, a mock stubbing more than 1-2 methods, or needing to step through production code to understand the test. Alternatives: real objects, fakes, hermetic local servers.\n\n")

    f.write("### Testing State vs. Testing Interactions\n")
    f.write("In most cases test state, not interactions: a passing interaction test proves a method was called, not that the result is correct (that Sort() was invoked says nothing about whether sorting works). Interaction testing is legitimate when correctness depends on HOW the result is produced: call count or order matters (exactly one email sent, bounded reads, deadlock-avoiding order) or MVC/MVP-style UI wiring.\n\n")
    
    f.write("## 2.2. Medium and Low Priority Principles\n\n")
    f.write("### Separation of Concerns? That's a Wrap!\n")
    f.write("Wrap external/third-party APIs behind your own types so API-call details stay out of domain logic — for maintainability, insulation from API changes, easier swapping, and readability. Caveat (YAGNI): don't wrap when the effort is huge or the API is simple and stable (e.g. List).\n\n")

    f.write("### Tests Too DRY? Make Them DAMP!\n")
    f.write("Production code should be DRY, but tests should be DAMP (Descriptive And Meaningful Phrases). Duplication in tests is acceptable when it improves readability and makes each test understandable at a glance. DAMP complements DRY rather than replacing it — helpers are still fine when they don't hurt clarity.\n\n")

    f.write("### Exercise Service Call Contracts in Tests\n")
    f.write("If code under test relies on a service's contract, prefer exercising the service call over mocking it out: use a fast, lightweight fake maintained by the service owners (don't hand-roll one you can't keep in sync), or a hermetic server started by the test on the same machine (slower). Mocks may be the only option when neither exists — then compensate with end-to-end tests or manual QA.\n\n")
    
    f.write("---\n\n")

    # --- PART 3: EXISTING SKILL RULES ---
    f.write("# Part 3: Active Skill Rules Repository\n\n")
    f.write(process_dir(general_dir, "General Rules"))
    f.write(process_dir(csharp_dir, "C# / .NET Rules"))
    f.write(process_dir(typescript_dir, "TypeScript/JavaScript Rules"))
    f.write(process_dir(post_dir, "Post-Generation Rules"))
    
print(f"Generated {output_file}")

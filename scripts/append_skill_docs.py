import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(ROOT, "BEST_PRACTICES.md"), "a") as out_f:
    out_f.write("\n\n---\n\n")
    out_f.write("# Part 4: AI Agent Workflow Specifications\n\n")
    out_f.write("This section details the exact workflows defined in the `SKILL.md` files that AI agents must follow when executing these skills.\n\n")

    with open(os.path.join(ROOT, "skills/generate-tests/SKILL.md"), "r") as in_f:
        out_f.write("## generate-tests SKILL.md\n\n")
        out_f.write(in_f.read())
        out_f.write("\n\n---\n\n")

    with open(os.path.join(ROOT, "skills/generate-test-cases/SKILL.md"), "r") as in_f:
        out_f.write("## generate-test-cases SKILL.md\n\n")
        out_f.write(in_f.read())
        out_f.write("\n\n---\n\n")

print("Appended SKILL.md contents to BEST_PRACTICES.md")

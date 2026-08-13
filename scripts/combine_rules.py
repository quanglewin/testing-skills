# DEPRECATED: superseded by generate_comprehensive_docs.py (which builds the full
# 5-part BEST_PRACTICES.md). This older variant still references the removed
# java/unit directory and a machine-specific artifact path. Kept for history only —
# do not run. Safe to delete.
import os

general_dir = "skills/generate-tests/rules/tests/general"
java_dir = "skills/generate-tests/rules/tests/java/unit"
post_dir = "skills/generate-tests/rules/tests/post-generation"
google_artifact = "/Users/anders/.gemini/antigravity-ide/brain/a47707b9-a0f7-4e93-91a2-9e584ac3d440/unit_test_best_practices.md"

output_file = "BEST_PRACTICES.md"

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

with open(output_file, "w") as f:
    f.write("# Unit Testing Best Practices\n\n")
    
    # Add the artifact summary
    if os.path.exists(google_artifact):
        with open(google_artifact, "r") as a:
            f.write(a.read())
            f.write("\n\n---\n\n")
            
    f.write(process_dir(general_dir, "General Rules"))
    f.write(process_dir(java_dir, "Java Rules"))
    f.write(process_dir(post_dir, "Post-Generation Rules"))

print(f"Created {output_file}")

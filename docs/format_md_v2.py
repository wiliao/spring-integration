#!/usr/bin/env python3
"""
Improved reformatting - fixes bugs from v1:
  - Don't damage heading text when removing duplicate body titles
  - Handle bullets after ) and ] not just .
  - Remove orphan ```
  - Better handle inline numbered lists
"""
import re

INPUT = r"C:\Samples-03-spring-integration-camel\spring-integration\docs\Enterprise Integration Patterns - Designing, Building And Deploying Messaging Solutions.md"


def step(msg):
    print(f"  {msg}")


def main():
    with open(INPUT, "r", encoding="utf-8") as f:
        content = f.read()

    orig_len = len(content)
    print(f"Input: {orig_len:,} chars")

    # 1. Remove orphan ``` at line 257: "``` Publisher, Subscriber Publisher, Subscriber"
    # Pattern: ``` followed by text on same line that isn't a code fence
    content = re.sub(r"^```\s+[A-Z][a-z].*$", "", content, flags=re.MULTILINE)
    step("[1] Removed orphan ``` with text on same line")

    # 2. Remove remaining orphan ``` markers (not at start of line as proper fence)
    # These appear as ``` Publisher or ``` in middle of paragraphs
    content = re.sub(r"\n```\s+[A-Z][^\n]*", "", content)
    content = re.sub(r"```\s+[A-Z][a-z][^\n]*\n", "\n", content)
    step("[2] Removed mid-paragraph ``` markers")

    # 3. Fix heading text corruption: "### Distributed Applications vs. " missing "Integration"
    # This happened because the previous script's duplicate removal damaged the heading.
    # Add back the missing words.
    content = content.replace("### Distributed Applications vs. \n", "### Distributed Applications vs. Integration\n")
    content = content.replace("### Distributed Applications vs.  ", "### Distributed Applications vs. Integration ")
    step("[3] Fixed corrupted heading text")

    # 4. Split bullets after ) ] " ' not just .
    # Pattern: "text) - Foo" or "text] - Foo" should split
    content = re.sub(r"([)\]\"'])\s+-\s+", r"\1\n- ", content)
    # Pattern: "text, - Foo" should split (less common but still valid)
    content = re.sub(r",\s+-\s+(?=[A-Z])", ",\n- ", content)
    step("[4] Split bullets after ) ] \" ' , ")

    # 5. Better numbered list splitting
    # Pattern: ". 1. Foo" should split, but "1. Foo" at start should not
    # We need to ensure the period before "1." is a sentence-ending period
    content = re.sub(r"(\w\w\.) (\d{1,2}\. [A-Z])", r"\1\n\2", content)
    # Pattern: " (1. Foo)" or " [1. Foo]" should split
    content = re.sub(r"([)\]\"']) (\d{1,2}\. [A-Z])", r"\1\n\2", content)
    step("[5] Better numbered list splitting")

    # 6. Format vendor comparison tables as code blocks (preserving layout)
    # Find patterns like "Enterprise Integration Patterns\nJava Message Service..."
    # followed by rows. Convert to code block for visual fidelity.
    # This is hard to detect generically, so just keep as is - the user can
    # manually format if needed.

    # 7. Break long paragraphs at "Title This" patterns
    # Where a known title (like "Synchronous and Asynchronous Call Semantics")
    # is followed by a sentence, split it
    # Already handled by step 4 in v1, but we can do more carefully
    # Skip for now to avoid breaking

    # 8. Clean up whitespace
    content = re.sub(r"\n{4,}", "\n\n\n", content)
    step("[6] Cleaned up excessive whitespace")

    # 9. Ensure blank line before headings (except first heading)
    content = re.sub(r"([^\n])\n(#{1,6}\s+)", r"\1\n\n\2", content)

    # 10. Ensure blank line after headings (except if followed by another heading)
    content = re.sub(r"(#{1,6}\s+[^\n]+)\n([^\n#\s])", r"\1\n\n\2", content)
    step("[7] Ensured blank lines around headings")

    # 11. Remove list item indentation
    content = re.sub(r"^[ \t]+(- )", r"\1", content, flags=re.MULTILINE)
    content = re.sub(r"^[ \t]+(\d+\. )", r"\1", content, flags=re.MULTILINE)
    step("[8] Cleaned list item indentation")

    # 12. Final whitespace cleanup
    content = re.sub(r"\n{3,}", "\n\n", content)
    step("[9] Final whitespace cleanup")

    with open(INPUT, "w", encoding="utf-8") as f:
        f.write(content)

    final_len = len(content)
    final_lines = content.count("\n")
    print(f"\nOutput: {final_len:,} chars, {final_lines:,} lines")
    print(f"Change: {final_len - orig_len:+,} chars")


if __name__ == "__main__":
    main()

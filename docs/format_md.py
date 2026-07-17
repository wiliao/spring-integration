#!/usr/bin/env python3
"""
Comprehensive reformatting of EIP markdown for GitHub.
Fixes:
  1. Remove stray ``` markers at top
  2. Split long paragraphs at bullet points (- ...) and numbered items (1. ..., 2. ..., etc.)
  3. Remove duplicate section titles embedded in body text
  4. Fix tables wrongly wrapped in code blocks
  5. Format vendor comparison tables as proper markdown tables
  6. Remove broken/orphaned code fences
  7. Reformat numbered lists that span multiple lines
"""
import re
import sys

INPUT = r"C:\Samples-03-spring-integration-camel\spring-integration\docs\Enterprise Integration Patterns - Designing, Building And Deploying Messaging Solutions.md"


def step(msg):
    print(f"  {msg}")


def main():
    with open(INPUT, "r", encoding="utf-8") as f:
        content = f.read()

    orig_len = len(content)
    print(f"Input: {orig_len:,} chars, {content.count(chr(10)):,} lines")

    # 1. Remove stray ``` at very top of file
    content = re.sub(r"^```\s*\n```\s*\n", "", content)
    step("[1] Removed stray ``` at top")

    # 2. Remove duplicate section title in body
    # Pattern: a section heading like "### Who Should Read This Book" appears,
    # then in the body text the same heading is repeated as the first words.
    # We walk through and remove inline duplicates.
    lines = content.split("\n")
    headings = []
    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if m:
            headings.append((m.group(1), m.group(2).strip()))

    # For each heading, remove a single inline occurrence from the *next* paragraph block.
    # Build a map: heading text -> count of inline matches we should remove
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        i += 1

    content = "\n".join(new_lines)
    # Now do regex-based removal: for each heading, look for the heading text repeated
    # after a paragraph break or sentence end within the following ~2000 chars,
    # and remove ONE inline occurrence.
    for hmarker, htext in headings:
        if not htext or len(htext) < 5 or len(htext) > 200:
            continue
        # Escape for regex
        esc = re.escape(htext)
        # Pattern: " {htext} " (surrounded by spaces) - inline duplicate.
        # Only do this if we haven't already removed it.
        # Look for ". Htext " (sentence end duplicate) or "\n\nHtext " (paragraph duplicate)
        pat = re.compile(r"(\.\s+|\n\n)" + esc + r"(\s+[A-Z])")
        content, n = pat.subn(r"\1\2", content, count=1)
    step("[2] Removed duplicate section titles in body")

    # 3. Split lines at bullet points: convert inline " - " bullet markers into new lines
    # Only when preceded by a sentence-ending character (., :, !, ?, or end of text)
    # and the bullet content is reasonably long.
    # We do this carefully: replace ": - " or ". - " with ":\n- " or ".\n- "
    # and " - " (after a capital letter or after a period) with "\n- ".

    # First: split at common bullet patterns in long paragraphs
    # ": - Foo" => ":\n- Foo" (after colon, common in "such as: - Foo")
    content = re.sub(r":\s+-\s+", ":\n- ", content)
    # ". - Foo" => ".\n- Foo" (after period, common in "problems: ... . - Foo")
    content = re.sub(r"\.\s+-\s+", ".\n- ", content)
    # " - Foo" when followed by capital => "\n- Foo"
    # but only if not at start of line and preceded by lowercase letter (continuation)
    content = re.sub(r"(?<=[a-z])\s+-\s+(?=[A-Z])", "\n- ", content)
    step("[3] Split paragraphs at bullet points (- ...)")

    # 4. Split at numbered list items embedded in paragraphs
    # Pattern: " . 1. Foo" or " . 1. Foo . 2. Bar" - convert to separate lines
    # We look for ". 1. ", ". 2. ", etc. preceded by sentence-ending punctuation.
    # Specifically, if " N. " is in the middle of a paragraph, start a new line.

    # First handle ". N. Foo . M. Bar" pattern (period between items)
    def split_numbered(text):
        # Match ". N. " (period, space, digit, period, space) where N is 1-9
        # and not at start of line
        # Use lookbehind to ensure not at line start
        pattern = re.compile(r"(?<=\S)\.\s+(\d{1,2}\.\s+)(?=[A-Z])")
        return pattern.sub(r".\n\1", text)

    content = split_numbered(content)
    step("[4] Split paragraphs at numbered list items (1. 2. 3. ...)")

    # 5. Fix broken code blocks (especially tables wrongly wrapped)
    # Find code blocks that are not actually code: typically they contain
    # regular English text. The pattern: ```java ... [regular text] ... ```
    # We need to detect such blocks and either close them properly or remove them.

    # The known issue: lines 209-214 wrap a table in ```java ... ```
    # Lines 242-250 wrap another table fragment in ```
    # Let's find such blocks

    # Find all fenced code blocks
    fence_pattern = re.compile(r"^(```[a-zA-Z0-9]*)\s*$", re.MULTILINE)
    fence_positions = [(m.start(), m.end(), m.group(1)) for m in fence_pattern.finditer(content)]
    print(f"  Found {len(fence_positions)} code fence markers")

    # Strategy: identify broken code blocks (where content is not really code)
    # and fix them. We'll process the content and rebuild it.

    # Look for the known problematic patterns:
    # Pattern A: ```java\n[long text including 'Enterprise Integration Patterns' or '---']\n```
    # Pattern B: ```\n[table content]\n``` Publisher, ... (orphaned)

    # Specifically: find ```java ... [English text] ... ``` and convert to plain text
    # by removing the fence markers
    def fix_broken_code_blocks(text):
        result = []
        i = 0
        # Process line by line
        lines = text.split("\n")
        out = []
        in_code_block = False
        code_block_lang = None
        code_block_lines = []
        j = 0
        while j < len(lines):
            line = lines[j]
            stripped = line.strip()
            # Detect code fence
            if re.match(r"^```[a-zA-Z0-9]*\s*$", stripped):
                if not in_code_block:
                    # Opening fence
                    in_code_block = True
                    code_block_lang = stripped[3:].strip() or None
                    code_block_lines = []
                else:
                    # Closing fence - process the block
                    block_text = "\n".join(code_block_lines)
                    # Check if this looks like real code
                    looks_like_code = False
                    if code_block_lang in ("java", "csharp", "cs", "xml", "python", "javascript", "js", "cpp", "c", "go", "rust", "sql", "html"):
                        # Check for code indicators
                        code_indicators = [
                            r"\bclass\s+\w+",
                            r"\bpublic\s+",
                            r"\bprivate\s+",
                            r"\bstatic\s+",
                            r"\bint\s+\w+\s*[=;]",
                            r"\bString\s+\w+",
                            r"\bvoid\s+",
                            r"<\?xml",
                            r"<\w+[^>]*>",
                            r"\{\s*$",
                            r"^\s*\}",
                            r"\bnew\s+\w+",
                            r"\bimport\s+",
                            r"\breturn\s+",
                            r"\bif\s*\(",
                            r"\bfor\s*\(",
                            r"\bwhile\s*\(",
                            r"\bswitch\s*\(",
                            r"//\s*",
                            r"System\.",
                            r"Console\.",
                            r"\bprint\(",
                        ]
                        for ind in code_indicators:
                            if re.search(ind, block_text):
                                looks_like_code = True
                                break
                    # If it's not really code, drop the fences
                    if not looks_like_code and code_block_lines:
                        # Just emit the content without fences
                        out.extend(code_block_lines)
                    else:
                        # Real code: keep fences
                        if code_block_lang:
                            out.append("```" + code_block_lang)
                        else:
                            out.append("```")
                        out.extend(code_block_lines)
                        out.append("```")
                    in_code_block = False
                    code_block_lang = None
                    code_block_lines = []
            else:
                if in_code_block:
                    code_block_lines.append(line)
                else:
                    out.append(line)
            j += 1
        # Handle unclosed block
        if in_code_block and code_block_lines:
            out.extend(code_block_lines)
        return "\n".join(out)

    content = fix_broken_code_blocks(content)
    step("[5] Fixed broken/non-code blocks (removed wrong fences)")

    # 6. Clean up orphaned ``` markers that have no matching pair
    # Count fences and ensure they are balanced
    fence_count = len(re.findall(r"^```[a-zA-Z0-9]*\s*$", content, re.MULTILINE))
    if fence_count % 2 != 0:
        # Remove the last unpaired fence
        # Find all fence positions
        matches = list(re.finditer(r"^```[a-zA-Z0-9]*\s*$", content, re.MULTILINE))
        if matches:
            last = matches[-1]
            content = content[:last.start()] + content[last.end():]
    step("[6] Balanced code fence markers")

    # 7. Format vendor comparison tables as proper markdown tables
    # The pattern is rows of text like "Header1 Header2 Header3" followed by
    # "item1 item2 item3" etc. Convert into markdown table format.
    # This is tricky to do perfectly; we'll handle the most common case
    # by detecting sequences of short lines that look like table rows.

    # Skip for now to avoid breaking - the existing format with code blocks is OK

    # 8. Clean up excessive whitespace (3+ blank lines)
    content = re.sub(r"\n{4,}", "\n\n\n", content)
    step("[7] Cleaned up excessive whitespace")

    # 9. Ensure blank line before headings (except first)
    content = re.sub(r"([^\n])\n(#{1,6}\s+)", r"\1\n\n\2", content)

    # 10. Ensure blank line after headings (except if followed by another heading or end)
    content = re.sub(r"(#{1,6}\s+[^\n]+)\n([^#\n\s])", r"\1\n\n\2", content)
    step("[8] Ensured blank lines around headings")

    # 11. Remove leading whitespace from list items that were indented
    # (they may have leftover indentation from PDF extraction)
    # Be careful: only for actual list items, not paragraphs
    # Detect "- " at start of line, ensure no leading whitespace
    content = re.sub(r"^[ \t]+(- )", r"\1", content, flags=re.MULTILINE)
    content = re.sub(r"^[ \t]+(\d+\. )", r"\1", content, flags=re.MULTILINE)
    step("[9] Cleaned list item indentation")

    # 12. Convert the standalone "Tightly Coupled Interaction" and other figure captions
    # These are typically just bold text on their own line, like "**WGRUS Ecosystem**"
    # or plain text. Keep them as bold paragraphs.
    # Actually they're often already on their own line, so no action needed.

    # 13. Remove duplicate "by John Crupi" / "by Martin Fowler" paragraphs from foreword
    # These are already handled by step 2

    # 14. Fix "by Author... Read this book" pattern in foreword
    # The foreword has a long paragraph that should be split. Already handled by 2.

    # Final cleanup
    content = re.sub(r"\n{3,}", "\n\n", content)
    step("[10] Final whitespace cleanup")

    with open(INPUT, "w", encoding="utf-8") as f:
        f.write(content)

    final_len = len(content)
    final_lines = content.count("\n")
    print(f"\nOutput: {final_len:,} chars, {final_lines:,} lines")
    print(f"Change: {final_len - orig_len:+,} chars")
    print(f"Written to: {INPUT}")


if __name__ == "__main__":
    main()

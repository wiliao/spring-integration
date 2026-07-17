#!/usr/bin/env python3
"""Extract PDF page 2 with full position/dict info."""
import fitz, json, sys

doc = fitz.open(r"C:\Samples-03-spring-integration-camel\spring-integration\docs\Enterprise Integration Patterns - Designing, Building And Deploying Messaging Solutions.pdf")
page = doc[1]  # page 2 (0-indexed)

# Get dict with position info
blocks = page.get_text("dict")["blocks"]

print(f"Page 2: {len(blocks)} blocks")
for bi, block in enumerate(blocks):
    if block["type"] == 0:  # text
        for line in block["lines"]:
            bbox = line["bbox"]
            x, y = bbox[0], bbox[1]
            text = ""
            for span in line["spans"]:
                text += span["text"]
            # Print position and text
            indent_level = int((x - 72) / 18) if x > 72 else 0  # rough indent calculation
            indent = "  " * indent_level
            sys.stdout.write(f"{indent}{text}\n")
    elif block["type"] == 1:  # image
        sys.stdout.write(f"[IMAGE: {block['width']}x{block['height']} at ({block['bbox'][0]:.0f},{block['bbox'][1]:.0f})]\n")


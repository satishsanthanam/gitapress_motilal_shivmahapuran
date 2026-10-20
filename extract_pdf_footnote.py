import sys
import os
import re
from pypdf import PdfReader

def extract_pdf_footnote_pages(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File '{pdf_path}' not found.")
        return

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    print(f"📄 Scanning '{pdf_path}' ({total_pages} pages)...\n")

    found_pages = []

    for page_idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        lines = [line.rstrip() for line in text.split('\n') if line.strip()]
        total_lines = len(lines)
        
        if not lines:
            continue

        page_footnotes = []
        i = 0
        while i < total_lines:
            line = lines[i]
            relative_pos = i / total_lines  # Position in page (0.0 = top, 1.0 = bottom)

            # 1. Ignore Table of Contents patterns (ending with dotted page numbers e.g. '... 65')
            is_toc_line = bool(re.search(r'[\.]{2,}\s*\d+\s*$', line) or re.search(r'\s{4,}\d+\s*$', line))

            # 2. Check for explicit Footnote markers
            is_asterisk_fn = bool(re.search(r'^\s*[\*\u2022]', line))
            is_numbered_fn = bool(re.search(r'^\s*[\(\[]?[०-९\d]+[\)\]\.]', line))
            is_explicit_fn = "[fn:" in line

            # A valid footnote must either be:
            # - An explicit [fn: ...] tag
            # - An asterisk footnote (*)
            # - A numbered footnote (1., (१)) located strictly in the BOTTOM 35% of the page
            is_valid_start = (
                is_explicit_fn or 
                (is_asterisk_fn and not is_toc_line) or 
                (is_numbered_fn and relative_pos >= 0.65 and not is_toc_line)
            )

            if is_valid_start:
                # Forward match: Collect multiline continuation until next block
                fn_block = [line.strip()]
                i += 1
                while i < total_lines:
                    next_line = lines[i]
                    next_rel_pos = i / total_lines
                    
                    # Stop if next line is a new footnote start, verse end (॥), or TOC line
                    if (re.search(r'^\s*[\*\u2022]', next_line) or 
                        re.search(r'^\s*[\(\[]?[०-९\d]+[\)\]\.]', next_line) or 
                        "[fn:" in next_line or 
                        re.search(r'[\.]{2,}\s*\d+\s*$', next_line)):
                        break
                    
                    fn_block.append(next_line.strip())
                    i += 1

                combined_fn = " ".join(fn_block)
                page_footnotes.append(combined_fn)
            else:
                i += 1

        if page_footnotes:
            found_pages.append((page_idx, page_footnotes))

    # --- Print Summary & Results ---
    if not found_pages:
        print("ℹ️ No footnotes found in this PDF.")
        return

    print("=" * 60)
    print(f"📌 FOOTNOTES FOUND ON {len(found_pages)} PAGE(S):")
    print("=" * 60)

    page_numbers_list = [p[0] for p in found_pages]
    print(f"Page Numbers List: {page_numbers_list}\n")

    for page_num, notes in found_pages:
        print(f"📖 Page {page_num}:")
        for note in notes:
            display_note = note[:120] + "..." if len(note) > 120 else note
            print(f"   • {display_note}")
        print("-" * 40)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        extract_pdf_footnote_pages(pdf_file)
    else:
        print("Usage: python extract_pdf_footnote.py <path_to_pdf>")
import os
import sys
import re
import pandas as pd

def extract_english_verse_range(text):
    """Extracts (v_start, v_end) tuple from English <p> verse markers."""
    # Match patterns like <p>1-2., <p>1—2., <p>3., <p>l-2. (handling OCR 'l' as '1')
    text_clean = re.sub(r'<p>\s*l\b', '<p>1', str(text), flags=re.IGNORECASE)
    m = re.search(r'<p>\s*(\d+)(?:\s*[-—–]|&mdash;|\s*to\s*)?\s*(\d+)?\.', text_clean, re.IGNORECASE)
    if m:
        v1 = int(m.group(1))
        v2 = int(m.group(2)) if m.group(2) else v1
        return (v1, v2)
    return None

def verify_english_csv(filepath):
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    try:
        df = pd.read_csv(filepath, header=None)
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return

    if df.empty:
        return

    col_idx = 1 if len(df.columns) > 1 else 0

    split_rows = []
    sequence_issues = []
    prev_end = 0

    for idx, row in df.iterrows():
        text = str(row.iloc[col_idx]).strip()

        # 1. SUPPRESS CSV HEADERS, CHAPTER HEADINGS, AND SPEAKER HEADINGS
        is_header_row = (idx == 0 and ("Slokas" in text or "Verses" in text or text == "0"))
        is_heading = bool(re.search(r'<(?:h[1-6]|p)>\s*(?:Section|Chapter|Description|Summary|\()', text, re.IGNORECASE))
        is_speaker = bool(re.search(r'<h2>.*?said', text, re.IGNORECASE))

        if is_header_row or is_heading or is_speaker:
            continue  # Completely skip non-verse structural elements

        vr = extract_english_verse_range(text)

        # 2. Check for real split / unnumbered rows
        if not vr:
            prev_row = str(df.iloc[idx-1].iloc[col_idx]).strip() if idx > 0 else "N/A"
            split_rows.append({
                'row': idx,
                'prev_row': idx - 1,
                'prev_text': prev_row[:80],
                'text': text[:100]
            })
            continue

        # 3. Check verse sequence tracking
        v_start, v_end = vr

        if v_start < prev_end:
            sequence_issues.append({
                'row': idx,
                'range': vr,
                'type': f'🔴 OUT OF ORDER / TYPO (Jumped back to verse {v_start} after verse {prev_end})',
                'snippet': text[:90]
            })
        elif v_start > prev_end + 1 and prev_end > 0:
            sequence_issues.append({
                'row': idx,
                'range': vr,
                'type': f'🟡 MISSING VERSE GAP (Missing verses {prev_end + 1} to {v_start - 1})',
                'snippet': text[:90]
            })

        prev_end = max(prev_end, v_end)

    # Only print report if genuine issues exist
    if not split_rows and not sequence_issues:
        return

    print("=" * 70)
    print(f"🔍 AUDITING ENGLISH CSV SEQUENCE: {filepath}")
    print("=" * 70)

    if split_rows:
        print(f"⚠️ Found {len(split_rows)} split/unnumbered continuation row(s):\n")
        for s in split_rows:
            print(f"🔴 Row {s['row']} (Split continuation of Row {s['prev_row']}):")
            print(f"   Previous Row ({s['prev_row']}): {s['prev_text']}...")
            print(f"   Split Content ({s['row']}) : {s['text']}...\n")

    if sequence_issues:
        print(f"⚠️ Found {len(sequence_issues)} verse sequence issue(s):\n")
        for issue in sequence_issues:
            print(f"Row {issue['row']} | Parsed Range: {issue['range']}")
            print(f"  {issue['type']}")
            print(f"  Snippet: {issue['snippet']}...\n")

def scan_all_english_csv(base_dir='.'):
    count = 0
    for root, dirs, files in os.walk(base_dir):
        if 'english.csv' in files:
            full_path = os.path.join(root, 'english.csv')
            verify_english_csv(full_path)
            count += 1
    if count == 0:
        print("No english.csv files found in subdirectories.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        verify_english_csv(sys.argv[1])
    else:
        scan_all_english_csv('.')
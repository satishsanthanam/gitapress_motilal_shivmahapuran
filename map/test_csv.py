import pandas as pd
import re
import sys
import os

def find_split_lines_in_csv(csv_path):
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    col_name = 'Slokas (Verses)' if 'Slokas (Verses)' in df.columns else df.columns[0]

    split_issues = []

    for idx, row in df.iterrows():
        text = str(row[col_name]).strip()
        
        # Check for verse number patterns like <p>12., <p>12-15., <h1>Chapter..., <h2>...said..., etc.
        has_verse_num = bool(re.search(r'<p>\s*\d+', text, re.IGNORECASE))
        has_heading = bool(re.search(r'<(?:h[1-6]|p)>\s*(?:Chapter|Description|\()', text, re.IGNORECASE))
        has_speaker = bool(re.search(r'<h2>.*?said', text, re.IGNORECASE))

        # If it has none of these, it is an unnumbered split line!
        if not (has_verse_num or has_heading or has_speaker):
            prev_row = str(df.iloc[idx-1][col_name]).strip() if idx > 0 else "N/A"
            split_issues.append({
                'row_index': idx,
                'text': text,
                'prev_row_index': idx - 1,
                'prev_text': prev_row
            })

    print("=" * 70)
    print(f"📊 REPORT FOR: {csv_path}")
    print("=" * 70)

    if not split_issues:
        print("✅ No split/missing verse marker lines found!")
        return

    print(f"⚠️ Found {len(split_issues)} split line(s) missing verse tags:\n")
    for issue in split_issues:
        print(f"🔴 Row {issue['row_index']} (Split continuation of Row {issue['prev_row_index']}):")
        print(f"   Previous Row ({issue['prev_row_index']}): {issue['prev_text'][:100]}...")
        print(f"   Split Content ({issue['row_index']}) : {issue['text'][:120]}...\n")

def scan_all_chapters(base_dir='.'):
    count = 0
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f == 'english.csv':
                full_path = os.path.join(root, f)
                find_split_lines_in_csv(full_path)
                count += 1

if __name__ == "__main__":
    if len(sys.argv) > 1:
        find_split_lines_in_csv(sys.argv[1])
    else:
        scan_all_chapters('.')

import os
import sys
import re

devanagari_num = '०१२३४५६७८९'
ascii_num = '0123456789'
trans = str.maketrans(devanagari_num, ascii_num)

def parse_verse_range(text):
    """Extracts verse range tuple (v_start, v_end) from verse marker."""
    m_dev = re.search(
        r'॥\s*([०-९\d]+)(?:\s*[-—–]\s*([०-९\d]+))?(?:\s*(?:\$\^\{[^}]*\}\$|<sup>.*?</sup>|[०-९\d]+)?\s*/\s*[०-९\d]+)?\s*॥',
        text
    )
    if m_dev:
        v1 = int(m_dev.group(1).translate(trans))
        v2 = int(m_dev.group(2).translate(trans)) if m_dev.group(2) else v1
        return (v1, v2)
    return None

def verify_hindi_file(filepath):
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8-sig') as f:
        text = f.read()

    blocks = [b.strip() for b in text.strip().split('\n\n') if b.strip()]
    
    print("=" * 70)
    print(f"🔍 AUDITING HINDI VERSE SEQUENCE: {filepath}")
    print("=" * 70)

    prev_end = 0
    issues = []

    for idx, b in enumerate(blocks):
        # Ignore colophons or chapter title headers
        if b.startswith('॥ इस प्रकार') or b.startswith('#'):
            continue

        vr = parse_verse_range(b)
        if not vr:
            continue

        v_start, v_end = vr

        # Issue 1: Out of order / Typo (e.g., jumping back to verse 13 after verse 92)
        if v_start < prev_end:
            issues.append({
                'block_idx': idx,
                'range': vr,
                'type': f'🔴 OUT OF ORDER / TYPO (Jumped back to verse {v_start} after verse {prev_end})',
                'snippet': b[:100]
            })

        # Issue 2: Missing Verse Gap (e.g., verse 54-55 followed by 58-62, missing 56-57)
        elif v_start > prev_end + 1 and prev_end > 0:
            issues.append({
                'block_idx': idx,
                'range': vr,
                'type': f'🟡 MISSING VERSE GAP (Missing verses {prev_end + 1} to {v_start - 1})',
                'snippet': b[:100]
            })

        prev_end = max(prev_end, v_end)

    if not issues:
        print("🎉 All verse numbers in this file are in strict sequential order!")
        return

    print(f"⚠️ Found {len(issues)} sequence anomaly / order issue(s):\n")
    for issue in issues:
        print(f"Block {issue['block_idx']} | Parsed Range: {issue['range']}")
        print(f"  {issue['type']}")
        print(f"  Snippet: {issue['snippet']}...\n")

def scan_all_hindi_files(base_dir='.'):
    count = 0
    for root, dirs, files in os.walk(base_dir):
        if 'hindi.txt' in files:
            full_path = os.path.join(root, 'hindi.txt')
            verify_hindi_file(full_path)
            count += 1
    if count == 0:
        print("No hindi.txt files found in subdirectories.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        verify_hindi_file(sys.argv[1])
    else:
        scan_all_hindi_files('.')

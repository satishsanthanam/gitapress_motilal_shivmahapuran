import os
import re
import sys
import glob

# Standard numbers
ONES_TEENS = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
    'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19
}

TENS = {
    'twenty': 20, 'tweney': 20,  # handles typo in Motilal source
    'thirty': 30, 'forty': 40, 'fourty': 40,
    'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90
}

ROMAN_VALS = {
    'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100, 'd': 500, 'm': 1000
}

SUPERSCRIPTS = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹', '          ')

def roman_to_int(s):
    s = s.lower()
    total = 0
    prev_val = 0
    for char in reversed(s):
        val = ROMAN_VALS.get(char, 0)
        if val == 0:
            return None
        if val < prev_val:
            total -= val
        else:
            total += val
            prev_val = val
    return total if total > 0 else None

def parse_compound_token(token):
    """Parses single fused words like 'fortynine', 'fiftyone', 'twentythree'."""
    for ten_word, ten_val in TENS.items():
        if token.startswith(ten_word):
            remainder = token[len(ten_word):]
            if not remainder:
                return ten_val
            if remainder in ONES_TEENS:
                return ten_val + ONES_TEENS[remainder]
    return None

def parse_chapter_number(num_str):
    """
    Parses chapter numbers from plain words, concatenated words ('fortynine'),
    Roman numerals, or digits, stripping footnotes and punctuation.
    """
    # Remove superscripts and punctuation
    cleaned = num_str.translate(SUPERSCRIPTS)
    cleaned = re.sub(r'[*_#:`~()\[\].\-,/]', ' ', cleaned).strip().lower()

    if not cleaned:
        return None

    tokens = [t for t in cleaned.split() if t not in ('and', 'chapter', 'section')]
    if not tokens:
        return None

    # Test the primary token
    first_token = tokens[0]

    # 1. Direct digit
    if first_token.isdigit():
        return int(first_token)

    # 2. Roman numeral
    if re.fullmatch(r'[ivxlcdm]+', first_token):
        val = roman_to_int(first_token)
        if val:
            return val

    # 3. Exact match in standard dictionaries
    if first_token in ONES_TEENS:
        return ONES_TEENS[first_token]
    if first_token in TENS:
        if len(tokens) > 1 and tokens[1] in ONES_TEENS:
            return TENS[first_token] + ONES_TEENS[tokens[1]]
        return TENS[first_token]

    # 4. Fused word (e.g. 'fortynine', 'fiftyone', 'twentyone')
    compound_val = parse_compound_token(first_token)
    if compound_val:
        return compound_val

    # 5. Multi-token evaluation fallback
    total = 0
    current = 0
    matched = False
    for t in tokens:
        if t in ONES_TEENS:
            current += ONES_TEENS[t]
            matched = True
        elif t in TENS:
            current += TENS[t]
            matched = True
        elif parse_compound_token(t):
            current += parse_compound_token(t)
            matched = True
        elif t.isdigit():
            current += int(t)
            matched = True
    total += current

    return total if matched and total > 0 else None

def resolve_target_dir(filepath, base_target=None):
    """
    Resolves targets matching:
    - 01ENGMotilal.txt     -> ./01
    - 02_1_ENGMotilal.txt   -> ./02/01
    - 02_5_ENGMotilal.txt   -> ./02/05
    - 07_1_ENGMotilal.txt   -> ./07/01
    """
    if base_target:
        return base_target

    base_name = os.path.basename(filepath)

    # Sub-sections like 02_1, 02_05, 07_1
    m_sub = re.match(r'^(\d{2})_(\d{1,2})', base_name)
    if m_sub:
        samhita = m_sub.group(1)
        section = f"{int(m_sub.group(2)):02d}"
        return os.path.join(samhita, section)

    # Single numbers like 01ENG... or 03_ENG...
    m_single = re.match(r'^(\d{2})', base_name)
    if m_single:
        return m_single.group(1)

    return "."

def split_english_file(filepath, target_dir=None):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    dst_dir = resolve_target_dir(filepath, target_dir)
    print(f"\nProcessing: {filepath} -> Destination: {dst_dir}/")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().replace('\r\n', '\n')

    # Matches any line with CHAPTER followed by text/digits
    chapter_pattern = re.compile(
        r'(?m)^[#\s]*CHAPTER\s+([^\n\r]+)'
    )
    matches = list(chapter_pattern.finditer(content))

    if not matches:
        print(f"No chapter headings found in '{filepath}'.")
        return

    # Extract Section Preamble prior to Chapter 1
    preamble = content[:matches[0].start()].strip()
    if preamble:
        ch00_dir = os.path.join(dst_dir, "ch_00")
        os.makedirs(ch00_dir, exist_ok=True)
        with open(os.path.join(ch00_dir, "English.txt"), 'w', encoding='utf-8') as f:
            f.write(preamble + '\n')
        print(f"  Saved Preamble -> {ch00_dir}/English.txt")

    # Extract individual chapters
    total_written = 0
    for idx, match in enumerate(matches):
        raw_header = match.group(1)
        ch_num = parse_chapter_number(raw_header) or (idx + 1)

        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        chapter_content = content[start:end].strip()

        ch_dir = os.path.join(dst_dir, f"ch_{ch_num:02d}")
        os.makedirs(ch_dir, exist_ok=True)
        out_path = os.path.join(ch_dir, "English.txt")

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(chapter_content + '\n')

        total_written += 1

    print(f"  Extracted {total_written} chapters into '{dst_dir}/'")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single file: python split_english.py 02_5_ENGMotilal.txt")
        print("  Batch mode:  python split_english.py *ENG*.txt")
        return

    files = []
    for arg in sys.argv[1:]:
        matched = glob.glob(arg)
        if matched:
            files.extend(matched)
        elif os.path.exists(arg):
            files.append(arg)

    if not files:
        print("No matching files found.")
        return

    # Explicit single file + explicit target directory
    if len(sys.argv) == 3 and os.path.isfile(sys.argv[1]) and not os.path.isfile(sys.argv[2]):
        split_english_file(sys.argv[1], sys.argv[2])
        return

    for file in sorted(files):
        if os.path.isfile(file) and file.endswith('.txt'):
            split_english_file(file)

if __name__ == "__main__":
    main()
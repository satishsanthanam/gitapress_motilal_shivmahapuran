import os
import re

DEVANAGARI_DIGITS = str.maketrans('0123456789', '०१२३४५६७८९')
ASCII_DIGITS = str.maketrans('०१२३४५६७८९', '0123456789')

def devanagari_to_ascii(s):
    """Converts Devanagari numbers ('१८-१९') to ASCII ('18-19')."""
    return s.translate(ASCII_DIGITS)

def ascii_to_devanagari(s):
    """Converts ASCII numbers ('18-19') to Devanagari ('१८-१९')."""
    return s.translate(DEVANAGARI_DIGITS)

def parse_sanskrit_verses(sanskrit_text):
    """
    Splits Sanskrit text into blocks mapped by verse numbers (Devanagari keys).
    """
    verse_pattern = re.compile(r'॥\s*([०-९\d]+(?:\s*[-–—]\s*[०-९\d]+)?)\s*॥')
    verses = {}
    last_pos = 0
    
    for match in verse_pattern.finditer(sanskrit_text):
        end_pos = match.end()
        v_num_raw = match.group(1).strip()
        v_text = sanskrit_text[last_pos:end_pos].strip()
        
        # Standardize key to Devanagari digits
        v_num_dev = ascii_to_devanagari(v_num_raw)
        verses[v_num_dev] = v_text
        last_pos = end_pos
        
    colophon = sanskrit_text[last_pos:].strip()
    return verses, colophon

def parse_english_verses(english_text):
    """Splits English text into blocks mapped by ASCII verse numbers."""
    num_pattern = re.compile(r'(?m)^\s*(\d+(?:\s*[-–—]\s*\d+)?)\.\s*')
    matches = list(num_pattern.finditer(english_text))
    
    header = ""
    if matches:
        header = english_text[:matches[0].start()].strip()
        
    verses = {}
    for i, match in enumerate(matches):
        v_num = match.group(1).strip()
        # Standardize dash/hyphen in verse range (e.g., '18-19')
        v_num_clean = re.sub(r'\s*[-–—]\s*', '-', v_num)
        
        start = match.start()
        end = matches[i+1].start() if i + 1 < len(matches) else len(english_text)
        
        text_block = english_text[start:end].strip()
        # Remove leading number prefix (e.g. '1-2. ' or '3. ')
        text_block = re.sub(r'^\s*\d+(?:\s*[-–—]\s*\d+)?\.\s*', '', text_block).strip()
        verses[v_num_clean] = text_block
        
    return header, verses

def expand_verse_range(range_str):
    """Expands '18-19' into list [18, 19], or '5' into [5]."""
    m = re.match(r'^(\d+)-(\d+)$', range_str)
    if m:
        return list(range(int(m.group(1)), int(m.group(2)) + 1))
    elif range_str.isdigit():
        return [int(range_str)]
    return []

def get_sanskrit_for_english_verse(v_num_en, sk_verses, used_sk_keys):
    """
    Finds and combines matching Sanskrit verse blocks for an English verse marker.
    Handles single verses, merged ranges in English, or merged ranges in Sanskrit.
    """
    v_num_dev = ascii_to_devanagari(v_num_en)
    
    # 1. Direct match (e.g. '१८-१९' or '१')
    if v_num_dev in sk_verses:
        used_sk_keys.add(v_num_dev)
        return sk_verses[v_num_dev]
    
    # 2. English range decomposition (e.g. '18-19' -> lookup '१८' and '१९')
    en_verses_list = expand_verse_range(v_num_en)
    matched_sk_blocks = []
    
    if len(en_verses_list) > 1:
        for v in en_verses_list:
            v_dev = ascii_to_devanagari(str(v))
            if v_dev in sk_verses:
                used_sk_keys.add(v_dev)
                matched_sk_blocks.append(sk_verses[v_dev])
        if matched_sk_blocks:
            return "\n\n".join(matched_sk_blocks)
            
    # 3. Sanskrit range lookup (e.g. English asked for '18', Sanskrit has '१८-१९')
    if len(en_verses_list) == 1:
        target_v = en_verses_list[0]
        for sk_key, sk_text in sk_verses.items():
            sk_key_ascii = devanagari_to_ascii(sk_key)
            sk_range = expand_verse_range(sk_key_ascii)
            if target_v in sk_range:
                used_sk_keys.add(sk_key)
                return sk_text

    return ""

def interleave_folder(folder_path, output_filename="san_eng.txt"):
    sk_path = os.path.join(folder_path, "sanskrit.txt")
    en_path = os.path.join(folder_path, "English.txt")
    out_path = os.path.join(folder_path, output_filename)

    if not os.path.exists(sk_path) or not os.path.exists(en_path):
        return False

    with open(sk_path, 'r', encoding='utf-8') as f:
        sk_content = f.read().replace('\r\n', '\n')
        
    with open(en_path, 'r', encoding='utf-8') as f:
        en_content = f.read().replace('\r\n', '\n')

    sk_verses, sk_colophon = parse_sanskrit_verses(sk_content)
    en_header, en_verses = parse_english_verses(en_content)

    output_blocks = []

    # 1. Output Clean Single-Line Chapter Header
    if en_header:
        header_raw = re.sub(r'^[#\s]+', '', en_header).strip()
        # Clean multi-line headers into a single title line
        title_clean = re.sub(r'\s*\n\s*', ' - ', header_raw)
        output_blocks.append(f"### **{title_clean}**")

    used_sk_keys = set()

    # 2. Interleave verse by verse
    for v_num_en, en_text in en_verses.items():
        sk_text = get_sanskrit_for_english_verse(v_num_en, sk_verses, used_sk_keys)
        
        block_lines = []
        if sk_text:
            block_lines.append("Sanskrit\n" + sk_text)
            
        if en_text:
            # Format English line ending with bracketed verse number e.g. (1-4.) or (8.)
            en_formatted = f"English\n{en_text} ({v_num_en}.)"
            block_lines.append(en_formatted)
            
        if block_lines:
            output_blocks.append("\n\n".join(block_lines))

    # 3. Append any unmapped Sanskrit verses
    unused_sk_keys = [k for k in sk_verses if k not in used_sk_keys]
    if unused_sk_keys:
        for k in sorted(unused_sk_keys, key=lambda x: int(expand_verse_range(devanagari_to_ascii(x))[0] if expand_verse_range(devanagari_to_ascii(x)) else 0)):
            output_blocks.append(f"Sanskrit\n{sk_verses[k]}")

    # 4. Append Colophon if present
    if sk_colophon:
        output_blocks.append(f"--- Colophon ---\n\nSanskrit\n{sk_colophon}")

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n\n---\n\n".join(output_blocks) + "\n")

    return True

def process_from_dir_file(dir_file="dir.txt", output_filename="san_eng.txt"):
    if not os.path.exists(dir_file):
        print(f"❌ Error: {dir_file} not found.")
        return

    with open(dir_file, 'r', encoding='utf-8') as f:
        paths = [line.strip() for line in f if line.strip()]

    directories = set()
    for path in paths:
        if path.endswith(".txt") or path.endswith(".csv") or path.endswith(".html"):
            directories.add(os.path.dirname(path))
        else:
            directories.add(path)

    success_count = 0
    for folder in sorted(directories):
        if interleave_folder(folder, output_filename=output_filename):
            print(f"✅ Generated: {folder}/{output_filename}")
            success_count += 1

    print(f"\n🎉 Completed batch processing for {success_count} chapter folder(s).")

if __name__ == "__main__":
    process_from_dir_file("dir.txt", "san_eng.txt")
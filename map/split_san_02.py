import os
import re

# Devanagari to ASCII translation table
devanagari_num = '०१२३४५६७८९'
ascii_num = '0123456789'
trans = str.maketrans(devanagari_num, ascii_num)

# Section 02 (Rudrasaṁhitā) file mapping:
# 1. Sṛṣṭikhaṇḍa -> ./02/01
# 2. Satīkhaṇḍa -> ./02/02
# 3. Pārvatīkhaṇḍa -> ./02/03
# 4. Kumārakhaṇḍa -> ./02/04
# 5. Yuddhakhaṇḍa -> ./02/05
file_mapping = {
    'san_02_1.txt': ('./02/01', r'(?:२\.१\.|2\.1\.)'),
    'san_02_2.txt': ('./02/02', r'(?:२\.२\.|2\.2\.)'),
    'san_02_3.txt': ('./02/03', r'(?:२\.३\.|2\.3\.)'),
    'san_02_4.txt': ('./02/04', r'(?:२\.४\.|2\.4\.)'),
    'san_02_5.txt': ('./02/05', r'(?:२\.५\.|2\.5\.)')
}

def split_and_save_sanskrit_02(file_path, base_target_dir, header_pattern):
    """Splits Section 02 Sanskrit files by chapter and saves into ch_XX folders."""
    if not os.path.exists(file_path):
        print(f"⚠️ Warning: File '{file_path}' not found, skipping...")
        return 0

    # Use 'utf-8-sig' to automatically strip any UTF-8 BOM
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # Split by chapter header e.g. २.१.१. प्रथमोऽध्यायः or 2.1.1.
    split_regex = rf'(\n?{header_pattern}\s*([०-९\d]+)\.\s*[^॥\n]+)'
    chapter_blocks = re.split(split_regex, content)
    
    chapters = {}
    current_ch = "00"
    
    for block in chapter_blocks:
        m = re.search(rf'{header_pattern}\s*([०-९\d]+)\.', block)
        if m:
            num_ascii = m.group(1).translate(trans)
            current_ch = f"{int(num_ascii):02d}"
        else:
            if current_ch not in chapters:
                chapters[current_ch] = ""
            chapters[current_ch] += block

    saved_count = 0
    for ch_num, text_content in chapters.items():
        if ch_num == "00" and not text_content.strip():
            continue
        
        ch_dir = os.path.join(base_target_dir, f"ch_{ch_num}")
        os.makedirs(ch_dir, exist_ok=True)
        
        output_file_path = os.path.join(ch_dir, "sanskrit.txt")
        with open(output_file_path, "w", encoding="utf-8") as out_f:
            out_f.write(text_content.strip())
        
        saved_count += 1
        print(f"  ✓ Saved {ch_dir}/sanskrit.txt")

    print(f"✅ Success: Processed '{file_path}' -> {saved_count} chapters stored under '{base_target_dir}'.\n")
    return saved_count

if __name__ == "__main__":
    total_chapters = 0
    for san_file, (target_dir, pattern) in file_mapping.items():
        total_chapters += split_and_save_sanskrit_02(san_file, target_dir, pattern)
    
    print(f"🎉 Completed! Total {total_chapters} Sanskrit chapter files created across Section 02.")

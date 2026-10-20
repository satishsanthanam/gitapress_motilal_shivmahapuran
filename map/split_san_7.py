import os
import re

# Devanagari to ASCII Translation Table
devanagari_num = '०१२३४५६७८९'
ascii_num = '0123456789'
trans = str.maketrans(devanagari_num, ascii_num)

# Section 7 file mapping
san_07_mapping = {
    'san_07_1.txt': ('./07/01', r'(?:७\.१\.|7\.1\.)'), # Purva Khanda
    'san_07_2.txt': ('./07/02', r'(?:७\.२\.|7\.2\.)')  # Uttara Khanda
}

def split_vayaviya_samhita(file_path, base_target_dir, header_pattern):
    """Splits Vayaviya Samhita files into individual chapter folders."""
    if not os.path.exists(file_path):
        print(f"⚠️ Warning: File '{file_path}' not found, skipping...")
        return 0

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split on headers matching 7.1.X. or 7.2.X.
    chapter_splits = re.split(rf'(\n{header_pattern}\s*([०-९\d]+)\.\s*[^॥\n]+)', content)

    chapters = {}
    current_ch = "00"

    for block in chapter_splits:
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

    print(f"✅ Success: Processed '{file_path}' -> {saved_count} chapters saved under '{base_target_dir}'.")
    return saved_count

if __name__ == "__main__":
    total = 0
    for filename, (target_dir, pattern) in san_07_mapping.items():
        total += split_vayaviya_samhita(filename, target_dir, pattern)

    print(f"\n🎉 Completed processing Section 07! Total {total} chapter files written.")
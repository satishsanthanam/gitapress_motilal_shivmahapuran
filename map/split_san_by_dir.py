import os
import re

# Devanagari to ASCII Translation Table
devanagari_num = '०१२३४५६७८९'
ascii_num = '0123456789'
trans = str.maketrans(devanagari_num, ascii_num)

# Section file to directory mapping
file_mapping = {
    'san_02_1.txt': './02/01',    # Vāyavīya Saṁhitā (Purva)[cite: 11]
    'san_02_2.txt': './02/02',    # Vāyavīya Saṁhitā (Uttara)[cite: 11]
    'san_02_3.txt': './02/03',    # Vāyavīya Saṁhitā (Purva)[cite: 11]
    'san_02_4.txt': './02/04',    # Vāyavīya Saṁhitā (Uttara)[cite: 11]
    'san_02_5.txt': './02/05'    # Vāyavīya Saṁhitā (Purva)[cite: 11]
}

def split_and_save_sanskrit_file(file_path, base_target_dir):
    """Splits a Sanskrit txt file by chapters and saves as sanskrit.txt in ch_XX folders."""
    if not os.path.exists(file_path):
        print(f"⚠️ Warning: File '{file_path}' not found, skipping...")
        return 0

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex splits by chapter headers like '०.१. प्रथमोऽध्यायः' or '0.1.'
    chapter_blocks = re.split(r'(\n(?:[०-९\d]+\.[०-९\d]+\.\s*[^॥\n]+))', content)
    
    chapters = {}
    current_ch = "0"
    
    for block in chapter_blocks:
        m = re.search(r'[०-९\d]+\.([०-९\d]+)\.', block)
        if m:
            # Normalize Devanagari numbers to integer strings
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
        
        # Target directory formatting e.g., ./00/ch_01/
        ch_dir = os.path.join(base_target_dir, f"ch_{ch_num}")
        os.makedirs(ch_dir, exist_ok=True)
        
        output_file_path = os.path.join(ch_dir, "sanskrit.txt")
        with open(output_file_path, "w", encoding="utf-8") as out_f:
            out_file_path = out_f.write(text_content.strip())
        
        saved_count += 1

    print(f"✅ Success: Processed '{file_path}' -> {saved_count} chapters stored under '{base_target_dir}'.")
    return saved_count

if __name__ == "__main__":
    total_chapters = 0
    for san_file, target_dir in file_mapping.items():
        total_chapters += split_and_save_sanskrit_file(san_file, target_dir)
    
    print(f"\n🎉 Completed! Total {total_chapters} Sanskrit chapter files placed in respective directories.")
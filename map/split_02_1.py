import os
import re

# Mapping Hindi chapter ordinals to 2-digit strings
chapter_name_to_num = {
    'पहला': '01', 'दूसरा': '02', 'तीसरा': '03', 'चौथा': '04', 'पाँचवाँ': '05',
    'छठा': '06', 'सातवाँ': '07', 'आठवाँ': '08', 'नौवाँ': '09', 'दसवाँ': '10',
    'ग्यारहवाँ': '11', 'बारहवाँ': '12', 'तेरहवाँ': '13', 'चौदहवाँ': '14',
    'पन्द्रहवाँ': '15', 'सोलहवाँ': '16', 'सत्रहवाँ': '17', 'अठारहवाँ': '18',
    'उन्नीसवाँ': '19', 'बीसवाँ': '20'
}

def split_and_save_srishtikhanda(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found.")
        return

    # Use 'utf-8-sig' to automatically strip any UTF-8 BOM header
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    ordinals_pattern = "|".join(chapter_name_to_num.keys())
    pattern = rf'(\n?(?:#+)?\s*(?:{ordinals_pattern})\s*अध्याय)'
    
    chapter_splits = re.split(pattern, content)

    chapters = {}
    current_ch = None

    for block in chapter_splits:
        m = re.search(rf'({ordinals_pattern})\s*अध्याय', block)
        if m:
            ordinal = m.group(1)
            current_ch = chapter_name_to_num.get(ordinal)
        elif current_ch:
            if current_ch not in chapters:
                chapters[current_ch] = ""
            chapters[current_ch] += block

    saved_count = 0
    for ch_num in sorted(chapters.keys()):
        text_content = chapters[ch_num]
        if not text_content.strip():
            continue

        # Target folder: ./02/01/ch_XX/ (Rudrasaṁhitā -> Sṛṣṭikhaṇḍa)
        ch_dir = os.path.join('./02/01', f"ch_{ch_num}")
        os.makedirs(ch_dir, exist_ok=True)

        output_file_path = os.path.join(ch_dir, "hindi.txt")
        with open(output_file_path, "w", encoding="utf-8") as out_f:
            out_f.write(text_content.strip())

        saved_count += 1
        print(f"  ✓ Saved ./02/01/ch_{ch_num}/hindi.txt")

    print(f"\n✅ Completed! Successfully processed {saved_count} chapters for Section 02 (Sṛṣṭikhaṇḍa).")

if __name__ == "__main__":
    split_and_save_srishtikhanda('hin_02_1.txt')
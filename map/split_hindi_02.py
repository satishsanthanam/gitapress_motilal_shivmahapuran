import os
import re

# Ordinal mapping for all 43 chapters of Satīkhaṇḍa
chapter_name_to_num = {
    'पहला': '01', 'दूसरा': '02', 'तीसरा': '03', 'चौथा': '04', 'पाँचवाँ': '05',
    'छठा': '06', 'सातवाँ': '07', 'आठवाँ': '08', 'नौवाँ': '09', 'दसवाँ': '10',
    'ग्यारहवाँ': '11', 'बारहवाँ': '12', 'तेरहवाँ': '13', 'चौदहवाँ': '14',
    'पन्द्रहवाँ': '15', 'सोलहवाँ': '16', 'सत्रहवाँ': '17', 'अठारहवाँ': '18',
    'उन्नीसवाँ': '19', 'बीसवाँ': '20', 'इक्कीसवाँ': '21', 'बाईसवाँ': '22',
    'तेईसवाँ': '23', 'चौबीसवाँ': '24', 'पच्चीसवाँ': '25', 'छब्बीसवाँ': '26',
    'सत्ताईसवाँ': '27', 'अट्ठाईसवाँ': '28', 'उन्तीसवाँ': '29', 'तीसवाँ': '30',
    'इकतीसवाँ': '31', 'बत्तीसवाँ': '32', 'तैंतीसवाँ': '33', 'चौतीसवाँ': '34',
    'पैंतीसवाँ': '35', 'छत्तीसवाँ': '36', 'सैंतीसवाँ': '37', 'अड़तीसवाँ': '38',
    'उनतालीसवाँ': '39', 'चालीसवाँ': '40', 'इकतालीसवाँ': '41', 'बयालीसवाँ': '42',
    'तैंतालीसवाँ': '43'
}

def split_and_save_satikhanda(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found.")
        return

    # Use 'utf-8-sig' to automatically remove any UTF-8 BOM header
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

        # Target directory: ./02/02/ch_XX/
        ch_dir = os.path.join('./02/02', f"ch_{ch_num}")
        os.makedirs(ch_dir, exist_ok=True)

        output_file_path = os.path.join(ch_dir, "hindi.txt")
        with open(output_file_path, "w", encoding="utf-8") as out_f:
            out_f.write(text_content.strip())

        saved_count += 1
        print(f"  ✓ Saved ./02/02/ch_{ch_num}/hindi.txt")

    print(f"\n✅ Completed! Successfully processed {saved_count} chapters for Section 02.02 (Satīkhaṇḍa).")

if __name__ == "__main__":
    split_and_save_satikhanda('hin_02_2.txt')

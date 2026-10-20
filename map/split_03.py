import os
import re

# Ordinal mapping for Hindi chapter headings
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
    'उनतालीसवाँ': '39', 'चालीसवाँ': '40', 'इकतालीसवाँ': '41', 'बयालीसवाँ': '42'
}

def split_and_save_shatarudrasamhita(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found.")
        return

    # Use 'utf-8-sig' to automatically strip any UTF-8 BOM header
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # Match both standard ordinals and numeric chapter headers
    ordinals_pattern = "|".join(chapter_name_to_num.keys())
    pattern = rf'(\n?(?:#+)?\s*(?:(?:{ordinals_pattern})\s*अध्याय|[०-९\d]+\s*अध्याय))'
    
    chapter_splits = re.split(pattern, content)

    chapters = {}
    current_ch = None

    for block in chapter_splits:
        # Check ordinal match
        m_ord = re.search(rf'({ordinals_pattern})\s*अध्याय', block)
        if m_ord:
            ordinal = m_ord.group(1)
            current_ch = chapter_name_to_num.get(ordinal)
        else:
            # Check numeric match
            m_num = re.search(r'([०-९\d]+)\s*अध्याय', block)
            if m_num:
                num_str = m_num.group(1)
                trans = str.maketrans('०१२३४५६७८९', '0123456789')
                num_ascii = int(num_str.translate(trans))
                current_ch = f"{num_ascii:02d}"
            elif current_ch:
                if current_ch not in chapters:
                    chapters[current_ch] = ""
                chapters[current_ch] += block

    saved_count = 0
    for ch_num in sorted(chapters.keys()):
        text_content = chapters[ch_num]
        if not text_content.strip():
            continue

        # Target directory: ./03/ch_XX/
        ch_dir = os.path.join('./03', f"ch_{ch_num}")
        os.makedirs(ch_dir, exist_ok=True)

        output_file_path = os.path.join(ch_dir, "hindi.txt")
        with open(output_file_path, "w", encoding="utf-8") as out_f:
            out_f.write(text_content.strip())

        saved_count += 1
        print(f"  ✓ Saved ./03/ch_{ch_num}/hindi.txt")

    print(f"\n✅ Completed! Successfully processed {saved_count} chapters for Section 03 (Śatarudrasaṁhitā).")

if __name__ == "__main__":
    split_and_save_shatarudrasamhita('hin_03.txt')

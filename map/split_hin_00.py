import os
import re

# Devanagari to ASCII translation table
devanagari_num = '०१२३४५६७८९'
ascii_num = '0123456789'
trans = str.maketrans(devanagari_num, ascii_num)

def split_and_save_hindi_00(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found.")
        return

    # Use 'utf-8-sig' to automatically strip the BOM character if present
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # Regex to split content by chapter headers (e.g. # पहला अध्याय, ## दूसरा अध्याय)
    chapter_splits = re.split(
        r'(\n?(?:#+)?\s*(?:पहला|दूसरा|तीसरा|चौथा|पाँचवाँ|छठा|सातवाँ)\s*अध्याय)',
        content
    )

    # Ordinal mapping to 2-digit chapter folder codes
    ordinal_map = {
        'पहला': '01',
        'दूसरा': '02',
        'तीसरा': '03',
        'चौथा': '04',
        'पाँचवाँ': '05',
        'छठा': '06',
        'सातवाँ': '07'
    }

    chapters = {}
    current_ch = None

    for block in chapter_splits:
        # Check if block is a chapter header
        m = re.search(r'(पहला|दूसरा|तीसरा|चौथा|पाँचवाँ|छठा|सातवाँ)\s*अध्याय', block)
        if m:
            ordinal = m.group(1)
            current_ch = ordinal_map.get(ordinal)
        elif current_ch:
            if current_ch not in chapters:
                chapters[current_ch] = ""
            chapters[current_ch] += block

    saved_count = 0
    for ch_num, text_content in chapters.items():
        if not text_content.strip():
            continue

        # Target directory: ./00/ch_XX/
        ch_dir = os.path.join('./00', f"ch_{ch_num}")
        os.makedirs(ch_dir, exist_ok=True)

        output_file_path = os.path.join(ch_dir, "hindi.txt")
        with open(output_file_path, "w", encoding="utf-8") as out_f:
            out_f.write(text_content.strip())

        saved_count += 1
        print(f"  ✓ Saved ./00/ch_{ch_num}/hindi.txt")

    print(f"\n✅ Completed! Successfully processed {saved_count} chapters for Section 00.")

if __name__ == "__main__":
    split_and_save_hindi_00('hin_01.txt')
import os
import re
import sys

def patch_last_line(aligned_file, sanskrit_file):
    if not os.path.exists(aligned_file) or not os.path.exists(sanskrit_file):
        print("❌ File not found! Please check file paths.")
        return

    # 1. Read sanskrit file and extract lines
    with open(sanskrit_file, 'r', encoding='utf-8') as f:
        sk_lines = [line.strip() for line in f.read().replace('\r\n', '\n').split('\n') if line.strip()]

    target_sk_line = ""
    
    # Strictly match line containing 'इति' and 'अध्याय'
    for line in reversed(sk_lines):
        clean_line = re.sub(r'\s+', ' ', line)
        if "इति" in clean_line and ("अध्याय" in clean_line or "अध्यायः" in clean_line):
            target_sk_line = clean_line
            break

    # Fallback: match line starting with 'इति श्री'
    if not target_sk_line:
        for line in reversed(sk_lines):
            clean_line = re.sub(r'\s+', ' ', line)
            if clean_line.startswith("इति श्री") or "इति श्री" in clean_line:
                target_sk_line = clean_line
                break

    if not target_sk_line:
        print("❌ Colophon line with 'इति' and 'अध्याय' not found in sanskrit file.")
        return

    print(f"🎯 Matched Colophon Line: {target_sk_line}")

    # 2. Read aligned file
    with open(aligned_file, 'r', encoding='utf-8') as f:
        aligned_content = f.read().replace('\r\n', '\n')

    blocks = aligned_content.split('\n--- ')
    if not blocks:
        print("❌ Aligned file is empty.")
        return

    last_block = blocks[-1]

    # 3. Replace Sanskrit section in the last block
    if 'Sanskrit' in last_block:
        pattern = r'(Sanskrit\s*\n)(.*?)(?=\s*\nHindi|\n---|$)'
        def replace_sk(match):
            return match.group(1) + target_sk_line + "\n\n"

        blocks[-1] = re.sub(pattern, replace_sk, last_block, flags=re.DOTALL | re.IGNORECASE)
    else:
        colophon_block = f"Colophon ---\n\nSanskrit\n{target_sk_line}\n"
        blocks.append(colophon_block)

    patched_content = '\n--- '.join(blocks)

    # 4. Save patched file
    with open(aligned_file, 'w', encoding='utf-8') as f:
        f.write(patched_content)

    print(f"✅ Successfully patched last Sanskrit line in: {aligned_file}")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        patch_last_line(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python patch_last_line.py <aligned_file.txt> <sanskrit.txt>")

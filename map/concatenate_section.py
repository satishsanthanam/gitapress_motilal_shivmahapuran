import os
import sys

def concatenate_section(section_path, output_filename=None):
    """
    Concatenates all `aligned_trilingual.txt` files inside `ch_XX` folders 
    for a given section directory (e.g. './01', './02/01', './07/02').
    """
    if not os.path.exists(section_path):
        print(f"❌ Error: Section path '{section_path}' does not exist.")
        return False

    # Find all ch_XX subdirectories
    ch_dirs = []
    for entry in os.listdir(section_path):
        full_p = os.path.join(section_path, entry)
        if os.path.isdir(full_p) and entry.startswith('ch_'):
            ch_dirs.append((entry, full_p))

    # Sort numerically by chapter number (ch_01, ch_02, ...)
    ch_dirs.sort(key=lambda x: int(x[0].replace('ch_', '')) if x[0].replace('ch_', '').isdigit() else 999)

    combined_blocks = []
    found_count = 0

    for ch_name, ch_path in ch_dirs:
        aligned_file = os.path.join(ch_path, 'aligned_trilingual.txt')
        if os.path.exists(aligned_file):
            with open(aligned_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            if content:
                header_banner = f"=========================================\n  {section_path.strip('./')} / {ch_name.upper()}\n========================================="
                combined_blocks.append(f"{header_banner}\n\n{content}")
                found_count += 1
        else:
            print(f"⚠️ Warning: 'aligned_trilingual.txt' not found in {ch_path}")

    if not combined_blocks:
        print(f"⚠️ No aligned_trilingual.txt files found in '{section_path}'.")
        return False

    if not output_filename:
        clean_name = section_path.strip('./').replace('/', '_')
        output_filename = os.path.join(section_path, f"section_{clean_name}_combined.txt")

    final_content = "\n\n\n".join(combined_blocks)
    with open(output_filename, 'w', encoding='utf-8') as out_f:
        out_f.write(final_content)

    print(f"✅ Success: Combined {found_count} chapters from '{section_path}' into '{output_filename}'")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_sec = sys.argv[1]
        concatenate_section(target_sec)
    else:
        print("Usage: python concatenate_section.py <section_path> (e.g. ./01 or ./02/01)")

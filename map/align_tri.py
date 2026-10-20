import os
import re

devanagari_num = '०१२३४५६७८९'
ascii_num = '0123456789'
trans = str.maketrans(devanagari_num, ascii_num)

def parse_verse_range(text):
    """
    Extracts verse range tuple (v_start, v_end) from text line or block.
    Automatically strips out fractional extensions, LaTeX markup, and <sup> tags:
    e.g., ॥ ४८—५०$^{१}$/२ ॥ -> (48, 50)
          ॥ ५४-५५<sup>१</sup>/२ ॥ -> (54, 55)
          ॥ ५४-५५ १/२ ॥        -> (54, 55)
    """
    m_dev = re.search(
        r'॥\s*([०-९\d]+)(?:\s*[-—–]\s*([०-९\d]+))?(?:\s*(?:\$\^\{[^}]*\}\$|<sup>.*?</sup>|[०-९\d]+)?\s*/\s*[०-९\d]+)?\s*॥',
        text
    )
    if m_dev:
        v1 = int(m_dev.group(1).translate(trans))
        v2 = int(m_dev.group(2).translate(trans)) if m_dev.group(2) else v1
        return (v1, v2)
    return None

def align_directory(ch_dir):
    sanskrit_path = os.path.join(ch_dir, 'sanskrit.txt')
    hindi_path = os.path.join(ch_dir, 'hindi.txt')
    
    if not os.path.exists(sanskrit_path) and not os.path.exists(hindi_path):
        return False

    # 1. Parse Sanskrit
    sk_dict = {}
    if os.path.exists(sanskrit_path):
        with open(sanskrit_path, 'r', encoding='utf-8-sig') as f:
            sk_text = f.read()
        sk_lines = sk_text.strip().split('\n')
        curr_sk = []
        for line in sk_lines:
            if line.strip().startswith('॥ श्रीगणेशाय') or line.strip().startswith('॥ श्रीगौरी') or line.strip().startswith('विद्येश्वरसंहिता'):
                continue
            curr_sk.append(line)
            vr = parse_verse_range(line)
            if vr:
                sk_block = "\n".join(curr_sk).strip()
                if 'इति श्रीशिवमहापुराणे' in sk_block:
                    parts = sk_block.split('इति श्रीशिवमहापुराणे')
                    sk_dict[vr] = parts[0].strip()
                    sk_dict['colophon'] = 'इति श्रीशिवमहापुराणे' + parts[1]
                else:
                    sk_dict[vr] = sk_block
                curr_sk = []

    # 2. Parse Hindi
    hi_groups = []
    if os.path.exists(hindi_path):
        with open(hindi_path, 'r', encoding='utf-8-sig') as f:
            hi_text = f.read()
        hi_blocks = [b.strip() for b in hi_text.strip().split('\n\n') if b.strip()]
        for b in hi_blocks:
            vr = parse_verse_range(b)
            hi_groups.append({'text': b, 'range': vr})

    # 3. Build Output (Bilingual: Sanskrit & Hindi)
    output_blocks = []

    # Heading / Invocation Block
    if hi_groups:
        mangala_block = f"{hi_groups[0]['text']}\n\n"
        if 0 in sk_dict or (1, 1) in sk_dict:
            mangala_block += f"Sanskrit\n{sk_dict.get((1,1), sk_dict.get(0, ''))}\n\n"
        if len(hi_groups) > 2 and hi_groups[2]['range'] is None:
            mangala_block += f"Hindi\n{hi_groups[2]['text']}"
        elif len(hi_groups) > 1 and hi_groups[1]['range'] is None:
            mangala_block += f"Hindi\n{hi_groups[1]['text']}"
            
        output_blocks.append(mangala_block)

    # Verse-by-Verse Blocks
    hi_idx = 0
    while hi_idx < len(hi_groups):
        hi_item = hi_groups[hi_idx]
        vr = hi_item['range']
        hi_idx += 1
        
        if not vr:
            continue

        v_start, v_end = vr
        verse_label = f"--- Verse {v_start} ---" if v_start == v_end else f"--- Verse {v_start}-{v_end} ---"
        
        # Sanskrit Lookup
        sk_match = sk_dict.get((v_start, v_end), "")
        if not sk_match:
            sk_parts = [sk_dict.get((v, v), "") for v in range(v_start, v_end + 1)]
            sk_match = "\n".join([p for p in sk_parts if p])

        block_str = f"{verse_label}\n\n"
        if sk_match:
            block_str += f"Sanskrit\n{sk_match}\n\n"
        block_str += f"Hindi\n{hi_item['text']}"

        output_blocks.append(block_str)

    # Colophon
    if 'colophon' in sk_dict or (hi_groups and 'इति' in hi_groups[-1]['text']):
        colophon_str = "--- Colophon ---\n\n"
        if 'colophon' in sk_dict:
            colophon_str += f"Sanskrit\n{sk_dict['colophon']}\n\n"
        if hi_groups and 'इति' in hi_groups[-1]['text']:
            colophon_str += f"Hindi\n{hi_groups[-1]['text']}"
        output_blocks.append(colophon_str)

    final_text = "\n\n".join(output_blocks)
    out_file = os.path.join(ch_dir, 'aligned_trilingual.txt')
    with open(out_file, 'w', encoding='utf-8') as out_f:
        out_f.write(final_text)

    print(f"  ✓ Saved {out_file}")
    return True

def process_all_directories(base_dir='.'):
    count = 0
    for root, dirs, files in os.walk(base_dir):
        if 'ch_' in os.path.basename(root):
            if align_directory(root):
                count += 1
    print(f"\n🎉 Completed alignment for {count} chapter folders.")

if __name__ == "__main__":
    process_all_directories('.')
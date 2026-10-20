import os
import re
import sys
import base64

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --bg-color: #f8f9fa;
            --card-bg: #ffffff;
            --text-color: #111827;
            --border-color: #e9ecef;
            --accent-color: #8b0000;
            --sanskrit-color: #0d1b2a;
            --translation-color: #111827;
            --fn-bg: #fff5f5;
            --fn-border: #feb2b2;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            margin: 0;
            padding: 20px 20px 80px 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        h1.section-title {{
            text-align: center;
            color: var(--accent-color);
            margin-bottom: 20px;
            font-size: 1.7rem;
            line-height: 1.4;
            border-bottom: 2px solid var(--accent-color);
            padding-bottom: 12px;
        }}

        .global-lang-header {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            background: #e2e8f0;
            padding: 10px 16px;
            border-radius: 6px;
            margin-bottom: 20px;
            border: 1px solid #cbd5e0;
            position: sticky;
            top: 10px;
            z-index: 100;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}

        .global-lang-title {{
            font-size: 0.95rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--accent-color);
            font-weight: 800;
            text-align: center;
        }}

        .verse-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            overflow: hidden;
        }}

        .verse-label {{
            background: #edf2f7;
            padding: 8px 16px;
            font-weight: bold;
            color: var(--accent-color);
            border-bottom: 1px solid var(--border-color);
            font-size: 1.05rem;
        }}

        .grid-2col {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 16px;
        }}

        .col-sanskrit {{
            color: var(--sanskrit-color);
            font-family: "Siddhanta", "Noto Sans Devanagari", "Kokila", serif;
            font-size: 1.5rem;
            font-weight: 600;
            border-right: 1px solid var(--border-color);
            padding-right: 20px;
            white-space: pre-line;
        }}

        .col-translation {{
            color: var(--translation-color);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans Devanagari", sans-serif;
            font-size: 1.15rem;
            font-weight: 600;
            white-space: pre-line;
        }}

        .custom-table-container {{
            overflow-x: auto;
            margin: 15px 0;
        }}

        table.markup-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
            background-color: #ffffff;
            border: 1px solid var(--border-color);
            border-radius: 6px;
        }}

        table.markup-table th {{
            background-color: #edf2f7;
            color: var(--accent-color);
            font-weight: bold;
            text-align: left;
            padding: 10px 12px;
            border-bottom: 2px solid var(--border-color);
        }}

        table.markup-table td {{
            padding: 8px 12px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-color);
        }}

        table.markup-table tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        .footnote-box {{
            margin-top: 12px;
            padding: 10px 14px;
            background-color: var(--fn-bg);
            border: 1px solid var(--fn-border);
            border-radius: 6px;
            font-size: 0.95rem;
            color: #742a2a;
            white-space: pre-line;
            line-height: 1.7;
            font-weight: normal;
        }}

        sup, .fn-star {{
            color: var(--accent-color);
            font-weight: bold;
            padding: 0 2px;
        }}

        .colophon {{
            background-color: #edf2f7;
            border-radius: 8px;
            padding: 18px;
            text-align: center;
            font-style: italic;
            margin-top: 30px;
        }}

        footer {{
            text-align: center;
            padding: 15px;
            margin-top: 40px;
            border-top: 1px solid var(--border-color);
            font-weight: bold;
            color: #4a5568;
            font-size: 0.95rem;
        }}

        @media (max-width: 768px) {{
            .global-lang-header {{
                display: none;
            }}
            .grid-2col {{
                grid-template-columns: 1fr;
            }}
            .col-sanskrit {{
                border-right: none;
                border-bottom: 1px solid var(--border-color);
                padding-right: 0;
                padding-bottom: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container" data-pagefind-body>
        <h1 class="section-title">{title}</h1>
        
        <div class="global-lang-header">
            <div class="global-lang-title">Sanskrit</div>
            <div class="global-lang-title">{second_lang}</div>
        </div>

        {content}

        <footer>
            🙏 Shri Krishnarpanam Asthu 🙏 | Maintained & published via <a href="https://ventpipe.blog/2026/10/20/shri-siva-mahapurana-trilingual-edition/" target="_blank" style="color: #8b0000; text-decoration: underline;">ventpipe.blog</a>
        </footer>
    </div>
</body>
</html>
"""

UNICODE_SUP_MAP = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹', '0123456789')

def pass1_normalize_superscripts(text):
    if not text:
        return ""
    text = re.sub(r'\$\^\{?(\d+)\}?\$', r'<sup>\1</sup>', text)

    def replace_unicode_sup(match):
        digits = match.group(1).translate(UNICODE_SUP_MAP)
        return f"<sup>{digits}</sup>"

    text = re.sub(r'([⁰¹²³⁴⁵⁶⁷⁸⁹]+)', replace_unicode_sup, text)
    return text

def convert_markdown_tables(text):
    def decode_b64_table(match):
        try:
            return base64.b64decode(match.group(1)).decode('utf-8')
        except Exception:
            return match.group(0)

    text = re.sub(r'markdowntable:\s*([A-Za-z0-9+/=]+)', decode_b64_table, text)
    table_pattern = re.compile(r'((?:\|[^\n]+\|\n?){2,})', re.MULTILINE)

    def replace_table(match):
        table_text = match.group(1).strip()
        lines = [line.strip() for line in table_text.split('\n') if line.strip()]
        if len(lines) < 2:
            return table_text

        html_table = ['<div class="custom-table-container"><table class="markup-table">']
        headers = [cell.strip() for cell in lines[0].split('|')[1:-1]]

        html_table.append('  <thead>\n    <tr>')
        for h in headers:
            html_table.append(f'      <th>{h}</th>')
        html_table.append('    </tr>\n  </thead>\n  <tbody>')

        for row in lines[2:]:
            cells = [cell.strip() for cell in row.split('|')[1:-1]]
            html_table.append('    <tr>')
            for c in cells:
                html_table.append(f'      <td>{c}</td>')
            html_table.append('    </tr>')
        html_table.append('  </tbody>\n</table></div>')

        return '\n'.join(html_table)

    return table_pattern.sub(replace_table, text)

def pass2_process_formatting_and_footnotes(text):
    if not text:
        return "", []

    footnotes = []
    fn_matches = re.findall(r'(\[fn:?\s*[^\]]+\])', text, re.DOTALL)
    for fn_raw in fn_matches:
        fn_content = re.sub(r'^\[fn:?\s*', '', fn_raw)
        fn_content = re.sub(r'\]$', '', fn_content).strip()
        fn_content = re.sub(r'(\*|[०-९\d]+\.)', r'<span class="fn-star">\1</span>', fn_content)
        fn_content = convert_markdown_tables(fn_content)
        fn_html = f'<div class="footnote-box"><b>[fn: {fn_content}]</b></div>'
        footnotes.append(fn_html)

    clean_text = re.sub(r'\[fn:?\s*[^\]]+\]', '', text, flags=re.DOTALL).strip()
    clean_text = re.sub(r'<sup>(.*?)</sup>', r'<sup class="fn-star"><b>\1</b></sup>', clean_text)
    clean_text = re.sub(r'(\*\*|__)(.*?)\1', r'<b>\2</b>', clean_text)
    clean_text = re.sub(r'(\*|_)(.*?)\1', r'<i>\2</i>', clean_text)
    clean_text = convert_markdown_tables(clean_text)

    return clean_text, footnotes

def parse_header_title(header_block, filepath):
    folder_name = os.path.basename(os.path.dirname(filepath))
    num_match = re.search(r'(\d+)', folder_name)
    nn = f"{int(num_match.group(1)):02d}" if num_match else "00"

    first_line = header_block.split('\n')[0].strip()
    raw = re.sub(r'^[#\s]+', '', first_line).strip()
    raw = re.sub(r'<sup>.*?</sup>', '', raw)
    raw = re.sub(r'\[fn:.*?\]', '', raw)

    parts = [p.strip() for p in raw.split(' - ') if p.strip()]
    clean_parts = []
    for part in parts:
        p_clean = re.sub(r'[*_`~]+', '', part).strip().strip('()')
        if p_clean and not re.search(r'said\s*:—', p_clean, re.IGNORECASE):
            clean_parts.append(p_clean)

    if len(clean_parts) >= 2:
        title_str = f"{clean_parts[0]} - ({clean_parts[1]})"
    elif clean_parts:
        title_str = clean_parts[0]
    else:
        title_str = "CHAPTER"

    return f"{nn} - {title_str}"

def process_file(filepath):
    if not os.path.exists(filepath):
        return False

    is_english = "san_eng" in os.path.basename(filepath)
    second_lang = "English" if is_english else "Hindi"

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().replace('\r\n', '\n').strip()

    raw_blocks = [b.strip() for b in content.split('---') if b.strip()]
    file_title = f"{second_lang} Translation"
    html_out = []

    for block in raw_blocks:
        if block.startswith("###") or block.startswith("#"):
            file_title = parse_header_title(block, filepath)
            _, header_fns = pass2_process_formatting_and_footnotes(pass1_normalize_superscripts(block))
            if header_fns:
                html_out.append("\n".join(header_fns))
            continue

        if "Colophon" in block:
            col_match = re.search(r'Sanskrit\n(.*)', block, re.DOTALL)
            col_text = col_match.group(1).strip() if col_match else block
            col_html = f'<div class="colophon"><div class="col-sanskrit">{col_text}</div></div>'
            html_out.append(col_html)
            continue

        sk_match = re.search(r'Sanskrit\n(.*?)(?=\n(?:English|Hindi)|\n\[fn:|\Z)', block, re.DOTALL)
        trans_match = re.search(rf'(?:English|Hindi)\n(.*?)(?=\n\[fn:|\Z)', block, re.DOTALL)

        sk_raw = sk_match.group(1).strip() if sk_match else ""
        trans_raw = trans_match.group(1).strip() if trans_match else ""

        if not sk_raw and not trans_raw:
            continue

        sk_pass1 = pass1_normalize_superscripts(sk_raw)
        trans_pass1 = pass1_normalize_superscripts(trans_raw)

        sk_text, sk_fns = pass2_process_formatting_and_footnotes(sk_pass1)
        trans_text, trans_fns = pass2_process_formatting_and_footnotes(trans_pass1)

        fn_html_combined = "\n".join(sk_fns + trans_fns)

        clean_trans_for_num = re.sub(r'\[fn:.*?\]', '', trans_raw, flags=re.DOTALL).strip()
        v_num_match = re.search(r'\((\d+(?:-\d+)?\.)\)', clean_trans_for_num)

        if not v_num_match:
            v_num_match = re.search(r'Verse\s*(\d+(?:-\d+)?)', block, re.IGNORECASE)

        if not v_num_match:
            sk_num_match = re.search(r'॥\s*([०-९0-9]+(?:\s*[-–—]\s*[०-९0-9]+)?)\s*॥', sk_raw)
            if sk_num_match:
                v_label = f"Verse {sk_num_match.group(1).translate(str.maketrans('०१२३४५६७८९', '0123456789'))}"
            else:
                v_label = "Verse"
        else:
            v_label = f"Verse {v_num_match.group(1).rstrip('.')}"

        card_html = f"""
        <div class="verse-card">
            <div class="verse-label">{v_label}</div>
            <div class="grid-2col">
                <div class="col-sanskrit">{sk_text}</div>
                <div class="col-translation">
                    {trans_text}
                    {fn_html_combined}
                </div>
            </div>
        </div>
        """
        html_out.append(card_html)

    final_html = HTML_TEMPLATE.format(
        title=file_title,
        second_lang=second_lang,
        content="\n".join(html_out)
    )

    if "aligned_trilingual" in filepath:
        out_html_path = os.path.join(os.path.dirname(filepath), "san-hin.html")
    else:
        out_html_path = filepath.replace('.txt', '.html')

    with open(out_html_path, 'w', encoding='utf-8') as out_f:
        out_f.write(final_html)

    print(f"✅ Generated: {out_html_path}")
    return True

def process_all_directories(root_dir="."):
    count = 0
    for root, _, filenames in os.walk(root_dir):
        for fname in ["san_eng.txt", "aligned_trilingual.txt"]:
            if fname in filenames:
                fpath = os.path.join(root, fname)
                if process_file(fpath):
                    count += 1
    print(f"\n🎉 Processed {count} HTML file(s) across all directories.")

if __name__ == "__main__":
    target_path = sys.argv[1] if len(sys.argv) > 1 else "."
    process_all_directories(target_path)
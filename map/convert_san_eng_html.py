import os
import re
import sys

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
            --text-color: #212529;
            --border-color: #e9ecef;
            --accent-color: #8b0000; /* Deep Red for headers & footnote superscripts */
            --sanskrit-color: #1a365d;
            --english-color: #1a202c;
            --fn-bg: #fff5f5;
            --fn-border: #feb2b2;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        h1.section-title {{
            text-align: center;
            color: var(--accent-color);
            margin-bottom: 30px;
            font-size: 1.8rem;
            line-height: 1.4;
            border-bottom: 2px solid var(--accent-color);
            padding-bottom: 15px;
        }}

        /* 2-Column Card Layout per Verse Block */
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
            font-size: 1.1rem;
        }}

        .grid-2col {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 16px;
        }}

        /* Column Specific Styles */
        .col-sanskrit {{
            color: var(--sanskrit-color);
            font-family: "Siddhanta", "Noto Sans Devanagari", "Kokila", serif;
            font-size: 1.05rem; /* Adjusted smaller Sanskrit font */
            border-right: 1px solid var(--border-color);
            padding-right: 20px;
            white-space: pre-line;
        }}

        .col-english {{
            color: var(--english-color);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 1.05rem;
            white-space: pre-line;
        }}

        .lang-title {{
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #718096;
            margin-bottom: 6px;
            font-weight: bold;
        }}

        /* Interactive Footnote Styling */
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

        /* Universal Styling for Superscripts and Footnote Reference Markers */
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

        /* Mobile Responsive Fallback to 1 Column */
        @media (max-width: 768px) {{
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
    <div class="container">
        <h1 class="section-title">{title}</h1>
        {content}
    </div>
</body>
</html>
"""

UNICODE_SUP_MAP = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹', '0123456789')

def pass1_normalize_superscripts(text):
    """PASS 1: Pre-process TeX and Unicode superscripts to <sup>...</sup>."""
    if not text:
        return ""
    text = re.sub(r'\$\^\{?(\d+)\}?\$', r'<sup>\1</sup>', text)

    def replace_unicode_sup(match):
        digits = match.group(1).translate(UNICODE_SUP_MAP)
        return f"<sup>{digits}</sup>"

    text = re.sub(r'([⁰¹²³⁴⁵⁶⁷⁸⁹]+)', replace_unicode_sup, text)
    return text

def pass2_process_formatting_and_footnotes(text):
    """PASS 2: Process bold, italics, <sup> tags, and [fn: ...] footnote boxes."""
    if not text:
        return "", []

    footnotes = []
    fn_matches = re.findall(r'(\[fn:?\s*[^\]]+\])', text, re.DOTALL)
    for fn_raw in fn_matches:
        fn_content = re.sub(r'^\[fn:?\s*', '', fn_raw)
        fn_content = re.sub(r'\]$', '', fn_content).strip()
        fn_content = re.sub(r'(\*|[०-९\d]+\.)', r'<span class="fn-star">\1</span>', fn_content)
        fn_html = f'<div class="footnote-box"><b>[fn: {fn_content}]</b></div>'
        footnotes.append(fn_html)

    clean_text = re.sub(r'\[fn:?\s*[^\]]+\]', '', text, flags=re.DOTALL).strip()
    clean_text = re.sub(r'<sup>(.*?)</sup>', r'<sup class="fn-star"><b>\1</b></sup>', clean_text)
    clean_text = re.sub(r'(\*\*|__)(.*?)\1', r'<b>\2</b>', clean_text)
    clean_text = re.sub(r'(\*|_)(.*?)\1', r'<i>\2</i>', clean_text)

    return clean_text, footnotes

def extract_chapter_number_from_path(filepath):
    """Determines 2-digit chapter number from folder path or filename."""
    folder_name = os.path.basename(os.path.dirname(filepath))
    num_match = re.search(r'(\d+)', folder_name)
    if num_match:
        return f"{int(num_match.group(1)):02d}"
    return "01"

def parse_header_title(header_block, filepath):
    """
    Parses headers like:
    ### **CHAPTER ONE - (*Greatness of Śivapurāṇa*)<sup>*</sup> - *Śaunaka*<sup>1</sup>...**
    Outputs formatted header: '<nn> - <title>'
    Example: '01 - CHAPTER ONE - (Greatness of Śivapurāṇa)'
    """
    nn = extract_chapter_number_from_path(filepath)

    raw = re.sub(r'^[#\s]+', '', header_block).strip()
    raw = re.sub(r'<sup>.*?</sup>', '', raw)  # Remove footnote superscript from title
    raw = re.sub(r'\[fn:.*?\]', '', raw)

    # Split by dashes or title boundaries
    parts = [p.strip() for p in raw.split(' - ') if p.strip()]

    clean_parts = []
    for part in parts:
        p_clean = re.sub(r'[*_`~]+', '', part).strip()
        p_clean = p_clean.strip('()')
        if p_clean and not re.search(r'said\s*:—', p_clean, re.IGNORECASE):
            clean_parts.append(p_clean)

    if len(clean_parts) >= 2:
        title_str = f"{clean_parts[0]} - ({clean_parts[1]})"
    elif clean_parts:
        title_str = clean_parts[0]
    else:
        title_str = "CHAPTER"

    return f"{nn} - {title_str}"

def parse_block(block):
    """Extracts Sanskrit, English, and Footnotes from an interleaved verse block."""
    sanskrit_match = re.search(r'Sanskrit\n(.*?)(?=\nEnglish|\n\[fn:|\Z)', block, re.DOTALL)
    english_match = re.search(r'English\n(.*?)(?=\n\[fn:|\Z)', block, re.DOTALL)

    sk_raw = sanskrit_match.group(1).strip() if sanskrit_match else ""
    en_raw = english_match.group(1).strip() if english_match else ""

    sk_pass1 = pass1_normalize_superscripts(sk_raw)
    en_pass1 = pass1_normalize_superscripts(en_raw)

    sk_text, sk_fns = pass2_process_formatting_and_footnotes(sk_pass1)
    en_text, en_fns = pass2_process_formatting_and_footnotes(en_pass1)

    fn_html_combined = "\n".join(sk_fns + en_fns)

    v_num_match = re.search(r'\((\d+(?:-\d+)?\.)\)\s*$', en_raw)
    v_label = f"Verse {v_num_match.group(1).rstrip('.')}" if v_num_match else "Verse"

    return v_label, sk_text, en_text, fn_html_combined

def parse_bilingual_file(text_filepath):
    """Parses san_eng.txt and generates san_eng.html in the same directory."""
    if not os.path.exists(text_filepath):
        return False

    with open(text_filepath, 'r', encoding='utf-8') as f:
        content = f.read().replace('\r\n', '\n').strip()

    raw_blocks = [b.strip() for b in content.split('---') if b.strip()]

    file_title = "Sanskrit - English Interleaved"
    html_out = []

    for block in raw_blocks:
        # Chapter Header
        if block.startswith("###"):
            file_title = parse_header_title(block, text_filepath)
            
            # Extract header footnote if present
            _, header_fns = pass2_process_formatting_and_footnotes(pass1_normalize_superscripts(block))
            if header_fns:
                html_out.append("\n".join(header_fns))
            continue

        # Colophon Block
        if "Colophon" in block:
            col_match = re.search(r'Sanskrit\n(.*)', block, re.DOTALL)
            col_text = col_match.group(1).strip() if col_match else block
            col_html = f'<div class="colophon"><div class="col-sanskrit">{col_text}</div></div>'
            html_out.append(col_html)
            continue

        # Verse Card Block
        v_label, sk_text, en_text, fn_html = parse_block(block)

        card_html = f"""
        <div class="verse-card">
            <div class="verse-label">{v_label}</div>
            <div class="grid-2col">
                <div class="col-sanskrit">
                    <div class="lang-title">Sanskrit</div>
                    {sk_text}
                </div>
                <div class="col-english">
                    <div class="lang-title">English</div>
                    {en_text}
                    {fn_html}
                </div>
            </div>
        </div>
        """
        html_out.append(card_html)

    final_html = HTML_TEMPLATE.format(title=file_title, content="\n".join(html_out))

    out_html_path = os.path.join(os.path.dirname(text_filepath), 'san_eng.html')
    with open(out_html_path, 'w', encoding='utf-8') as out_f:
        out_f.write(final_html)

    print(f"✅ Created HTML: {out_html_path}")
    return True

def process_directory(input_dir="."):
    """Traverses input_dir recursively and processes all san_eng.txt files found."""
    if not os.path.exists(input_dir):
        print(f"❌ Error: Input path '{input_dir}' does not exist.")
        return

    if os.path.isfile(input_dir):
        parse_bilingual_file(input_dir)
        return

    count = 0
    for root, _, filenames in os.walk(input_dir):
        if "san_eng.txt" in filenames:
            input_txt = os.path.join(root, "san_eng.txt")
            if parse_bilingual_file(input_txt):
                count += 1

    print(f"\n🎉 Successfully processed {count} directory/directories!")

if __name__ == "__main__":
    target_path = sys.argv[1] if len(sys.argv) > 1 else "."
    process_directory(target_path)
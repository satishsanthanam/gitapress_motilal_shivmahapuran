import os
import re
import sys

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="sa">
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
            --hindi-color: #1a202c;
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

        .chapter-header {{
            background: var(--accent-color);
            color: #ffffff;
            text-align: center;
            padding: 12px;
            font-size: 1.4rem;
            font-weight: bold;
            border-radius: 6px;
            margin: 40px 0 20px 0;
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
            font-size: 1.15rem;
            border-right: 1px solid var(--border-color);
            padding-right: 20px;
            white-space: pre-line;
        }}

        .col-hindi {{
            color: var(--hindi-color);
            font-family: "Noto Sans Devanagari", "Mangal", sans-serif;
            font-size: 1.1rem;
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
        }}

        /* Universal Styling for Superscripts and Footnote Reference Markers */
        sup, .fn-star {{
            color: var(--accent-color);
            font-weight: bold;
            padding: 0 2px;
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

def devanagari_to_ascii(text):
    """देवनागरी अंकों को ASCII अंकों में बदलता है।"""
    dev_digits = '०१२३४५६७८९'
    ascii_digits = '0123456789'
    trans = str.maketrans(dev_digits, ascii_digits)
    return text.translate(trans)

def extract_chapter_number(content):
    """फ़ाइल की अंतिम पंक्तियों से अध्याय/श्लोक संख्या (जैसे ॥ १६ ॥) निकालता है।"""
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    if not lines:
        return ""

    for line in reversed(lines):
        match = re.search(r'॥\s*([०-९0-9]+)\s*॥', line)
        if not match:
            match = re.search(r'\|\|\s*([०-९0-9]+)\s*\|\|', line)
        if not match:
            match = re.search(r'॥\s*([०-९0-9]+)\s*$', line)
        if not match:
            match = re.search(r'([०-९0-9]+)\s*॥?$', line)

        if match:
            return devanagari_to_ascii(match.group(1))
    return ""

def extract_title(content, fallback_title):
    """पहली पंक्ति से शीर्षक और अंतिम पंक्ति से संख्या निकालकर '# <संख्या>. <शीर्षक>' बनाता है।"""
    content_lines = content.split('\n')

    first_line_idx = -1
    for idx, line in enumerate(content_lines):
        if line.strip():
            first_line_idx = idx
            break

    if first_line_idx == -1:
        return fallback_title, content

    first_line = content_lines[first_line_idx].strip()

    # पहली पंक्ति से मार्कडाउन कैरेक्टर्स (#, **, __, HTML tags) साफ करें
    clean_text = re.sub(r'^[#\s]+', '', first_line)
    clean_text = re.sub(r'<[^>]+>', '', clean_text)
    clean_text = re.sub(r'[*_`~]+', '', clean_text).strip()

    # अंतिम पंक्तियों से अध्याय संख्या निकालें
    ch_num = extract_chapter_number(content)

    if ch_num:
        # यदि पहली पंक्ति में पहले से ही संख्या मौजूद हो तो दोहराव से बचें
        num_pattern = rf'^({ch_num}|[०-९]+)\s*[\.\s]*'
        if re.match(num_pattern, clean_text):
            clean_text = re.sub(num_pattern, '', clean_text).strip()
        full_title = f"# {ch_num}. {clean_text}"
    else:
        full_title = f"# {clean_text}"

    # पहली पंक्ति हटाने के बाद शेष फ़ाइल सामग्री
    remaining_lines = content_lines[first_line_idx + 1:]
    remaining_content = '\n'.join(remaining_lines).strip()

    return full_title, remaining_content

def format_footnote(match):
    """फुटनोट बॉक्स फ़ॉर्मैटिंग"""
    fn_content = match.group(1).strip()
    fn_content = re.sub(r'(\*|[०-९\d]+\.)', r'<span class="fn-star">\1</span>', fn_content)
    return f'<div class="footnote-box">💡 <b>Gita Press Footnote:</b>\n{fn_content}</div>'

def process_hindi_text(text):
    """हिंदी टेक्स्ट में बोल्ड, सुपेरसक्रिप्ट और फुटनोट संसाधित करता है"""
    if not text:
        return ""
    text = re.sub(r'(\*\*|__)(.*?)\1', r'<b>\2</b>', text)
    text = re.sub(r'<sup>(.*?)</sup>', r'<sup class="fn-star">\1</sup>', text)
    text = re.sub(r'\[fn:\s*(.*?)\]', format_footnote, text, flags=re.DOTALL)
    return text

def parse_bilingual_file(text_filepath):
    if not os.path.exists(text_filepath):
        print(f"❌ File not found: {text_filepath}")
        return

    # Windows (\r\n) और Unix (\n) न्यूलाइन्स को एकसमान करें
    with open(text_filepath, 'r', encoding='utf-8') as f:
        content = f.read().replace('\r\n', '\n').strip()

    fallback_title = os.path.basename(text_filepath).replace('.txt', '').replace('_', ' ').title()
    file_title, content = extract_title(content, fallback_title)

    chapter_blocks = re.split(r'={10,}\s*\n\s*(.*?)\s*\n={10,}', content)
    html_out = []

    if len(chapter_blocks) == 1:
        raw_chapters = [("CHAPTER", content)]
    else:
        raw_chapters = []
        for i in range(1, len(chapter_blocks), 2):
            raw_chapters.append((chapter_blocks[i].strip(), chapter_blocks[i+1].strip()))

    for ch_title, ch_text in raw_chapters:
        if len(raw_chapters) > 1:
            html_out.append(f'<div class="chapter-header">{ch_title}</div>')

        verse_chunks = re.split(r'(\n?--- (?:Verse|Colophon).*? ---\n?)', ch_text)

        # '--- Verse 1 ---' से पहले वाले ब्लॉक की जाँच
        first_block = verse_chunks[0].strip()
        if first_block:
            sk_match = re.search(r'Sanskrit\s*\n(.*?)(?=\s*Hindi|\n---|$)', first_block, re.DOTALL | re.IGNORECASE)
            hi_match = re.search(r'Hindi\s*\n(.*)', first_block, re.DOTALL | re.IGNORECASE)

            sk_text = sk_match.group(1).strip() if sk_match else ""
            hi_text = hi_match.group(1).strip() if hi_match else ""

            if hi_text and hi_text.lower() != '<em>प्रस्तावना</em>':
                hi_text = process_hindi_text(hi_text)
                intro_html = f"""
                <div class="verse-card">
                    <div class="verse-label">Chapter Intro</div>
                    <div class="grid-2col">
                        <div class="col-sanskrit">
                            <div class="lang-title">Sanskrit</div>
                            {sk_text}
                        </div>
                        <div class="col-hindi">
                            <div class="lang-title">Hindi</div>
                            {hi_text}
                        </div>
                    </div>
                </div>
                """
                html_out.append(intro_html)

        # सभी श्लोक ब्लॉक्स का प्रसंस्करण
        for idx in range(1, len(verse_chunks), 2):
            v_label = verse_chunks[idx].strip(' -\n')
            v_content = verse_chunks[idx+1].strip() if idx+1 < len(verse_chunks) else ""

            sk_match = re.search(r'Sanskrit\s*\n(.*?)(?=\s*Hindi|\n---|$)', v_content, re.DOTALL | re.IGNORECASE)
            hi_match = re.search(r'Hindi\s*\n(.*)', v_content, re.DOTALL | re.IGNORECASE)

            sk_text = sk_match.group(1).strip() if sk_match else ""
            hi_text = hi_match.group(1).strip() if hi_match else ""

            # यदि explicit Hindi टैग न मिले तो v_content का उपयोग करें
            if not hi_text and not sk_match:
                hi_text = v_content.strip()

            hi_text = process_hindi_text(hi_text)

            verse_html = f"""
            <div class="verse-card">
                <div class="verse-label">{v_label}</div>
                <div class="grid-2col">
                    <div class="col-sanskrit">
                        <div class="lang-title">Sanskrit</div>
                        {sk_text}
                    </div>
                    <div class="col-hindi">
                        <div class="lang-title">Hindi</div>
                        {hi_text}
                    </div>
                </div>
            </div>
            """
            html_out.append(verse_html)

    final_html = HTML_TEMPLATE.format(title=file_title, content="\n".join(html_out))

    out_html_path = text_filepath.replace('.txt', '.html')
    with open(out_html_path, 'w', encoding='utf-8') as out_f:
        out_f.write(final_html)

    print(f"✅ HTML Generated:\n   Title: '{file_title[:70]}...'\n   File:  '{out_html_path}'")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        parse_bilingual_file(sys.argv[1])
    else:
        print("Usage: python convert_to_html.py <path_to_aligned_txt_file>")
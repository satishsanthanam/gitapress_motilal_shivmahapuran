import os
import shutil
import tarfile
import re

SAMHITA_NAMES = {
    "00": "00 - Vidyeśvara Saṁhitā",
    "01": "01 - Rudra Saṁhitā (Sṛṣṭi Khaṇḍa)",
    "02": "02 - Rudra Saṁhitā",
    "03": "03 - Śatarudra Saṁhitā",
    "04": "04 - Koṭirudra Saṁhitā",
    "05": "05 - Umā Saṁhitā",
    "06": "06 - Kailāsa Saṁhitā",
    "07": "07 - Vāyavīya Saṁhitā"
}

# Sub-section / Khaṇḍa Mapping for Saṁhitās 02 and 07
SUBSECTION_NAMES = {
    "02": {
        "01": "Sṛṣṭi Khaṇḍa",
        "02": "Satī Khaṇḍa",
        "03": "Pārvatī Khaṇḍa",
        "04": "Kumāra Khaṇḍa",
        "05": "Yuddha Khaṇḍa"
    },
    "07": {
        "01": "Pūrva Bhāga",
        "02": "Uttara Bhāga"
    }
}

def build_site():
    build_dir = "html_out"
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)

    copied_count = 0
    chapter_list = []

    # 1. Traversal and Folder Mirroring to html_out
    for root, _, files in os.walk("."):
        if "html_out" in root or root.startswith("./."):
            continue

        for f in files:
            if f in ["san_eng.html", "san-hin.html"]:
                rel_path = os.path.relpath(root, ".").replace("\\", "/")
                target_folder = os.path.join(build_dir, rel_path)
                os.makedirs(target_folder, exist_ok=True)

                shutil.copy2(os.path.join(root, f), os.path.join(target_folder, f))
                copied_count += 1

                parts = rel_path.split("/")
                samhita = parts[0]
                
                if len(parts) == 3:
                    sub_sec = parts[1]
                    chapter = parts[2]
                else:
                    sub_sec = None
                    chapter = parts[1] if len(parts) > 1 else "ch_00"

                existing = next((item for item in chapter_list if item["path"] == rel_path), None)
                if not existing:
                    existing = {"samhita": samhita, "sub_sec": sub_sec, "chapter": chapter, "path": rel_path}
                    chapter_list.append(existing)

                if f == "san_eng.html":
                    existing["eng"] = f"{rel_path}/san_eng.html"
                else:
                    existing["hin"] = f"{rel_path}/san-hin.html"

    chapter_list.sort(key=lambda x: (x["samhita"], x["sub_sec"] or "", x["chapter"]))

    for idx, item in enumerate(chapter_list):
        item["prev_eng"] = chapter_list[idx-1]["eng"] if idx > 0 and "eng" in chapter_list[idx-1] else ""
        item["next_eng"] = chapter_list[idx+1]["eng"] if idx < len(chapter_list)-1 and "eng" in chapter_list[idx+1] else ""
        item["prev_hin"] = chapter_list[idx-1]["hin"] if idx > 0 and "hin" in chapter_list[idx-1] else ""
        item["next_hin"] = chapter_list[idx+1]["hin"] if idx < len(chapter_list)-1 and "hin" in chapter_list[idx+1] else ""

    # 2. Build Navigation Tree Structure
    tree_data = {}
    for item in chapter_list:
        s = item["samhita"]
        sub = item["sub_sec"]
        if s not in tree_data:
            tree_data[s] = {}
        
        if sub:
            if sub not in tree_data[s]:
                tree_data[s][sub] = []
            tree_data[s][sub].append(item)
        else:
            if "root" not in tree_data[s]:
                tree_data[s]["root"] = []
            tree_data[s]["root"].append(item)

    nav_html = []
    for s_key in sorted(tree_data.keys()):
        s_name = SAMHITA_NAMES.get(s_key, f"Saṁhitā {s_key}")
        nav_html.append(f'<details><summary>{s_name}</summary><ul>')

        sub_keys = sorted([k for k in tree_data[s_key].keys() if k != "root"])
        
        if "root" in tree_data[s_key]:
            for item in tree_data[s_key]["root"]:
                ch_num = re.sub(r'^\D+', '', item["chapter"])
                ch_display = f"Chapter {int(ch_num):02d}" if ch_num.isdigit() else item["chapter"].title()
                eng = item.get("eng", "")
                hin = item.get("hin", "")
                nav_html.append(f'<li><a href="#" data-eng="{eng}" data-hin="{hin}" onclick="loadChapter(\'{eng}\', \'{hin}\', \'{item["prev_eng"]}\', \'{item["next_eng"]}\', \'{item["prev_hin"]}\', \'{item["next_hin"]}\'); return false;">{ch_display}</a></li>')

        for sub in sub_keys:
            sub_name = SUBSECTION_NAMES.get(s_key, {}).get(sub, f"Section {sub}")
            nav_html.append(f'<li style="margin-left: -5px;"><details><summary style="background:#3182ce;">{sub_name}</summary><ul>')
            for item in tree_data[s_key][sub]:
                ch_num = re.sub(r'^\D+', '', item["chapter"])
                ch_display = f"Chapter {int(ch_num):02d}" if ch_num.isdigit() else item["chapter"].title()
                eng = item.get("eng", "")
                hin = item.get("hin", "")
                nav_html.append(f'<li><a href="#" data-eng="{eng}" data-hin="{hin}" onclick="loadChapter(\'{eng}\', \'{hin}\', \'{item["prev_eng"]}\', \'{item["next_eng"]}\', \'{item["prev_hin"]}\', \'{item["next_hin"]}\'); return false;">{ch_display}</a></li>')
            nav_html.append('</ul></details></li>')

        nav_html.append('</ul></details>')

    index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Śiva Purāṇa - Digital Library</title>
    <link href="/pagefind/pagefind-ui.css" rel="stylesheet">
    <script src="/pagefind/pagefind-ui.js"></script>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; height: 100vh; overflow: hidden; }}

        #sidebar {{ width: 340px; background: #1a365d; color: #ffffff; overflow-y: auto; padding: 15px; border-right: 2px solid #8b0000; flex-shrink: 0; display: flex; flex-direction: column; }}
        #sidebar h2 {{ font-size: 1.2rem; color: #feb2b2; text-align: center; border-bottom: 1px solid #4a5568; padding-bottom: 10px; margin-top: 5px; }}

        #search {{ margin-bottom: 15px; background: #ffffff; border-radius: 6px; padding: 5px; color: #000; }}

        #nav-tree {{ flex-grow: 1; overflow-y: auto; }}

        details {{ margin-bottom: 10px; }}
        summary {{ font-weight: bold; cursor: pointer; padding: 6px; background: #2c5282; border-radius: 4px; font-size: 0.95rem; margin-bottom: 4px; list-style: none; }}
        summary::-webkit-details-marker {{ display: none; }}

        ul {{ list-style: none; padding-left: 15px; margin: 5px 0; }}
        li {{ margin: 4px 0; }}
        a {{ color: #e2e8f0; text-decoration: none; font-size: 0.9rem; display: block; padding: 4px 8px; border-radius: 4px; transition: background 0.2s; }}
        a:hover, a.active-link {{ background: #3182ce; color: #fff; font-weight: bold; }}

        #main-content {{ flex-grow: 1; display: flex; flex-direction: column; background: #f8f9fa; position: relative; }}

        #tab-bar {{ background: #edf2f7; padding: 10px 20px 0 20px; border-bottom: 1px solid #cbd5e0; display: flex; justify-content: space-between; align-items: center; }}
        .tabs {{ display: flex; gap: 10px; }}
        .tab-button {{ padding: 8px 18px; border: 1px solid #cbd5e0; border-bottom: none; background: #e2e8f0; cursor: pointer; border-radius: 6px 6px 0 0; font-weight: bold; color: #4a5568; }}
        .tab-button.active {{ background: #ffffff; color: #8b0000; border-top: 3px solid #8b0000; }}

        #nav-controls {{ display: flex; gap: 8px; padding-bottom: 6px; }}
        .nav-btn {{ padding: 6px 14px; background: #8b0000; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 0.85rem; text-decoration: none; }}
        .nav-btn:disabled {{ background: #cbd5e0; cursor: not-allowed; }}

        #frame-container {{ flex-grow: 1; position: relative; }}
        iframe {{ width: 100%; height: 100%; border: none; position: absolute; top: 0; left: 0; display: none; }}
        iframe.active {{ display: block; }}

        footer.site-footer {{ background: #1a365d; color: #ffffff; text-align: center; padding: 8px; font-size: 0.85rem; font-weight: bold; border-top: 1px solid #4a5568; }}
    </style>
</head>
<body>

    <div id="sidebar">
        <h2>Śiva Purāṇa</h2>
        <div id="search"></div>
        <div id="nav-tree">
            {"".join(nav_html)}
        </div>
    </div>

    <div id="main-content">
        <div id="tab-bar">
            <div class="tabs">
                <button class="tab-button active" onclick="switchTab('eng')">Sanskrit - English</button>
                <button class="tab-button" onclick="switchTab('hin')">Sanskrit - Hindi</button>
            </div>
            <div id="nav-controls">
                <button id="btn-prev" class="nav-btn" onclick="goPrev()">&larr; Prev Chapter</button>
                <button id="btn-next" class="nav-btn" onclick="goNext()">Next Chapter &rarr;</button>
            </div>
        </div>
        <div id="frame-container">
            <iframe id="frame-eng" class="active" src="about:blank"></iframe>
            <iframe id="frame-hin" src="about:blank"></iframe>
        </div>
        <footer class="site-footer">
            | 🙏 ॐ नमः शिवाय 🙏 | 🙏 Shri Krishnarpanam Asthu 🙏 | Maintained & published via <a href="https://ventpipe.blog/2026/10/20/shri-siva-mahapurana-trilingual-edition/" target="_blank" style="color: #63b3ed; text-decoration: underline;">ventpipe.blog</a>
        </footer>
    </div>

    <script>
        let currentTab = 'eng';
        let state = {{ prev_eng: '', next_eng: '', prev_hin: '', next_hin: '' }};

        window.addEventListener('DOMContentLoaded', (event) => {{
            const pf = new PagefindUI({{
                element: "#search",
                showSubResults: true,
                resetFilters: false,
                processResult: function(result) {{
                    if (result.url && !result.url.endsWith('.html') && !result.url.includes('#')) {{
                        result.url = result.url + '.html';
                    }}
                    return result;
                }}
            }});

            document.addEventListener('click', function(e) {{
                const anchor = e.target.closest('a');
                if (anchor && anchor.closest('#search')) {{
                    let href = anchor.getAttribute('href');
                    if (!href || href === '#') return;

                    if (href.startsWith('/')) href = href.substring(1);
                    if (!href.endsWith('.html') && !href.includes('#')) href += '.html';

                    const cleanPath = href.split('#')[0];

                    const matchLink = document.querySelector(`#sidebar a[data-eng="${{cleanPath}}"]`) || 
                                      document.querySelector(`#sidebar a[data-hin="${{cleanPath}}"]`);

                    e.preventDefault();
                    e.stopPropagation();

                    if (matchLink) {{
                        matchLink.click();
                    }} else {{
                        if (cleanPath.includes('san-hin')) {{
                            switchTab('hin');
                            document.getElementById('frame-hin').src = cleanPath;
                        }} else {{
                            switchTab('eng');
                            document.getElementById('frame-eng').src = cleanPath;
                        }}
                    }}
                }}
            }}, true);
        }});

        function loadChapter(engPath, hinPath, pEng, nEng, pHin, nHin) {{
            state.prev_eng = pEng; state.next_eng = nEng;
            state.prev_hin = pHin; state.next_hin = nHin;

            document.getElementById('frame-eng').src = engPath || 'about:blank';
            document.getElementById('frame-hin').src = hinPath || 'about:blank';

            updateNavButtons();
        }}

        function updateNavButtons() {{
            const p = currentTab === 'eng' ? state.prev_eng : state.prev_hin;
            const n = currentTab === 'eng' ? state.next_eng : state.next_hin;

            document.getElementById('btn-prev').disabled = !p;
            document.getElementById('btn-next').disabled = !n;
        }}

        function goPrev() {{
            const p = currentTab === 'eng' ? state.prev_eng : state.prev_hin;
            if (p) findAndClickLink(p);
        }}

        function goNext() {{
            const n = currentTab === 'eng' ? state.next_eng : state.next_hin;
            if (n) findAndClickLink(n);
        }}

        function findAndClickLink(path) {{
            if (!path) return;
            const attr = currentTab === 'eng' ? 'data-eng' : 'data-hin';
            const link = document.querySelector(`#sidebar a[${{attr}}="${{path}}"]`);
            if (link) {{
                let parent = link.closest('details');
                while (parent) {{
                    parent.open = true;
                    parent = parent.parentElement ? parent.parentElement.closest('details') : null;
                }}
                
                document.querySelectorAll('#sidebar a').forEach(a => a.classList.remove('active-link'));
                link.classList.add('active-link');
                link.click();
            }}
        }}

        function switchTab(type) {{
            currentTab = type;
            const buttons = document.querySelectorAll('.tab-button');
            buttons.forEach(b => b.classList.remove('active'));

            document.getElementById('frame-eng').classList.remove('active');
            document.getElementById('frame-hin').classList.remove('active');

            if(type === 'eng') {{
                buttons[0].classList.add('active');
                document.getElementById('frame-eng').classList.add('active');
            }} else {{
                buttons[1].classList.add('active');
                document.getElementById('frame-hin').classList.add('active');
            }}
            updateNavButtons();
        }}

        window.onload = function() {{
            const firstLink = document.querySelector('#sidebar a');
            if(firstLink) {{
                let parent = firstLink.closest('details');
                while (parent) {{ parent.open = true; parent = parent.parentElement ? parent.parentElement.closest('details') : null; }}
                firstLink.click();
            }}
        }};
    </script>

</body>
</html>
"""

    with open(os.path.join(build_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_content)

if __name__ == "__main__":
    build_site()
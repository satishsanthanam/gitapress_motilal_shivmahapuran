# Shri Śīva Mahāpurāṇa: A Verse-Mapped Trilingual Edition (Sanskrit – English – Hindi)

<div align="center">

### ॥ ॐ नमः शिवाय ॥

</div>

A high-performance, responsive static web publication and search platform for the complete **Shri Śīva Mahāpurāṇa** across all 7 Saṁhitās (including multi-section hierarchies for Saṁhitā 02 and Saṁhitā 07). The platform provides side-by-side Sanskrit Devanagari text, English and Hindi translations, collapsible sidebar navigation, dual-pane viewing options, and client-side static site search via Pagefind.

🔗 **Live Application**: [https://gitapress-motilal-shivmahapuran.pages.dev/](https://gitapress-motilal-shivmahapuran.pages.dev/)

📂 **Deployment Platform**: Maintained & published via Cloudflare Pages with automated CI/CD build pipeline.

---

## Features

* **Complete 7 Saṁhitās Coverage**: Full digital edition encompassing all Adhyāyas (Chapters) across all 7 Saṁhitās formatted into clean, verse-mapped HTML pages.
* **Hierarchical Saṁhitā Support**: Full support for nested sub-sections (e.g., Saṁhitā 02 with 5 sub-sections and Saṁhitā 07 with 2 sub-sections).
* **Dual-Pane Trilingual Layout**: Interactive tab controls allowing readers to toggle seamlessly between **Sanskrit – English** and **Sanskrit – Hindi** dual-pane views.
* **Verse-Level Text Mapping**: Structured card grid format featuring Devanagari Sanskrit text alongside matching translations, formatted tables, and footnote details.
* **Collapsible Accordion Sidebar**: Interactive, multi-level directory tree that stays collapsed by default and automatically expands to highlight active chapter links.
* **Previous / Next Chapter Controls**: Floating navigation controls to easily transition between adjacent chapters without breaking iframe layout context.
* **Static Client-Side Search**: Embedded **Pagefind** search engine enabling instant full-text search across Sanskrit, English, and Hindi text directly in the browser.
* **Automated Cloudflare Pages Deployment**: Custom Python pipeline integrated with Cloudflare Pages for automated static builds on every push to `main`.

---

## Repository & Project Structure

```text
gitapress_motilal_shivmahapuran/
└── map/
    ├── convert_all_to_html.py   # Master text-to-HTML converter script
    ├── build_website.py         # Website bundler, iframe index loader & nav generator
    ├── dir.txt                  # Directory structure & folder mapping log
    ├── align_tri.py             # Script to align trilingual sources into structured text
    ├── split_san_by_dir.py      # Automated text splitting utility per folder
    ├── 00/ ... 07/              # Source text folders (with sub-sections for 02 & 07)
    │   └── ch_XX/
    │       ├── san_eng.txt      # Aligned Sanskrit + English text source
    │       └── san-hin.txt      # Aligned Sanskrit + Hindi text source
    └── html_out/                # Generated output directory served by Cloudflare Pages
        ├── index.html           # Master entrypoint UI layout
        ├── pagefind/            # Pagefind search assets & indexes
        └── 00/ ... 07/          # Compiled HTML chapter files

```

---

## Build Pipeline Architecture

The site build pipeline executes automatically on Cloudflare Pages on every push to `main`:

```
┌────────────────────────────────────────────────────────┐
│  Source Text Files (san_eng.txt & aligned_trilingual)  │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
   [1] convert_all_to_html.py  --> Converts raw text files to san_eng.html / san-hin.html
                            │
                            ▼
   [2] build_website.py        --> Mirrors structure to html_out/, generates collapsed nav
                                   tree & master index.html with dual-pane tabs
                            │
                            ▼
   [3] npx pagefind CLI        --> Generates static search index inside html_out/pagefind
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│              Cloudflare Pages Deployment               │  --> Serves static assets directly
└────────────────────────────────────────────────────────┘      from html_out/

```

---

## Primary Sources & Digitization Methodology

The digital edition of the *Shri Śīva Mahāpurāṇa* was assembled by stitching together three primary sacred text sources through a hybrid process combining automated AI OCR processing, custom Python dataset alignment, and manual verification:

### Primary Sources

* **English Translation**: *Śiva Purāṇa* — Translated by J. L. Shastri, published by **MOTILAL BANARSIDASS PUBLISHERS PVT. LTD., DELHI**.
* **Hindi Translation & Text**: *Shri Shiv Maha Puran Ank* (Kalyan 91st Year Special Edition / Visheshank - Hindi Translation with Sanskrit Verses) — Published by **Gita Press, Gorakhpur**. Digitized edition sourced via [Internet Archive](https://archive.org/details/shiv-puran_202402).
* **Sanskrit Devanagari Source**: Sourced from [Sanskrit Documents (doc_purana)](https://sanskritdocuments.org/doc_purana/).

### Digitization & Dataset Construction

1. **OCR Extraction**: Sourced print and PDF documents were extracted and digitized using **Mistral OCR AI** to generate structured raw text.
2. **Per-Folder Text Alignment (`san_eng.txt` & `san-hin.txt`)**:
* For every individual chapter across all 7 Saṁhitās (e.g., `./01/ch_05/` or `./02/01/ch_00/`), the raw Sanskrit verses, English translations, and Hindi translations were segmented and aligned into standardized per-folder text files:
* `san_eng.txt`: Verse-by-verse Sanskrit Devanagari mapped alongside matching English translation and footnotes.
* `aligned_trilingual.txt` / `san-hin.txt`: Verse-by-verse Sanskrit Devanagari mapped alongside Hindi translation from the Kalyan Visheshank edition.




3. **Automated & Manual Hybrid Stitching**: Verse boundaries, chapter titles, colophons, superscripts, and footnotes were partially aligned via automated Python splitting scripts (`split_san_by_dir.py`, `align_tri.py`) and refined through meticulous manual editing to preserve scriptural integrity.

---

## Cloudflare Pages Configuration

When deploying on Cloudflare Pages, use the following build configuration:

* **Framework preset**: `None`
* **Root directory (Advanced)**: `map`
* **Build command**:
```bash
python convert_all_to_html.py && python build_website.py && npx pagefind --site html_out

```


* **Build output directory**: `html_out`

---

## Local Setup & Development

### Prerequisites

* Python 3.10+
* Node.js & `npx` (for Pagefind execution)

### Running the Build Locally

1. **Clone the Repository**:
```bash
git clone [https://github.com/satishsanthanam/gitapress_motilal_shivmahapuran.git](https://github.com/satishsanthanam/gitapress_motilal_shivmahapuran.git)
cd gitapress_motilal_shivmahapuran/map

```


2. **Execute HTML Generator**:
```bash
python convert_all_to_html.py

```


3. **Execute Website Bundler**:
```bash
python build_website.py

```


4. **Generate Pagefind Search Index**:
```bash
npx pagefind --site html_out

```


5. **Preview Locally**:
```bash
cd html_out
python -m http.server 8000

```



Open `http://localhost:8000` in your web browser.

---

## Credits & Acknowledgments

* **Developer & Maintainer**: [Satish Santhanam](https://ventpipe.blog) — Engineered pipeline scripts, multi-level hierarchy processing, hybrid text stitching, and Cloudflare Pages deployment.
* **Publication Post**: [Shri Śīva Mahāpurāṇa: A Verse-Mapped Trilingual Edition on ventpipe.blog](https://ventpipe.blog/2026/10/20/shri-siva-mahapurana-trilingual-edition/)
* **AI Collaborator**: Google Gemini AI — Code architecture, Pagefind search integration, and UI template engineering.

---

## License & Dedication

**॥ ॐ नमः शिवाय ॥**

**🙏 Shri Krishnarpanam Asthu 🙏** | Maintained & published via [ventpipe.blog](https://ventpipe.blog/2026/10/20/shri-siva-mahapurana-trilingual-edition/)

Maintained as part of an open-access digital Sanskrit scripture preservation initiative. Free for non-commercial, educational, and research utilization.

## Pending activities

*  Footer mapping for english translation from third samhita
*  Comprehensive Proof reading
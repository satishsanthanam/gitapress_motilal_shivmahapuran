import os
import sys
import math
from pypdf import PdfReader, PdfWriter

def split_pdf_by_chunk_size(input_pdf_path, pages_per_chunk=75):
    """Splits a PDF into multiple parts of up to `pages_per_chunk` pages each."""
    if not os.path.exists(input_pdf_path):
        print(f"❌ Error: File '{input_pdf_path}' not found.")
        return

    reader = PdfReader(input_pdf_path)
    total_pages = len(reader.pages)
    base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]
    num_chunks = math.ceil(total_pages / pages_per_chunk)

    print(f"📖 Processing '{input_pdf_path}' ({total_pages} total pages)...")
    print(f"✂️ Splitting into {num_chunks} part(s) of max {pages_per_chunk} pages each:\n")

    for i in range(num_chunks):
        start_page = i * pages_per_chunk
        end_page = min((i + 1) * pages_per_chunk, total_pages)

        writer = PdfWriter()
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])

        output_filename = f"{base_name}_part_{i+1}_pages_{start_page+1}_to_{end_page}.pdf"
        with open(output_filename, "wb") as out_file:
            writer.write(out_file)

        print(f"✅ Created: '{output_filename}' (Pages {start_page+1} to {end_page})")

if __name__ == "__main__":
    # Usage: python split_75_pages.py <your_pdf_file.pdf>
    if len(sys.argv) > 1:
        input_pdf = sys.argv[1]
        chunk_size = int(sys.argv[2]) if len(sys.argv) > 2 else 75
        split_pdf_by_chunk_size(input_pdf, chunk_size)
    else:
        # Default fallback execution if no argument provided
        split_pdf_by_chunk_size("shivmahapuran.pdf", 75)
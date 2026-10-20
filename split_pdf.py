import sys
from pypdf import PdfReader, PdfWriter


def split_pdf(input_pdf_path, output_pdf_path, start_page, end_page):
    """Splits a PDF by extracting pages from start_page to end_page (1-indexed inclusive).

    :param input_pdf_path: Path to source PDF
    :param output_pdf_path: Path for output PDF
    :param start_page: Starting page number (1-indexed, e.g., 5)
    :param end_page: Ending page number (1-indexed, e.g., 15)
    """
    reader = PdfReader(input_pdf_path)
    total_pages = len(reader.pages)

    # Input Validation
    if start_page < 1 or end_page > total_pages or start_page > end_page:
        print(
            f"❌ Error: Invalid page range {start_page}-{end_page}. Document has {total_pages} pages."
        )
        return

    writer = PdfWriter()

    # pypdf uses 0-indexed page numbers (range from start_page-1 to end_page)
    for page_num in range(start_page - 1, end_page):
        writer.add_page(reader.pages[page_num])

    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)

    print(
        f"✅ Successfully created '{output_pdf_path}' with pages {start_page} to {end_page}!"
    )


if __name__ == "__main__":
    # Example Usage:
    # Python script.py input.pdf output.pdf start_page end_page
    if len(sys.argv) == 5:
        in_pdf = sys.argv[1]
        out_pdf = sys.argv[2]
        m = int(sys.argv[3])
        n = int(sys.argv[4])
        split_pdf(in_pdf, out_pdf, m, n)
    else:
        # Direct execution fallback
        input_file = "devi_bhagavatam.pdf"
        output_file = "extracted_pages.pdf"
        start_m = 10
        end_n = 25

        split_pdf(input_file, output_file, start_m, end_n)

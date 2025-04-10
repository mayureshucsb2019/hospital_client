from pathlib import Path

import markdown
from weasyprint import HTML


# Convert markdown to PDF using WeasyPrint
def convert_markdown_to_pdf(filename: str):
    with open(f"{filename}.txt", "r") as f:
        md_content = f.read()

    # Convert Markdown to HTML
    html_content = markdown.markdown(md_content)

    # Convert HTML to PDF using WeasyPrint
    HTML(string=html_content).write_pdf(f"{filename}.pdf")


def convert_markdown_txt_to_pdf(filename: Path):
    with open(filename, "r") as f:
        md_content = f.read()

    # Convert Markdown to HTML
    html_content = markdown.markdown(md_content)

    # Construct the output path in the same folder
    output_pdf_path = filename.parent / Path(f"{filename.stem}.pdf")

    # Convert HTML to PDF using WeasyPrint
    HTML(string=html_content).write_pdf(str(output_pdf_path))

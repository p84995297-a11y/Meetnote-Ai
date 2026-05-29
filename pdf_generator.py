
from fpdf import FPDF


def create_pdf(text, output_path):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font(
        "Arial",
        size=12
    )

    pdf.multi_cell(

        0,

        10,

        text

    )

    pdf.output(output_path)
from pdftotext import PDF

from kplc_interruptions.interruptions.models import (
    InterruptionPdf, InterruptionPdfText)


def extract_text_from_pdf():
    interruption_pdfs = InterruptionPdf.objects.filter(pdf_text__isnull=True)
    for interruption_pdf in interruption_pdfs:
        with open(interruption_pdf.pdf_file.path, "rb") as f:
            pdf = PDF(f)

        pdf_text, _ = InterruptionPdfText.objects.get_or_create(
            pdf=interruption_pdf, defaults={"pdf_text": "\n".join(pdf)})
        print("Extracted text from PDF {}".format(pdf_text))

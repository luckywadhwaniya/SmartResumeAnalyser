import pdfplumber
import io

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extracts text from an uploaded PDF file using pdfplumber.
    """
    text = ""
    try:
        # pdf_file is typically an UploadedFile object from Streamlit
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                extracted_page = page.extract_text()
                if extracted_page:
                    text += extracted_page + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

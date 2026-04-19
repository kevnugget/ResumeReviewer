import fitz  # PyMuPDF
import docx


def extract_text(file_bytes, filename):
    ext = filename.split(".")[-1].lower()  # grab the file extension to know how to parse it

    if ext == "pdf":
        return extract_from_pdf(file_bytes)
    elif ext in ("doc", "docx"):
        return extract_from_docx(file_bytes)
    elif ext == "txt":
        return file_bytes.decode("utf-8")  # txt is already plain text, just decode the bytes
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def extract_from_pdf(file_bytes):
    text = ""
    pdf = fitz.open(stream=file_bytes, filetype="pdf")  # open pdf from bytes, not a file path
    for page in pdf:
        text += page.get_text()  # pull raw text off each page
    return text


def extract_from_docx(file_bytes):
    import io
    doc = docx.Document(io.BytesIO(file_bytes))  # docx needs a file-like object, so wrap bytes in BytesIO
    return "\n".join([para.text for para in doc.paragraphs])  # join all paragraphs into one string

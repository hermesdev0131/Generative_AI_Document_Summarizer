import fitz  # PyMuPDF

def extract_section_block(full_text, section_title, next_section_title):
    start = full_text.find(section_title)
    end = full_text.find(next_section_title, start)
    return full_text[start:end].strip() if start != -1 and end != -1 else ""

def extract_template_sections(template_path):
    doc = fitz.open(template_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    return {
        "The Pitch": extract_section_block(full_text, "The Pitch", "Rewards"),
        "Client Needs": extract_section_block(full_text, "Client Needs", "The Elixir"),
        "Insurance+": extract_section_block(full_text, "Insurance+", "Landmines"),
    }
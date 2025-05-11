import fitz  # PyMuPDF
from docx import Document

SECTION_ORDER = ["Prospect Curator", "Back of the Napkin", "The Pitch", "Rewards", "Client Needs", "The Elixir", "Insurance+", "Landmines", "Path to Close", "What Will Clients Ask?", "Sustain Success", "Look Ahead"]
def extract_section_block(full_text, section_title, next_section_title):
    start = full_text.find(section_title)
    if next_section_title:
        end = full_text.find(next_section_title, start)
    else:   
        end = len(full_text)
    return full_text[start:end].strip() if start != -1 and end != -1 else ""

def extract_template_sections(template_path):
    doc = fitz.open(template_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    ## Split the text into lines
    summarizes = {}
    for section in SECTION_ORDER:
        next_section = SECTION_ORDER[SECTION_ORDER.index(section) + 1] if SECTION_ORDER.index(section) + 1 < len(SECTION_ORDER) else None
        summarizes[section] = extract_section_block(full_text, section, next_section)
    return summarizes

def create_section_block(full_text_list, section_title, next_section_title):
    full_text = "\n".join(full_text_list)
    start = full_text.find(section_title)
    if next_section_title:
        end = full_text.find(next_section_title, start)
    else:   
        end = len(full_text)
    return full_text[start:end].strip() if start != -1 and end != -1 else ""


def create_template_sections(template_path):
    print(f"Extracting sections from template: {template_path}")    
    doc = Document(template_path)

    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    summarizes = {}
    
    for section in SECTION_ORDER:
        next_section = SECTION_ORDER[SECTION_ORDER.index(section) + 1] if SECTION_ORDER.index(section) + 1 < len(SECTION_ORDER) else None
        summarizes[section] = create_section_block(full_text, section, next_section)
    return summarizes




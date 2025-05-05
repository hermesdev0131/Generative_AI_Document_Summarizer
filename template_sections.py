import fitz  # PyMuPDF

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

    return {
        "Prospect Curator": extract_section_block(full_text, "Prospect Curator", "Back of the Napkin"),
        "Back of the Napkin": extract_section_block(full_text, "Back of the Napkin", "The Pitch"),
        "The Pitch": extract_section_block(full_text, "The Pitch", "Rewards"),
        "Rewards": extract_section_block(full_text, "Rewards", "Client Needs"),
        "Client Needs": extract_section_block(full_text, "Client Needs", "The Elixir"),
        "The Elixir": extract_section_block(full_text, "The Elixir", "Insurance+"),
        "Insurance+": extract_section_block(full_text, "Insurance+", "Landmines"),                
        "Landmines": extract_section_block(full_text, "Landmines", "Path to Close"),
        "Path to Close": extract_section_block(full_text, "Path to Close", "Sustain Success"),        
        "Sustain Success": extract_section_block(full_text, "Sustain Success", ""),
    }

import openai
import pdfplumber

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def call_openai_summary(text, section_title, section_instruction, api_key):
    openai.api_key = api_key
    prompt = f"""
You are a professional summarizer. Based on the following instructions and document text, write the section titled '{section_title}'.

--- Instruction from Template ---
{section_instruction}

--- Document Text ---
{text}

Write the '{section_title}' section:
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message["content"].strip()

def summarize_pdf_sections(pdf_path, api_key, instructions):
    source_text = extract_text_from_pdf(pdf_path)
    return {
        section: call_openai_summary(source_text, section, instructions[section], api_key)
        for section in instructions.keys()
    }
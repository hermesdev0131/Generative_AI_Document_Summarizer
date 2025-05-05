import openai
import pdfplumber
import time
import logging

logging.basicConfig(level=logging.INFO)
def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def call_openai_summary(text, section_title, section_instruction, api_key):
    openai.api_key = api_key
    prompt = f"""
You are a professional summarizer. Based on the following instructions and document text, write the section titled ''.

--- Instruction from Template ---
{section_instruction}

--- Document Text ---
{text}

Write the '{section_title}' section:
"""
    retry_delay = 2
    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message["content"].strip()
        except openai.error.RateLimitError:
            print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
        except Exception as e:
            print(f"An error occurred: {e}")
            return ""
    

def summarize_pdf_sections(pdf_path, api_key, instructions):
    logging.info("Starting PDF summarization...")
    summaries = {}
    source_text = extract_text_from_pdf(pdf_path)

    for section_name in instructions.keys():
        # instruction = instructions.get(section_name, "Summarize the following:")
        print(f"Processing section: {section_name}")

        summary = call_openai_summary(
            source_text,
            section_name,
            instructions[section_name],
            api_key,
        )

        summaries[section_name] = summary

        # Optional: throttle between requests
        time.sleep(2)  # Add delay to help with TPM limits
    return summaries
    logging.info("Summarization completed.")
    
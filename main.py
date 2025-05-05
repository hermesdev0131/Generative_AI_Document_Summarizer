import os
from summarizer import summarize_pdf_sections
from template_sections import extract_template_sections
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
# Set up OpenAI API key

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")
INPUT_DIR = "input_doc"
TEMPLATE_PATH = "template_doc/1759_Prospect Curator_Template.pdf"
OUTPUT_DIR = "output_doc"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Get summarization instructions from template
instructions = extract_template_sections(TEMPLATE_PATH)

for filename in os.listdir(INPUT_DIR):
    if filename.endswith(".pdf"):
        input_path = os.path.join(INPUT_DIR, filename)
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(OUTPUT_DIR, f"{base_name}_summary.txt")

        print(f"Processing... ")

        summaries = summarize_pdf_sections(input_path, OPENAI_API_KEY, instructions)

        with open(output_path, "w") as f:
            for section, summary in summaries.items():
                f.write(f"{section}:\n{summary}\n\n")

        print(f"Created: {output_path}")
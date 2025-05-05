import os
from summarizer import summarize_pdf_sections, summarize_doc_sections
from template_sections import extract_template_sections, create_template_sections
from dotenv import load_dotenv
#NEW
from docx import Document
#NEW
from docx.shared import RGBColor, Pt, Inches
#NEW
from docx.enum.text import WD_ALIGN_PARAGRAPH
# Load environment variables from .env file
load_dotenv()
# Set up OpenAI API key

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

current_dir = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DOC_PATH = os.path.join(current_dir, "template_doc", "template.docx")
INPUT_DIR = "input_doc"
TEMPLATE_PATH = "template_doc/1759_Prospect Curator_Template.pdf"
# TEMPLATE_DOC_PATH = 
OUTPUT_DIR = "output_doc"
if not os.path.exists(TEMPLATE_DOC_PATH):
    raise FileNotFoundError(f"Template file not found at '{TEMPLATE_DOC_PATH}'")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# NEW - This code allows us to either use PDF template or provide plaintext guidelines
USE_PDF_TEMPLATE = False  # Set to False to use plaintext templates

if USE_PDF_TEMPLATE:
    # Get summarization instructions from template PDF
    instructions = extract_template_sections(TEMPLATE_PATH)
else:
    # Example of using plaintext templates
    instructions = create_template_sections(TEMPLATE_DOC_PATH)

SECTION_ORDER = ["Prospect Curator", "Back of the Napkin", "The Pitch", "Rewards", "Client Needs", "The Elixir", "Insurance+", "Landmines", "Path to Close", "What Will Clients Ask?", "Sustain Success", "Look Ahead"]

def create_formatted_docx(summaries, output_path):
    doc = Document()
    
    # Set default paragraph spacing and font
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    style.paragraph_format.space_after = Pt(12)
    
    # Define section header style
    def add_section_header(text):
        header = doc.add_paragraph()
        header.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = header.add_run(text)
        run.bold = True
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(0, 51, 102)  # Dark blue color
        header.space_before = Pt(24)
        header.space_after = Pt(12)
        
    # Add each section
    for section in SECTION_ORDER:
        if section in summaries:
            add_section_header(section)
            
            # Add content with proper paragraph formatting
            paragraphs = summaries[section].split('\n\n')
            for i, p in enumerate(paragraphs):
                if p.strip():
                    content = doc.add_paragraph()
                    # Justify all paragraphs except the last one
                    if i < len(paragraphs) - 1:
                        content.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    else:
                        content.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    content.add_run(p.strip())
    
    # Save the document
    doc.save(output_path)


for filename in os.listdir(INPUT_DIR):
    if filename.endswith(".pdf"):
        input_path = os.path.join(INPUT_DIR, filename)
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(OUTPUT_DIR, f"{base_name}_summary.docx")

        print(f"Processing {filename}...")

        # Get summaries for all sections
        summaries = summarize_doc_sections(input_path, OPENAI_API_KEY, instructions)

        # NEW - Create formatted Word document
        create_formatted_docx(summaries, output_path)

        print(f"Created: {output_path}")
import openai
import pdfplumber
import time
import logging
import os
import gc
from llama_cpp import Llama
from openai import AzureOpenAI, OpenAIError
from LLamaChunkedSummarizer import LLamaChunkedSummarizer
from docx import Document

logging.basicConfig(level=logging.INFO)

# Extract text from PDF files
def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)
    
# Extract text from DOCX files
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)


# Llama model
def call_llama_summary(text, section_title, section_instruction, model_path):
    """Generate summary using Llama model"""

    summarizer = LLamaChunkedSummarizer(
        model_path=model_path
    )

    summary = summarizer.summarize(
        document_text = text,
        section_title = section_title,
        section_instruction = section_instruction
    )

    return summary   


# Azure OpenAI API
def call_azure_openai_summary(text, section_title, section_instruction, api_key, endpoint, deployment_name):
    """Generate summary using Azure OpenAI"""

    client = AzureOpenAI(
        api_version="2025-01-01-preview",
        azure_endpoint=endpoint,
        api_key=api_key,
    )

    prompt = f"""
You are a professional summarizer. Based on the following instructions and document text, write the section titled '{section_title}'.

--- Instruction from Template ---
{section_instruction}

--- Document Text ---
{text}

Write the '{section_title}' section:
"""
    
    retry_delay = 2

    try:

        while True:

            try:
                response = client.chat.completions.create(
                    stream=True,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    max_tokens=4096,
                    temperature=1.0,
                    top_p=1.0,
                    model=deployment_name,
                )
                return response.choices[0].message.content.strip()
            except OpenAIError as e:
                if "Rate limit" in str(e):
                    logging.warning(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logging.error(f"An error occurred with Azure OpenAI: {e}")
                    return ""
    finally:
        client.close()


# OpenAI API
def call_openai_summary(text, section_title, section_instruction, api_key):
    """Legacy OpenAI API support"""

    # openai.api_key = api_key

    client = openai.OpenAI(
        api_key=api_key
        # api_type="openai"
        )

    prompt = f"""
You are a professional summarizer. Based on the following instructions and document text, write the section titled '{section_title}'.

--- Instruction from Template ---
{section_instruction}

--- Document Text ---
{text}

Write the '{section_title}' section:
"""
    
    retry_delay = 2

    while True:

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if "rate limit" in str(e).lower():
                logging.warning(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logging.error(f"Error occurred in OpenAI inference: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff for other errors too
                if retry_delay > 32:  # Give up after a few retries
                    return ""
    

# Extract text from PDF or DOCX file if the file extension is not specified
def extract_text(file_path):
    """Extract text from either PDF or DOCX file based on file extension"""
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format: {file_path}")

def summarize_document(file_path, config, instructions):
    """
    Summarize document sections using the specified model (Llama, Azure OpenAI, or OpenAI)
    
    Args:
        file_path: Path to the document file
        config: Dictionary containing model configuration
        instructions: Dictionary of section instructions
    """
    """Summarize document (PDF or DOCX) sections"""
    
    file_ext = file_path.lower().split('.')[-1]
    logging.info(f"Starting {file_ext.upper()} summarization...")
    
    summaries = {}
    source_text = extract_text(file_path)

    model_type = config.get("model_type", "openai")  # Default to OpenAI if not specified

    for section_name in instructions.keys():
        logging.info(f"Processing section: {section_name}")

        if model_type == "llama":
            summary = call_llama_summary(
                source_text,
                section_name,
                instructions[section_name],
                config.get("model_path")
            )
        elif model_type == "azure":
            summary = call_azure_openai_summary(
                source_text,
                section_name,
                instructions[section_name],
                config.get("api_key"),
                config.get("endpoint"),
                config.get("deployment_name")
            )
        else:  # Default to OpenAI
            summary = call_openai_summary(
                source_text,
                section_name,
                instructions[section_name],
                config.get("api_key")
            )

        summaries[section_name] = summary

        # Optional: throttle between requests
        time.sleep(2)  # Add delay to help with TPM limits
    
    logging.info("Summarization completed.")
    return summaries
    
def summarize_doc_sections(doc_path, config, instructions):
    return summarize_document(doc_path, config, instructions)
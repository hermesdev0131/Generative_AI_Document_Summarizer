import openai
import pdfplumber
import time
import logging
import os
import gc
from llama_cpp import Llama
# from azure.identity import DefaultAzureCredential
# from azure.ai.ml import MLClient

logging.basicConfig(level=logging.INFO)

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def chunk_text(text, max_length=2000):
    """Chunk text into smaller parts to fit model context."""
    chunks = []
    while len(text) > max_length:
        # Cut the text into chunks of `max_length` characters
        chunk = text[:max_length]
        chunks.append(chunk)
        text = text[max_length:]
    if text:
        chunks.append(text)  # Add any remaining text
    return chunks

def call_llama_summary(text, section_title, section_instruction, model_path):
    """Generate summary using local Llama model."""
    max_text_length = 1500  # Reduced to ensure we stay well within context limits
    text_chunks = chunk_text(text, max_length=max_text_length)

    prompt_template = """
You are a professional summarizer. Based on the following instructions and document text, write the section titled '{section_title}'.

--- Instruction from Template ---
{section_instruction}

--- Document Text ---
{text}

Write the '{section_title}' section:
"""

    summaries = []
    
    # Process each chunk separately with a fresh model instance
    for chunk in text_chunks:
        prompt = prompt_template.format(
            section_title=section_title,
            section_instruction=section_instruction,
            text=chunk
        )

        try:
            # Create a new model instance for each chunk
            llm = Llama(
                model_path=model_path, 
                n_ctx=2048,  # Context size
                n_threads=2,  # Reduced thread count for stability
                n_batch=128,  # Reduced batch size
                f16_kv=True
            )
            
            # Generate response from Llama model
            response = llm(
                prompt, 
                max_tokens=500,  # Reduced max tokens
                temperature=0.7, 
                stop=["</s>", "\n\n\n"], 
                echo=False
            )
            
            summaries.append(response["choices"][0]["text"].strip())
            
            # Clean up immediately
            del llm
            gc.collect()
            
        except Exception as e:
            logging.error(f"Error with Llama model: {e}")
            summaries.append("[Error: Failed to generate summary]")
            # Ensure cleanup even on error
            if 'llm' in locals():
                del llm
            gc.collect()

        # Additional pause between chunks
        time.sleep(1)

    return "\n".join(summaries)

# def call_azure_openai_summary(text, section_title, section_instruction, api_key, endpoint, deployment_name):
#     """Generate summary using Azure OpenAI"""
#     openai.api_type = "azure"
#     openai.api_key = api_key
#     openai.api_base = endpoint
#     openai.api_version = "2023-05-15"  # Update to the latest API version
    
#     prompt = f"""
# You are a professional summarizer. Based on the following instructions and document text, write the section titled '{section_title}'.

# --- Instruction from Template ---
# {section_instruction}

# --- Document Text ---
# {text}

# Write the '{section_title}' section:
# """
#     retry_delay = 2
#     while True:
#         try:
#             response = openai.ChatCompletion.create(
#                 deployment_id=deployment_name,
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.7,
#                 max_tokens=1000
#             )
#             return response.choices[0].message["content"].strip()
#         except openai.error.RateLimitError:
#             logging.warning(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
#             time.sleep(retry_delay)
#             retry_delay *= 2  # Exponential backoff
#         except Exception as e:
#             logging.error(f"An error occurred with Azure OpenAI: {e}")
#             return ""

def call_openai_summary(text, section_title, section_instruction, api_key):
    """Legacy OpenAI API support"""
    openai.api_key = api_key
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
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message["content"].strip()
        except openai.error.RateLimitError:
            logging.warning(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
        except Exception as e:
            logging.error(f"An error occurred with OpenAI: {e}")
            return ""
    



def summarize_pdf_sections(pdf_path, config, instructions):
    """
    Summarize PDF sections using the specified model (Llama, Azure OpenAI, or OpenAI)
    
    Args:
        pdf_path: Path to the PDF file
        config: Dictionary containing model configuration
        instructions: Dictionary of section instructions
    """
    logging.info("Starting PDF summarization...")
    summaries = {}
    source_text = extract_text_from_pdf(pdf_path)
    model_type = config.get("model_type", "openai")  # Default to OpenAI if not specified

    for section_name in instructions.keys():
        print(f"Processing section: {section_name}")

        if model_type == "llama":
            summary = call_llama_summary(
                source_text,
                section_name,
                instructions[section_name],
                config.get("model_path")
            )
        # elif model_type == "azure":
        #     summary = call_azure_openai_summary(
        #         source_text,
        #         section_name,
        #         instructions[section_name],
        #         config.get("api_key"),
        #         config.get("endpoint"),
        #         config.get("deployment_name")
        #     )
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

def summarize_doc_sections(pdf_path, config, instructions):
    """
    Summarize document sections using the specified model (Llama, Azure OpenAI, or OpenAI)
    
    Args:
        pdf_path: Path to the document file
        config: Dictionary containing model configuration
        instructions: Dictionary of section instructions
    """
    logging.info("Starting DOC summarization...")
    summaries = {}
    source_text = extract_text_from_pdf(pdf_path)
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
        # elif model_type == "azure":
        #     summary = call_azure_openai_summary(
        #         source_text,
        #         section_name,
        #         instructions[section_name],
        #         config.get("api_key"),
        #         config.get("endpoint"),
        #         config.get("deployment_name")
        #     )
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
    
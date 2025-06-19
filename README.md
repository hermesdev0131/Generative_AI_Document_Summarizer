# Generative AI Document Summarizer

A tool for summarizing PDF documents using various AI models including OpenAI, Azure OpenAI, and Llama.

## Features

- Extract text from PDF documents
- Generate summaries using different AI models:
  - OpenAI (GPT-4)
  - Azure OpenAI
  - Llama (local model)
- Create formatted Word documents with the summaries
- Customizable section templates

## Installation

1. Clone the repository:
```bash
git clone https://github.com/hermesdev0131/Generative_AI_Document_Summarizer.git
cd Generative_AI_Document_Summarizer
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your environment variables by creating a `.env` file:
```
# Model type: "openai", "azure", or "llama"
MODEL_TYPE=openai

# OpenAI configuration (used when MODEL_TYPE=openai)
OPENAI_API_KEY=your_openai_api_key_here

# Azure OpenAI configuration (used when MODEL_TYPE=azure)
AZURE_OPENAI_API_KEY=your_azure_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name

# Llama configuration (used when MODEL_TYPE=llama)
LLAMA_MODEL_PATH=/path/to/your/models/model.gguf
```

## Usage

1. Place your PDF documents in the `input_doc` directory.

2. Run the main script:
```bash
python main.py
```

3. The summarized documents will be saved as Word files in the `output_doc` directory.

## Configuration

### Model Selection

You can choose between three different AI models by setting the `MODEL_TYPE` environment variable in your `.env` file:

- `openai`: Uses the OpenAI GPT-4 model
- `azure`: Uses Azure OpenAI services
- `llama`: Uses a local Llama model

### Template Customization

You can customize the template sections by modifying the `template_sections.py` file or by providing a template document in the `template_doc` directory.

## Requirements

- Python 3.8+
- Required packages (see requirements.txt)
- For Llama model: A compatible GGUF model file

## License

[MIT License](LICENSE)

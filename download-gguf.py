import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)
# === CONFIGURATION ===
# url = "https://huggingface.co/NoelJacob/Meta-Llama-3-8B-Instruct-Q4_K_M-GGUF/resolve/main/meta-llama-3-8b-instruct.Q4_K_M.gguf"
url = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
output_dir = "models"  # relative path to ./models
output_file = os.path.join(output_dir, "meta-llama-3-8b-instruct.Q4_K_M.gguf")

hf_token = os.getenv("HF_TOKEN")  # or set like: "hf_abc123..."

# === ENSURE OUTPUT DIR EXISTS ===
os.makedirs(output_dir, exist_ok=True)

# === DOWNLOAD LOGIC ===
headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}

with requests.get(url, headers=headers, stream=True) as r:
    r.raise_for_status()
    total_size = int(r.headers.get('content-length', 0))
    downloaded = 0
    chunk_size = 8192  # 8 KB

    print(f"📥 Downloading to: {output_file} ({total_size / 1e6:.2f} MB)")
    with open(output_file, 'wb') as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                done = int(50 * downloaded / total_size)
                print(f"\r[{'█' * done}{'.' * (50 - done)}] {downloaded / 1e6:.2f}/{total_size / 1e6:.2f} MB", end='')

print("\n✅ Download complete.")

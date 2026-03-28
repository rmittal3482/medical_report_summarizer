import io
import os
import pytesseract
import pdfplumber
from PIL import Image
from transformers import pipeline
from pdf2image import convert_from_bytes
from dotenv import load_dotenv
import torch 

# Load env variables (for the HF_TOKEN)
load_dotenv()

# --- Model Loading ---
print("Loading AI models...")

# Check if GPU is available, otherwise use CPU
device_to_use = 0 if torch.cuda.is_available() else -1
print(f"Using device: {'GPU' if device_to_use == 0 else 'CPU'}")


# 1. Load the Summarizer (Flan-T5)
# We use Flan-T5 because it handles header-heavy documents better than BART in our tests.
print("Loading summarization model (Flan-T5)...")
summarizer = pipeline(
    "summarization",
    model="google/flan-t5-base",
    device=device_to_use
)

# 2. Load multilingual translator (NLLB)
print("Loading multilingual translation model (NLLB)...")
translator = pipeline(
    "translation",
    model="facebook/nllb-200-distilled-600M",
    device=device_to_use
)

# 3. Language code mapping for NLLB
LANGUAGE_CODE_MAP = {
    "hi": "hin_Deva",    # Hindi
    "pa": "pan_Guru",    # Punjabi
    "bn": "ben_Beng",    # Bengali
    "mr": "mar_Deva",    # Marathi
    "ta": "tam_Taml",    # Tamil
    "te": "tel_Telu",    # Telugu
    "gu": "guj_Gujr",    # Gujarati
    "kn": "kan_Knda",    # Kannada
    "ml": "mal_Mlym",    # Malayalam
    "ur": "urd_Arab",    # Urdu
    "or": "ory_Orya",    # Odia
    "as": "asm_Beng",    # Assamese
}
ENGLISH_CODE = "eng_Latn"

print("Models loaded successfully.")
# -------------------------------------------


def extract_text_from_pdf(file_contents: bytes) -> str:
    """
    Extracts text from a PDF, handling both text-based and scanned (image-based) PDFs.
    """
    text = ""

    # 1. Try with pdfplumber (for digital PDFs)
    print("Attempting to read text with pdfplumber...")
    try:
        with io.BytesIO(file_contents) as pdf_file:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
    except Exception as e:
        print(f"pdfplumber failed: {e}. Trying OCR.")

    # 2. If no text found, use Tesseract OCR (for scanned PDFs)
    if not text.strip():
        print("No text found with pdfplumber, attempting OCR...")
        try:
            images = convert_from_bytes(file_contents)
            for i, img in enumerate(images):
                print(f"Reading page {i+1} with Tesseract...")
                text += pytesseract.image_to_string(img) + "\n"
        except Exception as e:
            print(f"Tesseract OCR failed: {e}")
            return "Error: Could not extract text from PDF."

    if not text.strip():
        return "Error: No text could be found in this document by either method."

    return text


def summarize_text(text: str) -> str:
    """
    Generates a simple summary of the extracted medical text using Flan-T5.
    Includes robust error handling for empty results.
    """
    if not text.strip():
        return "No text provided to summarize."

    # Truncate input to prevent memory crashes
    MAX_INPUT_CHARS = 5000 
    if len(text) > MAX_INPUT_CHARS:
        print(f"Input text is too long ({len(text)} chars), truncating to {MAX_INPUT_CHARS} chars.")
        text_to_summarize = text[:MAX_INPUT_CHARS]
    else:
        text_to_summarize = text

    if not text_to_summarize.strip():
        return "Error: Input text is effectively empty after processing."

    print("Generating summary...")

    try:
        # Generate Summary
        summary_result = summarizer(
            text_to_summarize,
            max_new_tokens=250, 
            min_length=50,      
            do_sample=False
        )

        # Check if result is valid
        if (isinstance(summary_result, list) and
                len(summary_result) > 0 and
                isinstance(summary_result[0], dict) and
                'summary_text' in summary_result[0]):
            
            summary_text = summary_result[0]['summary_text']
            if summary_text and summary_text.strip():
                 return summary_text
            else:
                print(f"Summarizer returned empty text.")
                return "Error: Summarization produced empty text."
        else:
            print(f"Summarizer returned invalid result: {summary_result}")
            return "Error: Summarization model did not produce any output."

    except IndexError as ie:
        print(f"IndexError during summarization: {ie}")
        return "Error: Summarization failed (index error)."
    except Exception as e:
        print(f"Unexpected exception during summarization: {type(e).__name__} - {e}")
        return "Error: An unexpected exception occurred during summarization."


def translate_text(text: str, lang_code: str) -> str:
    """
    Translates the text (summary) to the specified language using the NLLB model.
    """
    if not text or text.startswith("Error:") or not text.strip():
        return None

    target_lang_code = LANGUAGE_CODE_MAP.get(lang_code)

    if not target_lang_code:
        print(f"No NLLB language code found for input code: {lang_code}")
        return None

    print(f"Generating translation for: {target_lang_code}...")

    try:
        translation_result = translator(
            text,
            src_lang=ENGLISH_CODE,
            tgt_lang=target_lang_code,
            max_length=512
        )

        if (isinstance(translation_result, list) and
                len(translation_result) > 0 and
                'translation_text' in translation_result[0]):
            return translation_result[0]['translation_text']
        else:
            print(f"Translator returned unexpected result format: {translation_result}")
            return None

    except Exception as e:
        print(f"Exception during translation: {e}")
        return None
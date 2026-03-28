# medical_report_summarizer
Developed an AI-Powered Summarization API: Engineered a RESTful backend using FastAPI to automate the ingestion, text extraction, and summarization of complex medical reports.

Integrated Advanced NLP Models: Utilized Hugging Face Transformers and PyTorch to deploy Google’s Flan-T5 for abstractive text summarization and Facebook’s NLLB-200 for seamless translation into multiple regional languages.

Built a Robust Text Extraction Pipeline: Implemented a dual-method extraction system utilizing pdfplumber for digital PDFs and pytesseract (OCR) with pdf2image as a fallback for high-accuracy text retrieval from scanned documents.

Managed Persistent Data Storage: Designed and integrated a relational database schema using SQLAlchemy ORM to securely store extracted text, English summaries, and translated outputs.

Implemented Error Handling & Scalability: Incorporated input truncation and dynamic device mapping (CPU/GPU) to optimize memory usage and prevent model crashes during heavy processing loads.

import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import core_logic
from database import engine, Base, get_db

load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Medical Report Summarizer",
    description="Upload a medical report PDF and get a simple summary."
)

# CORS (Allow Frontend to talk to Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Medical Report Summarizer API."}

@app.post("/upload")
async def upload_report(
    db: Session = Depends(get_db),
    lang: str = Form("en"),
    file: UploadFile = File(...)
):
    try:
        contents = await file.read()

        # 1. Extract Text
        extracted_text = core_logic.extract_text_from_pdf(contents)
        if "Error:" in extracted_text:
            raise HTTPException(status_code=400, detail=extracted_text)

        # 2. Generate English Summary
        summary_en = core_logic.summarize_text(extracted_text)

        final_summary_to_return = summary_en
        translation_to_save = None

        # 3. Translate if requested
        if lang != "en":
            translated_summary = core_logic.translate_text(summary_en, lang)
            if translated_summary:
                final_summary_to_return = translated_summary
                translation_to_save = translated_summary
            else:
                 final_summary_to_return = summary_en + f"\n\n(Translation to '{lang}' failed.)"

        # 4. Save to Database
        new_report = models.Report(
            filename=file.filename,
            extracted_text=extracted_text,
            summary=summary_en,
            translation=translation_to_save
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        return {
            "id": new_report.id,
            "filename": new_report.filename,
            "summary": final_summary_to_return,
            "lang": lang
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
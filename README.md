# LiteEMR

LiteEMR is a lightweight Flask + SQLite web app for **patient registration** and **clinical record logging** (diseases, symptoms, and an approximate severity score), with **type-ahead suggestions** backed by a **hard-coded medical vocabulary** plus optional **BioBERT NER suggestions** via Hugging Face Transformers.

---

## Features

- Patient registry (name, DOB, gender, notes)
- Per-patient records (diseases, symptoms, timestamp)
- Automatic **severity scoring** (1–10) derived from matched diseases/symptoms
- Live suggestion endpoint:
  - Hard-coded disease/symptom lists (with synonyms + severity)
  - Optional BioBERT NER-based suggestions

---

## Tech Stack

- Python + Flask
- Flask-SQLAlchemy + SQLite (`medical.db`)
- Hugging Face Transformers `pipeline("ner")` using `dmis-lab/biobert-v1.1`
- Jinja2 templates (`templates/*.html`)

---


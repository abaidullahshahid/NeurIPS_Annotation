# NeurIPS Paper Annotation Project

This project automates the process of scraping and annotating NeurIPS research papers using Python and LLM APIs.

## 📂 Files in this Repository
- `scrap.py` - Scrapes NeurIPS papers and extracts metadata.
- `annotate.py` - Uses LLMs to classify papers into predefined categories.
- `output.csv` - Extracted metadata (title, abstract, PDF URL).
- `output_annotated.csv` - Final dataset with assigned labels.

## 🚀 How to Run the Code
1. **Install Dependencies**  
   ```sh
   pip install openai pandas requests concurrent.futures

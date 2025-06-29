# AutoExam

This project provides a simple pipeline to OCR PDF files, process the text with a large language model and store the results in a SQLite database. A small Tkinter GUI is included to run the workflow.

## Usage

1. Install dependencies:
   ```bash
   pip install easyocr pymupdf pandas tkinter
   ```
   If you want to use OpenAI API, also install `openai` and configure your API key.

2. Run the application:
   ```bash
   python -m src.gui
   ```

3. In the GUI select the folder containing PDF files and provide a system prompt for the language model. Click **Run Pipeline** to perform OCR and data processing. When finished you can export the aggregated data to a CSV file.

All intermediate data is stored in `data.db` in the project directory.


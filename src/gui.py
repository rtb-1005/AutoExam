import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

from .db_utils import get_db_connection, initialize_db
from .ocr_utils import scan_folder
from .ai_utils import call_large_model_api
from .data_processing import aggregate_data


def log(text_widget: scrolledtext.ScrolledText, message: str):
    text_widget.insert(tk.END, message + "\n")
    text_widget.see(tk.END)


def run_pipeline(folder: str, prompt: str, text_widget: scrolledtext.ScrolledText):
    conn = get_db_connection()
    initialize_db(conn)
    log(text_widget, f"Scanning {folder} for PDFs...")
    scan_folder(folder, conn)
    log(text_widget, "OCR finished. Calling large model...")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT pdf_file FROM ocr_results")
    pdf_files = [row['pdf_file'] for row in cursor.fetchall()]
    for pdf in pdf_files:
        cursor.execute("SELECT text FROM ocr_results WHERE pdf_file=? ORDER BY page", (pdf,))
        texts = [row['text'] for row in cursor.fetchall()]
        full_text = '\n'.join(texts)
        result = call_large_model_api(prompt, full_text)
        if result:
            cursor.execute(
                "INSERT INTO extracted_data(chinese, english, ppt_pages, description) VALUES (?,?,?,?)",
                (
                    result.get('chinese', ''),
                    result.get('english', ''),
                    result.get('ppt_pages', ''),
                    result.get('description', result.get('raw', '')),
                )
            )
    conn.commit()
    log(text_widget, "Large model processing finished. Aggregating data...")
    aggregate_data(conn)
    conn.close()
    log(text_widget, "Pipeline finished. You can now export CSV.")


def export_csv(path: str, text_widget: scrolledtext.ScrolledText):
    conn = get_db_connection()
    df = None
    try:
        df = pd.read_sql_query("SELECT * FROM aggregated_data", conn)
    except Exception as exc:
        messagebox.showerror("Error", f"Failed to read aggregated data: {exc}")
        return
    if df is not None:
        df.to_csv(path, index=False, encoding='utf-8-sig')
        log(text_widget, f"CSV exported to {path}")
    conn.close()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AutoExam Pipeline")
        self.geometry("600x400")
        tk.Label(self, text="PDF Folder:").pack(anchor='w')
        frame = tk.Frame(self)
        frame.pack(fill='x')
        self.folder_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.folder_var).pack(side='left', fill='x', expand=True)
        tk.Button(frame, text="Browse", command=self.browse_folder).pack(side='left')
        tk.Label(self, text="System Prompt:").pack(anchor='w', pady=(10, 0))
        self.prompt_text = scrolledtext.ScrolledText(self, height=5)
        self.prompt_text.pack(fill='both', expand=False)
        tk.Button(self, text="Run Pipeline", command=self.start_pipeline).pack(pady=5)
        tk.Button(self, text="Export CSV", command=self.save_csv).pack()
        self.log_widget = scrolledtext.ScrolledText(self, height=10)
        self.log_widget.pack(fill='both', expand=True, pady=(10, 0))

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def start_pipeline(self):
        folder = self.folder_var.get()
        if not os.path.isdir(folder):
            messagebox.showerror("Error", "Invalid folder")
            return
        prompt = self.prompt_text.get('1.0', tk.END).strip()
        if not prompt:
            messagebox.showerror("Error", "System prompt required")
            return
        self.log_widget.delete('1.0', tk.END)
        run_pipeline(folder, prompt, self.log_widget)

    def save_csv(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')])
        if path:
            export_csv(path, self.log_widget)


if __name__ == '__main__':
    App().mainloop()


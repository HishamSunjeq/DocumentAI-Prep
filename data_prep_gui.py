import os
import tkinter as tk
from tkinter import filedialog, scrolledtext
import threading
import contextlib
import io

from inspection_agent import process_data_folder
from OCR_Extractor import process_folder_with_ocr
from split_text_chunks import process_text_files_and_vectorize
from generate_qa import QAGenerator
from remove_metadata_fromjson import clean_json_files


class DataPrepGUI:
    def __init__(self, master):
        self.master = master
        master.title("Document AI Prep GUI")

        # Path variables with defaults
        self.data_dir_var = tk.StringVar(value="data")
        self.ocr_output_var = tk.StringVar(value="output/ocr_output")
        self.chunk_output_var = tk.StringVar(value="output/chunked_output")
        self.qa_output_var = tk.StringVar(value="output/qa_pairs")
        self.clean_output_var = tk.StringVar(value="output/cleaned_json_output")

        row = 0
        self._add_path_selector("Data Folder", self.data_dir_var, row); row += 1
        self._add_path_selector("OCR Output", self.ocr_output_var, row); row += 1
        self._add_path_selector("Chunk Output", self.chunk_output_var, row); row += 1
        self._add_path_selector("QA Output", self.qa_output_var, row); row += 1
        self._add_path_selector("Clean Output", self.clean_output_var, row); row += 1

        # Buttons for steps
        button_frame = tk.Frame(master)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        tk.Button(button_frame, text="Run All", command=lambda: self.run_in_thread(self.run_all)).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Step 1", command=lambda: self.run_in_thread(self.step1)).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Step 2", command=lambda: self.run_in_thread(self.step2)).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Step 3", command=lambda: self.run_in_thread(self.step3)).grid(row=0, column=3, padx=5)
        tk.Button(button_frame, text="Step 4", command=lambda: self.run_in_thread(self.step4)).grid(row=0, column=4, padx=5)
        tk.Button(button_frame, text="Step 5", command=lambda: self.run_in_thread(self.step5)).grid(row=0, column=5, padx=5)
        row += 1

        # Log area
        self.log = scrolledtext.ScrolledText(master, width=100, height=25)
        self.log.grid(row=row, column=0, columnspan=3, padx=5, pady=5)

    def _add_path_selector(self, label, var, row):
        tk.Label(self.master, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=2)
        entry = tk.Entry(self.master, textvariable=var, width=50)
        entry.grid(row=row, column=1, padx=5, pady=2)
        tk.Button(self.master, text="Browse", command=lambda: self._browse(var)).grid(row=row, column=2, padx=5, pady=2)

    def _browse(self, var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)

    def append_log(self, text):
        self.log.insert(tk.END, text)
        self.log.see(tk.END)

    def run_in_thread(self, target):
        threading.Thread(target=target, daemon=True).start()

    def execute(self, func, *args, **kwargs):
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
                func(*args, **kwargs)
        except Exception as e:
            buffer.write(f"Error: {e}\n")
        self.append_log(buffer.getvalue())

    # Step implementations
    def step1(self):
        self.append_log("\n=== Step 1: File Inspection ===\n")
        data = self.data_dir_var.get()
        metadata_out = os.path.join("output", "metadata")
        os.makedirs(metadata_out, exist_ok=True)
        self.execute(process_data_folder, data, metadata_out)
        self.append_log("Step 1 complete\n")

    def step2(self):
        self.append_log("\n=== Step 2: OCR Extraction ===\n")
        self.execute(process_folder_with_ocr, self.data_dir_var.get(), self.ocr_output_var.get())
        self.append_log("Step 2 complete\n")

    def step3(self):
        self.append_log("\n=== Step 3: Text Chunking ===\n")
        self.execute(process_text_files_and_vectorize, self.ocr_output_var.get(), self.chunk_output_var.get())
        self.append_log("Step 3 complete\n")

    def step4(self):
        self.append_log("\n=== Step 4: QA Generation ===\n")
        os.environ["QA_INPUT_FOLDER"] = self.chunk_output_var.get()
        os.environ["QA_OUTPUT_FOLDER"] = self.qa_output_var.get()
        def run_qa():
            generator = QAGenerator()
            if generator.test_ollama_connection():
                generator.process_all_files()
        self.execute(run_qa)
        self.append_log("Step 4 complete\n")

    def step5(self):
        self.append_log("\n=== Step 5: Clean JSON Output ===\n")
        self.execute(clean_json_files, self.qa_output_var.get(), self.clean_output_var.get())
        self.append_log("Step 5 complete\n")

    def run_all(self):
        for step in (self.step1, self.step2, self.step3, self.step4, self.step5):
            step()


def main():
    root = tk.Tk()
    app = DataPrepGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

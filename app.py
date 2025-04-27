from flask import Flask, render_template, request, redirect, url_for
import os
from PyPDF2 import PdfReader
from docx import Document
from pptx import Presentation
import openpyxl
import subprocess
import sys

# Supported file types
SUPPORTED_EXT = [".pdf", ".docx", ".pptx", ".txt", ".xlsx"]

app = Flask(__name__)

# Global index
file_index = {}

def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    text = ""
    try:
        if ext == ".pdf":
            reader = PdfReader(filepath)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif ext == ".docx":
            doc = Document(filepath)
            text = "\n".join([p.text for p in doc.paragraphs])
        elif ext == ".pptx":
            prs = Presentation(filepath)
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text += shape.text + "\n"
        elif ext == ".txt":
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
        elif ext == ".xlsx":
            wb = openpyxl.load_workbook(filepath, data_only=True)
            for sheet in wb.worksheets:
                for row in sheet.iter_rows(values_only=True):
                    text += " ".join([str(cell) for cell in row if cell]) + "\n"
    except Exception as e:
        print(f"Failed to read {filepath}: {e}")
    return text.lower()

def index_files(root_dir):
    index = {}
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            filepath = os.path.join(dirpath, file)
            if os.path.splitext(file)[1].lower() in SUPPORTED_EXT:
                print(f"Indexing: {filepath}")
                index[filepath] = extract_text(filepath)
    return index

def query_files(query, index):
    query = query.lower()
    results = []
    for path, content in index.items():
        if query in content:
            results.append(path)
    return results

def open_file(filepath):
    try:
        if os.name == 'nt':  # Windows
            os.startfile(filepath)
        elif os.name == 'posix':  # macOS/Linux
            subprocess.call(['open' if sys.platform == 'darwin' else 'xdg-open', filepath])
    except Exception as e:
        print(f"Error opening file: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    global file_index
    if request.method == "POST":
        folder = request.form.get("folder_path").strip()
        if os.path.isdir(folder):
            print("Indexing files...")
            file_index = index_files(folder)
            print(f"Indexed {len(file_index)} files.")
            return render_template("index.html", files=file_index.keys(), query_results=[], query="")

    return render_template("index.html", files=[], query_results=[], query="")

@app.route("/query", methods=["POST"])
def query():
    query_text = request.form.get("query").strip()
    results = query_files(query_text, file_index)
    return render_template("index.html", files=file_index.keys(), query_results=results, query=query_text)

@app.route("/open/<path:filepath>")
def open(filepath):
    open_file(filepath)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)

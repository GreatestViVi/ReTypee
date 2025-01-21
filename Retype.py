import tkinter as tk
from tkinter import filedialog
import pdfplumber
import pandas as pd
import os
import json
from PIL import Image, ImageTk
from itertools import cycle
import sys


# Function to get the correct path for resources / Функція для отримання правильного шляху до ресурсів

def resource_path(relative_path):
    """ Get the absolute path to the resource / Отримати абсолютний шлях до ресурсу. """
    try:
        base_path = sys._MEIPASS  # Path for PyInstaller / Шлях для PyInstaller
    except AttributeError:
        base_path = os.path.abspath(".")  # Path for development / Шлях для розробки
    return os.path.join(base_path, relative_path)
# Language settings save / Збереження мови
CONFIG_FILE = "config.json"

# Load or save language preference / Завантаження або збереження налаштувань мови
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get("language", "en")
    return "en"

def save_config(language):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"language": language}, f)

# Language dictionary / Перелік слів, словник мов
LANGUAGES = {
    "en": {
        "title": "ReType - PDF to CSV",
        "select_pdf": "Select PDF File",
        "no_pdf": "No PDF file selected",
        "select_output": "Select Output Directory",
        "no_output": "No output directory selected",
        "convert": "Convert PDF to CSV",
        "processing": "Processing",
        "success": "Tables extracted and saved as CSV files!",
        "no_tables": "No tables found in the PDF.",
        "warning_pdf": "Please select a PDF file first.",
        "warning_output": "Please select an output directory first.",
        "crafted": "Crafted with ❤ by ReType"
    },
    "uk": {
        "title": "ReType - PDF у CSV",
        "select_pdf": "Вибрати PDF файл",
        "no_pdf": "PDF файл не вибрано",
        "select_output": "Вибрати папку для збереження",
        "no_output": "Папку для збереження не вибрано",
        "convert": "Перетворити PDF у CSV",
        "processing": "Обробка",
        "success": "Таблиці успішно збережені у CSV файли!",
        "no_tables": "Таблиць у PDF не знайдено.",
        "warning_pdf": "Спочатку виберіть PDF файл.",
        "warning_output": "Спочатку виберіть папку для збереження.",
        "crafted": "Створено з ❤ у ReType"
    }
}

# Current language selection / Поточний вибір мови(налаштування зберігаються при перезаході)
current_language = load_config()

def translate(key):
    return LANGUAGES[current_language].get(key, key)

# Create a unique folder for output / Створення унікальної папкт для збереження

def create_unique_folder(base_dir, pdf_name):
    folder_name = os.path.splitext(os.path.basename(pdf_name))[0]
    folder_path = os.path.join(base_dir, folder_name)
    counter = 1

    while os.path.exists(folder_path):
        folder_path = os.path.join(base_dir, f"{folder_name} ({counter})")
        counter += 1

    os.makedirs(folder_path)
    return folder_path

# Extract tables from PDF / Витяг таблиць з PDF
def extract_tables_from_pdf(pdf_path, output_dir):
    try:
        output_folder = create_unique_folder(output_dir, pdf_path)

        with pdfplumber.open(pdf_path) as pdf:
            tables_extracted = False
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if tables:
                    for j, table in enumerate(tables):
                        df = pd.DataFrame(table[1:], columns=table[0])
                        output_file = os.path.join(output_folder, f"page_{i + 1}_table_{j + 1}.csv")
                        df.to_csv(output_file, index=False, encoding="utf-8-sig")
                        tables_extracted = True
            return tables_extracted
    except Exception as e:
        show_custom_message("Error", f"Failed to extract tables: {str(e)}", "#8B0000")
        return False

# Select PDF file / Вибір PDF файлу
def select_pdf():
    global selected_pdf_path
    selected_pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if selected_pdf_path:
        pdf_label.config(text=f"{translate('select_pdf')}: {os.path.basename(selected_pdf_path)}")

# Select output directory / Вибір папки для збереження
def select_output_dir():
    global selected_output_dir
    selected_output_dir = filedialog.askdirectory(title=translate("select_output"))
    if selected_output_dir:
        output_dir_label.config(text=f"{translate('select_output')}: {selected_output_dir}")

# Show custom message window / Відображення вікна з повідомленням
def show_custom_message(title, message, color):
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.geometry("400x200")
    popup.config(bg="#222222")
    popup.resizable(False, False)

    message_label = tk.Label(
        popup, text=message, font=("Verdana", 14), bg="#222222", fg=color, wraplength=350, justify="center"
    )
    message_label.pack(expand=True, pady=40)

    close_button = tk.Button(
        popup, text="OK", font=("Verdana", 12), bg="#444444", fg="#ffffff", relief="flat", command=popup.destroy
    )
    close_button.pack(pady=10)

# Process the PDF file / Обробка PDF файлу
def process_pdf():
    global selected_pdf_path, selected_output_dir

    if not selected_pdf_path:
        show_custom_message("Warning", translate("warning_pdf"), "#8B0000")
        return
    if not selected_output_dir:
        show_custom_message("Warning", translate("warning_output"), "#8B0000")
        return

    show_processing_animation()

    root.update()
    tables_found = extract_tables_from_pdf(selected_pdf_path, selected_output_dir)
    if tables_found:
        show_custom_message("Success", translate("success"), "#228B22")
        # Reset file and output selection / Скидання вибору файлу та папки
        selected_pdf_path = ""
        selected_output_dir = ""
        update_labels_after_reset()
    else:
        show_custom_message("Info", translate("no_tables"), "#8B0000")

    stop_processing_animation()

# Update labels after reset / Оновлення після скидання
def update_labels_after_reset():
    pdf_label.config(text=translate("no_pdf"))
    output_dir_label.config(text=translate("no_output"))

# Toggle language / Зміна мови
def toggle_language():
    global current_language
    current_language = "uk" if current_language == "en" else "en"
    save_config(current_language)
    update_language()

# Update UI language / Оновлення мови інтерфейсу
def update_language():
    title_label.config(text=translate("title"))
    pdf_button.config(text=translate("select_pdf"))
    output_dir_button.config(text=translate("select_output"))
    process_button.config(text=translate("convert"))
    footer_label.config(text=translate("crafted"))
    language_button.config(image=flag_ukraine if current_language == "en" else flag_uk)

# Load and resize flag image / Завантаження та зміна розміру зображення прапора
def load_and_resize_flag(relative_path, size=(30, 20)):
    absolute_path = resource_path(relative_path)  # Отримати абсолютний шлях
    img = Image.open(absolute_path)
    img = img.resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)

# Create GUI / Створення графічного інтерфейсу
def create_gui():
    global root, processing_label, pdf_label, output_dir_label, selected_pdf_path, selected_output_dir, title_label
    global process_button, pdf_button, output_dir_button, footer_label, language_button, flag_ukraine, flag_uk

    selected_pdf_path = ""
    selected_output_dir = ""

    root = tk.Tk()
    root.title("ReType")
    root.geometry("800x600")
    root.config(bg="#2c2c2c")
    root.resizable(False, False)

    # Load and resize flags / Завантаження та зміна розмір прапорів
    flag_ukraine = load_and_resize_flag("Flag_of_Ukraine.png")
    flag_uk = load_and_resize_flag("Flag_of_United_Kingdom.png")

    # Title Label / Заголовок
    title_label = tk.Label(root, text=translate("title"), font=("Verdana", 24, "bold"), bg="#2c2c2c", fg="#ffffff")
    title_label.pack(pady=20)

    # Language Toggle Button / Кнопка перемикання мови
    language_button = tk.Button(root, image=flag_ukraine if current_language == "en" else flag_uk, bg="#2c2c2c",
                                 borderwidth=0, command=toggle_language)
    language_button.place(x=760, y=10)

    # PDF Selection Button / Кнопка для вибору PDF
    pdf_button = tk.Button(root, text=translate("select_pdf"), font=("Verdana", 14), bg="#444444", fg="#ffffff", relief="flat",
                           command=select_pdf)
    pdf_button.pack(pady=10)
    pdf_label = tk.Label(root, text=translate("no_pdf"), font=("Verdana", 12), bg="#2c2c2c", fg="#999999")
    pdf_label.pack(pady=5)

    # Output Directory Selection Button / Кнопка для вибору папки
    output_dir_button = tk.Button(root, text=translate("select_output"), font=("Verdana", 14), bg="#444444", fg="#ffffff",
                                  relief="flat", command=select_output_dir)
    output_dir_button.pack(pady=10)
    output_dir_label = tk.Label(root, text=translate("no_output"), font=("Verdana", 12), bg="#2c2c2c", fg="#999999")
    output_dir_label.pack(pady=5)

    # Process Button / Кнопка обробки
    process_button = tk.Button(root, text=translate("convert"), font=("Verdana", 14), bg="#228B22", fg="#ffffff",
                               relief="flat", command=process_pdf)
    process_button.pack(pady=20)

    # Processing Animation / Анімація обробки
    processing_label = tk.Label(root, text="", font=("Verdana", 12), bg="#2c2c2c", fg="#ffffff")
    processing_label.pack(pady=10)

    # Footer
    footer_label = tk.Label(root, text=translate("crafted"), font=("Verdana", 10), bg="#2c2c2c", fg="#999999")
    footer_label.pack(side="bottom", pady=10)

    update_language()
    root.mainloop()

# Show processing animation / Показ анімації обробки
def show_processing_animation():
    animation_frames = ["|", "/", "-", "\\"]
    animation_cycle = cycle(animation_frames)

    def animate():
        processing_label.config(text=f"{translate('processing')} {next(animation_cycle)}")
        global animation_id
        animation_id = root.after(200, animate)

    animate()

# Stop processing animation / Зупинка анімації обробки
def stop_processing_animation():
    if 'animation_id' in globals():
        root.after_cancel(animation_id)
        processing_label.config(text="")

if __name__ == "__main__":
    create_gui()

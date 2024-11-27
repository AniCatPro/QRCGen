import qrcode
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import tempfile
import os
from decimal import Decimal
import tkinter as tk
from tkinter import filedialog, messagebox


def generate_qr_code(url, file_path):
    """Создает QR-код и сохраняет его как изображение."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img.save(file_path)


def trim_image(img_path):
    """Обрезает белые поля вокруг изображения QR-кода."""
    with Image.open(img_path) as img:
        img = img.convert("RGBA")
        bbox = img.getbbox()
        img_cropped = img.crop(bbox)
        return img_cropped


def save_trimmed_image(img, output_path):
    """Сохраняет обрезанное изображение QR-кода."""
    img.save(output_path)


def get_qr_position(page_width, page_height):
    """Определяет позицию QR-кода в зависимости от размеров страницы."""
    qr_width = qr_height = 0.7 * inch

    qr_x = 6
    qr_y = page_height - qr_height - 25

    return qr_x, qr_y


def add_qr_with_link_to_pdf(input_pdf, output_pdf, qr_code_path, url):
    """Добавляет QR-код в указанный PDF-файл и текст под QR-кодом с использованием шрифта GOST."""
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    temp_pdf_path = "qr_canvas.pdf"

    pdfmetrics.registerFont(TTFont('GOST', 'GOST_A.TTF'))

    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)

        c = canvas.Canvas(temp_pdf_path, pagesize=(width, height))

        cropped_qr_path = "cropped_qr.png"
        trimmed_img = trim_image(qr_code_path)
        save_trimmed_image(trimmed_img, cropped_qr_path)

        qr_x, qr_y = get_qr_position(width, height)
        c.drawImage(cropped_qr_path, qr_x, qr_y, width=0.7 * inch, height=0.7 * inch)
        c.linkURL(url, (qr_x, qr_y, qr_x + 0.7 * inch, qr_y + 0.7 * inch), relative=0)

        text = "проверка версии"
        c.setFont("GOST", 7)
        text_width = c.stringWidth(text, "GOST", 7)
        text_x = qr_x + (0.7 * inch - text_width) / 2
        space_below_qr = 0.05 * inch
        text_y = qr_y - space_below_qr - 7

        c.drawString(text_x, text_y, text)
        c.save()

        qr_page = PdfReader(temp_pdf_path).pages[0]
        page.merge_page(qr_page)
        writer.add_page(page)

    with open(output_pdf, "wb") as f:
        writer.write(f)


def process_pdf(input_pdf, url, output_folder):
    if not os.path.isfile(input_pdf):
        messagebox.showerror("Ошибка", f"Файл {input_pdf} не существует.")
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as qr_code_file:
        qr_code_path = qr_code_file.name

    try:
        generate_qr_code(url, qr_code_path)

        file_name = os.path.basename(input_pdf)
        file_name_without_ext, file_extension = os.path.splitext(file_name)
        output_pdf = os.path.join(output_folder, f"{file_name_without_ext}_with_qr{file_extension}")

        add_qr_with_link_to_pdf(input_pdf, output_pdf, qr_code_path, url)

        messagebox.showinfo("Успех", f"QR-код добавлен. Выходной файл: {output_pdf}")

    finally:
        if os.path.isfile(qr_code_path):
            os.remove(qr_code_path)
        temp_pdf_path = "qr_canvas.pdf"
        if os.path.isfile(temp_pdf_path):
            os.remove(temp_pdf_path)
        cropped_qr_path = "cropped_qr.png"
        if os.path.isfile(cropped_qr_path):
            os.remove(cropped_qr_path)


def select_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF файлы", "*.pdf")])
    if file_path:
        pdf_path_entry.delete(0, tk.END)
        pdf_path_entry.insert(0, file_path)


def select_output_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        output_folder_entry.delete(0, tk.END)
        output_folder_entry.insert(0, folder_path)


def on_submit():
    input_pdf = pdf_path_entry.get()
    url = url_entry.get()
    output_folder = output_folder_entry.get()

    if not input_pdf or not url or not output_folder:
        messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
        return

    process_pdf(input_pdf, url, output_folder)


# Создание GUI
root = tk.Tk()
root.title("Добавление QR-кода в PDF")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill=tk.BOTH, expand=True)

tk.Label(frame, text="Путь к PDF-файлу:").grid(row=0, column=0, sticky=tk.W, pady=5)
pdf_path_entry = tk.Entry(frame, width=50)
pdf_path_entry.grid(row=0, column=1, pady=5)
tk.Button(frame, text="Выбрать", command=select_pdf).grid(row=0, column=2, padx=5)

tk.Label(frame, text="Ссылка:").grid(row=1, column=0, sticky=tk.W, pady=5)
url_entry = tk.Entry(frame, width=50)
url_entry.grid(row=1, column=1, pady=5)

tk.Label(frame, text="Папка для сохранения:").grid(row=2, column=0, sticky=tk.W, pady=5)
output_folder_entry = tk.Entry(frame, width=50)
output_folder_entry.grid(row=2, column=1, pady=5)
tk.Button(frame, text="Выбрать", command=select_output_folder).grid(row=2, column=2, padx=5)

tk.Button(frame, text="Обработать", command=on_submit).grid(row=3, column=0, columnspan=3, pady=10)

root.mainloop()

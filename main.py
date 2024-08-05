import qrcode
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import tempfile
import os

def generate_qr_code(url, file_path):
    """Создает QR-код и сохраняет его как изображение."""
    qr = qrcode.make(url)
    qr.save(file_path)

def add_qr_with_link_to_pdf(input_pdf, output_pdf, qr_code_path, url):
    """Добавляет QR-код в указанный PDF-файл и текст под QR-кодом с использованием шрифта GOST."""
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Создание временного PDF с QR-кодом и текстом
    c = canvas.Canvas("qr_canvas.pdf", pagesize=letter)

    # Регистрация шрифта Arial
    pdfmetrics.registerFont(TTFont('GOST', 'GOST_A.TTF'))

    qr_width = qr_height = 0.8 * inch
    qr_x = letter[0] - qr_width - inch  # Позиция по x
    qr_y = inch  # Позиция по y

    # Рисуем QR-код на холсте
    c.drawImage(qr_code_path, qr_x, qr_y, width=qr_width, height=qr_height)
    c.linkURL(url, (qr_x, qr_y, qr_x + qr_width, qr_y + qr_height), relative=0)

    # Рисуем текст под QR-кодом
    text_x = qr_x
    text_y = qr_y - 0.5 * inch - 1  # Позиция текста чуть ниже QR-кода
    c.setFont("GOST", 8)  # Используем GOST для текста
    c.drawString(text_x, text_y, "проверка актуальной версии")

    c.save()

    qr_page = PdfReader("qr_canvas.pdf").pages[0]

    # Проход по страницам PDF и добавление QR-кода
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        page.merge_page(qr_page)
        writer.add_page(page)

    # Сохранение результата
    with open(output_pdf, "wb") as f:
        writer.write(f)

def main():
    # Ввод пути до PDF и ссылки
    input_pdf = input("Введите путь до PDF-файла: ").strip()
    url = input("Введите ссылку облачного хранилища: ").strip()

    if not os.path.isfile(input_pdf):
        print(f"Ошибка: Файл {input_pdf} не существует.")
        return

    # Генерация временного файла для QR-кода
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as qr_code_file:
        qr_code_path = qr_code_file.name

    try:
        generate_qr_code(url, qr_code_path)

        # Определение имени выходного файла
        file_name, file_extension = os.path.splitext(input_pdf)
        output_pdf = f"{file_name}_with_qr{file_extension}"

        add_qr_with_link_to_pdf(input_pdf, output_pdf, qr_code_path, url)

        print(f"QR-код добавлен. Выходной файл: {output_pdf}")

    finally:
        # Удаление временного файла QR-кода
        if os.path.isfile(qr_code_path):
            os.remove(qr_code_path)

        # Удаление временного PDF с QR-кодом
        temp_pdf_path = "qr_canvas.pdf"
        if os.path.isfile(temp_pdf_path):
            os.remove(temp_pdf_path)

if __name__ == "__main__":
    main()

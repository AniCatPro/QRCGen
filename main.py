import qrcode
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import tempfile
import os
from decimal import Decimal


def generate_qr_code(url, file_path):
    """Создает QR-код и сохраняет его как изображение."""
    qr = qrcode.make(url)
    qr.save(file_path)


def add_qr_with_link_to_pdf(input_pdf, output_pdf, qr_code_path, url):
    """Добавляет QR-код в указанный PDF-файл и текст под QR-кодом с использованием шрифта GOST."""
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Создание временного PDF с QR-кодом и текстом
    temp_pdf_path = "qr_canvas.pdf"

    # Регистрация шрифта
    pdfmetrics.registerFont(TTFont('GOST', 'GOST_A.TTF'))

    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        width = float(page.mediabox.width)  # Преобразование в float
        height = float(page.mediabox.height)  # Преобразование в float

        # Создание холста для текущей страницы
        c = canvas.Canvas(temp_pdf_path, pagesize=(width, height))

        # Установка размеров QR-кода
        qr_width = qr_height = 0.7 * inch
        qr_x = width - qr_width - inch  # Позиция по x
        qr_y = height - qr_height - inch  # Позиция по y

        # Рисуем QR-код на холсте
        c.drawImage(qr_code_path, qr_x, qr_y, width=qr_width, height=qr_height)
        c.linkURL(url, (qr_x, qr_y, qr_x + qr_width, qr_y + qr_height), relative=0)

        # Рисуем текст под QR-кодом
        text = "проверка версии"
        c.setFont("GOST", 7)  # Используем GOST для текста
        text_width = c.stringWidth(text, "GOST", 7)  # Измеряем ширину текста
        text_x = qr_x + (qr_width - text_width) / 2  # Центрируем по x относительно QR-кода

        # Расстояние между QR-кодом и текстом
        space_below_qr = 0.005 * inch  # Например, 0.2 дюйма ниже QR-кода
        text_y = qr_y - space_below_qr - 8  # Позиция текста ниже QR-кода. Высота шрифта 8

        c.drawString(text_x, text_y, text)

        c.save()

        # Добавление QR-кода и текста на страницу PDF
        qr_page = PdfReader(temp_pdf_path).pages[0]
        page.merge_page(qr_page)
        writer.add_page(page)

    # Сохранение результата
    with open(output_pdf, "wb") as f:
        writer.write(f)


def main():
    # Ввод пути до PDF и ссылки
    input_pdf = input("Введите путь до PDF-файла: ").strip()
    url = input("Введите ссылку на файл в облачном хранилище: ").strip()

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

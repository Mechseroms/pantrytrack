import pymupdf
import os
import PIL

def create_pdf_preview(pdf_path, output_path, size=(600, 400)):
    pdf = pymupdf.open(pdf_path)
    page = pdf[0]
    file_name = os.path.basename(pdf_path).replace('.pdf', "")
    pix = page.get_pixmap()
    img = PIL.Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    output_path = output_path + file_name + '.jpg'
    img.thumbnail(size)
    img.save(output_path)
    return file_name + '.jpg'
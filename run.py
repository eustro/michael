# coding=utf-8


from utility import walk_dir
from image_process import process_pdf_stack
from image_process import process_image_stack
from ocr import ocr_on_image_stack
from chronicle import process_chronicle


in_dir = "/Users/eugenstroh/Desktop/michael_the_syrian_1/"
out_dir = in_dir


def main():
    if not in_dir:
        return False

    pdf_stack = process_pdf_stack(in_dir, out_dir)

    if not pdf_stack:
        return False

    image_stack = process_image_stack(in_dir)

    if not image_stack:
        return False

    chronicle = process_chronicle(in_dir)

    if not chronicle:
        return False

    ocr = ocr_on_image_stack(in_dir)

    if not ocr:
        return False


if __name__ == '__main__':
    main()

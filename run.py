# coding=utf-8

import argparse
import logging

from app.chronicle_processor import ChronicleProcessor
from app.image_processor import ImageProcessor
from app.ocr_processor import OCRProcessor
from app.pdf_processor import PDFProcessor
from app.pos_processor import POSProcessor

from app.config import Config

parser = argparse.ArgumentParser(prog='PDFCrop')
parser.add_argument('--dump_conf', help='Dump default config as json files.', action='store_true')
parser.add_argument('inp', help='Specify input directory.')
parser.add_argument('out', help='Specify output directory.')
parser.add_argument('--lang', help='Specify language to use for OCR and POS tagging.')
parser.add_argument('--config_dir', help='Specify configuration files, if you have some custom ones.')
parser.add_argument('--image_type', help='Type of image you want to process.')
parser.add_argument('--dpi', help='DPI for image converting.', action="store_true")
parser.add_argument('--pdf', help='Process pdf files, if not already done.', action="store_true")
parser.add_argument('--image', help='Process image files from pdf files.', action="store_true")
parser.add_argument('--chronicle', help='Process chronicle of Michael the Syrian.', action="store_true")
parser.add_argument('--ocr', help='Run Google Tesseract OCR on data.', action='store_true')
parser.add_argument('--nlp', help='Run NLP operations on data', action='store_true')
parser.add_argument('--pos', help='Run POS tagging on data.', action='store_true')
parser.add_argument('--draw', help='Run matplotlib to show calculations', action='store_true')

process_order = ('pdf', 'image', 'chronicle', 'ocr', 'nlp', 'draw')

args = parser.parse_args()


def main():
    conf = Config(args.inp, args.out)

    if args.config_dir:
        conf.config_dir = args.config_dir
    if args.image_type:
        conf.immage_type = args.image_type
    if args.dpi:
        conf.pdf_dpi = args.dpi
    if args.dump_conf:
        conf.dump_conf = args.dump_conf

    if args.pdf:
        pdf_processor = PDFProcessor(conf)
    else:
        pdf_processor = None

    if args.image:
        image_processor = ImageProcessor(conf)
    else:
        image_processor = None

    if args.chronicle:
        order_chronicle = ChronicleProcessor(conf)
    else:
        order_chronicle = None

    if args.ocr:
        ocr_processor = OCRProcessor(conf)
    else:
        ocr_processor = None

    if args.pos:
        pos_processor = POSProcessor(conf)
    else:
        pos_processor = None

    if args.nlp:
        pass

    if args.draw:
        pass

    ops = (pdf_processor,
           image_processor,
           order_chronicle,
           ocr_processor,
           pos_processor)

    for o in ops:
        if o:
            try:
                o.run()
            except Exception as e:
                logging.error(e)
                continue


if __name__ == '__main__':
    main()

# coding=utf-8

import argparse
import sys

from chronicle_processor import ChronicleProcessor
from image_processor import ImageProcessor
from ocr_processor import OCRProcessor
from pdf_processor import PDFProcessor

from app.config import Config

parser = argparse.ArgumentParser(prog='PDFCrop')
parser.add_argument('--dump_conf', help='Dump default config as json files.', action='store_true')
parser.add_argument('inp', help='Specify input directory.')
parser.add_argument('out', help='Specify output directory.')
parser.add_argument('--config_dir', help='Specify configuration files, if you have some custom ones.')
parser.add_argument('--image_type', help='Type of image you want to process.')
parser.add_argument('--dpi', help='DPI for image converting.', action="store_true")
parser.add_argument('--pdf', help='Process pdf files, if not already done.', action="store_true")
parser.add_argument('--image', help='Process image files from pdf files.', action="store_true")
parser.add_argument('--chronicle', help='Process chronicle of Michael the Syrian.', action="store_true")
parser.add_argument('--ocr', help='Run Google Tesseract OCR on data.', action='store_true')
parser.add_argument('--nlp', help='Run nlp operations on data', action='store_true')
parser.add_argument('--draw', help='Run matplotlib to show calculations', action='store_true')

process_order = ('pdf', 'image', 'chronicle', 'ocr', 'nlp', 'draw')

args = parser.parse_args()


def dump_config_files():
    if args.config_dir:
        conf = Config(args.inp, args.out, config_dir=args.config_dir, dump_conf=True)
    else:
        conf = Config(args.inp, args.out, dump_conf=True)
    # Dump config files
    sys.exit(0)


def main():
    if args.dump_conf:
        dump_config_files()

    conf = Config(args.inp, args.out)

    if args.config_dir:
        conf.config_dir = args.config_dir
    if args.image_type:
        conf.immage_type = args.image_type
    if args.dpi:
        conf.pdf_dpi = args.dpi

    if args.pdf:
        pdf_proccessor = PDFProcessor(conf)
    else:
        pdf_proccessor = None

    if args.image:
        image_proccessor = ImageProcessor(conf)
    else:
        image_proccessor = None

    if args.chronicle:
        order_chronicle = ChronicleProcessor(conf)
    else:
        order_chronicle = None

    if args.ocr:
        ocr_processor = OCRProcessor(conf)
    else:
        ocr_processor = None

    if args.nlp:
        pass

    if args.draw:
        pass

    ops = (pdf_proccessor, image_proccessor, order_chronicle, ocr_processor)

    for o in ops:
        if o:
            o.run()


if __name__ == '__main__':
    main()

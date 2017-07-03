# coding=utf-8

import argparse


parser = argparse.ArgumentParser(prog='PDFCrop')

# Required positional arguments
parser.add_argument('input_dir', help='Specify input directory.')
parser.add_argument('output_dir', help='Specify output directory.')
parser.add_argument('language', help='Specify language to use for OCR and POS tagging.')
parser.add_argument('image_type', help='Type of image you want to process.')
parser.add_argument('dpi', help='DPI for image converting.')

# At least one of the arguments is required.
parser.add_argument('--pdf', help='Process pdf files, if not already done.', action="store_true")
parser.add_argument('--image', help='Process image files from pdf files.', action="store_true")
parser.add_argument('--chronicle', help='Process chronicle of Michael the Syrian.', action="store_true")
parser.add_argument('--ocr', help='Run Google Tesseract OCR on data.', action='store_true')
parser.add_argument('--pos', help='Run POS tagging on data.', action='store_true')
parser.add_argument('--verbose', help='Print computation progress.', action='store_true')

# Optional
parser.add_argument('--conf_dir', help='Specify configuration files directory, if you have some custom ones.')
parser.add_argument('--dump_conf', help='Dump default config as json files.', action='store_true')

process_order = ('pdf', 'image', 'chronicle', 'ocr', 'pos')

args = parser.parse_args()


def main():
    from app.chronicle_processor import ChronicleProcessor
    from app.layout_processor import ImageProcessor
    from app.ocr_processor import OCRProcessor
    from app.pdf_processor import PDFProcessor
    from app.pos_processor import POSProcessor
    from app.config import Config

    conf = Config(in_dir=args.input_dir,
                  out_dir=args.output_dir,
                  lang=args.language,
                  dpi=args.dpi,
                  image_type=args.image_type)

    if args.conf_dir:
        conf.conf_dir = args.conf_dir
    if args.image_type:
        conf.immage_type = args.image_type
    if args.dpi:
        conf.pdf_dpi = args.dpi
    if args.verbose:
        conf.verbose = True
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

    ops = (pdf_processor,
           image_processor,
           order_chronicle,
           ocr_processor,
           pos_processor)

    if not any(ops):
        print('You must specify at least one of the following: pdf, image, chronicle, ocr or pos!')
        exit(0)

    for o in ops:
        if o:
            try:
                o.run()
            except Exception as e:
                print("Could not run {0}: {1}".format(repr(o), repr(e)))
                continue


if __name__ == '__main__':
    main()

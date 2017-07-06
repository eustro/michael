#Layout Analysis for printed documents
This repository is a byproduct of a BA-thesis in history. It was written to perform a layout anlysis of the French translation of the chronicle of Michael the Syrian by Jeean-Baptiste Chabot.  
This is a simple command line tool that can perform a layout analysis on a stack of images. There is an optional part that can convert a multipage PDF into single page images to process them further. After that a layout analysis will be performed where all found parts of the page layout will be saved in a separate image file. After that an OCR based on Google Tesseract can be performed.  
There is also a special module that was written to assign paarts of the layout to logical parts in the chronicle which is very specific to the chronicle so that it can be used elsewhere.
Above that, the tool contains a POS tagging module where each text file of each component can be lemmatised.

##1. Prerequisites
The tool was written in Python and tested with interpreter version 3.5.2. You will need to install a 3.5.X version of the interpreter.  

Also, you should consider to work with a virtual environment for Python: [Virtualenv wiki](https://virtualenv.pypa.io/en/stable/installation/).  

If you want to convert a multipage PDF for processing its layout, you also have to install Ghostscript: [Ghostscript wiki](https://ghostscript.com/doc/9.21/Install.htm). You also can do this externally, if you want to. 

For the OCR module you would need to install the tesseract-ocr: [Tesseract wiki](https://github.com/tesseract-ocr/tesseract/wiki). You don't need this however, if you do not intend to use it.  

Note that the tool also will work an Windows host, but you would need to install numpy module. In order to do so, you would also need to compile and install lablas and lapack for Windows together with a Fortran compiler.  

##2. Getting started
To get started clone this repository:  
```
$ git clone https://github.com/eustro/michael
```
Then get into the cloned repository and install al dependencies:  
```
$ virtualenv venv
$ source venv/bin/activate
$ (venv) pip install -r requirements.txt
```
Note that you maybe need to specify the Python interpreter binaries in order to get the right version of Python:  
```
$ virtualenv --python=/path/to/binaries/Python3.5/python3.5 venv
```
After successfully installing all prerequisites and dependencies you can try the tool out:
```
$ (venv) python run.py --help

positional arguments:
  input_dir            Specify input directory.
  output_dir           Specify output directory.
  language             Specify language to use for OCR and POS tagging.
  image_type           Type of image you want to process.
  dpi                  DPI for image converting.

optional arguments:
  -h, --help           show this help message and exit
  --pdf                Process pdf files, if not already done.
  --image              Process image files from pdf files.
  --chronicle          Process chronicle of Michael the Syrian.
  --ocr                Run Google Tesseract OCR on data.
  --pos                Run POS tagging on data.
  --verbose            Print computation progress.
  --conf_dir CONF_DIR  Specify configuration files directory, if you have some
                       custom ones.
  --dump_conf          Dump default config as json files.
```

All the positional arguments above are required. So the minimum input for the layout anlysis would be:  
```
$ (venv) python run.py --image /input_dir/test /input_dir/test fra png 600
```
I also recommend to set the verbosity option to see how the procession is proceeding:
```
$ (venv) python run.py --image --verbose /input_dir/test /input_dir/test fra png 600
```
Note that the computation will need some time to complete, depending on number of pages and resolution. The algorithm will check every pixel, so be not surprised if this takes some time.  

##3. Parameters
There are a few preset parameters to get the tool to work. The most important ones are the layout analysis parameters:  
```python
        params = {'black_value': 0.1,
                  'white_value': 0.9,

                  'min_white_lines': 0.008,
                  'min_crop_ratio': 11.0,
                  'max_distance': 1.0,
                  'density_filter': 0.008 * dim_2,

                  'correction_upper': -20,
                  'correction_lower': +10,
                  'correction_left': -20,
                  'correction_right': +20,

                  'vertical_margin': int(0.01 * float(dim_2)),
                  'horizontal_margin': int(0.01 * float(dim_1))}

        params['min_white_lines'] *= max(dim_1, dim_2)
```
The most important ones are ```min_white_lines```, ```max_distance``` and ```density_filter```:
1. *min_white_lines*: Indicator of how large the white space between two layout components can be as a minimum.
2. *max_distance*: The distance between black pixels. The shorter the distance, the greater the probability that we are dealing with text here. Increase this parameter, if characters in a line are widely spread.
3. *density_filter*: This value describers how many black pixels at least should be considered as noise, i. e. not considered at all. Try to increase that value in case the image is very noisy. Decrease it, if text lines are very short, one word or maybe only some characters.  

In dependence of the text and dataset you want to analyse you probably would need to adjust those parameters. You can dump those into a json file via command line. After that you can adjust all parameters you want to and start the analysis. The tool will read in the configuration from the files.  

##4. The layout algorithm
The layout detection algorithm is a simplified version of a whitespace algorithm. It considers whitespaces between lines and text boxes as a generic delimiter. Thus a detection of the maximum white boarders between text boxes also yields the bounding boxes of a layout component.  
Check **Thomas M. Breuel**, *Two Geometric Algorithms for Layout Analysis* for further reading.

##5. Troubleshooting
If you encounter problem or inaccuracies with using the layout detection, there are some parameters that you can try to change in order to get better results:  
1. **The algorithm produces the input page as output**:  
Two could have three reasons. The first reason ist that the number of **max_cuts** (vertical or horizontal) are to low. The second is, that min_white_lines is set to high. The **density_filter** could also be set to high. Try to decrease the wo latter values.
2. **The algorithm produces to many cuts**:
This is the opposite case of *1.*. Try to increase the **min_white_lines** and the **density_filter**. As second step also try to decrease **max_cuts** (horizontal or vertical).

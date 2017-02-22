# coding=utf-8


from os.path import dirname
from os.path import exists
from os.path import join
from os.path import realpath

from utility import json_to_obj
from utility import obj_to_json


class Config:
    """
    Class holds all config files for the application.

    All configurations are specified in a json file.
    If there is no json file, default configurations are used.
    """

    config_file_names = {'params_text_box': 'params_text_box.json',
                         'params_text_cut': 'params_text_cut.json',
                         'params_ocr': 'params_ocr.json',
                         'params_tagger': 'params_tagger.json',
                         'params_chronicle': 'params_chronicle.json'}

    def __init__(self,
                 config_dir=dirname(realpath(__file__)),
                 resolution=None):
        """
        Constructor initializes Config.

        If there are no json config files, default values are used.
        If default values are used, they are exported as json config files.
        All module use this class for configuration.
        """
        self.config_dir = config_dir
        self.resolution = resolution
        self.config_files = self.read_config_files()

        self.params_text_box = self.set_params_text_box(resolution)
        self.params_text_cut = self.set_params_text_cut()
        self.params_ocr = self.set_params_ocr()
        self.params_chronicle = self.set_params_chronicle()

    def read_config_files(self) -> dict:
        """
        Function sets json config files.

        JSON files are read to a dictionary and stored within Config class.
        If a config file is not found, file set to none.
        """
        config_dicts = {'params_text_box': None,
                        'params_text_cut': None,
                        'params_ocr': None,
                        'params_tagger': None,
                        'params_chronicle': None}

        for key in config_dicts:
            if key not in Config.config_file_names:
                continue
            json_path = join(self.config_dir, Config.config_file_names[key])
            obj = json_to_obj(json_path)
            if obj:
                config_dicts[key] = obj

        return config_dicts

    def set_params_text_box(self, resolution: tuple, default_dim=(1200, 1600)) -> dict:
        """
        Function sets params for text box recognition.

        If json config not found, default values are used.
        """
        if self.config_files['params_text_box']:
            return self.config_files['params_text_box']

        if resolution:
            dim_1, dim_2 = resolution
        else:
            dim_1, dim_2 = 1200, 1600
        # Reference resolution of 150 dpi.
        # Resolution lower than that yields inaccurate results.
        def_dim_1, def_dim_2 = default_dim

        params = {'black_value': 0.1,
                  'white_value': 0.9,

                  'min_black_pixels': 0.00625 * min(dim_1, dim_2) + 5,
                  'min_white_pixels': min(dim_1, dim_2),
                  'min_white_lines': 0.006,
                  'min_black_lines': 0.001875,
                  'min_crop_ratio': 9.0,

                  'correction_upper': -10,
                  'correction_lower': -5,
                  'correction_left': -15,
                  'correction_right': +15,

                  'vertical_margin': int(0.01 * float(dim_2)),
                  'horizontal_margin': int(0.01 * float(dim_1))}

        params['min_white_lines'] *= max(dim_1, dim_2)

        params['min_black_lines'] *= max(dim_1, dim_2)

        if params['horizontal_margin'] > 0:
            params['min_white_pixels'] -= 2 * params['horizontal_margin']

        if dim_1 + dim_2 > def_dim_1 + def_dim_2:
            ratio = float(dim_1 + dim_2) / float(def_dim_1 + def_dim_2)
            params['correction_upper'] *= ratio
            params['correction_lower'] *= ratio
            params['correction_left'] *= ratio
            params['correction_right'] *= ratio

        if not self.config_files['params_text_box']:
            obj_to_json(self.config_dir,
                        Config.config_file_names['params_text_box'],
                        params)

        return params

    def set_params_text_cut(self) -> dict:
        """
        Function sets params for text cuts after text box recognition.

        If json config not found, default values are used.
        """
        if self.config_files['params_text_cut']:
            return self.config_files['params_text_cut']

        params = {'filter_small_hor': 0.035,
                  'filter_small_ver': 0.15,
                  'max_no_of_hor_cuts': 10,
                  'max_no_of_ver_cuts': 2}

        if not self.config_files['params_text_cut']:
            obj_to_json(self.config_dir,
                        Config.config_file_names['params_text_cut'],
                        params)

        return params

    def set_params_ocr(self) -> dict:
        """
        Function sets params for tesseract ocr after text box cuts.

        If json config not found, default values are used.
        """
        if self.config_files['params_ocr']:
            return self.config_files['params_ocr']

        params = {'tess_dir': '/opt/local/share',
                  'lan': 'fra',
                  'page_mode': 3}

        if not self.config_files['params_ocr']:
            obj_to_json(self.config_dir,
                        Config.config_file_names['params_ocr'],
                        params)

        return params

    def set_params_chronicle(self):
        if self.config_files['params_chronicle']:
            return self.config_files['params_chronicle']

        params = {'width_ratio': 0.5,
                  # DIN A4 PDF page.
                  'length_res': 0,
                  'width_res': 1,
                  # Regular pages with 4 major parts.
                  'parts_4': 4,
                  'parts_5': 5,
                  # Upper part
                  'political': 1,
                  # Left column
                  'eccles': 2,
                  # Right column
                  'secular': 3,
                  # Lower part
                  'footnotes': 4}

        if not self.config_files['params_chronicle']:
            obj_to_json(self.config_dir,
                        Config.config_file_names['params_chronicle'],
                        params)

        return params

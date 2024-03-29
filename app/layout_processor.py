# coding=utf-8


"""
Module provides optical text box recognition in image files.
"""

import logging
from os.path import basename
from os.path import exists
from os.path import join

import numpy as np
from skimage import io

from .util import clear_dir
from .util import list_sub_dirs
from .util import walk_dir

from app.config import Config


class ImageProcessor:
    def __init__(self, conf):
        if not isinstance(conf, Config) or not conf:
            raise TypeError('Need instance of Config class!')
        self.conf = conf

    def __detect_text_boxes(self, image: np.ndarray, vertical=False) -> list:
        from math import floor
        from skimage.transform import rotate
        if image.ndim > 2 or 0 in image.shape:
            return []

        params = self.conf.set_params_text_box(image.shape)

        dim1, dim2 = image.shape

        if vertical and max(dim1, dim2) / min(dim1, dim2) > params['min_crop_ratio']:
            return []

        if vertical:
            image_copy = rotate(image, 270, resize=True)
        else:
            image_copy = image

        dim1, dim2 = image_copy.shape
        
        state_in, state_out = False, True

        curr_white_lines = 0

        cut_positions = []

        for row in range(params['vertical_margin'], dim1 - params['vertical_margin']):
            black_pixels_read = []
            for col in range(params['horizontal_margin'], dim2 - params['horizontal_margin']):
                if state_in:
                    if image_copy[row, col] <= params['black_value']:
                        black_pixels_read.append(col)

                    if col == (dim2 - params['horizontal_margin'] - 1):

                        if self.__black_pixels_are_dense(black_pixels_read,
                                                         params['max_distance'],
                                                         params['density_filter']):
                            curr_white_lines = 0
                        else:
                            curr_white_lines += 1

                        if curr_white_lines >= params['min_white_lines']:
                            curr_white_lines = 0
                            state_out, state_in = True, False
                            entry_p = cut_positions[-1][0]
                            exit_p = row
                            if vertical:
                                cut_positions[-1] = (floor(entry_p + params['correction_left']),
                                                     floor(exit_p + params['correction_right']))
                            else:
                                cut_positions[-1] = (floor(entry_p + params['correction_upper']),
                                                     floor(exit_p + params['correction_lower']))
                            break
                        else:
                            continue

                elif state_out:
                    if image_copy[row, col] <= params['black_value']:
                        black_pixels_read.append(col)
                    if col == (dim2 - params['horizontal_margin'] - 1):
                        if self.__black_pixels_are_dense(black_pixels_read,
                                                         params['max_distance'],
                                                         params['density_filter']):
                            state_in, state_out = True, False
                            entry_point = row
                            cut_positions.append((entry_point, None))

        cut_positions[:] = [pos for pos in cut_positions if None not in pos]

        return cut_positions

    @staticmethod
    def __black_pixels_are_dense(black_pixels: list, max_distance: float, density_filter: int):
        from math import log
        from math import floor
        from math import ceil

        if not black_pixels:
            return False

        if len(black_pixels) < density_filter:
            return False

        distances = []
        black_pixels = black_pixels[::-1]

        for i in range(len(black_pixels) - 1):
            distances.append(log(black_pixels[i] - black_pixels[i + 1]))

        average = sum(distances) / len(black_pixels)
        if floor(average) <= ceil(max_distance):
            return True
        else:
            return False

    def __cut_text_from_image(self, image: np.ndarray) -> list:
        params = self.conf.params_text_cut

        text_images = []

        horizontal_cuts = self.__detect_text_boxes(image)

        # If not boxes detected, leave image as it is.
        if not horizontal_cuts:
            return [image]

        # If too many cuts detected, leave image as it is.
        if len(horizontal_cuts) > params['max_no_of_hor_cuts']:
            return [image]

        # If any reasonable cuts detected, crop image.
        for hor_cut in horizontal_cuts:

            x_in, x_out = hor_cut

            x_in = int(x_in)
            x_out = int(x_out)

            # If crops too small, don't cut.
            if abs(x_out - x_in) < image.shape[0] * params['filter_small_hor']:
                continue

            # Cut image.
            horizontal_image = image[x_in:x_out][:]
            # Now see, if any vertical cuts can be made.
            vertical_cuts = self.__detect_text_boxes(horizontal_image, vertical=True)

            # If no vertical cuts detected, use horizontal cuts.
            if not vertical_cuts:
                text_images.append(horizontal_image)
                continue

            # If too many cuts detected, don't do anything.
            if len(vertical_cuts) > params['max_no_of_ver_cuts']:
                text_images.append(horizontal_image)
                continue

            # Process vertical cuts.
            for ver_cut in vertical_cuts:

                y_in, y_out = ver_cut

                y_in = int(y_in)
                y_out = int(y_out)

                if abs(y_out - y_in) < image.shape[1] * params['filter_small_ver']:
                    # text_images.append(horizontal_image)
                    break

                vertical_image = horizontal_image[:, y_in:y_out]

                text_images.append(vertical_image)

        return text_images

    def __save_text_box(self, image: np.ndarray, out_dir: str, file_name: str) -> bool:
        # If not enough axes or empty slice, break.
        if (image.ndim < 2) or (0 in image.shape):
            return False
        if not exists(out_dir):
            return False
        if not out_dir.endswith('/'):
            out_dir += '/'
        path = join(out_dir, file_name)
        try:
            io.imsave(path, image)
            return True
        except IOError as e:
            logging.error(e)
            return False

    def __process_image(self, image: np.ndarray, out_dir: str, page_no: str, image_type: str) -> bool:
        from os import mkdir

        path = join(out_dir, page_no)

        if exists(path) and walk_dir(path, file_type="." + image_type):
            clear_dir(path, del_sudirs=True, file_ext="." + image_type)

        dir_name = join(out_dir, page_no)
        try:
            mkdir(dir_name)
        except OSError as e:
            if not exists(join(out_dir, page_no)):
                raise Exception("Could not create out_dir with page_no: {0}, {1}".format(join(out_dir, page_no), repr(e)))

        file_name = 1

        for text_image in self.__cut_text_from_image(image):
            fname = str(file_name) + '.' + image_type
            self.__save_text_box(text_image, path, fname)
            file_name += 1

        return True

    def __process_image_stack(self) -> bool:
        """
        process_image_stack(in_dir, out_dir) -> Bool.

        Get all image files in the subdirectories of in_dir and get all text boxes.
        Save each of the text boxes as png in a separate file in a subdirectory.



        Constructs a structure of a pdf pag like following:
            page1.png
            page1:
                text_box_1
                text_box_2
                ...
            page2.png
            page2:
                text_box_1
                ...
            page3.png
            page3:
                ...

        Return True on success or False on failure or in case of empty input.
        """
        in_dir = self.conf.in_dir
        image_type = self.conf.image_type

        dirs = list_sub_dirs(in_dir)

        if self.conf.verbose:
            print("++ Layout Processor ++")
            print("   Processing file(s) in path " + in_dir)

        if not dirs:
            raise Exception('Path tree seems to invalid in: {0}. Path has different structure'.format(in_dir))

        for d in dirs:
            image_files = walk_dir(d, image_type)
            if not image_files:
                continue

            for image_path in image_files:
                if self.conf.verbose:
                    print("    ... " + image_path + " ... ")
                image = io.imread(image_path, as_grey=True)
                page_no = str(basename(image_path).split('.')[0])
                self.__process_image(image, d, page_no, image_type)
        if self.conf.verbose:
            print("++++++++++++++++++++++")

        return True

    def run(self) -> None:
        try:
            self.__process_image_stack()
        except KeyboardInterrupt:
            print("\nComputation cancelled.")


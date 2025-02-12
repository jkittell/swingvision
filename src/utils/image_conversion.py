from PIL import Image
import numpy as np
import cv2


def convert_frames_to_images(frames):
    """
    Convert a list of frames (NumPy arrays) to PIL Images.

    :param frames: List of frames as NumPy arrays.
    :return: List of frames as PIL Images.
    """
    pil_images = [Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) for frame in frames]
    return pil_images

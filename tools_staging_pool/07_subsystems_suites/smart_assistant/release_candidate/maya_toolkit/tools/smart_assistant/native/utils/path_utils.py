from ...config_io import sequence
def is_image_sequence_folder(path):
    try:sequence(path);return True
    except (ValueError,OSError):return False

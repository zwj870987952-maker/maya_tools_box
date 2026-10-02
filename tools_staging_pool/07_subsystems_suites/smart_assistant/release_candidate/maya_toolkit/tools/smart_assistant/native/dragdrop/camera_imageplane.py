from ...config_io import sequence
from ...operations import create_sequence
def create_camera_with_sequence(folder_path):return create_sequence(sequence(folder_path),open_view=True)

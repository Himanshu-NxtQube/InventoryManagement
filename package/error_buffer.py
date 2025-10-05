from package.error_codes import ErrorCodes
import os


class ErrorBuffer:
    def __init__(self):
        pass
    
    def add_error(self, image_path, error: ErrorCodes):
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        tmp_file = open(f'__{base_name}.tmp', 'a')

        tmp_file.write(str(error.value) + '.')
        tmp_file.close()
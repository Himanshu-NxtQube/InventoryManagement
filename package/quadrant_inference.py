from package.config_loader import get_config

class RackQuadrantInferer:
    def __init__(self):
        self.CONFIG = get_config()
        import importlib.util
        import sys

        file_path = self.CONFIG['rack_infer_func']['path']
        module_name = "rack_quadrant_inferer"

        # Load module from file
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Get the function
        self.infer_Q3_Q4 = getattr(module, "infer_Q3_Q4")

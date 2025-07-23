import os
import sys
import time
from package.google_ocr import OCRClient
from concurrent.futures import ThreadPoolExecutor
from package.config_loader import set_config, get_config
from package.boundary_detection import BoundaryDetector
from package.container_detection import ContainerDetector
from package.rack_box_extraction import RackBoxExtractor
from package.quadrant_inference import RackQuadrantInferer
from package.data_retriever import RDSDataFetcher
from package.mapping_func import RecordMapper
from package.utils import Utilities
from package.rack_stack_validator import RackStackValidator
from package.depth_estimation import DepthEstimator
from package.part_numbers_fetcher import get_left_right_part_numbers
from package.exclusions import get_exclusion
from package.json_result import print_json

# print(type(sys.argv[1]))
set_config(sys.argv[1])
CONFIG = get_config()
extras = CONFIG['extras']

# Detection models
boundary_detector = BoundaryDetector()
ocr_client = OCRClient()
container_detector = ContainerDetector()

if 'pallet_status' in extras:
    depth_estimator = DepthEstimator("depth_anything_v2")
    rack_stack_validator = RackStackValidator()

# Logical Components
util = Utilities()
rack_box_extractor = RackBoxExtractor()
rack_quad_infer = RackQuadrantInferer()
data_fetcher = RDSDataFetcher()
mapper = RecordMapper()




def process_single_image(image_path):
    

    with ThreadPoolExecutor(max_workers=4) as executor:
        future_annotations = executor.submit(ocr_client.get_annotations, image_path)
        future_boundaries = executor.submit(boundary_detector.get_boundaries, image_path)
        future_container = executor.submit(container_detector.get_detections, image_path)
        if 'pallet_status' in extras:
            future_depth_map = executor.submit(depth_estimator.get_depth_map, image_path)
            depth_map = future_depth_map.result()

        left_line_x, right_line_x, upper_line_y, lower_line_y = future_boundaries.result()
        annotations = future_annotations.result()
        container_res = future_container.result()
        
            
        
    start = time.time()
    # contains ROI
    boundaries = left_line_x, right_line_x, upper_line_y, lower_line_y
    
    # dimensions of image
    dims = util.get_image_dimensions(image_path)

    # extracting rack_ids & unique_ids
    rack_dict, box_dict = rack_box_extractor.extract_ocr_info(annotations[1:], boundaries, dims)

    print("\nBefore Rack dict:", rack_dict)

    # infer missing rack ids
    rack_dict = rack_quad_infer.infer_Q3_Q4(rack_dict)

    print("\nAfter Rack dict:", rack_dict)

    # fetch all records
    records = data_fetcher.gather_all_records(box_dict, sys.argv[1])

    print("\nBox dict:", box_dict)
    print("\nRecords:", records)

    # mapping the records to pallet
    mapping_info = mapper.process(box_dict, container_res, boundaries)

    # get pallet status (if required)
    if 'pallet_status' in extras:
        part_numbers = get_left_right_part_numbers(box_dict, dims, records)
        pallet_status = rack_stack_validator.get_status(image_path, depth_map, boundaries, dims, part_numbers)
    else:
        pallet_status = None

    # get exclusion per rack id (side) 
    exclusions = get_exclusion(mapping_info, img_dims=dims)

    # print the final json result
    print_json(image_path, dims, rack_dict, records, mapping_info, exclusions, pallet_status)

    
    print("\nRequired time: ", time.time() - start)
    


def main():
    # image_directory = CONFIG['input']['image_dir']
    image_directory = CONFIG['input']['debug_image_dir']

    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')

    for image_file in os.listdir(image_directory):
        print("\nProcessing",image_file)
        if not image_file.lower().endswith(image_extensions):
            continue

        image_path = os.path.join(image_directory,image_file)  
        process_single_image(image_path)
        # break

if __name__ == "__main__":
    main()

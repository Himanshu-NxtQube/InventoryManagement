import os
import sys
import time
import shutil
import pymysql
from dotenv import load_dotenv
from package.google_ocr import OCRClient
from concurrent.futures import ThreadPoolExecutor, as_completed
from package.config_loader import set_config, get_config
from package.boundary_detection import BoundaryDetector
from package.container_detection import ContainerDetector
from package.rack_box_extraction import RackBoxExtractor
from package.quadrant_inference import RackQuadrantInferer
from package.data_retriever import RDSDataFetcher
from package.mapping_func import RecordMapper
from package.utils import Utilities
from multiprocessing import Pool, cpu_count, set_start_method
from package.rack_stack_validator import RackStackValidator
from package.depth_estimation import DepthEstimator
from package.part_numbers_fetcher import get_left_right_part_numbers
from package.exclusions import get_exclusion
from package.rds_operator import RDSOperator
from package.json_result import print_json

# setting up global variables
user_id = sys.argv[1]
set_config(user_id)
CONFIG = get_config()
extras = CONFIG['extras']
load_dotenv('package/.env')


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
rds_operator = RDSOperator()
mapper = RecordMapper()

# --- Connection Configuration ---
conn = pymysql.connect(
    host=os.getenv("rds_host"),  # RDS Endpoint
    user=os.getenv("rds_user"),                    # DB username
    password=os.getenv("rds_password"),                # DB password
    database=os.getenv("rds_dbname"),           # Target DB name
    port=int(os.getenv("rds_port", 3306))                                # Default MySQL port
)


def process_single_image(image_path, report_id):
    
    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_annotations = executor.submit(ocr_client.get_annotations, image_path)
        future_boundaries = executor.submit(boundary_detector.get_boundaries, image_path)
        future_container = executor.submit(container_detector.get_detections, image_path)
        future_image_obj_key_id = executor.submit(rds_operator.store_img_info, image_path, conn)
        if 'pallet_status' in extras:
            future_depth_map = executor.submit(depth_estimator.get_depth_map, image_path)
            depth_map = future_depth_map.result()

        left_line_x, right_line_x, upper_line_y, lower_line_y = future_boundaries.result()
        annotations = future_annotations.result()
        container_res = future_container.result()
        image_obj_key_id = future_image_obj_key_id.result()
        
            
        
    
    # contains ROI
    boundaries = left_line_x, right_line_x, upper_line_y, lower_line_y
    # print("boundaries:",boundaries)
    
    # dimensions of image
    dims = util.get_image_dimensions(image_path)

    # extracting rack_ids & unique_ids
    rack_dict, box_dict = rack_box_extractor.extract_ocr_info(annotations[1:], boundaries, dims)

    # FallBack Mechanism: if upper/lower bars fails then using rack id coordinates
    upper_line_y = int(rack_box_extractor.min_y)
    lower_line_y = int(rack_box_extractor.max_y)
    boundaries = left_line_x, right_line_x, upper_line_y, lower_line_y

    print("\nBefore Rack dict:", rack_dict)

    # infer missing rack ids
    rack_dict = rack_quad_infer.infer_Q3_Q4(rack_dict)

    print("\nAfter Rack dict:", rack_dict)

    # fetch all records
    records = data_fetcher.gather_all_records(box_dict, sys.argv[1])

    # print("\nBox dict:", box_dict)
    # print("\nRecords:", records)

    # mapping the records to pallet
    mapping_info = mapper.process(box_dict, container_res, boundaries)

    # get pallet status (if required)
    if 'pallet_status' in extras:
        part_numbers = get_left_right_part_numbers(box_dict, dims, records)
        pallet_status = rack_stack_validator.get_status(image_path, depth_map, boundaries, dims, part_numbers)
        stack_counts, box_counts = rack_stack_validator.get_counts()
    else:
        pallet_status = None
        stack_counts, box_counts = None, None

    # get exclusion per rack id (side) 
    exclusions = get_exclusion(mapping_info, img_dims=dims)
    # print(exclusions)

    # print the final json result
    print_json(image_path, dims, rack_dict, records, mapping_info, exclusions, pallet_status=pallet_status, box_counts=box_counts, stack_counts=stack_counts)

    # TODO: tidy up this process (i.e. storing this data to RDS ) and arguments
    # storing result in RDS process
    rds_operator.store_data_to_RDS(image_path, conn, user_id, image_obj_key_id, report_id, dims, rack_dict, records, mapping_info, exclusions, pallet_status)

    
    print("\nRequired time: ", time.time() - start)
    

is_threading = False
def main():
    _dir = CONFIG['input']['image_dir']
    folders = [f for f in os.listdir(_dir) if os.path.isdir(os.path.join(_dir, f))]

    if folders:
        image_directory = os.path.join(_dir,folders[0])  # First in the list
        print("First folder found:", image_directory)
    else:
        print("No folders found in", _dir)
        return

    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')

    image_files = sorted([
            f for f in os.listdir(image_directory)
            if f.lower().endswith(image_extensions)
        ])
    
    # creation of report
    report_id = 0
    report_id = rds_operator.create_report(conn, user_id, report_name=image_directory)
    print(report_id)

    if(is_threading):
        #  - - - - - - - - - - - - - - - - - - - - - -
        # Multihreading was causing issue in output, so using multiprocessing
        # - - - - - - - - - - - - - - - - - - - - - -
        # 
        # def process(image_file):
        #     print("\nProcessing", image_file)
        #     image_path = os.path.join(image_directory, image_file)
        #     process_single_image(image_path)

        # with ThreadPoolExecutor(max_workers=8) as executor:
        #     futures = [executor.submit(process, image_file) for image_file in image_files]
        #     for future in as_completed(futures):
        #         try:
        #             future.result()
        #         except Exception as e:
        #             print("Error:", e)
        # - - - - - - - - - - - - - - - - - - - - - - 
        set_start_method('spawn', force=True)
        num_workers = max(4, cpu_count())
        image_paths = [(os.path.join(image_directory, f), report_id) for f in image_files]

        print(f"Running with {num_workers} processes...")

        with Pool(processes=num_workers) as pool:
            pool.map(process_single_image_safe, image_paths)
    else:
        for image_file in image_files:
            print("\nProcessing",image_file)
            if not image_file.lower().endswith(image_extensions):
                continue

            image_path = os.path.join(image_directory,image_file)  
            process_single_image(image_path, report_id)
    shutil.rmtree(image_directory)


def process_single_image_safe(args):
    image_path, report_id = args
    try:
        print("\nProcessing", os.path.basename(image_path))
        process_single_image(image_path, report_id)  # your actual image logic
    except Exception as e:
        print(f"Error processing {os.path.basename(image_path)}: {e}")
    

if __name__ == "__main__":
    a = time.time()
    main()
    print("Total time required:", time.time() - a)

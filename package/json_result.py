import os
import csv
import json
from package.s3_operator import upload_images



def build_json_result(image_path, img_dims, rack_dict, records, mapping_info, exclusions, pallet_status, box_counts, stack_counts):
    final_output = []
    image_name = os.path.basename(image_path)

    output_template = {
        'IMG_ID':         image_name, 
        'RACK_ID':        None,  
        'BARCODE_ID':     None,  
        'UNIQUE_ID':      None,  
        'BOXNUMBER':      None,  
        'BOXQUANTITY':    None,  
        'PARTNUMBER':     None,  
        'INVOICE_NUMBER': None,  
        'EXCLUSION':      None,  
    }

    if not rack_dict:
        # output_template['EXCLUSION'] = "No Rack ID found"
        # return output_template
        exclusions['left'] = "No Rack ID found"
        exclusions['right'] = "No Rack ID found"
        rack_dict['Q3'] = ""
        rack_dict['Q4'] = ""

    left_rack = False
    right_rack = False

    mappings = mapping_info['mappings']
    unmapped_containers = mapping_info['unmapped_containers']

    for unique_id, (p_cx, p_cy) in mappings.items():
        temp_output = output_template.copy()
        if p_cx < img_dims[0]/2:
            left_rack = True
            temp_output['RACK_ID'] = rack_dict['Q3']
            temp_output['EXCLUSION'] = exclusions['left']
            if pallet_status:
                if exclusions['left'] == "" or exclusions['left'] == "No Rack ID found":
                    temp_output['STATUS'] = pallet_status[0] if pallet_status[0] != 'empty' else 'partial'
                else:
                    temp_output['STATUS'] = ""
                temp_output['BOX_COUNT'] = box_counts[0]
                temp_output['STACK_COUNT'] = stack_counts[0]
        else:
            right_rack = True
            temp_output['RACK_ID'] = rack_dict['Q4']
            temp_output['EXCLUSION'] = exclusions['right']
            if pallet_status:
                if exclusions['right'] == "" or exclusions['right'] == "No Rack ID found":
                    temp_output['STATUS'] = pallet_status[1] if pallet_status[1] != 'empty' else 'partial'
                else:
                    temp_output['STATUS'] = ""
                temp_output['BOX_COUNT'] = box_counts[1]
                temp_output['STACK_COUNT'] = stack_counts[1]

        result = next((record for record in records if record['uniqueId'] == unique_id), None)

        if not result:
            print("Unique id not found in records")
            temp_output['BARCODE_ID'] = ""
            temp_output['UNIQUE_ID'] = unique_id
            temp_output['BOXNUMBER'] = ""
            temp_output['BOXQUANTITY'] = ""
            temp_output['PARTNUMBER'] = ""
            temp_output['INVOICE_NUMBER'] = ""
        else:
            temp_output['BARCODE_ID'] = result['barcode_number']
            temp_output['UNIQUE_ID'] = result['uniqueId']
            temp_output['BOXNUMBER'] = result['box_number']
            temp_output['BOXQUANTITY'] = result['box_quantity']
            temp_output['PARTNUMBER'] = result['part_number']
            temp_output['INVOICE_NUMBER'] = result['invoice_number']

        final_output.append(temp_output)

    if not left_rack:
        temp_output = output_template.copy()
        temp_output['RACK_ID'] = rack_dict['Q3']
        temp_output['EXCLUSION'] = exclusions['left']
        if pallet_status:
            if exclusions['left'] == 'empty rack':
                temp_output['STATUS'] = 'empty'
            else:
                temp_output['STATUS'] = ""
            temp_output['BOX_COUNT'] = ""
            temp_output['STACK_COUNT'] = ""
            # if exclusions['left'] == 'empty rack':
            #     temp_output['STATUS'] = 'empty'
            # elif pallet_status[0] == 'empty':
            #     temp_output['STATUS'] = 'partial'
            # else:
            #     temp_output['STATUS'] = pallet_status[0]
        final_output.append(temp_output)
    if not right_rack:
        temp_output = output_template.copy()
        temp_output['RACK_ID'] = rack_dict['Q4']
        temp_output['EXCLUSION'] = exclusions['right']
        if pallet_status:
            if exclusions['right'] == 'empty rack':
                temp_output['STATUS'] = 'empty'
            else:
                temp_output['STATUS'] = ""
            temp_output['BOX_COUNT'] = ""
            temp_output['STACK_COUNT'] = ""
            # if exclusions['right'] == 'empty rack':
            #     temp_output['STATUS'] = 'empty'
            # elif pallet_status[1] == 'empty':
            #     temp_output['STATUS'] = 'partial'
            # else:
            #     temp_output['STATUS'] = pallet_status[1]
        final_output.append(temp_output)

    return final_output

def print_json(image_path, img_dims, rack_dict, records, mapping_info, exclusions, csv_output=True, pallet_status=None, box_counts=None, stack_counts=None):
    final_output = build_json_result(image_path, img_dims, rack_dict, records, mapping_info, exclusions, pallet_status, box_counts, stack_counts)
    json_obj = json.dumps(final_output, indent=4)
    print(json_obj)
    if csv_output:
        write_to_csv(final_output, 'output.csv')

def write_to_csv(output, output_file):
    if not output:
        raise ValueError("output list is empty.")

    fieldnames = list(output[0].keys())
    file_exists = os.path.exists(output_file)
    write_header = not file_exists or os.path.getsize(output_file) == 0

    with open(output_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(output)

"""
{
    'IMG_ID':         image_id, ✅
    'RACK_ID':        rack_id, ✅ 
    'BARCODE_ID':     None, ✅ 
    'UNIQUE_ID':      None, ✅ 
    'BOXNUMBER':      None, ✅ 
    'BOXQUANTITY':    None, ✅ 
    'PARTNUMBER':     None, ✅ 
    'INVOICE_NUMBER': None, ✅ 
    'EXCLUSION':      exclusion, ✅ 
}
"""
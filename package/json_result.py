import os
import json
from package.s3_operator import upload_images



def build_json_result(image_path, img_dims, rack_dict, records, mapping_info, exclusions, pallet_status):
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
        output_template['EXCLUSION'] = "No Rack ID found"
        return output_template

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
                temp_output['STATUS'] = pallet_status[0] if pallet_status[0] != 'empty' else 'partial'
        else:
            right_rack = True
            temp_output['RACK_ID'] = rack_dict['Q4']
            temp_output['EXCLUSION'] = exclusions['right']
            if pallet_status:
                temp_output['STATUS'] = pallet_status[1] if pallet_status[1] != 'empty' else 'partial'

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
            temp_output['STATUS'] = pallet_status[0] 
        final_output.append(temp_output)
    if not right_rack:
        temp_output = output_template.copy()
        temp_output['RACK_ID'] = rack_dict['Q4']
        temp_output['EXCLUSION'] = exclusions['right']
        if pallet_status:
            temp_output['STATUS'] = pallet_status[1]
        final_output.append(temp_output)

    return final_output

def print_json(image_path, img_dims, rack_dict, records, mapping_info, exclusions, pallet_status=None):
    final_output = build_json_result(image_path, img_dims, rack_dict, records, mapping_info, exclusions, pallet_status)
    json_obj = json.dumps(final_output, indent=4)
    print(json_obj)


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
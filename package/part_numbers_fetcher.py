def get_left_right_part_numbers(box_dict, img_dims, records):
    left_part_number = None
    right_part_number = None

    for unique_id, (cx, cy) in box_dict.items():
        result = next((record for record in records if record['uniqueId'] == unique_id), None)
        if not result:
            continue
        if cx < img_dims[0]//2:
            left_part_number = result['part_number']
        else:
            right_part_number = result['part_number']

    return [left_part_number, right_part_number]

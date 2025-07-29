from package.config_loader import get_config


def get_exclusion(mapping_info, img_dims):
    config = get_config()
    left_rack_exclusion = ""
    right_rack_exclusion = ""

    mappings = mapping_info['mappings']
    unmapped_conatiners = mapping_info['unmapped_containers']

    mapped_containers = set(mappings.values())

    left_mapped_containers_cnt = \
            sum([1 for (cx, cy) in mapped_containers # count of mapped containers on the left
            if cx < (img_dims[0]/2) ])
    
    left_unmapped_containers_cnt = \
        sum([1 for (cx, cy) in unmapped_conatiners # count of unmapped containers on the left
                if cx < (img_dims[0]/2) ])
    

    right_mapped_containers_cnt = \
            sum([1 for (cx, cy) in mapped_containers # count of mapped containers on the right
            if cx >= (img_dims[0]/2) ])
    
    right_unmapped_containers_cnt = \
        sum([1 for (cx, cy) in unmapped_conatiners # count of mapped containers on the right
                if cx >= (img_dims[0]/2) ])

    left_containers_cnt = left_mapped_containers_cnt + left_unmapped_containers_cnt
            
    right_containers_cnt = right_mapped_containers_cnt + right_unmapped_containers_cnt

    if left_unmapped_containers_cnt != 0:
        left_rack_exclusion = f"There are {left_containers_cnt} {config['nomenclature']}, but there is some issue with the sticker of {left_unmapped_containers_cnt} {config['nomenclature']}"
    elif left_containers_cnt == 0:
        left_rack_exclusion = f"Empty Rack"
    
    if right_unmapped_containers_cnt != 0:
        right_rack_exclusion = f"There are {right_containers_cnt} {config['nomenclature']}, but there is some issue with the sticker of {right_unmapped_containers_cnt} {config['nomenclature']}"
    elif right_containers_cnt == 0:
        right_rack_exclusion = f"Empty Rack"


    return {'left': left_rack_exclusion,
            'right': right_rack_exclusion}
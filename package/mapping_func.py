from package.config_loader import get_config

class RecordMapper:
    # def segregate_ids(self, box_dict, dims):
    #     width, height = dims

    #     left_ids = [] 
    #     right_ids = []
    #     for unique_id, coordinates in box_dict.items():
    #         x, y = coordinates
    #         if x < width/2:
    #             left_ids.append((unique_id, coordinates))
    #         else:
    #             right_ids.append((unique_id, coordinates))

    #     return left_ids, right_ids

    # def segregate_pallet(self, container_res, dims):
    #     width, height = dims
    #     mid_x = width / 2.0

    #     left_containers = []
    #     right_containers = []

    #     xyxy = container_res[0].boxes.xyxy.cpu().numpy()  # [[x1,y1,x2,y2], ...]
    #     for (x1, y1, x2, y2) in xyxy:
    #         cx = int( (x1 + x2) / 2 )
    #         cy = int( (y1 + y2) / 2 )
    #         bbox = (int(x1), int(y1), int(x2), int(y2))
            

    #         if cx < mid_x:
    #             left_containers.append((bbox, (cx, cy)))
    #         else:
    #             right_containers.append((bbox, (cx, cy)))
        
    #     return left_containers, right_containers
        

    def process(self, box_dict, containers, boundaries):
        left_line_x, right_line_x, upper_line_y, lower_line_y = boundaries

        ids = [(k, v) for k,v in box_dict.items()]
        # sorting ids by y
        ids.sort(key=lambda x:x[1][1])

        # sorting containers by y
        containers.sort(key=lambda x:x[1][1])

        # print("\nids:",ids)
        # print("\ncontainers:",containers)

        mappings = {}
        mapped_ids = set()
        visited_containers = set()

        for i,(bbox, (p_center_x, p_center_y)) in enumerate(containers):
            x1, y1, x2, y2 = bbox
            # print("\nx1 and x2:", x1, x2)
            # print("y1 and y2:", y1, y2)

            if left_line_x > p_center_x or p_center_x > right_line_x or upper_line_y > p_center_y or p_center_y > lower_line_y:
                visited_containers.add(bbox)
                print("skipped this box")
                continue
            
            for j, (id, (id_center_x, id_center_y)) in enumerate(ids):
                if id in mapped_ids:
                    continue
                # print("id:", id)
                # print("id_center_x:",id_center_x)
                
                if x1 < id_center_x < x2 and id_center_y < y2:
                    mappings[id] = (p_center_x, p_center_y)
                    mapped_ids.add(id)
                    visited_containers.add(bbox)
        
        unmapped_ids = [(id,(id_center_x, id_center_y)) for id,(id_center_x, id_center_y) in ids if id not in mapped_ids]
        
        # create mappings of unmapped_ids too, detected unique id data should not be lost
        for id, (id_center_x, id_center_y) in unmapped_ids:
            mappings[id] = (id_center_x, id_center_y)

        unmapped_containers = [(p_center_x, p_center_y) for bbox,(p_center_x, p_center_y) in containers if bbox not in visited_containers]

        # print("\nmappings:", mappings)
        # print("\nunmapped_containers:", unmapped_containers)

        return {"mappings": mappings,
                "unmapped_containers": unmapped_containers}

        #  - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """
        Ask either Saiesh or Omkar about how to solve issue when 
        upper bar is not detected or upper pallet is detected,
        then it will throw an exclusion.
        Saiesh's initial approach was to choose the pallets 
        closer to lower bar are only taken, but what if lower bar 
        fails to detect and also it will fail if there are two
        pallets placed on one rack
        """
        #  - - - - - - - - - - - - - - - - - - - - - - - - - - -



        # # segregating ids on the x coordinate
        # left_ids, right_ids = self.segregate_ids(box_dict, dims)

        # # sorting ids on y
        # left_ids.sort(key= lambda x: x[1][1])
        # right_ids.sort(key= lambda x: x[1][1])

        # print(f"\n{left_ids = }")
        # print(f"\n{right_ids = }")


        # # segregating pallets on the x coordinate
        # left_containers, right_containers = self.segregate_pallet(container_res, dims)

        # # sorting containers on y
        # left_containers.sort(key= lambda x: x[1][1])
        # right_containers.sort(key= lambda x: x[1][1])

        # print(f"\n{left_containers = }")
        # print(f"\n{right_containers = }")

        # mappings = {}

        # for bbox, (p_center_x, p_center_y) in left_containers:
        #     x1, y1, x2, y2 = bbox
        #     for i, (id, (id_center_x, id_center_y)) in enumerate(left_ids):
        #         if x1 < id_center_x < x2 and id_center_y < p_center_y:
        #             mappings[id] = (p_center_x, p_center_y, 'left')
        #             left_ids.pop(i)

        # for bbox, (p_center_x, p_center_y) in right_containers:
        #     x1, y1, x2, y2 = bbox
        #     for i, (id, (id_center_x, id_center_y)) in enumerate(right_ids):
        #         if x1 < id_center_x < x2 and id_center_y < p_center_y:
        #             mappings[id] = (p_center_x, p_center_y, 'right')
        #             right_ids.pop(i)
        
        # print(mappings)


        







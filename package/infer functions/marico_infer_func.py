import re
from package.config_loader import get_config

CONFIG = get_config()
_RACK_RE = re.compile(CONFIG['rack_id']['pattern'])

def infer_Q3_Q4(rack_dict: dict) -> dict:
    # Filter only valid rack ids
    rack_dict = {k: v for k, v in rack_dict.items() if _RACK_RE.match(v)}
    # inv_rack_dict = {v: k for k, v in rack_dict.items()}

    if 'Q1' in rack_dict.keys() and 'Q2' in rack_dict.keys():
        rack_dict['Q4'] = rack_dict['Q1'][:2] + str(int(rack_dict['Q1'][2]) - 1) + rack_dict['Q1'][-2:]
        rack_dict['Q3'] = rack_dict['Q2'][:2] + str(int(rack_dict['Q2'][2]) - 1) + rack_dict['Q2'][-2:]
        
    elif 'Q1' in rack_dict.keys():
        rack_dict['Q4'] = rack_dict['Q1'][:2] + str(int(rack_dict['Q1'][2]) - 1) + rack_dict['Q1'][-2:]

        if ord(rack_dict['Q4'][0]) % 2 == 0:
            num = str(int(rack_dict['Q4'][-2:]) - 1)
            if len(num) == 1:
                num = '0' + num 
        else:
            num = str(int(rack_dict['Q4'][-2:]) + 1)
            if len(num) == 1:
                num = '0' + num

        rack_dict['Q3'] = rack_dict['Q4'][:3] + num   
    elif 'Q2' in rack_dict.keys():
        rack_dict['Q3'] = rack_dict['Q2'][:2] + str(int(rack_dict['Q2'][2]) - 1) + rack_dict['Q2'][-2:]

        if ord(rack_dict['Q3'][0]) % 2 == 0:
            num = str(int(rack_dict['Q3'][-2:]) + 1)
            if len(num) == 1:
                num = '0' + num 
        else:
            num = str(int(rack_dict['Q3'][-2:]) - 1)
            if len(num) == 1:
                num = '0' + num
                
        rack_dict['Q4'] = rack_dict['Q3'][:3] + num  

    if 'Q3' not in rack_dict.keys():
        if 'Q4' in rack_dict.keys():
            if ord(rack_dict['Q4'][0]) % 2 == 0:
                num = str(int(rack_dict['Q4'][-2:]) - 1)
                if len(num) == 1:
                    num = '0' + num 
            else:
                num = str(int(rack_dict['Q4'][-2:]) + 1)
                if len(num) == 1:
                    num = '0' + num

            rack_dict['Q3'] = rack_dict['Q4'][:3] + num
        
    if 'Q4' not in rack_dict.keys():
        if 'Q3' in rack_dict.keys():
            if ord(rack_dict['Q3'][0]) % 2 == 0:
                num = str(int(rack_dict['Q3'][-2:]) + 1)
                if len(num) == 1:
                    num = '0' + num 
            else:
                num = str(int(rack_dict['Q3'][-2:]) - 1)
                if len(num) == 1:
                    num = '0' + num
                    
            rack_dict['Q4'] = rack_dict['Q3'][:3] + num

    # return {v: k for k, v in inv_rack_dict.items()}
    return rack_dict


# === EXAMPLES ===
if __name__ == '__main__':
    # print("Example 1:", infer_Q3_Q4({'BL323': 'Q2'}))
    print("Example 2:", infer_Q3_Q4({'CL369': 'Q1'}))
    # print("Example 3:", infer_Q3_Q4({'BL356': 'Q1', 'BL355': 'Q2'}))

import re
from package.config_loader import get_config

CONFIG = get_config()
_RACK_RE = re.compile(CONFIG['rack_id']['pattern'])

def infer_Q3_Q4(rack_dict: dict) -> dict:
    # Filter only valid rack ids
    # rack_dict = {k: v for k, v in rack_dict.items() if _RACK_RE.match(k)}
    # inv_rack_dict = {v: k for k, v in rack_dict.items()}

    if 'Q1' in rack_dict and 'Q2' in rack_dict:
        rack_dict['Q4'] = rack_dict['Q1'][:-1] + chr(ord(rack_dict['Q1'][-1]) - 1)
        rack_dict['Q3'] = rack_dict['Q2'][:-1] + chr(ord(rack_dict['Q2'][-1]) - 1)

    elif 'Q1' in rack_dict:
        rack_dict['Q4'] = rack_dict['Q1'][:-1] + chr(ord(rack_dict['Q1'][-1]) - 1)
        num = int(rack_dict['Q4'][3:5])
        num = str(num - 2 if num % 2 else num + 2).zfill(2)
        rack_dict['Q3'] = rack_dict['Q4'][:3] + num + rack_dict['Q4'][-2:]

    elif 'Q2' in rack_dict:
        rack_dict['Q3'] = rack_dict['Q2'][:-1] + chr(ord(rack_dict['Q2'][-1]) - 1)
        num = int(rack_dict['Q3'][3:5])
        num = str(num + 2 if num % 2 else num - 2).zfill(2)
        rack_dict['Q4'] = rack_dict['Q3'][:3] + num + rack_dict['Q3'][-2:]

    if 'Q3' not in rack_dict and 'Q4' in rack_dict:
        num = int(rack_dict['Q4'][3:5])
        num = str(num - 2 if num % 2 else num + 2).zfill(2)
        rack_dict['Q3'] = rack_dict['Q4'][:3] + num + rack_dict['Q4'][-2:]

    if 'Q4' not in rack_dict and 'Q3' in rack_dict:
        num = int(rack_dict['Q3'][3:5])
        num = str(num + 2 if num % 2 else num - 2).zfill(2)
        rack_dict['Q4'] = rack_dict['Q3'][:3] + num + rack_dict['Q3'][-2:]

    # return {v: k for k, v in inv_rack_dict.items()}
    return rack_dict


# === EXAMPLES ===
if __name__ == '__main__':
    print("Example 1:", infer_Q3_Q4({'RD-17-G': 'Q4'}))
    # print("Example 2:", infer_Q3_Q4({'RD-03-C': 'Q1'}))
    # print("Example 3:", infer_Q3_Q4({'BL356': 'Q1', 'BL355': 'Q2'}))

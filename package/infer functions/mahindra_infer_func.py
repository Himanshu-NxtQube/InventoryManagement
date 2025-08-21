import re
from package.config_loader import get_config

CONFIG = get_config()
_RACK_RE = re.compile(CONFIG['rack_id']['pattern'])

def infer_Q3_Q4(rack_dict: dict) -> dict:
    # Filtering valid rack ids
    rack_dict = {k: v for k, v in rack_dict.items() if _RACK_RE.match(v)}
    # inv_rack_dict = {v: k for k, v in rack_dict.items()}

    if 'Q3' in rack_dict.keys() and 'Q4' in rack_dict.keys():
        if rack_dict['Q3'][:-2] != rack_dict['Q4'][:-2] or abs(int(rack_dict['Q3'][-2:]) - int(rack_dict['Q4'][-2:])) != 1:

                if 'Q1' in rack_dict.keys():
                    if rack_dict['Q4'] == rack_dict['Q1'][:-4] + chr(ord(rack_dict['Q1'][-4]) - 1) + rack_dict['Q1'][-3:]:
                        rack_dict.pop('Q3', None)
                    elif rack_dict['Q3'][:-3] == rack_dict['Q1'][:-4] + chr(ord(rack_dict['Q1'][-4]) - 1):
                        if abs(int(rack_dict['Q3'][-2:]) - int(rack_dict['Q1'][-2:])) == 1:
                            rack_dict.pop('Q4', None)

                elif 'Q2' in rack_dict.keys():
                    if rack_dict['Q3'] == rack_dict['Q2'][:-4] + chr(ord(rack_dict['Q2'][-4]) - 1) + rack_dict['Q2'][-3:]:
                        rack_dict.pop('Q4', None)
                    elif rack_dict['Q4'][:-3] == rack_dict['Q2'][:-4] + chr(ord(rack_dict['Q2'][-4]) - 1):
                        if abs(int(rack_dict['Q4'][-2:]) - int(rack_dict['Q2'][-2:])) == 1:
                            rack_dict.pop('Q3', None)
                else:
                    return {}

    if 'Q3' not in rack_dict.keys() and 'Q4' not in rack_dict.keys():
        if 'Q1' in rack_dict.keys():
            rack_dict['Q4'] = rack_dict['Q1'][:-4] + chr(ord(rack_dict['Q1'][-4]) - 1) + rack_dict['Q1'][-3:]

            if int(rack_dict['Q4'][3:5]) % 2 == 0:
                num = str(int(rack_dict['Q4'][-2:]) + 1)
                if len(num) == 1:
                    num = '0' + num
                rack_dict['Q3'] = rack_dict['Q4'][:-2] + num
            else:
                num = str(int(rack_dict['Q4'][-2:]) - 1)
                if len(num) == 1:
                    num = '0' + num
                rack_dict['Q3'] = rack_dict['Q4'][:-2] + num

        elif 'Q2' in rack_dict.keys():
            rack_dict['Q3'] = rack_dict['Q2'][:-4] + chr(ord(rack_dict['Q2'][-4]) - 1) + rack_dict['Q2'][-3:]

            if int(rack_dict['Q3'][3:5]) % 2 == 0:
                num = str(int(rack_dict['Q3'][-2:]) - 1)
                if len(num) == 1:
                    num = '0' + num
                rack_dict['Q4'] = rack_dict['Q3'][:-2] + num
            else:
                num = str(int(rack_dict['Q3'][-2:]) + 1)
                if len(num) == 1:
                    num = '0' + num
                rack_dict['Q4'] = rack_dict['Q3'][:-2] + num

    elif 'Q3' not in rack_dict.keys():
        if int(rack_dict['Q4'][3:5]) % 2 == 0:
            num = str(int(rack_dict['Q4'][-2:]) + 1)
            if len(num) == 1:
                num = '0' + num
            rack_dict['Q3'] = rack_dict['Q4'][:-2] + num
        else:
            num = str(int(rack_dict['Q4'][-2:]) - 1)
            if len(num) == 1:
                num = '0' + num
            rack_dict['Q3'] = rack_dict['Q4'][:-2] + num

    elif 'Q4' not in rack_dict.keys():
        if int(rack_dict['Q3'][3:5]) % 2 == 0:
            num = str(int(rack_dict['Q3'][-2:]) - 1)
            if len(num) == 1:
                num = '0' + num
            rack_dict['Q4'] = rack_dict['Q3'][:-2] + num
        else:
            num = str(int(rack_dict['Q3'][-2:]) + 1)
            if len(num) == 1:
                num = '0' + num
            rack_dict['Q4'] = rack_dict['Q3'][:-2] + num

    # inv_rack_dict = {v: k for k, v in rack_dict.items()}
    return rack_dict

# === EXAMPLE ===
if __name__ == '__main__':
    print(infer_Q3_Q4({'Q2': 'HD-04/C/02','Q1': 'HD-04/C/01'}))
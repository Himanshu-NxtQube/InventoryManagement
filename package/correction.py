import os
import pymysql

def make_correction(user_id, final_output):
    if user_id:
        conn = pymysql.connect(
            host=os.getenv("rds_host"),  # RDS Endpoint
            user=os.getenv("rds_user"),                    # DB username
            password=os.getenv("rds_password"),                # DB password
            database=os.getenv("rds_dbname"),           # Target DB name
            port=int(os.getenv("rds_port", 3306))                                # Default MySQL port
        )
        
        if user_id == '12':
            for output in final_output:
                if 'there' in output['EXCLUSION'].lower():
                    rack_id = output['RACK_ID'].replace('-','')
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT uniqueId, box_quantity, part_number, isDispatched FROM `row-data` WHERE rack_location = %s ORDER BY id DESC LIMIT 1;", (rack_id))
                        res = cursor.fetchall()
                        if res and not res[0][3]:
                            output['UNIQUE_ID'] = res[0][0]
                            output['BOXQUANTITY'] = res[0][1]
                            output['PARTNUMBER'] = res[0][2]
                            output['EXCLUSION'] = 'Predicted'
        
    return final_output

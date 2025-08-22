import os
import pymysql
from dotenv import load_dotenv
load_dotenv('package/.env')

conn = pymysql.connect(
    host=os.getenv("rds_host"),  # RDS Endpoint
    user=os.getenv("rds_user"),                    # DB username
    password=os.getenv("rds_password"),                # DB password
    database=os.getenv("rds_dbname"),           # Target DB name
    port=int(os.getenv("rds_port", 3306))                                # Default MySQL port
)


with conn.cursor() as cursor:
    query = "select count(*) from `inferances` where userId = 1 and DATE(updatedAt) = '2025-08-13' and exclusion = 'No Rack ID found' and isDeleted = false and isDispatched = false and reportId = 849;"
    cursor.execute(query)
    res = cursor.fetchall()[-1:]
    for row in res:
        print(row)
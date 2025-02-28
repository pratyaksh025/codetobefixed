import mysql.connector as msc

def mycon():
    conn= msc.connect(
    host="mydb.cbawyqc62v0z.us-east-1.rds.amazonaws.com",
    username="prat",
    password="Pass123456789",
    database="sbidb"
    )
    return conn

# if conn.is_connected():
#     print("Connection Established")



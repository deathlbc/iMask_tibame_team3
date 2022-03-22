import csv  # 讀寫csv
import os  # 讀檔案
import pymysql.cursors # 跟mysql連線

# create connection (remember to close connection in the end)
connection = pymysql.connect(host="hostname",
                             user="username",
                             password="password",
                             database="databasename",
                             charset='charset',
                             cursorclass=pymysql.cursors.DictCursor)

# execute the connection cursor
with connection.cursor() as cursor:

    # write your sql
    sql = f"select a.LOCATION, a.region, s.RDATE, s.RTIME, s.CPIN,  " \
          f"a.longitude, a.latitude from slog as s join aiot as a limit 10"
    cursor.execute(sql)

    # This part is used to observe what you get from database.
    # result = cursor.fetchone()
    # result["RDATE"] = str(result["RDATE"])
    # result["RTIME"] = str(result["RTIME"])
    # print(result, "\n", "-" * 50)

    # you'll get list from fetchall
    result_list = cursor.fetchall()

    # update local data
    filename = "testcsv.csv"  # your data name
    with open(filename, "w", newline='') as csvfile:  # overwrite local data

        # write the columns
        data_column = ["branch_name", "region", "datetime", "people_in", "altitude", "latitude"]
        write = csv.writer(csvfile)
        write.writerow(data_column)
        print(data_column,"\n","以上寫入完成")

        # write the data
        data_list = []
        for row in result_list:
            # preprocess the data
            rdate = row["RDATE"] = str(row["RDATE"])  # preprocess the date data
            rtime = row["RTIME"] = str(row["RTIME"])  # preprocess the time data
            rdate_time = rdate + " " + rtime  # combine date and time
            data_list = [row["LOCATION"], row["region"], rdate_time, row["CPIN"], row["longitude"], row["latitude"]]
            write.writerow(data_list)
            print(data_list, "\n", "以上寫入完成")

cursor.close()
connection.close()  # database will thank you very much
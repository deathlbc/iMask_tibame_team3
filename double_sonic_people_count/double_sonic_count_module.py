import argparse  # 用於控管指令參數
import RPi.GPIO as GPIO  # 用於與 Jetson nano 溝通
import time  # 計時
from datetime import datetime  # 紀錄日期
import csv  # 讀寫csv
import os  # 讀檔案
import schedule  # 排程


# 設定能接收來自指令的變數，以及變數預設值
def setup_parser():
    parser = argparse.ArgumentParser(prog='arg_test.py', description='test arg')
    parser.add_argument('--aiotno', '-no', default='cfi-001', type=str, required=False, help="機器編號")
    parser.add_argument('--detect_range', '-dr', default='150', type=int, required=False, help="感測距離(cm)")
    parser.add_argument('--t_count', '-tc', default='0.1', type=float, required=False, help="時間精準度")
    parser.add_argument('--people_in', '-cpin', default='0', type=int, required=False, help="初始化進入人數")
    parser.add_argument('--people_out', '-cpout', default='0', type=int, required=False, help="初始化離開人數")
    parser.add_argument('--t_count_sleep', '-tcs', default='0.3', type=float, required=False, help="計數後空檔")
    parser.add_argument('--show_range_print', '-srp', default="yes", type=str, required=False, help="是否顯示距離")

    # 管家上班
    args = parser.parse_args()

    global aiotno, people_out, people_in, detect_range, t_count, t_count_sleep, show_range_print

    # 分配參數給變數
    aiotno = args.aiotno
    people_out = args.people_out
    people_in = args.people_in
    detect_range = args.detect_range
    t_count = args.t_count
    t_count_sleep = args.t_count_sleep
    show_range_print = args.show_range_print


# 硬體設定
def setup_gpio():
    # GPIO 設定
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)  # pin mode

    global TRIG, ECHO, TRIG2, ECHO2

    # pin of inner machine
    TRIG = 16
    ECHO = 18
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    # pin of outer machine
    TRIG2 = 22
    ECHO2 = 24
    GPIO.setup(TRIG2, GPIO.OUT)
    GPIO.setup(ECHO2, GPIO.IN)


# inner machine get distance
def get_in_distance():
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(t_count)
    GPIO.output(TRIG, GPIO.LOW)

    while GPIO.input(ECHO) == 0:
        Din_start = time.time()
        # print("start:", start)
    while GPIO.input(ECHO) == 1:
        Din_end = time.time()
        # print("end", end)

    D1 = (Din_end - Din_start) * 17150
    return int(D1)


# outer machine get distance
def get_out_distance():
    GPIO.output(TRIG2, GPIO.HIGH)
    time.sleep(t_count)
    GPIO.output(TRIG2, GPIO.LOW)

    while GPIO.input(ECHO2) == 0:
        Dout_start = time.time()
        # print("start:", start)
    while GPIO.input(ECHO2) == 1:
        Dout_end = time.time()
        # print("end", end)

    D2 = (Dout_end - Dout_start) * 17150
    return int(D2)


# save the logs
def wcsv():
    # set record date & time
    record_date = datetime.now().strftime("%Y-%m-%d")
    record_time = datetime.now().strftime("%H:%M:%S")
    # the content to be saved
    record_list = [aiotno, record_date, record_time, people_in, people_out, people_in - people_out]

    # filename and the place
    filename = f"{aiotno}_log.csv"
    filepath = f"filepath/{filename}"
    data_col_title = ["aiotno", "record_date", "record_time", "people_in", "people_out", "now_in"]

    # check the csv already exists of not
    if os.path.isfile(filename):
        with open(filename, 'a+', newline='') as csvfile:
            write = csv.writer(csvfile)
            write.writerow(record_list)
        print("寫入完成")
    else:
        print("開新檔案")
        with open(filename, 'w', newline='') as csvfile:
            write = csv.writer(csvfile)
            write.writerow(data_col_title)
            write.writerow(record_list)
    print("欄位名稱: ", data_col_title)
    print("紀錄內容: ", record_list)
    print(f"檔案存放在 {filepath}")


# 計數字
def countp():
    while True:
        schedule.run_pending()   # run schedule
        ai = get_in_distance()
        ao = get_out_distance()
        if show_range_print == "yes":  # show logs on terminal or not?
            print("~Chill~", f"內機距離:{ai}", f"外機距離:{ao}")
        if ai < detect_range and ao > detect_range:  # inner sensor detect first
            print(" ~內機先感測到了~ ", f"內機距離:{ai}", f"外機距離:{ao}")
            while True:
                bo = get_out_distance()
                if bo < detect_range:
                    print(" ~外機也感測到了~ :", f"外機距離：{bo}")
                    while True:
                        co = get_out_distance()
                        if co > detect_range:
                            global people_out
                            people_out += 1
                            print("\n", f"有人離開，目前離開人數{people_out}人", "\n", f"外機距離：{co}", "\n")
                            time.sleep(t_count_sleep)
                            break
                    break

        elif ai > detect_range and ao < detect_range:  # outer sensor detect first
            print(" ~外機先感測到了~ ", f"內機距離:{ai}", f"外機距離:{ao}")
            while True:
                bi = get_in_distance()  # 裡
                if bi < detect_range:
                    print(" ~內機也感測到了~ :", f"內機距離:{bi}")
                    while True:
                        ci = get_in_distance()  # 裡
                        if ci > detect_range:
                            global people_in
                            people_in += 1
                            print("\n", f"有人進入，目前進入人數{people_in}人", "\n", f"內機距離:{ci}", "\n")
                            time.sleep(t_count_sleep) # 避免偵測到計數後後馬上再偵測的空檔
                            break
                    break


schedule.every(1).minutes.do(wcsv)  # how often write csv

if __name__ == "__main__":
    try:
        setup_parser()
        setup_gpio()
        countp()
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
        wcsv()  # save the final record
# jetson nano as a publisher
from paho.mqtt import publish
import os
import pandas as pd
import argparse


def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--aiotno', '-no', default='cfi-001', type=str, required=False, help="機器編號")

    # make parser deal with the args
    args = parser.parse_args()

    global aiotno
    aiotno = args.aiotno


# make parser work
setup_parser()

YOUR_BROKER = 'Broker IP'  # the public of your VM
topic = 'Your_Topic'  # subscribe topic
filename = f"{aiotno}_log.csv"  # your file name with "ABSOLUTE PATH" if you need linux crontab

df = pd.read_csv(filename)  # read log.csv
final_row_list = df.tail(1).values.tolist()[0]  # get tail data of log file, and turn them into list
final_row_list_str = [str(int) for int in final_row_list]  # turn int into str
print(final_row_list_str)

# send message
msg = ",".join(final_row_list_str)  # turn list into string
# print(msg)  # see what is msg before send
publish.single(topic, msg, hostname=YOUR_BROKER)  # send msg to broker
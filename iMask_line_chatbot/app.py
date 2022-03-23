from __future__ import unicode_literals
from flask import Flask, request, abort, render_template, url_for, session,redirect
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import json
from datetime import datetime
import configparser
import os
from urllib import parse
import pymysql
import traceback  
app = Flask(__name__, static_url_path='/static')
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])


config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))
my_line_id = config.get('line-bot', 'my_line_id')
end_point = config.get('line-bot', 'end_point')
line_login_id = config.get('line-bot', 'line_login_id')
line_login_secret = config.get('line-bot', 'line_login_secret')
my_phone = config.get('line-bot', 'my_phone')
HEADER = {
    'Content-type': 'application/json',
    'Authorization': F'Bearer {config.get("line-bot", "channel_access_token")}'
}


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return 'ok'
    body = request.json
    events = body["events"]
    print(body)
    if "replyToken" in events[0]:
        payload = dict()
        replyToken = events[0]["replyToken"]
        payload["replyToken"] = replyToken
        if events[0]["type"] == "message":
            if events[0]["message"]["type"] == "text":
                text = events[0]["message"]["text"]

                if text == "一般使用者":
                    payload["messages"] = [peopleLocation()]
                elif text == "打卡":

                    payload["messages"] = [{
                                            "type": "template",
                                            "altText": "打卡",
                                            "template": {
                                                "type": "buttons",
                                                "text": "請選擇打卡地點",
                                                "actions": [
                                                    {
                                                        "type": "location",
                                                        "label": "Location"
                                                    }
                                                ]
                                            }
                                        }]

                elif text == "打卡查詢":
                    payload["messages"] = [dakaSearch()]

                elif text == "中壢店":
                    x = '中壢店'
                    a = data(x)[0][0]
                    b = data(x)[0][1]
                    c = data(x)[0][2]
                    payload["messages"] = [
                        {
                            "type": "text",
                            "text": f"您好:{a}\n "
                                    f"在{b}\n "
                                    f"人流量為{c}"
                        }
                    ]

                elif text == "桃園店":
                    x = '桃園店'
                    a = data(x)[0][0]
                    b = data(x)[0][1]
                    c = data(x)[0][2]
                    payload["messages"] = [
                        {
                            "type": "text",
                            "text": f"您好:{a}\n "
                                    f"在{b}\n "
                                    f"人流量為{c}"
                        }
                    ]

                elif text == "測試":
                    payload["messages"] = [flex_test()]

                elif text == "日報表":
                    payload["messages"] = [chartTime(1234)]

                elif text == "月報表":
                    payload["messages"] = [monthReport()]

                elif text == "季報表":
                    payload["messages"] = [seasonReport()]
                elif text == "疫情":
                    payload["messages"] = [covid19maps()]
                    
                elif text == "登出":
                    x = events[0]['source']['userId']
                    outuserid(x)
                    payload["messages"] = [getoffStickerMessage()] 
                    
                else:
                    payload["messages"] = [
                            {
                                "type": "text",
                                "text": text
                            }
                        ]
                replyMessage(payload)

            elif events[0]["message"]["type"] == "location":
                x = events[0]['source']['userId']
                latitude = events[0]["message"]["latitude"]
                longitude = events[0]["message"]["longitude"]
                if (24.957 <= latitude <= 24.960) and (121.225 <= longitude <= 121.2261):
                    daka(x)
                    payload["messages"] = [getPlayStickerMessage()]
                    replyMessage(payload)
                    
                else:
                    payload["messages"] = [
                        {
                            "type": "text",
                            "text": "請誠實打卡!!!"
                        }
                    ]
                    replyMessage(payload)
          

        elif events[0]["type"] == "postback":
            if events[0]["postback"]["data"] == 'storeId=123':
                x = events[0]["postback"]["params"]["date"]
                y = events[0]['source']['userId']
                try:
                    a = showDakaSearchFirst(x, y)[0][0]
                    b = showDakaSearchFirst(x, y)[0][1]
                    c = showDakaSearchlast(x, y)[0][0]
                    d = showDakaSearchlast(x, y)[0][1]
                    payload["messages"] = [
                        {
                            "type": "text",
                            "text": f"第一次打卡時間:{a} {b}\n最後一次打卡時間:{c} {d}"
                        }]

                    replyMessage(payload)
                except IndexError:
                    payload["messages"] = [
                        {
                            "type": "text",
                            "text": f"該日沒有打卡紀錄"
                        }]

                    replyMessage(payload)
                    
            elif events[0]["postback"]["data"] == 'storeId=1234':
                x = events[0]["postback"]["params"]["date"]
                y = x.split("-")
                payload["messages"] =[chartDay(y[1], y[2])]
                
                replyMessage(payload)
            
            elif events[0]["postback"]["data"] == 'menu1':
                payload["messages"] = [covid19maps()]
                replyMessage(payload)
                
            elif events[0]["postback"]["data"] == 'menu2':
                payload["messages"] = [dakaSearch()]
                replyMessage(payload)
            
            elif events[0]["postback"]["data"] == 'menu3':
                payload["messages"] = [region()]
                replyMessage(payload)
                
            elif events[0]["postback"]["data"] == 'menu0':
                payload["messages"] = [region()]
                replyMessage(payload)
                
            elif events[0]["postback"]["data"] == 'menu4':
                payload["messages"] = [report()]
                replyMessage(payload)
            
            elif events[0]["postback"]["data"] == 'menu5':
                x = events[0]["source"]["userId"]
                payload["messages"] = [getoffStickerMessage()]
                replyMessage(payload)
                outuserid(x)
            
            elif 'region' in events[0]["postback"]["data"]:
                if events[0]["postback"]["data"] == 'region=north':
                    payload["messages"] =[north()]
                    replyMessage(payload)
                elif events[0]["postback"]["data"] == 'region=central':
                    payload["messages"] =[central()]
                    replyMessage(payload)
                elif events[0]["postback"]["data"] == 'region=south':
                    payload["messages"] =[south()]
                    replyMessage(payload)
                elif events[0]["postback"]["data"] == 'region=east':
                    payload["messages"] =[east()]
                    replyMessage(payload)
                
            elif events[0]["postback"]["data"] == 'month=1':
                x = events[0]["postback"]["data"]
                y = x.split("=")
                payload["messages"] =[chartMonth(y[1])]
                replyMessage(payload)
                
            elif events[0]["postback"]["data"] == 'month=2':
                x = events[0]["postback"]["data"]
                y = x.split("=")
                payload["messages"] =[chartMonth(y[1])]
                replyMessage(payload)
                
            elif events[0]["postback"]["data"] == 'month=3':
                x = events[0]["postback"]["data"]
                y = x.split("=")
                payload["messages"] =[chartMonth(y[1])]
                replyMessage(payload)
            
            elif events[0]["postback"]["data"] == 'month=4':
                x = events[0]["postback"]["data"]
                y = x.split("=")
                payload["messages"] =[chartMonth(y[1])]
                replyMessage(payload)
            
            elif events[0]["postback"]["data"] == 'month=5':
                x = events[0]["postback"]["data"]
                y = x.split("=")
                payload["messages"] =[chartMonth(y[1])]
                replyMessage(payload)
            
            elif events[0]["postback"]["data"] == 'month=6':
                x = events[0]["postback"]["data"]
                y = x.split("=")
                payload["messages"] =[chartMonth(y[1])]
                replyMessage(payload)
                
            elif events[0]["postback"]["data"] == 'month=7':
                x = events[0]["postback"]["data"]
                y = x.split("=")
                payload["messages"] =[chartMonth(y[1])]
                replyMessage(payload)
            
            elif events[0]["postback"]["data"] == 'month=8':
                x = events[0]["postback"]["data"]
                y = x.split("=")
                payload["messages"] =[chartMonth(y[1])]
                replyMessage(payload)
            
            elif events[0]["postback"]["data"] == 'month=9':
                x = events[0]["postback"]["data"]
                y = x.split("=")
                payload["messages"] =[chartMonth(y[1])]
                replyMessage(payload)
            
            elif events[0]["postback"]["data"] == 'month=10':
                x = events[0]["postback"]["data"]
                y = x.split("=")
                payload["messages"] =[chartMonth(y[1])]
                replyMessage(payload)
            
            elif events[0]["postback"]["data"] == 'month=11':
                x = events[0]["postback"]["data"]
                y = x.split("=")
                payload["messages"] =[chartMonth(y[1])]
                replyMessage(payload)
                
            elif events[0]["postback"]["data"] == 'month=12':
                x = events[0]["postback"]["data"]
                y = x.split("=")
                payload["messages"] =[chartMonth(y[1])]
                replyMessage(payload)
            
            elif events[0]["postback"]["data"] == 'season=1':
                x = events[0]["postback"]["data"]
                y = x.split("=")
                payload["messages"] =[chartSeason(y[1])]
                replyMessage(payload)
            
            elif events[0]["postback"]["data"] == 'season=2':
                x = events[0]["postback"]["data"]
                y = x.split("=")
                payload["messages"] =[chartSeason(y[1])]
                replyMessage(payload)
            
            elif events[0]["postback"]["data"] == 'season=3':
                x = events[0]["postback"]["data"]
                y = x.split("=")
                payload["messages"] =[chartSeason(y[1])]
                replyMessage(payload)
            
            elif events[0]["postback"]["data"] == 'season=4':
                x = events[0]["postback"]["data"]
                y = x.split("=")
                payload["messages"] =[chartSeason(y[1])]
                replyMessage(payload)
                
            elif events[0]["postback"]["data"] == 'day':
                payload["messages"] = [chartTime(1234)]
                replyMessage(payload)
            
            elif events[0]["postback"]["data"] == 'month':
                payload["messages"] = [monthReport()]
                replyMessage(payload)
            
            elif events[0]["postback"]["data"] == 'season':
                payload["messages"] = [seasonReport()]
                replyMessage(payload)
            
            
    return 'OK'


def getPlayStickerMessage(): #標示打卡成功用的
    message = dict()
    message["type"] = "sticker"
    message["packageId"] = "6325"
    message["stickerId"] = "10979904"
    return message


def replyMessage(payload):
    response = requests.post("https://api.line.me/v2/bot/message/reply",headers=HEADER,data=json.dumps(payload))
    return 'OK'


def pushMessage(payload):
    response = requests.post("https://api.line.me/v2/bot/message/push",headers=HEADER,data=json.dumps(payload))
    return 'OK'

def getoffStickerMessage():
    message = dict()
    message["type"] = "sticker"
    message["packageId"] = "8525"
    message["stickerId"] = "16581300"
    return message  
  

def daka(x):  # 打卡功能
    connection = pymysql.connect(host="hostname",
                                 user="username",
                                 password="password",
                                 database="database")


    cursor = connection.cursor()
    create_date = datetime.today().strftime('%Y-%m-%d')  # 得到當前日期
    create_time = datetime.today().strftime('%H:%M:%S')  # 得到當前時間
    # 在mysql中，時間資料也是字串，故create_date和create_time還要有一組雙引號
    sql = f"insert into wlog (EMPNO , CREATE_DATE, CREATE_TIME) values ('{x}', '{create_date}', '{create_time}')"
    cursor.execute(sql)

    connection.commit()
    cursor.close()
    connection.close()


def data(x):  # 人流查詢功能
    connection = pymysql.connect(host="hostname",
                                 user="username",
                                 password="password",
                                 database="database")

    cursor = connection.cursor()
    # 在mysql中，時間資料也是字串，故create_date和create_time還要有一組雙引號
    d = datetime.today().strftime('%Y-%m-%d')
    h = datetime.now().hour
    sql = f'''
        select s.RDATE, a.LOCATION, s.NOWIN
        from slog s join aiot a on s.AIOTNO = a.AIOTNO
        where
        s.AIOTNO = (select AIOTNO from aiot where location = "{x}")
        and RDATE = '{d}' and hour(RTIME) = {h}
        order by RDATE desc , RTIME desc  
        limit 1;
        '''
    cursor.execute(sql)
    result = cursor.fetchall()
    connection.commit()
    cursor.close()
    connection.close()
    return result


def dakaSearch(): #打卡時間選擇
    message = {
        "type": "flex",
        "altText": "this is a flex message",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "horizontal",
                "justifyContent": "center",
                "contents": [
                    {
                        "type": "text",
                        "text": "請選擇查詢時間",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#FFFFFFFF",
                        "align": "center",
                        "contents": []
                    },
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [{"type": "button",
                              "action": {
                                            "type": "datetimepicker",
                                            "label": "Select date",
                                            "data": "storeId=123",
                                            "mode": "date"
                              }
                              }
                            ]
                
            },
              "styles": {
                "header": {
                          "backgroundColor": "#67C9D4FF",
                            },
                "footer": {
                          "backgroundColor": "#D6F2EDFF"
                            }
            }
        }
    }
    return message


def showDakaSearchFirst(x, y):  # 打卡查詢功能
    connection = pymysql.connect(host="hostname",
                                 user="username",
                                 password="password",
                                 database="database")

    cursor = connection.cursor()
    # 在mysql中，時間資料也是字串，故create_date和create_time還要有一組雙引號

    sql = f"""select CREATE_DATE, CREATE_TIME 
                from wlog
                where CREATE_DATE ='{x}' and EMPNO = '{y}'
                order by CREATE_TIME 
                limit 1;
                """
    cursor.execute(sql)
    result = cursor.fetchall()
    connection.commit()
    cursor.close()
    connection.close()
    return result


def showDakaSearchlast(x, y):  # 打卡查詢功能
    connection = pymysql.connect(host="hostname",
                                 user="username",
                                 password="password",
                                 database="database")

    cursor = connection.cursor()
    # 在mysql中，時間資料也是字串，故create_date和create_time還要有一組雙引號

    sql = f"""select CREATE_DATE, CREATE_TIME 
                from wlog
                where CREATE_DATE ='{x}' and EMPNO = '{y}'
                order by CREATE_TIME desc 
                limit 1;
                """
    cursor.execute(sql)
    result = cursor.fetchall()
    connection.commit()
    cursor.close()
    connection.close()
    return result


def userIdVs():  # 打卡查詢功能
    connection = pymysql.connect(host="hostname",
                                 user="username",
                                 password="password",
                                 database="database")

    cursor = connection.cursor()
    # 在mysql中，時間資料也是字串，故create_date和create_time還要有一組雙引號
    sql = f"""select distinct EMPNO
                from wlog;
                """
    cursor.execute(sql)
    result = cursor.fetchall()
    connection.commit()
    cursor.close()
    connection.close()
    return result


def region():
    message = {"type": "flex",
               "altText": "this is a flex message",
               "contents": {
                        "type": "bubble",
                        "header": {
                                      "type": "box",
                                      "layout": "horizontal",
                                      "justifyContent": "center",
                                      "contents": [
                                          {
                                              "type": "text",
                                              "text": "人流查詢",
                                              "weight": "bold",
                                              "size": "xl",
                                              "color": "#FFFFFFFF",
                                              "align": "center",
                                              "contents": []
                                          },
                                      ]
                                  },
                        "footer": {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "backgroundColor": "#D6F2EDFF",
                                    "contents": [{"type": "button",
                                                  "action": {
                                                      "type": "postback",
                                                      "label": "北區",
                                                      "data": "region=north"
                                                  }
                                                  },
                                                 {"type": "button",
                                                  "action": {
                                                      "type": "postback",
                                                      "label": "中區",
                                                      "data": "region=central"
                                                  }
                                                  },
                                                 {"type": "button",
                                                  "action": {
                                                      "type": "postback",
                                                      "label": "南區",
                                                      "data": "region=south"
                                                  }
                                                  },
                                                 {"type": "button",
                                                  "action": {
                                                      "type": "postback",
                                                      "label": "東區",
                                                      "data": "region=east"
                                                  }
                                                  }
                                                ]
                                  },
                         "styles": {
                           "header": {
                               "backgroundColor": "#67C9D4FF",
                                     }
                                    }
                        }
                }
    return message


def north():
    message = {
                "type": "flex",
                "altText": "this is a flex message",
                "contents": {
                                "type": "bubble",
                                "header": {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "justifyContent": "center",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "人流查詢",
                                            "weight": "bold",
                                            "size": "xl",
                                            "color": "#FFFFFFFF",
                                            "align": "center",
                                            "contents": []
                                        },
                                    ]
                                },
                                "footer": {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "backgroundColor": "#D6F2EDFF",
                                    "contents": [{
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "flex": 1,
                                                    "contents": [
                                                                 {"type": "button",
                                                                  "action": {
                                                                             "type": "message",
                                                                             "label": "中壢店",
                                                                             "text": "中壢店"
                                                                            }
                                                                 },
                                                                {"type": "button",
                                                                 "action": {
                                                                             "type": "message",
                                                                             "label": "桃園店",
                                                                             "text": "桃園店"
                                                                            }
                                                                 },
                                                                {"type": "button",
                                                                 "action": {
                                                                             "type": "message",
                                                                             "label": "台北店",
                                                                             "text": "台北店"
                                                                            }
                                                                 },
                                                                {"type": "button",
                                                                 "action": {
                                                                             "type": "message",
                                                                             "label": "板橋店",
                                                                             "text": "板橋店"
                                                                            }
                                                                 },
                                                                {"type": "button",
                                                                 "action": {
                                                                             "type": "message",
                                                                             "label": "竹科店",
                                                                             "text": "竹科店"
                                                                            }
                                                                 },                                
                                                                {"type": "button",
                                                                 "action": {
                                                                             "type": "message",
                                                                             "label": "宜蘭店",
                                                                             "text": "宜蘭店"
                                                                            }
                                                                 }
                                                                ]
                                                 },
                                                 {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "flex": 2,
                                                    "contents": [
                                                                 {"type": "button",
                                                                  "action": {
                                                                              "type": "message",
                                                                              "label": "信義店",
                                                                              "text": "信義店"
                                                                            }
                                                                  },
                                                                 {"type": "button",
                                                                  "action": {
                                                                              "type": "message",
                                                                              "label": "內湖店",
                                                                              "text": "內湖店"
                                                                            }
                                                                  },
                                                                 {"type": "button",
                                                                  "action": {
                                                                              "type": "message",
                                                                              "label": "新竹店",
                                                                              "text": "新竹店"
                                                                            }
                                                                  },
                                                                 {"type": "button",
                                                                  "action": {
                                                                              "type": "message",
                                                                              "label": "新北店",
                                                                              "text": "新北店"
                                                                            }
                                                                  },
                                                                 {"type": "button",
                                                                  "action": {
                                                                              "type": "message",
                                                                              "label": "竹科二店",
                                                                              "text": "竹科二店"
                                                                            }
                                                                  },
                                                                  {"type": "button",
                                                                  "action": {
                                                                              "type": "postback",
                                                                              "label": "區域列表",
                                                                              "data": "menu3"
                                                                            }
                                                                  },
                                                                ]
                                                 }
                                                ]
                                            },
                                            "styles": {
                                                "header": {
                                                          "backgroundColor": "#67C9D4FF",
                                                            }

                                            }
                            }
            }
    return message


def central():
    message = {
                "type": "flex",
                "altText": "this is a flex message",
                "contents": {
                                "type": "bubble",
                                "header": {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "justifyContent": "center",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "人流查詢",
                                            "weight": "bold",
                                            "size": "xl",
                                            "color": "#FFFFFFFF",
                                            "align": "center",
                                            "contents": []
                                        },
                                    ]
                                },
                                "footer": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "backgroundColor": "#D6F2EDFF",
                                    "contents": [
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "message",
                                                                 "label": "台中店",
                                                                 "text": "台中店"
                                                               }
                                                    },
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "message",
                                                                 "label": "清水店",
                                                                 "text": "清水店"
                                                               }
                                                    },
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "message",
                                                                 "label": "苗栗店",
                                                                 "text": "苗栗店"
                                                               }
                                                    },
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "postback",
                                                                 "label": "區域列表",
                                                                 "data": "menu3"
                                                               }
                                                    }
                                                 ]
                                            }, 
                                            "styles": {
                                                "header": {
                                                          "backgroundColor": "#67C9D4FF",
                                                            }

                                                          }
                            }
            }
    return message


def south():
    message = {
                "type": "flex",
                "altText": "this is a flex message",
                "contents": {
                                "type": "bubble",
                                "header": {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "justifyContent": "center",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "人流查詢",
                                            "weight": "bold",
                                            "size": "xl",
                                            "color": "#FFFFFFFF",
                                            "align": "center",
                                            "contents": []
                                        },
                                    ]
                                },
                                "footer": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "backgroundColor": "#D6F2EDFF",
                                    "contents": [
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "message",
                                                                 "label": "高雄店",
                                                                 "text": "高雄店"
                                                               }
                                                    },
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "message",
                                                                 "label": "台南店",
                                                                 "text": "台南店"
                                                               }
                                                    },
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "message",
                                                                 "label": "嘉義店",
                                                                 "text": "嘉義店"
                                                               }
                                                    },
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "message",
                                                                 "label": "義大店",
                                                                 "text": "義大店"
                                                               }
                                                    },
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "message",
                                                                 "label": "屏東店",
                                                                 "text": "屏東店"
                                                               }
                                                    },
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "message",
                                                                 "label": "巨蛋店",
                                                                 "text": "巨蛋店"
                                                               }
                                                    },
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "postback",
                                                                 "label": "區域列表",
                                                                 "data": "menu3"
                                                               }
                                                    }
                                                 ]
                                            }, 
                                            "styles": {
                                                "header": {
                                                          "backgroundColor": "#67C9D4FF",
                                                            }

                                                          }
                            }
            }
    return message


def east():
    message = {
                "type": "flex",
                "altText": "this is a flex message",
                "contents": {
                                "type": "bubble",
                                "header": {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "justifyContent": "center",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "人流查詢",
                                            "weight": "bold",
                                            "size": "xl",
                                            "color": "#FFFFFFFF",
                                            "align": "center",
                                            "contents": []
                                        },
                                    ]
                                },
                                "footer": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "backgroundColor": "#D6F2EDFF",
                                    "contents": [
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "message",
                                                                 "label": "花蓮店",
                                                                 "text": "花蓮店"
                                                               }
                                                    },
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "postback",
                                                                 "label": "區域列表",
                                                                 "data": "menu3"
                                                               }
                                                    }
                                                 ]
                                            }, 
                                            "styles": {
                                                "header": {
                                                          "backgroundColor": "#67C9D4FF",
                                                            }

                                                          }
                            }
            }
    return message


# def changeBot():  # 跳轉linebot
#     message = {
#         "type": "template",
#         "altText": "this is a confirm template",
#         "template": {
#             "type": "confirm",
#             "text": "請問是否要連接至員工工作區",
#             "actions": [
#                 {
#                     "type": "uri",
#                     "label": "是",
#                     "uri": 'https://line.me/ti/p/@202qizud'
#                 },
#                 {
#                     "type": "message",
#                     "label": "否",
#                     "text": "否"
#                 }
#             ]
#         }
#     }
#     return message


def report():
    message = {
        "type": "flex",
        "altText": "this is a flex message",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "horizontal",
                "justifyContent": "center",
                "contents": [
                    {
                        "type": "text",
                        "text": "報表選擇",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#FFFFFFFF",
                        "align": "center",
                        "contents": []
                    },
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [{"type": "button",
                              "action": {
                                           "type": "postback",
                                           "label": "日報表",
                                           "data": "day"
                                          }
                                       
                              },
                             {"type": "button",
                              "action": {
                                           "type": "postback",
                                           "label": "月報表",
                                           "data": "month"
                                          }
                                       
                              },
                             {"type": "button",
                              "action": {
                                           "type": "postback",
                                           "label": "季報表",
                                           "data": "season"
                                          }
                                       
                              },
                             ]
            },
              "styles": {
                "header": {
                          "backgroundColor": "#67C9D4FF",
                            },
                "footer": {
                          "backgroundColor": "#D6F2EDFF"
                            }
            }
        }
    }
    return message



def chartDay(x, y):  # 日報表
    message = {
                "type": "image",
                "originalContentUrl": F"{end_point}/static/day_pic/day_{x}{y}.png",
                "previewImageUrl": F"{end_point}/static/day_pic/day_{x}{y}.png"
              }
    return message


def chartMonth(x):  # 月報表
    message = {
                "type": "image",
                "originalContentUrl": F"{end_point}/static/month_pic/month_{x}.png",
                "previewImageUrl": F"{end_point}/static/month_pic/month_{x}.png"
              }
    return message


def chartSeason(x):  # 季報表
    message = {
                "type": "image",
                "originalContentUrl": F"{end_point}/static/season_pic/season_{x}.png",
                "previewImageUrl": F"{end_point}/static/season_pic/season_{x}.png"
              }
    return message


def chartTime(x):  # 選擇報表時間
    message = {
        "type": "flex",
        "altText": "this is a flex message",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "horizontal",
                "justifyContent": "center",
                "contents": [
                    {
                        "type": "text",
                        "text": "請選擇查詢時間",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#FFFFFFFF",
                        "align": "center",
                        "contents": []
                    },
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [{"type": "button",
                              "action": {
                                          "type": "datetimepicker",
                                          "label": "Select date",
                                          "data": f"storeId={x}",
                                          "mode": "date"
                              }
                              }
                             ]
            },
              "styles": {
                "header": {
                          "backgroundColor": "#67C9D4FF",
                            },
                "footer": {
                          "backgroundColor": "#D6F2EDFF"
                            }
                        }
        }
    }
    return message


def monthReport():  # 月報表選單
    message = {
          "type": "flex",
          "altText": "this is a flex message",
          "contents": {
                        "type": "bubble",
                        "header": {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "justifyContent": "space-between",
                                    "contents": [
                                                  {
                                                    "type": "text",
                                                    "text": "月報表-月份選擇",
                                                    "weight": "bold",
                                                    "size": "xl",
                                                    "color": "#FFFFFFFF",
                                                    "align": "center",
                                                    "contents": []
                                                  }
                                                ]
                                  },
                        "footer": {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [{
                                                        "type": "box",
                                                        "layout": "vertical",
                                                        "flex": 1,
                                                        "contents": [
                                                                        {"type": "button",
                                                                         "action": {
                                                                                    "type": "postback",
                                                                                    "label": "1月",
                                                                                    "data": "month=1"
                                                                                  }
                                                                         },
                                                                        {"type": "button",
                                                                          "action": {
                                                                             "type": "postback",
                                                                             "label": "2月",
                                                                             "data": "month=2"
                                                                                    }
                                                                         },
                                                                        {"type": "button",
                                                                         "action": {
                                                                             "type": "postback",
                                                                             "label": "3月",
                                                                             "data": "month=3"
                                                                         }
                                                                         },
                                                                        {"type": "button",
                                                                         "action": {
                                                                             "type": "postback",
                                                                             "label": "4月",
                                                                             "data": "month=4"
                                                                         }
                                                                         },
                                                                        {"type": "button",
                                                                         "action": {
                                                                             "type": "postback",
                                                                             "label": "5月",
                                                                             "data": "month=5"
                                                                         }
                                                                         },
                                                                        {"type": "button",
                                                                         "action": {
                                                                             "type": "postback",
                                                                             "label": "6月",
                                                                             "data": "month=6"
                                                                         }
                                                                         }
                                                                    ]
                                                  },
                                                    {
                                                        "type": "box",
                                                        "layout": "vertical",
                                                        "flex": 2,
                                                        "contents": [
                                                            {"type": "button",
                                                             "action": {
                                                                 "type": "postback",
                                                                 "label": "7月",
                                                                 "data": "month=7"
                                                             }
                                                             },
                                                            {"type": "button",
                                                             "action": {
                                                                 "type": "postback",
                                                                 "label": "8月",
                                                                 "data": "month=8"
                                                             }
                                                             },
                                                            {"type": "button",
                                                             "action": {
                                                                 "type": "postback",
                                                                 "label": "9月",
                                                                 "data": "month=9"
                                                             }
                                                             },
                                                            {"type": "button",
                                                             "action": {
                                                                 "type": "postback",
                                                                 "label": "10月",
                                                                 "data": "month=10"
                                                             }
                                                             },
                                                            {"type": "button",
                                                             "action": {
                                                                 "type": "postback",
                                                                 "label": "11月",
                                                                 "data": "month=11"
                                                             }
                                                             },
                                                            {"type": "button",
                                                             "action": {
                                                                 "type": "postback",
                                                                 "label": "12月",
                                                                 "data": "month=12"
                                                             }
                                                             }
                                                        ]
                                                    }
                                                ]
                                  },
                        "styles": {
                            "header": {
                                    "backgroundColor": "#67C9D4FF",
                                        },
                            "footer": {
                                    "backgroundColor": "#D6F2EDFF"
                                        }
                                    }
        }
    }
    return message



def seasonReport():  # 季報表選單
    message = {
          "type": "flex",
          "altText": "this is a flex message",
          "contents": {
                        "type": "bubble",
                        "header": {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "justifyContent": "center",
                                    "contents":[
                                                  {
                                                    "type": "text",
                                                    "text": "季度",
                                                    "weight": "bold",
                                                    "size": "xl",
                                                    "color": "#FFFFFFFF",
                                                    "align": "center",
                                                    "contents": []
                                                  }
                                                ]
                                  },
                        "footer": {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [{"type": "button",
                                                      "action": {
                                                                  "type": "postback",
                                                                  "label": "第一季",
                                                                  "data": "season=1"
                                                                }
                                                                },
                                                     {"type": "button",
                                                      "action": {
                                                                  "type": "postback",
                                                                  "label": "第二季",
                                                                  "data": "season=2"
                                                                }
                                                                },
                                                     {"type": "button",
                                                      "action": {
                                                                  "type": "postback",
                                                                  "label": "第三季",
                                                                  "data": "season=3"
                                                                }
                                                                },
                                                     {"type": "button",
                                                      "action": {
                                                                  "type": "postback",
                                                                  "label": "第四季",
                                                                  "data": "season=4"
                                                                }
                                                                }

                                                ]
                                  },
                                  "styles": {
                                    "header": {
                                            "backgroundColor": "#67C9D4FF",
                                                },
                                    "footer": {
                                            "backgroundColor": "#D6F2EDFF"
                                                }
                                            }
                        }
                }
    return message


def covid19maps():  # covid19疫情地圖
    message = {
          "type": "flex",
          "altText": "this is a flex message",
          "contents": {
                        "type": "bubble",
                        "hero": {
                                    "type": "image",
                                    "url": F"{end_point}/static/covid19.png",
                                    "size": "full",
                                    "aspectMode": "cover"
                                },
                        "header": {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "justifyContent": "center",
                                    "contents":[
                                                  {
                                                    "type": "text",
                                                    "text": "ovid-19疫情地圖",
                                                    "weight": "bold",
                                                    "size": "xl",
                                                    "color": "#FFFFFFFF",
                                                    "align": "center",
                                                    "contents": []
                                                  }
                                                ]
                                  },
                        "footer": {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [{"type": "button",
                                                      "action": {
                                                                  "type": "uri",
                                                                  "label": "當日台灣確診人數地圖",
                                                                  "uri": "https://covid19.biobank.org.tw/narl/city_today.aspx"
                                                                }
                                                                },
                                                    {"type": "button",
                                                      "action": {
                                                                  "type": "uri",
                                                                  "label": "台灣確診人數累計地圖",
                                                                  "uri": "https://covid19.biobank.org.tw/narl/city_total.aspx"
                                                                }
                                                                },
                                                    {"type": "button",
                                                      "action": {
                                                                  "type": "uri",
                                                                  "label": "全球累計確診地圖",
                                                                  "uri": "https://covid-19.nchc.org.tw/map.php"
                                                                 }
                                                     }

                                                ]
                                  },
                                    "styles": {
                                    "header": {
                                              "backgroundColor": "#67C9D4FF",
                                                },
                                    "footer": {
                                              "backgroundColor": "#D6F2EDFF"
                                                }
                                            }
        }
    }
    return message
    
@app.route('/login', methods=["GET", "POST"])
def line_login():
    if request.method == 'POST':
        ACCOUNT = request.form['ACCOUNT']
        PASSW = request.form['PASSW']
        connection = pymysql.connect(host="hostname",
                                     user="username",
                                     password="password",
                                     database="database")
        cursor = connection.cursor()

        sql = f"""select e.* 
                  from emp e 
                  where e.ACCOUNT ='{ACCOUNT}' and e.PASSW ='{PASSW}';
                  """	
        cursor.execute(sql)
        user = cursor.fetchall()
        cursor.close()
        if len(user) != 1:
            return redirect('https://domain/loginerror')
        else:
            return redirect('https://domain/loginok');
    else:
        return render_template("imask-login.html")
    
    connection.commit()
    connection.close()

def outuserid(x):
    line_bot_api.unlink_rich_menu_from_user(x)
    
@app.route('/loginerror')
def line_error():
    return render_template("login-error.html")
    
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


@app.route('/loginok', methods=['GET',"POST"])
def loginok():
    global userID
    code = request.args.get("code", None)
    state = request.args.get("state", None)
    if code and state:
            HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}
            url = "https://api.line.me/oauth2/v2.1/token"
            FormData = {"grant_type": 'authorization_code', "code": code, "redirect_uri": F"{end_point}/loginok",
                        "client_id": line_login_id, "client_secret": line_login_secret}
            data = parse.urlencode(FormData)
            content = requests.post(url=url, headers=HEADERS, data=data).text
            content = json.loads(content)
            url = "https://api.line.me/v2/profile"
            HEADERS = {'Authorization': content["token_type"] + " " + content["access_token"]}
            content = requests.get(url=url, headers=HEADERS).text
            content = json.loads(content)
            name = content["displayName"]
            userID = content["userId"]
            # pictureURL = content["pictureUrl"]
            # statusMessage = content["statusMessage"]
            print(content)
            print('登入成功', userID)
            line_bot_api.link_rich_menu_to_user(userID, 'richmenu-e6120436c6919eade5f8162193654230')
            return render_template("login-ok.html")
    return redirect(f'https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id={line_login_id}&redirect_uri={end_point}/loginok&scope=profile%20openid%20email&state=123453sdfgfd')



  
if __name__ == "__main__":
    app.debug = True
    app.run()


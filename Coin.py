# -*- coding:utf8 -*-

"""
"""

import requests
#import json
import schedule
import datetime
import sched
import time
import collections
import logging

logger_name = 'coin'

logging.basicConfig(filename='logger.log', leve=logging.INFO)

logger = logging.getLogger(__name__)



class Coin():

    def __init__(self, name, drawed, price, percent, total, c_name, coin_detail, icon, coin_id, coin_num, online_time):
        self.name = name
        self.drawed = drawed
        self.price = price
        self.percent = percent
        self.total = total
        self.c_name = c_name
        self.coin_detail = coin_detail
        self.icon = icon
        self.coin_id = coin_id
        self.coin_num = coin_num
        self.online_time = online_time

    def description(self):
        return self.c_name + "coin at" + self.online_time + "can draw" + self.coin_num

"""获取验证码， 以及验证码签名"""
def request_captcha():
    captcha_url = "http://api.dqdgame.com/app/captcha/get?test=0"

    header = {"X-Requested-With": "com.manymanycoin.android",
              "authorization": "1c6b5e2129cb20297eb438ace708408bd5d43423b411265ba8a0025083fb2c",
              "uuid": "@3rbV2tIxYRCgAB2wracnvoW4tnWgkBnyGcJisjpr3x9XBiREXEzCk8oLa8ZSMMWyWMvS3CfYeRo=",
              "User-Agent": "Mozilla/5.0 (Linux; Android 8.0.0; MI 6 Build/OPR1.170623.027; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/65.0.3325.109 Mobile Safari/537.36 NewsApp/4 Rong/2.0 NetType/ news/4",
              "Referer": "https://m.dqdgame.com/getCoins"
              }

    captcha_req = requests.get(captcha_url, headers=header)
    if captcha_req.status_code == requests.codes.ok:
        captcha_sign = captcha_req.headers["captcha-sign"]
        resp = captcha_req.json()
        captcha = resp["data"]["captcha"]
        print captcha + "--------" + captcha_sign
        return captcha, captcha_sign


"""
draw coin, when 
"""
def draw_coin(code_id):
    captcha, captcha_sign = request_captcha()
    draw_url = "http://api.dqdgame.com/app/benefit/draw"
    coin = TODAY_DRAWABLE_COINS[code_id]
    draw_msg = "draw coin", code_id, coin.c_name
    logging.info(draw_msg)
    draw_header = {"X-Requested-With": "com.manymanycoin.android",
                   "authorization": "1c6b5e2129cb20297eb438ace708408bd5d43423b411265ba8a0025083fb2c",
                   "uuid": "@3rbV2tIxYRCgAB2wracnvoW4tnWgkBnyGcJisjpr3x9XBiREXEzCk8oLa8ZSMMWyWMvS3CfYeRo=",
                   "User-Agent": "Mozilla/5.0 (Linux; Android 8.0.0; MI 6 Build/OPR1.170623.027; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/65.0.3325.109 Mobile Safari/537.36 NewsApp/4 Rong/2.0 NetType/ news/4",
                   "Referer": "https://m.dqdgame.com/getCoins",
                   "Origin": "https://m.dqdgame.com",
                   "captcha-code": captcha,
                   "captcha-sign": captcha_sign,
                   "id": str(code_id)
                   }

    payload = {"id": str(code_id)}

    requests.post(draw_url, data=payload, headers=draw_header)

    create_draw_coin_sched(code_id + 1)


# cache today all drawable coins
TODAY_DRAWABLE_COINS = []


def request_coin_list():
    coin_url = 'https://api.dqdgame.com/app/benefit/list'
    # headers = {"Referer": "https://m.dqdgame.com/getCoins",
    #            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E5216a BDD/1.3.1 NetType/NA Technology/Wifi bundleID/com.manymanycoin.yyc (iPhone; iOS 11.3; Scale/2.00) (modelIdentifier/iPhone8,1 )",
    #            "Access-Control-Request-Headers": "authorization,uuid,version-name"}
    req = requests.get(coin_url)
    json = req.json()

    coin_data = json["data"]
    current_coins = {}

    for coin in coin_data:
        c = Coin(coin["name"], coin["drawed"], coin["price"], coin["percent"], coin["num"], coin["cn_name"], coin["detail_url"], coin["icon"],
                 int(coin["id"]), coin["unit"], coin["online_time"])
        current_coins[c.coin_id] = c
# as online_time des
    return current_coins


def create_draw_coin_sched(coin_id):
    last_coin_id = TODAY_DRAWABLE_COINS.keys()[-1]
    if last_coin_id < coin_id:
        return
    coin = TODAY_DRAWABLE_COINS[coin_id]
    draw_date = datetime.datetime.strptime(coin.online_time, "%Y-%m-%d %H:%M:%S")
    seconds_delta = int((draw_date - datetime.datetime.now()).total_seconds())
    if seconds_delta > 0 or coin.percent != "100%":
        s = sched.scheduler(time.time, time.sleep)
        seconds_delta += 3.0
        s.enter(seconds_delta, 0, draw_coin, (coin_id, ))

        info = "current draw coin id is", coin_id, 'coin name is ', coin.c_name,'and minutes is ', seconds_delta / 60.0
        print 'log msg 1', info
        logger.info(info)
        s.run()
    else:
        msg = coin_id, ' current percentage ', coin.percent
        print 'log msg ', msg
        logger.info(msg)
        create_draw_coin_sched(coin_id + 1)

if __name__ == '__main__':
    TODAY_DRAWABLE_COINS = request_coin_list()
    TODAY_DRAWABLE_COINS = collections.OrderedDict(sorted(TODAY_DRAWABLE_COINS.items()))
    create_draw_coin_sched(TODAY_DRAWABLE_COINS.keys()[0])

# -*- coding:utf8 -*-

import requests
import YiMa_SMS
from time import sleep
import logging
import time
import string
import random


Token = '00397229e4479e2d92629ff4049e09a49da7af66'
Base_Url = 'http://api.fxhyd.cn/UserInterface.aspx?' + 'token=' + Token
ym = YiMa_SMS.YiMaSMS()

t = int(time.time())

logger_name = "example"
logger = logging.getLogger(logger_name)
logger.setLevel(logging.INFO)

# create file handler

log_path = "./log/log" + str(t) + '.log'
fh = logging.FileHandler(log_path)
fh.setLevel(logging.ERROR)

# create formatter
fmt = "%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d %(message)s"
datefmt = "%a %d %b %Y %H:%M:%S"
formatter = logging.Formatter(fmt, datefmt)

# add handler and formatter to logger
fh.setFormatter(formatter)
logger.addHandler(fh)

startIndex  = 0

'''
获取登录的验证码
'''
def get_liepiao_login_sms(phone):

    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Mobile/14E304',
               'Accept-Encoding': 'gzip, deflate',
               'Origin': 'file://',
               'Content-Type': "application/json",
               "Accept": "application/json, text/plain, */*"}
    register_url = 'https://service.liepiaowang.com/api/user/customer/registerOrLogin/appRequest'

    pay_load = {
                    'mobile': phone,
                    'validatedStr': 'mzOfVvWJ6EOuec1NOaGWV82MKr/3Hd5YOC3SqExB0y0='
                }

    requests.post(register_url, json=pay_load, headers=headers, verify=False)


def login_liepiao_with_sms(sms, phone):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Mobile/14E304',
        'Accept-Encoding': 'gzip, deflate',
        'Origin': 'file://',
        'Content-Type': "application/json",
        "Accept": "application/json, text/plain, */*"}

    request_url = 'https://service.liepiaowang.com/api/user/customer/registerOrLogin/finish?mobile=' + phone + '&dynamicKey=' + sms
    req = requests.post(request_url, headers=headers, verify=False)

    return req.json()


def get_liepiao_change_pwd_sms(auth_key, phone):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Mobile/14E304',
        'Accept-Encoding': 'gzip, deflate',
        'Origin': 'file://',
        'Content-Type': "application/json",
        "Accept": "application/json, text/plain, */*",
        'x-auth-token': auth_key,
    }

    request_url = 'https://service.liepiaowang.com/api/user/customer/account/change_password/request?mobile=' + phone

    req = requests.post(request_url, headers=headers, verify=False)
    print req.status_code


def set_password(auth_key, phone, sms):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Mobile/14E304',
        'Accept-Encoding': 'gzip, deflate',
        'Origin': 'file://',
        'Content-Type': "application/json",
        "Accept": "application/json, text/plain, */*",
        'x-auth-token': auth_key,
    }

    pwd = generate_activation_code(10)

    pay_load = {
        'mobile': phone,
        'dynamicKey': sms,
        'password': pwd
    }

    requests_url = 'https://service.liepiaowang.com/api/user/customer/account/change_password/finish'
    req = requests.post(requests_url, json=pay_load, headers=headers, verify=False)

    if req.status_code == requests.codes.ok:
        msg = 'phone is: ' + phone + ' password is ' + pwd
        logger.error(msg)


def generate_activation_code(len=16, n=1):
    random.seed()
    chars = string.ascii_letters + string.digits
    return [''.join([random.choice(chars) for _ in range(len)]) for _ in range(n)][0]


def create_liepiao_user():
    # 获取手机号码
    print('start get phone number')
    phone = ym.get_phone_number_by_item_id('1906')
    if phone is None:
        return
    print('get phone number is' + phone)
    phone = phone.encode('utf-8')
    print('start get sms')
    get_liepiao_login_sms(phone)
    # 发送验证码
    sms_code = None
    item_id = '1906'

    count = 0

    while True:
        if sms_code is None or sms_code == '3001':
            if count > 7:
                release_mobile(phone)
                return
            sms_code = ym.get_sms_by_item_id(item_id, phone, False)
            sleep(8)
            count += 1
        else:
            print sms_code
            break

    # 登录
    print('start login new user')
    auth_info = login_liepiao_with_sms(sms_code, phone)
    auth_token = auth_info['token']
    auth_token = auth_token.encode('utf-8')

    print auth_info

    # 获取设置密码的验证码
    print('start get change pwd sms')
    get_liepiao_change_pwd_sms(auth_token, phone)

    sms_code = None
    # 获取设置验证码的code
    count = 0
    while True:
        if sms_code is None or sms_code == '3001':
            if count > 7:
                release_mobile(phone)
            sms_code = ym.get_sms_by_item_id(item_id, phone, True)
            sleep(8)
            count += 1
        else:
            print sms_code
            break
    logger.info('change pwd')
    set_password(auth_token, phone, sms_code)

    global startIndex
    startIndex += + 1

    if startIndex < 300:
        sleep(5)
        print('start create user')
        create_liepiao_user()


def release_mobile(phone):
    ym.release_phone(phone)
    create_liepiao_user()


if __name__ == '__main__':
    print startIndex
    create_liepiao_user()
# -*- coding: utf-8 -*-
# @Time    : 2018/4/21 上午11:07
# @Author  : Aries
# @Site    : 
# @File    : YiMa_SMS.py
# @Software: PyCharm

import requests
import re


class YiMaSMS():

    def __init__(self):
        self.token = '00397229e4479e2d92629ff4049e09a49da7af66'
        self.base_url = 'http://api.fxhyd.cn/UserInterface.aspx?' + 'token=' + self.token + '&isp = 1'

    def get_sms_by_item_id(self, item_id, phone, is_release):
        action = 'action=getsms'
        sms_req_url = self.base_url + '&' + action + '&itemid=' + item_id + '&mobile=' + phone
        if is_release:
            sms_req_url = sms_req_url + '&release=1'

        sms_req = requests.get(sms_req_url)

        if sms_req.status_code == requests.codes.ok:
            result = sms_req.text
            result = result.encode('utf-8')
            pattern = '\d{6}'
            code = re.search(pattern, result)
            if code:
                return code.group()
            else:
                return None
        elif sms_req.status_code == 3001:
            return '3001'
        else:
            return None

    def get_phone_number_by_item_id(self, item_id):
        action = 'action=getmobile'
        phone_number_request_url = self.base_url + '&' + action + '&itemid=' + item_id
        req = requests.get(phone_number_request_url)
        resp_str = req.text
        print(req.content)
        split_str = '|'
        if len(resp_str) == 19 and split_str in resp_str:
            phone_str = resp_str.split(split_str)[1]

            return phone_str

        return None

    def release_phone(self, phone):
        action = '&action=release&itemid=1906'
        release_url = self.base_url + action + '&mobile=' + phone
        requests.get(release_url)
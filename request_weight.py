import asyncio
from time import sleep, time
import requests
import sys


import configs
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class request_weight:
    def __init__(self):
        self.req_header = {'Connection': 'close', 'cache-control': 'max-age=0', 'x-cache': 'Miss from cloudfront'}
        get_weight_fs_r = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo", headers=self.req_header)
        get_weight_fs = get_weight_fs_r.json()["rateLimits"]
        for i in get_weight_fs:
            if i["rateLimitType"] == "REQUEST_WEIGHT":
                self.req_limit = i["limit"]
                req_int = i["interval"]
                req_int_num = i["intervalNum"]

        if req_int == "SECOND":
            req_int_l = 1
        elif req_int == "MINUTE":
            req_int_l = 60
        elif req_int == "HOUR":
            req_int_l = 3600
        elif req_int == "DAY":
            req_int_l = 86400

        self.reset_time = req_int_num * req_int_l
        self.weight = int(get_weight_fs_r.headers['x-mbx-used-weight-1m'])

    def close_weight(self):
        print("Weight kapatıldı")
        sys.exit()

    def update_weight(self):
        get_weight_fs_r = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo", headers=self.req_header)
        get_weight_fs = get_weight_fs_r.json()["rateLimits"]
        for i in get_weight_fs:
            if i["rateLimitType"] == "REQUEST_WEIGHT":
                self.req_limit = i["limit"]
                req_int = i["interval"]
                req_int_num = i["intervalNum"]

        if req_int == "SECOND":
            req_int_l = 1
        elif req_int == "MINUTE":
            req_int_l = 60
        elif req_int == "HOUR":
            req_int_l = 3600
        elif req_int == "DAY":
            req_int_l = 86400

        self.reset_time = req_int_num * req_int_l

    def reset_weight(self):
        sayac = 0
        while True:
            try:
                serv = requests.get("https://fapi.binance.com/fapi/v1/time", headers=configs.header).json()
                self.server_time = serv["serverTime"] / 1000 + 2
                sleep(self.reset_time - (self.server_time % self.reset_time) + 2)
                print("Weight sıfırlanıyor...")
                self.weight = 0
                if sayac == 10:
                    self.update_weight()
                    sayac = 0
                sayac += 1

            except Exception as E:
                print("Weight hata verdi:", E)


    def check_server_wei(self, server_wei):
        if self.weight < 100:
            pass
        elif server_wei < self.weight - 500 or server_wei > self.weight:
            self.weight = server_wei



    def check_weight(self):
        if self.weight > self.req_limit - 500:
            return False
        else:
            return True

    def add_weight(self, add_weight):
        self.weight = self.weight + add_weight

    def get_weight(self):
        return self.weight

    def set_weight(self, set_weight):
        self.weight = set_weight

    async def get(self, session, url, add_weight):
        while True:
            self.add_weight(add_weight)
            if self.check_weight():
                try:
                    async with session.get(url) as response:
                        #self.check_server_wei(int(response.headers['x-mbx-used-weight-1m']))
                        #print(f"{int(response.headers['x-mbx-used-weight-1m'])} ", response.headers['X-Cache'], self.weight)
                        retu = await response.json()
                    return retu
                except Exception as E :
                    print(E)
                    sleep(0.1)
                    continue
            else:
                sleep(0.5)
                continue

if "__main__" == __name__:
    test = request_weight()

    test.update_weight()
    test.update_weight()
    test.update_weight()
    test.update_weight()
    test.update_weight()
    test.update_weight()
    test.update_weight()
    test.update_weight()

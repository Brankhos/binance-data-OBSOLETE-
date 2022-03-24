import asyncio
import multiprocessing
import re
import sys
import threading
from datetime import datetime
import time
from time import sleep
import mysql.connector
from mysql.connector import errorcode
import aiohttp
import requests as requests

import configs
from database_setup import setup_cnx
from get_list import get_list
from request_weight import request_weight
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def reset_wei(weight):
    weight.reset_weight()

class random_request:
    def __init__(self, check_timeout=8):
        self.timeout = aiohttp.ClientTimeout(total=check_timeout)
        self.start_time = datetime.now()
        self.start_request_index = -1
        self.ip_and_ports = []
        self.__proxy_urls = {
            "hidemy.name": "https://hidemy.name/tr/proxy-list/?type=s#list",
            "sslproxies": "https://www.sslproxies.org/",
            "google-proxy": "https://www.google-proxy.net/",
            "free-proxy-list": "https://free-proxy-list.net/",
            "us-proxy": "https://www.us-proxy.org/",
            "free-proxy-list2": "https://free-proxy-list.net/uk-proxy.html",
            "free-proxy-list3": "https://free-proxy-list.net/anonymous-proxy.html",
            "spys": "http://spys.me/proxy.txt",
            "api.proxyscrape": "https://api.proxyscrape.com/?request=getproxies&proxytype=http&country=all&ssl=yes&anonymity=all",
            "api.proxyscrape2": "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=yes&anonymity=all&simplified=true",
            "proxynova": "https://www.proxynova.com/proxy-server-list/",
            "proxy-list": "https://www.proxy-list.download/HTTPS",
            "openproxy": "https://openproxy.space/list/http",
        }
        self.__headers = configs.header
        self.ip_and_ports_last = []
        self.start_async_update_proxy()

    def start_async_update_proxy(self):
        asyncio.run(self.async_before_update_proxys())

    async def async_before_update_proxys(self):

        for i in self.ip_and_ports_last:
            self.ip_and_ports.append(i)
        self.update_tasks = []
        connector = aiohttp.TCPConnector(limit=50)
        session = aiohttp.ClientSession(connector=connector, trust_env=True, headers=self.__headers)
        try:
            for urls in self.__proxy_urls:
                self.update_tasks.append(asyncio.create_task(self.update_proxys(session, urls)))
            await asyncio.gather(*self.update_tasks)
        except Exception as E:
            print("Session hata sonucu kapatıldı", E)
            await session.close()
        else:
            await session.close()
            # print("Tüm proxy sayısı: ", len(self.ip_and_ports))
            self.ip_and_ports = list(dict.fromkeys(self.ip_and_ports))
            cpu_count = multiprocessing.cpu_count()
            per_cpu = int(len(self.ip_and_ports) / cpu_count)
            cout = len(self.ip_and_ports) % cpu_count
            add_start = 0
            add_stop = 0
            task = []
            self.will_del_index = []
            for cpu in range(cpu_count):
                if add_stop < cout:
                    add_stop += 1
                t = threading.Thread(target=asyncio.run,
                                     args=(self.async_before_check(add_start, per_cpu * (cpu + 1) + add_stop),),
                                     daemon=True)
                task.append(t)

                add_start = per_cpu * (cpu + 1) + add_stop

            for i in task:
                i.start()
            for i in task:
                i.join()
            # print("Benzersiz proxy sayısı: ", len(self.ip_and_ports))
            # print("Bozuk proxy sayısı: ", len(self.will_del_index))
            for index in sorted(self.will_del_index, reverse=True):
                del self.ip_and_ports[index]
            self.ip_and_ports_last = self.ip_and_ports
            print("Sorunsuz proxy sayısı", len(self.ip_and_ports_last))
            self.start_request_index = 0
        finally:
            self.ip_and_ports = []
            self.update_tasks = []
            self.update_start = 0

    async def update_proxys(self, session, urls):
        try:
            if urls in ["sslproxies", "hidemy.name", "google-proxy", "free-proxy-list", "us-proxy", "free-proxy-list2",
                        "free-proxy-list3"]:
                async with session.get(self.__proxy_urls[urls], timeout=self.timeout) as r:
                    r = await r.text()
                matches = re.findall(
                    r'\d+\.\d+\.\d+\.\d+\s*</td>\s*<td>\s*\d+', r)
                proxies = [re.sub(r"\s*</td>\s*<td>\s*", ":", m) for m in
                           matches]
                for i in proxies:
                    self.ip_and_ports.append(i)
            elif urls == "spys":
                async with session.get(self.__proxy_urls[urls], timeout=self.timeout) as r:
                    r = await r.text()
                matches = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+ .*?-S!? ?\+?\-?', r)
                proxies = [re.sub(re.compile(' .*?-S!? ?\+?\-?'), "", x) for x in matches]
                for i in proxies:
                    self.ip_and_ports.append(i)
            elif urls in ["api.proxyscrape", "api.proxyscrape2"]:
                async with session.get(self.__proxy_urls[urls], timeout=self.timeout) as r:
                    r = await r.text()
                matches = re.split("\r\n", r)
                matches = matches[:-1]
                for i in matches:
                    self.ip_and_ports.append(i)
            elif urls == "proxynova":
                async with session.get(self.__proxy_urls[urls], timeout=self.timeout) as r:
                    r = await r.text()
                r = re.sub("\n* *", "", r)
                matches = re.findall(r'\(\'.*?"left">\d+', r)
                match_sub = [re.sub(r"\(?\'?\+?\)?\;?", "", x) for x in matches]
                match_sub = [re.sub(r"</script></abbr></td><tdalign=\"left\">", ":", x) for x in match_sub]
                for i in match_sub:
                    self.ip_and_ports.append(i)
            elif urls == "proxy-list":
                async with session.get(self.__proxy_urls[urls], timeout=self.timeout) as r:
                    r = await r.text()
                r = re.sub("\n* *", "", r)
                matches = re.findall(r'\d+\.\d+\.\d+\.\d+</td><td>\d+', r)
                proxies = [re.sub(r"</td><td>", ":", x) for x in matches]
                for i in proxies:
                    self.ip_and_ports.append(i)
            elif urls == "openproxy":
                async with session.get(self.__proxy_urls[urls], timeout=self.timeout) as r:
                    r = await r.text()
                matches = re.findall(r'items:\[\"\d+\.\d+\.\d+\.\d+:\d+.*?\"\]', r)
                proxies = [re.sub(re.compile(r'(items:\[\")*(\")*(\])*'), "", x) for x in matches]
                proxies_split = [re.split(",", x) for x in proxies]
                flatten_proxies = [item for sublist in proxies_split for item in sublist]
                for i in flatten_proxies:
                    self.ip_and_ports.append(i)
        except Exception as E:
            print("Şu bölümde sorun oluştu: ", urls)
            print("Hata: ", E)

    async def async_before_check(self, start_index, stop_index):
        tasks = []
        connector = aiohttp.TCPConnector(limit=50)
        session = aiohttp.ClientSession(connector=connector, trust_env=True, headers=self.__headers)

        try:
            for k, prox in enumerate(self.ip_and_ports[start_index:stop_index]):
                tasks.append(asyncio.create_task(self.async_check(session, start_index + k, prox)))
            await asyncio.gather(*tasks)

        except Exception as E:
            print("Session hata sonucu kapatıldı", E)
            await session.close()
        else:
            await session.close()

    async def async_check(self, session, current_index, prox):
        try:
            async with session.get("https://fapi.binance.com/fapi/v1/ping", proxy="http://" + prox,
                                   timeout=self.timeout):
                pass
        except:
            self.will_del_index.append(current_index)

    async def get(self, session, url):
        len_last = len(self.ip_and_ports_last)
        if len_last <= self.start_request_index:
            self.start_request_index = -1
        self.start_request_index += 1
        in_loop_start_request_index = self.start_request_index
        proxy_ip = self.ip_and_ports_last[in_loop_start_request_index]
        proxy = "http://" + proxy_ip
        while True:
            try:
                if len_last <= 2:
                    if len_last == 0:
                        proxy = None
                    if len(self.update_tasks) == 0 and self.update_start == 0:
                        threading.Thread(target=asyncio.run,
                                         args=(self.async_before_update_proxys(),),
                                         daemon=True).start()
                        self.update_start = 1
                async with session.get(url, proxy=proxy, timeout=self.timeout) as response:
                    return response
            except Exception as E:
                try:
                    self.ip_and_ports_last.remove(proxy_ip)
                except:
                    pass
                proxy_ip = self.ip_and_ports_last[
                    in_loop_start_request_index - abs(len_last - len(self.ip_and_ports_last)) + 1]
                proxy = "http://" + proxy_ip
                print("Veri alınırken hata oluştu: ", E)

async def coin_calculator(symbol_name, cursor,  session, periods, weight):

    for period in periods:
        cursor.execute("USE {}".format(configs.database_name+period))
        cursor.execute("SELECT `open_time` FROM `" + symbol_name +
                       "` ORDER BY `open_time` DESC LIMIT 1")
        try:
            last_open = cursor.fetchall()[0][0]
            cursor.execute(("DELETE FROM `{}` WHERE `open_time` = '{}'".format(symbol_name, last_open)))
            new_start = 0
        except:
            print(f"Veritabanında veri yok sıfırdan çekiliyor {symbol_name}-{period}")
            last_open = configs.start_day
            new_start = 1

        sp = int(period[:-1])

        sp2 = period[-1]

        if sp2 == "m":
            cc = 60
        elif sp2 == "h":
            cc = 3600
        elif sp2 == "d":
            cc = 86400
        elif sp2 == "w":
            cc = 604800

        start_time = (time.time() - (sp * cc * 95)) * 1000

        if last_open - start_time < 0:
            remaining_limit = 1000
            add_weight = 5
        else:
            remaining_limit = 99
            add_weight = 1

        last_stop = configs.stop_day

        if last_stop is not None and last_open >= last_stop:
            last_stop = None

        while True:
            resp = await weight.get(session, f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol_name}&interval={period}&limit={remaining_limit}&startTime={last_open}&endTime={last_stop}',add_weight)

            resp = list(resp)
            cur_time = time.time()
            diviner = cur_time % (sp * cc)
            last_cur_time = cur_time - diviner

            if configs.back_test is True and resp[-1][0] == last_cur_time:
                #print("kırıldı 1")
                resp = resp[:-1]
            if len(resp) == 0:
                #print("kırıldı 2")
                break
            add_coindata = (
                "INSERT INTO {} (open_time, open, high, low, close, volume, close_time, quote_asset_volume, number_of_trades, taker_buy_base_asset_volume, taker_buy_quote_asset_volume, ignore_it) "
                "VALUES ".format(symbol_name))
            klines = "(" + "),(".join(",".join(str(x) for x in y) for y in resp) + ")"
            add_coindata_t = add_coindata + klines
            cursor.execute("USE {}".format(configs.database_name+period))
            cursor.execute(add_coindata_t)
            last_open = int(resp[-1][6]) + 1

            """
            if configs.back_test is False and last_open > cur_time:
                print("kırıldı 3")

            elif configs.stop_day is not None and last_open >= configs.stop_day + 1:
                print("kırıldı 4")
            """
            break

    pass

async def prepare_coin(array, periods, t):
    try:
        cnx = setup_cnx(pri=False)
        cursor = cnx.cursor()
        for period in periods:
            cursor.execute("USE {}".format(configs.database_name+period))
            for symbol_name in array:
                xec = "CREATE TABLE `" + symbol_name + "` (" \
                                                       "  `open_time` bigint NOT NULL primary key," \
                                                       "  `open` FLOAT NOT NULL," \
                                                       "  `high` FLOAT NOT NULL," \
                                                       "  `low` FLOAT NOT NULL," \
                                                       "  `close` FLOAT NOT NULL," \
                                                       "  `volume` FLOAT NOT NULL," \
                                                       "  `close_time` bigint NOT NULL," \
                                                       "  `quote_asset_volume` FLOAT NOT NULL," \
                                                       "  `number_of_trades` int(11) NOT NULL," \
                                                       "  `taker_buy_base_asset_volume` FLOAT NOT NULL," \
                                                       "  `taker_buy_quote_asset_volume` FLOAT NOT NULL," \
                                                       "  `ignore_it` FLOAT NOT NULL" \
                                                       ") ENGINE=InnoDB"
                try:
                    cursor.execute(xec)
                except mysql.connector.Error:
                    pass
        tasks = []
        connector = aiohttp.TCPConnector(limit=50)
        session = aiohttp.ClientSession(connector=connector, trust_env=True, headers={'Connection': 'close', 'cache-control': 'max-age=0'})

        try:
            for symbol_name in array:
                tasks.append(asyncio.create_task(coin_calculator(symbol_name, cursor, session, periods, t)))
            await asyncio.gather(*tasks)

        except mysql.connector.Error as E:
            print("Session hata sonucu kapatıldı", E)
        finally:
            await session.close()
    finally:
        cnx.close()
        cursor.close()


def main():
    weight = request_weight()
    waitable = 0
    cpu_count = multiprocessing.cpu_count()
    cnx = setup_cnx(configs.delete_database, configs.delete_another, pri=True)
    server_datas = get_list(cnx)
    server_time = server_datas.server_time
    if waitable == 1:
        wait_time = configs.start_time_diviner - (int(server_time / 1000) % configs.start_time_diviner) - 30
    else:
        wait_time = 1
    print("Cpu Sayısı:", cpu_count)
    print(f"Hazırlıklar tamamlandı. {wait_time} saniye sonra işlemlere başlanacak.")
    print(int((wait_time / 60) / 60) % 60, "Saat", int(wait_time / 60) % 60, "Dakika", wait_time % 60, "Saniye")
    time.sleep(wait_time)
    print("30 saniye içinde işlemlere başlanacak. Proxy ve coin listesi güncelleniyor. Weight başlatılıyor")
    res_wei_task = threading.Thread(target=reset_wei, args=(weight,), daemon=True).start()
    while True:
        start_time = time.time()
        server_datas.update_coins()
        server_time = server_datas.server_time
        coin_list = server_datas.coin_infos
        periods = server_datas.periods
        if waitable == 1 :
            wait_time = configs.start_time_diviner - (int(server_time / 1000) % configs.start_time_diviner) + 1
        else:
            wait_time = 1
        print("Güncel Coin sayısı:", len(coin_list))
        print(f"Güncellemeler tamamlandı. {wait_time} saniye sonra işlemlere başlanacak.")
        print(int((wait_time / 60) / 60) % 60, "Saat", int(wait_time / 60) % 60, "Dakika", wait_time % 60, "Saniye")
        time.sleep(wait_time)
        # per_cpu = int(len(coin_list) / cpu_count)
        per_cpu = int(len(coin_list))
        cout = len(coin_list) % cpu_count
        task = []
        last_start = 0
        add_stop = 0
        listed_before = [x for x in coin_list]

        for count in range(per_cpu + 1):
            if add_stop < cout:
                add_stop += 1
            t = threading.Thread(target=asyncio.run,
                                 args=(prepare_coin(listed_before[last_start:per_cpu * (count + 1) + add_stop], periods, weight),),
                                 daemon=True)
            task.append(t)
            last_start = per_cpu * (count + 1) + add_stop
        for i in task:
            i.start()
        for i in task:
            i.join()

        server_datas.update_coins()
        server_time = server_datas.server_time
        if waitable == 1:
            wait_time = configs.start_time_diviner - (int(server_time / 1000) % configs.start_time_diviner) - 30
        else:
            wait_time = 20
        print(f"Döngü {time.time()-start_time} sürede bitirildi")
        print(f"Döngü bitirildi. {wait_time} saniye sonra işlemlere başlanacak.")
        print(int((wait_time / 60) / 60) % 60, "Saat", int(wait_time / 60) % 60, "Dakika", wait_time % 60, "Saniye")
        break


if __name__ == "__main__":
    main()

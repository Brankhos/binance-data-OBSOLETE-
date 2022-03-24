import requests
import mysql.connector
from mysql.connector import errorcode
import configs
from database_setup import setup_cnx


class get_list:
    def __init__(self, cnx):
        self.cnx = cnx
        self.coin_infos = {}
        self.block_list = []
        self.white_list = []
        self.periods = configs.using_periods
        datas = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo", headers=configs.header).json()
        symbol_infos = datas["symbols"]
        for symbol_info in symbol_infos:
            cond1 = symbol_info["quoteAsset"] == "USDT"
            cond2 = symbol_info["status"] == "TRADING"
            cond3 = symbol_info["contractType"] == "PERPETUAL"
            cond4 = not symbol_info["baseAsset"] in self.block_list
            if cond1 and cond2 and cond3 and cond4:
                self.coin_infos[symbol_info["symbol"]] = configs.using_periods

        self.update_database()
        serv = requests.get("https://fapi.binance.com/fapi/v1/time", headers=configs.header).json()
        self.server_time = serv["serverTime"]

    def update_coins(self):
        temple_coin_infos = {}
        datas = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo", headers=configs.header).json()
        symbol_infos = datas["symbols"]
        for symbol_info in symbol_infos:
            cond1 = symbol_info["quoteAsset"] == "USDT"
            cond2 = symbol_info["status"] == "TRADING"
            cond3 = symbol_info["contractType"] == "PERPETUAL"
            cond4 = not symbol_info["baseAsset"] in self.block_list
            if cond1 and cond2 and cond3 and cond4:
                if symbol_info["symbol"] in self.coin_infos:
                    temple_coin_infos[symbol_info["symbol"]] = self.coin_infos[symbol_info["symbol"]]
                else:
                    temple_coin_infos[symbol_info["symbol"]] = configs.using_periods

        self.coin_infos = temple_coin_infos
        self.update_database()
        serv = requests.get("https://fapi.binance.com/fapi/v1/time", headers=configs.header).json()
        self.server_time = serv["serverTime"]

    def update_database(self):
        cursor = self.cnx.cursor()
        for period in configs.using_periods:
            cursor.execute("USE `{}`".format(configs.database_name + period))
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            will_del = [item[0] for item in tables if item[0].upper() not in self.coin_infos]
            for del_item in will_del:
                print(f"Coin siliniyor: {del_item}-{period}\t", end="")
                try:
                    cursor.execute("DROP TABLE {}".format(del_item))
                except mysql.connector.Error as err:
                    if err.errno == errorcode.ER_BAD_TABLE_ERROR:
                        print("Başarısız")
                    else:
                        print(err)
                else:
                    print("Başarılı")
        cursor.close()


if __name__ == '__main__':
    cnx2 = setup_cnx(configs.delete_database)

    get_list(cnx2)

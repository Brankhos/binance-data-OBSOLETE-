database_name = "test_coins_"
delete_database = False

back_test = True

delete_another = {"setting": False, "output": False}
header = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Connection': 'close',
            'Referer': 'https://www.google.com/'
        }

db_att = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'raise_on_warnings': True,
    'autocommit': True
}
import time

# Bütün periyodlar
usable_periods = {"1w": {"calculate": False, "check_signal": None},
                  "1d": {"calculate": True, "check_signal": None},
           "12h": {"calculate": False, "check_signal": None},
           "4h": {"calculate": False, "check_signal": None},
           "1h": {"calculate": False, "check_signal": "down"},
           "30m": {"calculate": False, "check_signal": None},
           "15m": {"calculate": True, "check_signal": None},
           "5m": {"calculate": True, "check_signal": None},
           "1m": {"calculate": False, "check_signal": None},
                  }
current_time = time.time()

# Periyodlardaki en geniş zaman dilimine göre stop zamanı
if back_test == True:
    for period in usable_periods:
        if usable_periods[period]["calculate"]:
            time_symbol = period[-1]
            if time_symbol == "w":
                multiplier = 604800
            elif time_symbol == "d":
                multiplier = 86400
            elif time_symbol == "h":
                multiplier = 3600
            elif time_symbol == "m":
                multiplier = 60
            mod_value = int(period[:-1]) * multiplier
            ex_time = current_time % mod_value
            stop_day = (int(current_time - ex_time) * 1000) - 1
            break
else:
    stop_day = None

# Periyodlardaki en geniş zaman dilimine göre start zamanı
start_day_mod = current_time % (604800)
start_day = int(current_time - 604800 * 9 - start_day_mod) * 1000
print(start_day)
# Her periyodun içindeki gerekli değerler
period_detail = {"ashi_bar": None,
                 "ashi_signal": None}
using_periods = {}

# Periyodlara gerekli değerlerin yerleştirilmesi
for period in usable_periods:
    if usable_periods[period]["calculate"]:
        using_periods[period] = period_detail | {"check_signal": usable_periods[period]["check_signal"]}

time_multiplier ={}
for k,using_period in enumerate(using_periods):
    if k == 0:
        time_multip = 1
    else:
        if last_w == using_period[-1]:
            time_multip = last_v / int(using_period[:-1])
        elif using_period[-1] == "d":
            if last_w == "w":
                time_multip = (7 * last_v) / int(using_period[:-1])
        elif using_period[-1] == "h":
            if last_w == "w":
                time_multip = (7 * 24 * last_v) / int(using_period[:-1])
            elif last_w == "d":
                time_multip = (24 * last_v) / int(using_period[:-1])
        elif using_period[-1] == "m":
            if last_w == "w":
                time_multip = (7 * 24 * 60 * last_v) / int(using_period[:-1])
            elif last_w == "d":
                time_multip = (24 * 60 * last_v) / int(using_period[:-1])
            elif last_w == "h":
                time_multip = (60 * last_v) / int(using_period[:-1])
    time_multiplier[using_period] = int(time_multip)

    last_w = using_period[-1]
    last_v = int(using_period[:-1])

reversed_time_cap = dict(reversed(list(usable_periods.items())))
for reversed_time in reversed_time_cap:
    if reversed_time_cap[reversed_time]["calculate"]:
        time_symbol = reversed_time[-1]
        if time_symbol == "w":
            start_time_diviner = 604800
        elif time_symbol == "d":
            start_time_diviner = 86400
        elif time_symbol == "h":
            start_time_diviner = 3600
        elif time_symbol == "m":
            start_time_diviner = 60

        start_time_diviner *= int(reversed_time[:-1])

        break
if __name__ == '__main__':
    print(time_multiplier)
    print(dict(reversed(list(usable_periods.items()))))
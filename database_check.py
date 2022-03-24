from database_setup import setup_cnx

cnx = setup_cnx(pri=True)
cursor = cnx.cursor()
cursor.execute("USE test_coins_1d")
cursor.execute("SELECT `open_time` FROM `btcusdt` ORDER BY `open_time`")
datas = cursor.fetchall()

print(len(datas))
for k,i in enumerate(datas):
    if k == 0:
        continue
    if datas[k][0] == datas[k-1][0] + 300000*12*24:
        print("yes")
    else:
        print("no")


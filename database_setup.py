from mysql.connector import pooling
import configs
from mysql.connector import errorcode
import mysql.connector


def setup_cnx(delete_database=False, delete_another=None, pri=False):
    if delete_another is None:
        delete_another = {"setting": False, "output": False}

    config = configs.db_att

    try:
        cnx = mysql.connector.connect(**config)
        if pri:
            print("Veritabanına bağlantı başarılı")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print("", err)
    cnx.autocommit = True

    cursor = cnx.cursor()
    for period in configs.using_periods:
        if pri:
            print(f"{period}\t\t", end="")


        if delete_database:
            try:
                cursor.execute("DROP DATABASE `{}`".format(configs.database_name + period))  # Databaseyi silmek için
                if pri:
                    print("Veritabanı silindi.\t\t", end="")
            except mysql.connector.Error as err:
                if pri:
                    print("Veritabanı silinemedi.\t", end="")
                if err.errno == errorcode.ER_DB_DROP_EXISTS:
                    if pri:
                        print("Veritabanı yok.\t\t")
                else:
                    print(err)
        if period in configs.using_periods:
            try:
                cursor.execute("CREATE DATABASE `{}`".format(configs.database_name + period))
                if pri:
                    print("Veritabanı oluşturuldu.")
            except mysql.connector.Error as E:
                if E.errno == errorcode.ER_DB_CREATE_EXISTS:
                    if pri:
                        print("Veritabanı zaten var.")
                else:
                    print(E)


    for deleting in delete_another:
        if pri:
            print(f"{deleting.capitalize()}\t\t", end="")
        if delete_another[deleting]:
            try:
                cursor.execute("DROP DATABASE `{}`".format(configs.database_name + deleting))  # Databaseyi silmek için
                if pri:
                    print("Veritabanı silindi.\t\t", end="")
            except mysql.connector.Error as err:
                if pri:
                    print("Veritabanı silinemedi.\t", end="")
                if err.errno == errorcode.ER_DB_DROP_EXISTS:
                    if pri:
                        print("Veritabanı yok.\t\t", end="")
                else:
                    print(err)
        try:
            cursor.execute("CREATE DATABASE `{}`".format(configs.database_name + deleting))
            if pri:
                print("Veritabanı oluşturuldu.")
        except mysql.connector.Error as E:
            if E.errno == errorcode.ER_DB_CREATE_EXISTS:
                if pri:
                    print("Veritabanı zaten var.")
            else:
                print(E)

    cursor.close()

    return cnx


if __name__ == "__main__":
    setup_cnx(True,{"setting": True, "output": True}, pri=True)

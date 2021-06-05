import psycopg2
import configparser

config = configparser.ConfigParser()
config.read("config/settings.ini")

try:
    connection = psycopg2.connect(
        database=config["PostgreSQL"]["database"],
        user=config["PostgreSQL"]["user"],
        password=config["PostgreSQL"]["password"],
        host=config["PostgreSQL"]["host"],
        port=config["PostgreSQL"]["port"]
    )
    print("connect!")
except Exception as err:
    raise Exception("Ошибка подключения к БД", err)

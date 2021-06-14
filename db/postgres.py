import psycopg2
from psycopg2 import Error
import logging


class Postgres:
    def __init__(self, config):
        try:
            self.connection = psycopg2.connect(
                database=config["database"],
                user=config["user"],
                password=config["password"],
                host=config["host"],
                port=config["port"]
            )
            self.cursor = self.connection.cursor()
            logging.info("Подключение к БД установлено")
        except (Exception, Error) as error:
            logging.critical("Ошибка подключения к БД: {0}".format(error))
            raise Error("Ошибка подключения к БД", error)

    def get_location(self, location, rounding):
        try:
            logging.info("Обработка точки ({lng} {lat})...".format(lng=location["lng"], lat=location["lat"]))
            query = """SELECT segment_id 
                       FROM geozone 
                       WHERE ST_Distance('POINT({lng} {lat})', coordinates) < {rounding}
                       ORDER BY parent_id
                       LIMIT 1; 
                    """.format(lng=location["lng"], lat=location["lat"], rounding=rounding)
            self.cursor.execute(query)
            raw = self.cursor.fetchone()
            if raw:
                return raw[0]

            return 0
        except (Exception, Error) as error:
            logging.error(
                "Ошибка выполнения запроса с параметрами POINT({lng} {lat}, rounding={rounding}: {error}".format(
                    lng=location["lng"], lat=location["lat"], rounding=rounding, error=error))
            return 0

    def __del__(self):
        try:
            if self.connection:
                self.cursor.close()
                self.connection.close()
                logging.info("Соединение с БД закрыто")
        except AttributeError as error:
            logging.error("Ошибка при закрытии соединения с БД: {0}".format(error))

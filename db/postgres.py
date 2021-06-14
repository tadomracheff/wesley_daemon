import psycopg2
from psycopg2 import Error


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
            print("Connect")
        except (Exception, Error) as error:
            raise Error("Ошибка подключения к БД", error)

    def get_location(self, location, rounding):
        try:
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
            print("err", error)
            return 0

    def __del__(self):
        try:
            if self.connection:
                self.cursor.close()
                self.connection.close()
        except AttributeError as error:
            print(error)

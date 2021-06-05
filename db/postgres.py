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


def get_location(lat, lng):
    try:
        cursor = connection.cursor()
        query = """SELECT segment_id 
                   FROM geozone 
                   WHERE ST_Distance('POINT({lng} {lat})', coordinates) < {rounding}
                   ORDER BY parent_id
                   LIMIT 1; 
                """.format(lng=lng, lat=lat, rounding=config["common"]["rounding"])
        cursor.execute(query)
        raw = cursor.fetchone()
        if raw:
            return raw[0]

        return 0
    except Exception as err:
        print("err", err)

        return 0
    finally:
        if connection:
            cursor.close()

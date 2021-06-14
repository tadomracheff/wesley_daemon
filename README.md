Демон для проекта "Часы Уизли". Отлеживает изменения координат пользователей в FiriStore и отправляет клиенту arduino пакет с id пользователя и id сегмента часов по постоянному сокетному соединению

## Предварительные условия
* Python 3
* PostgreSQL
* Postgis

## Установка
### Установка проекта
`git clone https://github.com/taprigorodoff/wesley_server` <br>
`pip install -r requirements.txt` <br> 

### Firestore
* создать проект Firebase, завести учетную запись службы для связи с Firebase, создать файл конфигурации serviceAccount.json (https://firebase.google.com/docs/admin/setup#python_1)
* разместить serviceAccount.json в директории проекта
* в файле конфигурации проекта config/settings.ini в блоке Firestore прописать путь до serviceAccount.json 
* в базе Firebase создать коллекцию <br>`<название_коллекции>/<логин_пользователя_в_firestore>/<документ с полями lat и lng>`
* в файле конфигурации проекта config/settings.ini в блоке Firestore в поле listen_collection прописать <название_коллекции> для прослушивания

### Инициализация БД
* создать пустую базу в PostgreSQL
* в файле конфигурации config/settings.ini в блоке PostgreSQL прописать параметры для подключения к бд
* выполнить:<br>
```
CREATE EXTENSION postgis; 

CREATE TABLE public.segment (
	id int4 NOT NULL, -- id сегмента часов
	description text NULL, -- описание 
	CONSTRAINT segment_pkey PRIMARY KEY (id)
);

CREATE TABLE public.geozone (
	id serial NOT NULL,
	"name" text NULL, -- название объекта геометрии
	coordinates geometry NOT NULL, -- объект геометрии
	segment_id int4 NOT NULL,
	parent_id int4 NULL, -- внешний ключ на эту же таблицу для обеспечения иерархии геозон (если один объект включает в себя другой, например, точка больницы в полигоне города)  
	CONSTRAINT geozone_pkey PRIMARY KEY (id)
);

ALTER TABLE public.geozone ADD CONSTRAINT fk_geozone_geozone_parent FOREIGN KEY (parent_id) REFERENCES public.geozone(id);
ALTER TABLE public.geozone ADD CONSTRAINT fk_geozone_segment FOREIGN KEY (segment_id) REFERENCES public.segment(id);
```
* заполнить базу данными. <br>
Объекты геометрии заполнять в формате EPSG:4326 <br>
`(POINT(lng lat), LINESTRING(lng_1 lat_1, ..., lng_n lat_n ), POLYGON((lng_1 lat_1, ..., lng_n lat_n, lng_1 lat_1)))`

### Логирование
* в файле конфигурации config/settings.ini в блоке Logging прописать параметры для логирования

### Информация о пользователях
* в файле конфигурации config/settings.ini в блоке users прописать пользователей в формате <br>
`<логин_пользователя_в_firestore>=<id_пользователя_для_arduino>`

## Запуск
`python3 main.py`

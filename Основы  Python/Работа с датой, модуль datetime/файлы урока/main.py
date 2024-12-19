"""
модуль datetime для работы со временем и датой
- класс date
- класс time
- класс datetime
- класс timedelta
"""
# import datetime

# date_time_now = datetime.datetime.now()
# date_now = datetime.date.today()
# time_now = datetime.datetime.now().time()
# print(type(date_time_now), date_time_now)
# print(type(date_now), date_now)
# print(type(time_now), time_now)


# from datetime import datetime, date, timedelta, time
# print(datetime.now())


from datetime import datetime, timezone, timedelta, date, time
from time import sleep

# локальная дата и время
local_datetime = datetime.now()

# создание объекта часового пояса UTC + 3
bangkok_tz = timezone(timedelta(hours=3))

# создаем объект datetime с учетом часового пояса
bangkok_tz_datetime = datetime.now(bangkok_tz)

# получаем локальную дату и время без учета часового пояса
local_datetime_2 = datetime.today()

# получаем дату и время по UTC
utc_datetime = datetime.utcnow()

timestamp = '1734592554.24536'  # время в секундах с 1 января 1970 года
date_time_from_timestamp = datetime.fromtimestamp(float(timestamp))

date = date(2021, 1, 1)
time = time(12, 30, 5)

compare_datetime = datetime.combine(date, time)

datetime_from_cls = datetime(2021, 1, 1)

datetime_str = '12:30:05 25/07/2021'
datetime_from_str = datetime.strptime(datetime_str, '%H:%M:%S %d/%m/%Y')

# методы объекта datetime
# получение объекта date
local_datetime.date()
# получение объекта time
local_datetime.time()

# замена значений объекта datetime
local_datetime.replace(year=2022, month=1, day=1)

# преобразование объекта datetime в строку
local_datetime.strftime('%H:%M:%S %d/%m/%Y')

# преобразование объекта datetime в timestamp
local_datetime.timestamp()

# день недели с понедельника (0) по воскресенье (6)
local_datetime.weekday()

# день недели с понедельника (1) по воскресенье (7)
local_datetime.isoweekday()

# дата в формате С
local_datetime.ctime()

# дата в формате ISO
local_datetime.isoformat()

# атрибуты объекта datetime
year = local_datetime.year
month = local_datetime.month
day = local_datetime.day
hour = local_datetime.hour
minute = local_datetime.minute
second = local_datetime.second
microsecond = local_datetime.microsecond

# timedelta

# создание объекта timedelta
delta = timedelta(days=1, seconds=1, microseconds=1, milliseconds=1, minutes=1, hours=1, weeks=1)

delta2 = timedelta(days=1, seconds=1, microseconds=1, milliseconds=1, minutes=1, hours=1)

# сложение timedelta с datetime
today = date.today()
tomorrow = today + timedelta(days=1)

# вычитание timedelta из datetime
yesterday = today - timedelta(days=1)

# сложение timedelta с timedelta
two_weeks = timedelta(weeks=1) + timedelta(weeks=1)

# вычитание timedelta из timedelta
one_week = timedelta(weeks=2) - timedelta(weeks=1)

# умножение timedelta на число
three_weeks = timedelta(weeks=1) * 3

# деление timedelta на число
one_week = timedelta(weeks=2) / 2

# вычитание datetime из datetime
delta = datetime(2021, 5, 1, hour=15) - datetime(2020, 1, 1)

date_start = datetime.now()
sleep(5)
date_end = datetime.now()
print(date_end - date_start)

# сравнение объектов datetime
date1 = datetime(2021, 1, 1)
date2 = datetime(2020, 1, 1)

week_ago = datetime.now() - timedelta(weeks=1)

work_date = '2021-01-01'
work_date = datetime.strptime(work_date, '%Y-%m-%d')
if work_date < week_ago:
    print('work')

today = datetime.now() + timedelta(days=5)
print(today.strftime('%d/%m/%Y'))

date_from_table = '2021-01-01'
date_from_table = datetime.strptime(date_from_table, '%Y-%m-%d')
if date_from_table < datetime.now():
    print('work')

timestamp = 1734592554.24536

date_from_timestamp = datetime.fromtimestamp(timestamp)

if date_from_timestamp >= datetime.now():
    print('work')

deadline = datetime.now() + timedelta(minutes=30)
timestamp = deadline.timestamp()
print(int(timestamp))















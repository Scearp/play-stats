import json
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as pdt

plt.style.use('fivethirtyeight')

def parse_csv(play):
    date = pdt.date2num(datetime.strptime(play[3], "%d %b %Y %H:%M").date())
    artist = play[0]
    album = play[1]
    track = play[2]
    return [date, track, album, artist]

def parse_json(play):
    date = pdt.date2num(datetime.strptime(play['endTime'],
                                          '%Y-%m-%d %H:%M').date())
    artist = play['artistName']
    album = None
    track = play['trackName']
    play_time = play['msPlayed']
    return [play_time, date, track, album, artist]

def load_plays(filename, mn = 30000):
    file_type = filename.split('.')[-1]
    if file_type == 'json':
        with open(filename, encoding="utf-8") as jf:
            data = json.load(jf)
            all_plays = map(parse_json, data)
            valid_plays = filter(lambda p: p[0] >= mn, all_plays)
            plays = list(map(lambda p: p[1:], valid_plays))
    elif file_type == 'csv':
        with open(filename, "r") as csvfile:
            reader = csv.reader(csvfile, delimiter=',',quotechar='|')
            plays = list(map(parse_csv, reader))
    else:
        raise ValueError("Unsupported filetype: %s" % file_type)
    return(plays)

def track_plays(plays):
    tracks = list(map(lambda p: "%s - %s" % (p[1], p[3], plays)))
    dates = list(map(lambda p: p[0], plays))
    return list(zip(dates, tracks))

def album_plays(plays):
    valid_plays = filter(lambda p: p[2] != None, plays)
    albums = map(lambda p: "%s - %s" % (p[2], p[3]), valid_plays)
    dates = map(lambda p: p[0], valid_plays)
    return list(zip(dates, albums))

def artist_plays(plays):
    artists = map(lambda p: p[3], plays)
    dates = map(lambda p: p[0], plays)
    return list(zip(dates, artists))

def trailing_sum(y, trail):
    if trail > 1:
        return list(map(lambda i: sum(y[i:i + trail]),
                        list(range(0, len(y)))[trail:]))
    else:
        return y

def running_sum(y, trail):
    if trail > 1:
        return list(map(lambda i: sum(y[i - trail:i]),
                        list(range(0, len(y)))[trail:]))
    else:
        return y

def prepend_sum(x, y, y_daily, trail):
    y_pre = []
    if trail > 1:
        y_pre.append(y_daily[0])
        for i in range(1, trail):
            y_pre.append(sum(y_daily[0:i]))
    x = [x[0] - 1] + x
    y = [0] + y_pre + y
    while len(x) < len(y):
        x.append(x[len(x) - 1] + 1)

    return [x, y]

def plot(daily_plays, trail = 1):
    trail -= 1
    x = sorted(list(daily_plays.keys()))
    y_daily = list(map(lambda d: daily_plays[d], x))
    y = running_sum(y_daily + [0] * (trail + 1), trail)
    xy = prepend_sum(x, y, y_daily, trail)
    x = xy[0]
    y = xy[1]

    plt.plot(x, y)
    plt.gca().xaxis.set_major_formatter(pdt.DateFormatter('%d/%m/%Y'))

def weekly_plays(daily_plays, period = 7, weekday = 3):
    trail = period - 1
    x = sorted(list(daily_plays.keys()))
    y_daily = list(map(lambda d: daily_plays[d], x))
    y = running_sum(y_daily + [0] * period, trail)

    xy = prepend_sum(x, y, y_daily, trail)
    x = xy[0][1:]
    y = xy[1][1:]

    daily_dictionary = {}
    i = 0
    while i < len(x):
        daily_dictionary[x[i]] = y[i]
        i += 1
    x = list(filter(lambda a: pdt.num2date(a).weekday() == weekday, x))
    y = list(map(lambda a: daily_dictionary[a], x))

    i = 0
    weekly_dictionary = {}
    while i < len(x):
        weekly_dictionary[x[i]] = y[i]
        i += 1

    return weekly_dictionary

def fill_dict(days):
    start = min(days)
    end = int(max(days))
    filled_days = [start + i for i in range(end - int(start) + 1)]
    return dict(zip(filled_days, [0] * len(filled_days)))

def daily(name, play_list):
    plays = list(filter(lambda p: name in p, play_list))
    days = set(map(lambda p: p[0], plays))
    daily_plays = fill_dict(days)
    for p in plays:
        daily_plays[p[0]] += 1
    return daily_plays

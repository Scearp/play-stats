import json
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as pdt

plt.style.use('fivethirtyeight')

def load_albums():
    albums = []

    with open("./resources/album.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=',',quotechar='|')
        for r in reader:
            albums.append([r[0], r[1], r[2]])
            
    return albums

def load_plays(filename, mn = 30000):
    track_plays = []
    artist_plays = []
    album_plays = []

    if "json" in filename:
        with open(filename, encoding="utf-8") as jf:
            data = json.load(jf)
            for track in data:
                if track["msPlayed"] > mn:
                    date = pdt.date2num(datetime.strptime(track["endTime"],
                                                          "%Y-%m-%d %H:%M").date())
                    track_plays.append([date,
                                        track["trackName"] + " - "
                                        + track["artistName"]])
                    artist_plays.append([date, track["artistName"]])
                    for a in albums:
                        if track["trackName"] in a:
                            if track["artistName"] == a[2]:
                                album_plays.append([date, a[1] + " - "
                                                    +  track["artistName"]])
    if "csv" in filename:
        with open(filename, "r") as csvfile:
            reader = csv.reader(csvfile, delimiter=',',quotechar='|')
            for r in reader:
                date = pdt.date2num(datetime.strptime(r[3], "%d %b %Y %H:%M").date())
                track_plays.append([date, r[2] + " - " + r[0]])
                album_plays.append([date, r[1] + " - " + r[0]])
                artist_plays.append([date, r[0]])

    return([track_plays, album_plays, artist_plays])

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

def fill(daily_dict):
    start = min(daily_dict)
    end = max(daily_dict)

    for i in range(int(end - start)):
        if (start + i) not in daily_dict:
            daily_dict[start + i] = 0  

    return daily_dict

def daily(name, play_list):
    plays = filter(lambda p: name in p, play_list)
    daily_plays = {}

    for p in plays:
        try:
            daily_plays[p[0]] += 1
        except:
            daily_plays[p[0]] = 1

    return fill(daily_plays)

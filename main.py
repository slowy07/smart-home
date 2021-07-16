import datetime

import requests
from bs4 import BeautifulSoup

night_label = []
for night in range(17, 24):
    night_label.append(night)

time_now = datetime.datetime.now()
time_now_res = str(time_now.strftime("%H"))

web = requests.get(
    "https://weather.com/id-ID/weather/today/l/ed6821bd8cf3ad861528ee66546ca0573862c4e1678f1c85732fba7d3e5298f1"
)
getpar = BeautifulSoup(web.text, "html.parser")
location = getpar.find("h1", class_="CurrentConditions--location--2_osB").text
weather_info = getpar.find("div", class_="CurrentConditions--phraseValue--17s79").text
temperature = getpar.find("div", class_="CurrentConditions--primary--39Y3f").span.text


print(type(location))
print(type(temperature))
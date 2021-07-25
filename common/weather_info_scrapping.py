import requests
from bs4 import BeautifulSoup


class Weather_information:
    def __init__(self, link):
        self.link = link
        self.web = requests.get(str(link))
        self.get_dat = BeautifulSoup(self.web.text, "html.parser")

    def get_time_location(self):
        time_location = self.get_dat.find("div", class_="CurrentConditions--timestamp--3_-CV").text
        return time_location

    def get_data_location(self):
        location = self.get_dat.find("h1", class_="CurrentConditions--location--2_osB").text
        return location

    def get_current_temp(self):
        current_temp = self.get_dat.find('div', class_="CurrentConditions--primary--39Y3f").span.text
        return current_temp

    def get_current_weather_information(self):
        current_weather_information = self.get_dat.find("div", class_="CurrentConditions--phraseValue--17s79").text
        return current_weather_information
    
    def get_prediction_weather_information(self):
        get_current_prediction = self.get_dat.find("div", class_="CurrentConditions--precipValue--1RgXi").span.text
        return get_current_prediction

    def get_air_quality(self):
        get_air_quality = self.get_dat.find("div", class_="AirQuality--col--44Mxy").text
        return get_air_quality

    def get_max_min_temperature(self):
        get_max_min_temp = self.get_dat.find("div", class_="WeatherDetailsListItem--wxData--2bzvn").text
        return get_max_min_temp
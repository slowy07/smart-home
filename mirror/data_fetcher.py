import pandas
import logging
from bs4 import BeautifulSoup
import requests

# weather_info = pandas.read_csv('data/weather_info.csv')
# print(weather_info.loc[weather_info['Year'] == 2018].values[0])
# print(weather_info.loc[weather_info['Year'] == 2018])
# print(weather_info.at[147,"Fahrenheit High Temp"])
LINK = 'https://weather.com/id-ID/weather/today/l/be2f7870c2d1f8d852e68f947ef0293164afb704a7dfc18bc7f3d53aa76c575c'


class weather_info:
    def __init__(self, path):
        self.path = pandas.read_csv(path)
        try:
            if self.path is None:
                logging.info("Path is not found!")
        except Exception as error:
            logging.exception(f"Error : {error}")

    def getWheaterInfoTemperature(self, temperature_type):
        try:
            if temperature_type == 'Fahrenheit':
                temperature = self.path.at[147, "Fahrenheit High Temp"]
                type = 'F'
            elif temperature_type == 'Celcius':
                temperature = self.path.at[147, "Celcius High Temp"]
                type = 'C'
        except Exception as error:
            logging.exception(f"Error : {error}")

        return f"{temperature}°{type}"
    
    def getWheaterInfo(self):
        return "Snow"

class weather_scrapping:
    def __init__(self, link_req):
        self.link = requests.get(link_req)
        self.data_scrapping = BeautifulSoup(self.link.text, "html.parser")

    
    def get_weather_information(self):
        weather_info = self.data_scrapping.find('div', class_='CurrentConditions--phraseValue--17s79').text
        return weather_info

    def get_temperature(self):
        temperature = self.data_scrapping.find('div', class_= 'CurrentConditions--primary--39Y3f').span.text
        return temperature
        
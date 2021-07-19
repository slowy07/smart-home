from tkinter import *
import time
import locale
import threading
import datetime
import traceback
import logging
import random

# from PIL import ImageTk, Image
from contextlib import contextmanager

import data_fetcher as weather_info
import wikipedia_gen as wiki
import data_fetcher as weather_data_info

LOCALE = threading.Lock()

ui_locale = ''
date_format = "%b %d %Y"
time_format = 24
xlarge_text_size = 94
large_text_size = 48
medium_text_size = 28
small_text_size = 14

@contextmanager
def set_locale(name):
    with LOCALE:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        except Exception as err:
            logging.exception(f"Error : {err}")

class clock_information(Frame):
    def __init__(self, parent, *arg, **kwargs):
        Frame.__init__(self, parent, bg = 'black')
        
        self.time1 = ''
        self.time_label = Label(self, font = ('Helvetica', large_text_size), fg = 'white', bg = 'black')
        self.time_label.pack(side=TOP, anchor=E)

        self.day_of_week = ''
        self.day_of_week_label = Label(self, text = self.day_of_week, font = ('Helvetica', small_text_size), fg = 'white', bg = 'black' )
        self.day_of_week_label.pack(side = TOP, anchor = E)

        self.date = ''
        self.date_label = Label(self, text = self.date, font = ('Helvetica', small_text_size), fg = 'white', bg = 'black')
        self.date_label.pack(side = TOP, anchor = E)

        self.tick()
    
    def tick(self):
        with set_locale(ui_locale):
            try:
                if time_format == 12:
                    time2 = time.strftime('%H:%M %p')
                else:
                    time2 = time.strftime('%H:%M:%S')
                
                day_of_week = time.strftime('%A')
                date2 = time.strftime(date_format)
                try:
                    if time2 != self.time1:
                        self.time1 = time2
                        self.time_label.config(text = time2)
                except Exception:
                    logging.exception("time is not initialized!")
                
                try:
                    if day_of_week != self.day_of_week:
                        self.day_of_week = day_of_week
                        self.day_of_week_label.config(text = day_of_week)
                except Exception:
                    logging.exception("day is not initialized!")
                
                try:
                    if date2 != self.date:
                        self.date = date2
                        self.date_label.config(text = date2)
                except Exception:
                    logging.exception("date is not initialized!")
                self.time_label.after(200, self.tick)
            except Exception as err:
                logging.exception(f"error ! : {err}")

class weather_data(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg = 'black')
        data = weather_data_info.weather_scrapping(weather_data_info.LINK)
        self.forecast = data.get_weather_information()
        self.temperature = data.get_temperature()
        self.forecast_label = Label(self, text = self.forecast, font = ('Helvetica', medium_text_size), fg = 'white', bg = 'black')
        self.forecast_label.pack(side = TOP, anchor = W)

        self.temperature_label = Label(self, text = self.temperature, font = ('Helvetica', small_text_size), fg = 'white', bg = 'black')
        self.temperature_label.pack(side = LEFT, anchor = N)

        self.get_information_forecast()

    def get_information_forecast(self):
        information_forecast = weather_data_info.weather_scrapping(weather_data_info.LINK)
        information_forecast_today = information_forecast.get_weather_information()
        information_temperature = information_forecast.get_temperature()
        if information_forecast != self.forecast:
            self.forecast = information_forecast_today
            self.forecast_label.config(text = information_forecast_today)
        if information_temperature != self.temperature:
            self.temperature = information_temperature
            self.temperature_label.config(text = information_temperature)

        self.temperature_label.after(600000, self.get_information_forecast)



class wikipedia_knowledge(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.config(bg = 'black')
        self.title = 'Knowledge today'
        self.title_label = Label(self, text = self.title, font = ('Helvetica', medium_text_size), fg = 'white', bg = 'black')
        self.title_label.pack(side = TOP, anchor = W)

        self.content_data = wiki.wikipedia_info(random.choice(wiki.keyword_info))
        self.content_label = Label(self, text = self.content_data, font = ('Helvetica', small_text_size), fg = 'white', bg = 'black', justify = LEFT, wraplength = 1000)
        self.content_label.pack(side = TOP, anchor = W)

        self.wiki_data()

    def wiki_data(self):
        get_name_event = wiki.wikipedia_info(random.choice(wiki.keyword_info)).info_get_wiki()
        if get_name_event != self.content_data:
            self.event_name = get_name_event
            self.content_label.config(text = get_name_event)
        self.content_label.after(600000, self.wiki_data)

class say_today_information(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg = 'black')
        time_delta = datetime.datetime.now()
        self.get_date_information = str(time_delta.strftime('%H'))
        
        self.say_ai_label = Label(self, text = self.get_date_information, font = ('Helvetica', small_text_size), fg = 'white', bg = 'black')
        self.say_ai_label.pack(side = TOP, anchor = S)
        self.get_time_information()

    def get_time_information(self):
        time_information_result = self.get_time(self.get_date_information)
        self.get_date_information_dat = time_information_result
        self.say_ai_label.config(text = time_information_result)
        self.say_ai_label.after(600000, self.get_time_information)


    def get_time(self, time_information):
        night_label = []
        for night in range(17,24):
            night_label.append(str(night))

        time_now = datetime.datetime.now()
        time_now_res = str(time_now.strftime('%H'))

        if str(night_label) in time_now_res:
            say = "Goodnight !"
        else:
            say = "Morning !"

        return say
            

class FullScreenWindow:
    def __init__(self):
        self.tk = Tk()
        self.tk.configure(background = 'black')
        self.topFrame = Frame(self.tk, background = 'black')
        self.bottomFrame = Frame(self.tk, background = 'black')

        self.topFrame.pack(side = TOP, fill = BOTH, expand = YES)
        self.bottomFrame.pack(side = TOP, fill = BOTH, expand = YES)
        self.state = False
        self.tk.bind("<Return>", self.toggle_full_screen)
        self.tk.bind("<Escape>", self.end_full_screen)

        self.ai = say_today_information(self.bottomFrame)
        self.ai.pack(side = TOP, anchor = S)

        self.clock = clock_information(self.topFrame)
        self.clock.pack(side = RIGHT, anchor = N, padx = 90, pady = 65)

        self.wiki1 = wikipedia_knowledge(self.bottomFrame)
        self.wiki1.pack(side = LEFT, anchor = S, padx = 95, pady = 50)

        self.weather = weather_data(self.topFrame)
        self.weather.pack(side = LEFT, anchor = N, padx = 95, pady = 60)

    def toggle_full_screen(self, event = None):
        self.state = not self.state
        self.tk.attributes("-fullscreen", self.state)

        return 'break'
    
    def end_full_screen(self):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return 'break'


if __name__ == "__main__":
    window = FullScreenWindow()
    window.tk.title('mirror')
    window.tk.mainloop()
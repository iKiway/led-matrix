#!/usr/bin/python3.11

# @Author Kimon Beyer

# standard imports
import time
from typing import Any
import numpy as np
import threading
import sys
sys.path.append('/home/kimon/.local/lib/python3.11/site-packages')

# imports for the db api
from deutsche_bahn_api import api_authentication as aa
from deutsche_bahn_api import station_helper as sh
from deutsche_bahn_api import timetable_helper as th
from deutsche_bahn_api import train
from datetime import datetime

# imports for the LED RGB Matrix
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from rgbmatrix import graphics



# setting options for the RGB Matrix
options = RGBMatrixOptions()
options.rows = 64  # Anzahl der Reihen Ihrer Matrix
options.cols = 64  # Anzahl der Spalten Ihrer Matrix
options.chain_length = 1
options.parallel = 2
options.gpio_slowdown = 4
# options.limit_refresh_rate_hz = 500
test_matrix = RGBMatrix(options=options)

print(RGBMatrixOptions.show_refresh_rate)

# Class for all Apps
class App:
    def __init__(self,RGBMatrix: RGBMatrix, color: tuple, hertz: int) -> None:
        self.matrix = RGBMatrix
        self.accent_color = color
        self.graphics_accent_color = graphics.Color(self.accent_color[0],self.accent_color[1],self.accent_color[2])
        self.canvas = RGBMatrix.CreateFrameCanvas()
        self.display_canvas = RGBMatrix.CreateFrameCanvas()
        self.hertz = hertz
        self.show_display = True

# @Returns the graphics.Color color for graphics class
    def background(self):
        pass

# Setting up the display for one frame
    def display(self):
        self.background()
        

# displays the current canvas on the Display
# therefore it uses the given frequence
    def display_to_matrix(self):
        while True:
            self.display()
            self.display_canvas = self.get_canvas()
            matrix = self.matrix
            # self.matrix.SwapOnVSync(self.display_canvas)
            time.sleep(1/self.hertz)
            self.canvas = self.matrix.SwapOnVSync(self.display_canvas)
    
    def get_canvas(self):
        return self.canvas



# Class for the DB App
# 
class DB_App(App):
    def __init__(self, RGBMatrix: RGBMatrix, color: tuple, hertz: int,  station_name: str, show_departure=True, ankunft_anzeigen=False) -> None:
        super().__init__(RGBMatrix,color,hertz)
        self.station_name = station_name
        self.show_departure = show_departure
        self.show_arrival = ankunft_anzeigen
        self.client_id = 'a8776f6d99d99b5c12275942493f4605'
        self.client_secret = '6f4bb86ac0b06ebf644cacbbea2bfc04'
        self.font_small = graphics.Font()
        self.font_normal = graphics.Font()
        self.api = None
        self.train_list = None
        self.station_helper = None
        self.station = None
        self.timetable_helper = None
        self.train_list = None
        self.x_running_text_upper = self.matrix.width-2
        self.x_running_text_lower = self.matrix.width-2

# Sets up all nessesary parameters/ variables of the class
    def setup(self):
        client_id = 'a8776f6d99d99b5c12275942493f4605'
        client_secret = '6f4bb86ac0b06ebf644cacbbea2bfc04'

        api = aa.ApiAuthentication(client_id, client_secret)
        success = api.test_credentials()
        print(success)

        self.station_helper = sh.StationHelper()
        self.station_helper.load_stations()
        found_station_by_name = self.station_helper.find_stations_by_name(self.station_name)[0]


        try:
            self.api = aa.ApiAuthentication(self.client_id, self.client_secret)
            success = self.api.test_credentials()
            print(success)
        except:
            print("Fehler beim laden der API. Bitte überprüfen Sie die client_id und die client_secret")
        try:
            self.station_helper = sh.StationHelper()
            self.station_helper.load_stations()
            self.station = self.station_helper.find_stations_by_name(self.station_name)[0]
        except Exception as e:
            print("Die von ihnen gewählte Station existiert nicht. Bitte überprüfen sie die Eingabe")
            print(e)
        try:
            self.timetable_helper = th.TimetableHelper(self.station,self.api)
        except:
            print("Fehler beim laden des timetable_helper")
        try:
            self.font_small.LoadFont("rpi-rgb-led-matrix/fonts/4x6.bdf")
            self.font_normal.LoadFont("rpi-rgb-led-matrix/fonts/5x7.bdf")
        except:
            print("Fehler beim laden der Fonts")

# Sortiert die Abfahrtszeit
    def sorte(self,trains: train):
        try:
            return trains.train_changes.departure
        
        except:
            return trains.departure
    
    # ermittelt die nächsten 2 züge, welche ankommen bzw ausfallen. 
    # Bei Verspätung gilt die verspätete uhrzeit als referenzuhrzeit gelten und bei ausgefallenen die tatsächliche uhrzeit
    def set_current_train_list(self):
        aktuelle_zeit = datetime.now()
        zeitformat = aktuelle_zeit.strftime('%y%m%d%H%M')
        trains_in_this_hour = self.timetable_helper.get_timetable()
        trains_in_next_hour = self.timetable_helper.get_timetable()
        current_listq = trains_in_next_hour
        print(len(current_listq))
        current_list = self.timetable_helper.get_timetable_changes(current_listq)
        for i in current_listq:
            print(i.departure)
        current_list = [train for train in current_list if self.sorte(train) > zeitformat] 
        current_list.sort(key=lambda x: self.sorte(x))
        print(len(current_list))
        self.train_list = current_list[:2]
        
        

    def departure_time(self):
        print("ls")


# prints the icon @param lower or upper to the canvas
# if @param train_type is an S ( S Bahn) it shows the symbol of the S Bahn
# otherwise it prints the train type in a gray area with the train number unterneath
    def icon(self,train_type,train_number,lower = False):
        if lower == False:
            y_pixel = 1
        else:
            y_pixel = 17
        if train_type =='S':
            image = Image.open(f'icons/{train_type}{train_number}.png')
        else:
            image = Image.open('icons/standard.png')
        image = image.convert("RGB")
        for x in range(17):
            for y in range(14):
                r, g, b = image.getpixel((x, y))
                self.canvas.SetPixel(x+1, y+y_pixel, r, g, b)
        if train_type != 'S':
            graphics.DrawText(self.canvas,self.font_normal,2,7+y_pixel,graphics.Color(255,255,255),train_type)
            graphics.DrawText(self.canvas,self.font_small,2,14+y_pixel,graphics.Color(255,255,255),str(train_number))

# generates the background line arround the matrix in the accent_color
    def background(self):
        super().background()
        graphics.DrawLine(self.canvas,0,0,64,0,self.graphics_accent_color)
        graphics.DrawLine(self.canvas,0,15,64,15,self.graphics_accent_color)
        graphics.DrawLine(self.canvas,0,16,64,16,self.graphics_accent_color)
        graphics.DrawLine(self.canvas,0,31,64,31,self.graphics_accent_color)
        graphics.DrawLine(self.canvas,0,0,0,32,self.graphics_accent_color)
        graphics.DrawLine(self.canvas,63,0,63,32,self.graphics_accent_color)
        graphics.DrawLine(self.canvas,18,0,18,31,self.graphics_accent_color)
        # print(type(self.canvas))

# zeigt den bereich von typ und nummer des zuges (später irrelevant)
    def background_type_and_number(self):
        for x in range(17):
            for y in range(14):
                self.canvas.SetPixel(x+1, y+1, 0,0,0)
                self.canvas.SetPixel(x+1, y+17, 255,0,0)


    def display_departure(self,train: train,lower = False):
        if lower == True:
            y = 16
        else:
            y = 0
        departure_time = datetime.strptime(train.departure, '%y%m%d%H%M')
        graphics.DrawText(self.canvas,self.font_normal,20,15+y,graphics.Color(255,255,255),departure_time.strftime('%H:%M'))
        # print(train.train_changes.departure)

        departure_time_changed = datetime.strptime(train.train_changes.departure, '%y%m%d%H%M')
        delay_difference = departure_time_changed - departure_time
        delay = round(delay_difference.total_seconds()/60)
        graphics.DrawText(self.canvas,self.font_normal,20,15+y,graphics.Color(255,255,255),f"{departure_time.strftime('%H:%M')}")
        try:
            if delay == 0:
                color = graphics.Color(255,255,255)
            elif delay <5:
                color = graphics.Color(0,255,0)
            else:
                color = graphics.Color(255,0,0)
            if getattr(train.train_changes, "passed_stations",None) == "":
                graphics.DrawText(self.canvas,self.font_normal,47,15+y,graphics.Color(255,0,0),"XX")
            else:
                graphics.DrawText(self.canvas,self.font_normal,47,15+y,color,f"+{delay}")
        except Exception as e:
            print(e)

    def display_final_destination(self, train: train,lower = False):
        if lower == True:
            y = 16
            station = train.stations.split("|")
            final_destination = station[-1]
            len = graphics.DrawText(self.canvas,self.font_normal,self.x_running_text_lower,8+y,graphics.Color(255,255,255),final_destination)

            self.x_running_text_lower -=1

            if self.x_running_text_lower + len < 19:
                self.x_running_text_lower = self.matrix.width -2
            self.background_type_and_number()
        else:
            y = 0
            station = train.stations.split("|")
            final_destination = station[-1]
            len = graphics.DrawText(self.canvas,self.font_normal,self.x_running_text_upper,8+y,graphics.Color(255,255,255),final_destination)

            self.x_running_text_upper -=1

            if self.x_running_text_upper + len < 19:
                self.x_running_text_upper = self.matrix.width -2
            self.background_type_and_number()
        


    def display(self):
        current_list = self.train_list
        self.canvas.Clear()
        self.display_final_destination(current_list[0])
        self.display_final_destination(current_list[1],True)
        self.background_type_and_number()

        super().display()
        # print(current_list[0].train_changes.departure)
        self.display_departure(current_list[0])
        self.display_departure(current_list[1],True)
        # self.background_type_and_number()
        if current_list[0].train_type == 'S' or current_list[0].train_type == "MEX" or getattr(current_list[0], "trip_type",None) == "N":
            number = current_list[0].train_line
        else:
            number = current_list[0].train_number

        self.icon(current_list[0].train_type,number)
        if current_list[1].train_type == 'S'or current_list[1].train_type == "MEX" or getattr(current_list[1], "trip_type",None) == "N":
            number = current_list[1].train_line
        else:
            number = current_list[1].train_number
        self.icon(current_list[1].train_type,number,True)
        

    def main(self):
        self.setup()
        self.display_to_matrix()



    

color = list(np.random.choice(range(256), size=3))
color = (255,255,255)
Test = DB_App(test_matrix,color,10,"Rommelshausen",False,False)

def thread():
    while True:
        Test.set_current_train_list()
        print("sldk")
        time.sleep(60)

Test.setup()
thread_reload = threading.Thread(target=thread, group=None)
thread_reload.start()
Test.set_current_train_list()
Test.display_to_matrix()
time.sleep(5)


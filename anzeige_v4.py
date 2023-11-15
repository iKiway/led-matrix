#!/usr/bin/python3.11

# @Author Kimon Beyer

# standard imports
import time
from typing import Any
import threading
import sys
sys.path.append('/home/kimon/.local/lib/python3.11/site-packages')

# imports for the db api
from pyhafas import HafasClient
from pyhafas.profile import DBProfile
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
            # time.sleep(1/self.hertz)
            self.canvas = self.matrix.SwapOnVSync(self.display_canvas)
    
    def get_canvas(self):
        return self.canvas



# Class for the DB App
# 
class DB_App(App):
    def __init__(self, RGBMatrix: RGBMatrix, color: tuple, hertz: int,  station_name: str, show_departure=True, ankunft_anzeigen=False) -> None:
        super().__init__(RGBMatrix,color,hertz)
        self.station_name = station_name
        self.client = HafasClient(DBProfile())
        self.train_list = None
        self.current_list = self.train_list
        self.show_departure = show_departure
        self.show_arrival = ankunft_anzeigen
        self.station_number = self.client.locations(station_name)[0].id

        self.font_small = graphics.Font()
        self.font_normal = graphics.Font()
        self.x_running_text_upper = self.matrix.width-2
        self.x_running_text_lower = self.matrix.width-2
        
        self.setup()

# Sets up all nessesary parameters/ variables of the class
    def setup(self):
        
            self.font_small.LoadFont("4x6.bdf")
            self.font_normal.LoadFont("5x7.bdf")
        
    

    def sortieren(self,train):
        if train.delay == None:
            return train.dateTime
        else:
            return train.dateTime + train.delay
    
    # ermittelt die nächsten 2 züge, welche ankommen bzw ausfallen. 
    # Bei Verspätung gilt die verspätete uhrzeit als referenzuhrzeit gelten und bei ausgefallenen die tatsächliche uhrzeit
    def set_train_list(self):
        try:
            api_list = self.client.departures(
                station=self.station_number,
                date = datetime.now(),
                max_trips=10,
                products={
                    'long_distance_express': True,
                    'regional_express': True,
                    'regional': True,
                    'suburban': True,
                    'bus': False,
                    'ferry': False,
                    'subway': False,
                    'tram': False,
                    'taxi': False
                }
            )
            api_list.sort(key=lambda x: self.sortieren(x))
            
            self.train_list = api_list[:2]   
        except Exception as e:
            print(e)
            print(datetime.now())

        
    def set_current_train_list(self):
        self.current_list = self.train_list

    def departure_time(self):
        print("ls")




# prints the icon @param lower or upper to the canvas
# if @param train_type is an S ( S Bahn) it shows the symbol of the S Bahn
# otherwise it prints the train type in a gray area with the train number unterneath
    def icon(self,train,lower = False):
        if lower == False:
            y_pixel = 1
        else:
            y_pixel = 17

        train_type = ''.join([char for char in train.name if char.isalpha()]) 
        train_number =  ''.join([char for char in train.name if char.isdigit()])
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
            if len(train_number) <= 4:
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
                self.canvas.SetPixel(x+1, y+17, 0,0,0)


    def display_departure(self,train,lower = False):
        if lower == True:
            y = 16
        else:
            y = 0
        departure_time = train.dateTime
        # print(train.train_changes.departure)

        if train.cancelled == True:
            graphics.DrawText(self.canvas,self.font_normal,20,15+y,graphics.Color(255,0,0),departure_time.strftime('%H:%M'))
            graphics.DrawText(self.canvas,self.font_normal,47,15+y,graphics.Color(255,0,0),"X")
        elif train.delay != None:
            delay = round(train.delay.seconds/60)
            graphics.DrawText(self.canvas,self.font_normal,20,15+y,graphics.Color(255,255,255),f"{departure_time.strftime('%H:%M')}")
            if delay == 0:
                color = graphics.Color(255,255,255)
            elif delay <5:
                color = graphics.Color(0,255,0)
            else:
                color = graphics.Color(255,0,0)
            graphics.DrawText(self.canvas,self.font_normal,47,15+y,color,f"+{delay}")
        else:
            graphics.DrawText(self.canvas,self.font_normal,20,15+y,graphics.Color(255,255,255),f"{departure_time.strftime('%H:%M')}")



    def display_final_destination(self,train,lower = False):
        if lower == True:
            y = 16
            len = graphics.DrawText(self.canvas,self.font_normal,self.x_running_text_lower,8+y,graphics.Color(255,255,255),train.direction)

            self.x_running_text_lower -=1

            if self.x_running_text_lower + len < 19:
                self.x_running_text_lower = self.matrix.width -2
            self.background_type_and_number()
        else:
            y = 0

            len = graphics.DrawText(self.canvas,self.font_normal,self.x_running_text_upper,8+y,graphics.Color(255,255,255),train.direction)

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
        self.background_type_and_number()


        self.icon(current_list[0])

        self.icon(current_list[1],True)
        

    def main(self):
        self.setup()
        self.display_to_matrix()

    




    

color = (100,100,100)
Test = DB_App(test_matrix,color,1,"Rommelshausen",False,False)
Test.set_train_list()
def thread():
    while True:
        Test.set_train_list()
        time.sleep(30)


thread_reload = threading.Thread(target=thread, group=None)
thread_reload.start()
# Test.set_current_train_list()
Test.display_to_matrix()
# time.sleep(5)


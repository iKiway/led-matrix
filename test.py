import time
import threading
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics


# Konfigurieren Sie die Matrix
options = RGBMatrixOptions()
options.rows = 64  # Anzahl der Reihen Ihrer Matrix
options.cols = 64  # Anzahl der Spalten Ihrer Matrix
options.chain_length = 1
options.parallel = 2
options.gpio_slowdown = 4


# Configure options as needed

# Create an instance of RGBMatrix with the specified options
matrix = RGBMatrix(options=options)

# Create a Canvas associated with the matrix
canvas = matrix.CreateFrameCanvas()

# Text, Schriftart und Farbe
text = "Hello, World!"
font = graphics.Font()
font.LoadFont("fonts/6x10.bdf")  # Passe dies entsprechend an
color = graphics.Color(255, 0, 0)

x = matrix.width

def clock(zeit):
    time.sleep(zeit)

     
def running_text(text,font,color,x):
    while True:
        # Lösche den vorherigen Inhalt
        canvas.Clear()

        # Zeichne den Text auf die aktuelle Position
        len = graphics.DrawText(canvas, font, x, 10, color, text)

        # Verschiebe den Text nach links
        x -= 1

        # Wenn der Text aus dem Display verschwindet, setze die Position zurück
        if x + len < 0:
            x = matrix.width

        # Zeige den aktuellen Frame auf dem Display an
        for x in range(17):
            for y in range(14):
                canvas.SetPixel(x+1, y+1, 0,0,0)
                canvas.SetPixel(x+1, y+17, 255,0,0)
        canvas = matrix.SwapOnVSync(canvas)

        # Kurze Verzögerung für die Animation
        time.sleep(0.05)

def running_text_time(canvas,text,font,color,x,seconds):
    clock_thread = threading.Thread(target=clock, args=(seconds,))
    clock_thread.start()
    while clock_thread.is_alive():
        # Lösche den vorherigen Inhalt
        canvas.Clear()

        # Zeichne den Text auf die aktuelle Position
        len = graphics.DrawText(canvas, font, x, 10, color, text)

        # Verschiebe den Text nach links
        x -= 1

        # Wenn der Text aus dem Display verschwindet, setze die Position zurück
        if x + len < 0:
            x = matrix.width

        # Zeige den aktuellen Frame auf dem Display an
        canvas = matrix.SwapOnVSync(canvas)

        # Kurze Verzögerung für die Animation
        time.sleep(0.05)


running_text_time(canvas,text,font,color,x,10)


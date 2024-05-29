import numpy as np
import pygame as pg
import time

numbers_pixels = {
    '0': ("11111",
          "10001",
          "10001",
          "10001",
          "11111"),

    '1': ("01100",
          "00100",
          "00100",
          "00100",
          "01110"),

    '2': ("11111",
          "00001",
          "11111",
          "10000",
          "11111"),

    '3': ("11111",
          "00001",
          "00111",
          "00001",
          "11111"),

    '4': ("10001",
          "10001",
          "11111",
          "00001",
          "00001"),

    '5': ("11111",
          "10000",
          "11111",
          "00001",
          "11111"),

    '6': ("11111",
          "10000",
          "11111",
          "10001",
          "11111"),

    '7': ("11111",
          "00001",
          "00001",
          "00001",
          "00001"),

    '8': ("11111",
          "10001",
          "11111",
          "10001",
          "11111"),

    '9': ("11111",
          "10001",
          "11111",
          "00001",
          "00001"),

    ':': ("00000",
          "00100",
          "00000",
          "00100",
          "00000"),
    '.': ("00000",
            "00000",
            "00000",
            "00000",
            "00100"),
    ' ': ('00000',
          '00000',
          '00000',
          '00000',
          '00000'),

    '-': ('00000',
            '00000',
            '01110',
            '00000',
            '00000'),
    '+': ('00000',
            '00100',
            '01110',
            '00100',
            '00000'),
             
    
}




from datetime import datetime
class ClockManager:
    def __init__(self, update_interval=1000):
        self.update_interval = update_interval
        self.time = datetime.now()

        self.timestamp = 0
        
    def update(self, now):
        # interval in milliseconds
        if now - self.timestamp > self.update_interval / 1000:
            self.time = datetime.now()
            self.timestamp = now


from pydexcom import Dexcom
class DexcomManager:
    def __init__(self, username, password, update_interval=100000): # 100 seconds
        self.update_interval = update_interval
        self.service = Dexcom(username, password)
        self.data = None
        self.timestamp = 0

    def update(self, now):
        if now - self.timestamp < self.update_interval / 1000:
            return
        print('Updating Dexcom')
        
        self.timestamp = now

        glucose = self.service.get_current_glucose_reading()

        self.data = {
            'glucose': glucose,
            'glucose_value': glucose.value,
            'mmol_l': glucose.mmol_l,
            'trend': glucose.trend,
            'trend_description': glucose.trend_description,
            'trend_direction': glucose.trend_direction,
            'trend_arrow': glucose.trend_arrow
        }

        # replace arrows with + and -
        self.data['trend_arrow'] = self.data['trend_arrow'].replace('→', '').replace('↑', '+').replace('↓', '-').replace('↗' , '+').replace('↘', '-')



class ClockScreen:
    def __init__(self, size, tick_rate):
        pg.init()
        self.screen = pg.display.set_mode(size)
        self.clock = pg.time.Clock()
        self.tick_rate = tick_rate
        self.running = False

        self.matrix = np.zeros((size[0], size[1], 3), dtype=np.uint8) # 3 channels for RGB
        
        # set the window caption
        pg.display.set_caption('Pi-Clock')
        # set the window icon
        icon = pg.image.load('icon.png')

        self.clock_manager = ClockManager()
        # read from pass.txt
        with open('pass.txt') as f:
            lines = f.readlines()
            username = lines[0].strip()
            password = lines[1].strip()
        self.dexcom_manager = DexcomManager(username, password)

        self.nightmode = False


    def run(self):
        self.running = True
        while self.running:
            self.clock.tick(self.tick_rate)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_f:
                    pg.display.toggle_fullscreen()
                    # if fullscreen, hide mouse
                    if pg.display.get_surface() == pg.display.get_surface():
                        pg.mouse.set_visible(False)
                    else:
                        pg.mouse.set_visible(True)
                
                # Q to quit
                elif event.key == pg.K_q:
                    self.running = False

    def update(self):
        now = time.time()

        # midnight to 7am
        if self.clock_manager.time.hour <= 7:
            self.nightmode = True
        else:
            self.nightmode = False

        self.clock_manager.update(now)
        self.dexcom_manager.update(now)

    def draw(self):
        self.screen.fill((0, 0, 0)) # clear screen
        self.draw_clock()
        pg.surfarray.blit_array(self.screen, self.matrix) # draw matrix
        pg.display.flip() # update display


    def draw_clock(self):
        # clear matrix
        self.matrix.fill(0)

        # 12 hour clock
        time_str = self.clock_manager.time.strftime("%I:%M:%S")

        color = (255, 255, 255)
        if self.nightmode:
            color = (200, 200, 200)
        
        # draw time
        self.draw_numbers(time_str, x=50, y=80, color=color, scale=10, spacing=20)

        # draw glucose
        if self.dexcom_manager.data:
            
            glucose_str = '---'
            if self.dexcom_manager.data['glucose_value']:
                glucose_str = str(self.dexcom_manager.data['glucose_value']) + str(self.dexcom_manager.data['trend_arrow'])
                
            if self.nightmode:
                scale = 15
            else:
                scale = 10
            self.draw_numbers(glucose_str, x=50, y=360, color=color, scale=scale, spacing=20)


        # everything after this is not drawn in nightmode
        if self.nightmode:
            return
        
        # draw date
        # 0 = Monday, 6 = Sunday
        # day/month no year
        day_int = self.clock_manager.time.weekday()
        date_str = self.clock_manager.time.strftime("%m-%d")
        date_str = str(day_int)+ ' ' + date_str
        self.draw_numbers(date_str, x=90, y=170, color=color, scale=6, spacing=20)



    def draw_numbers(self, numbers, x, y, color, scale=1, spacing=10):
        current_x = x
        for number in numbers:
            self.draw_number(number, current_x, y, color, scale)
            # Move to the next character position
            # Assuming each character is 5 pixels wide plus the spacing
            current_x += 5 * scale + spacing


    def draw_number(self, number, x, y, color, scale):
        number_pixels = numbers_pixels[number]
        for i, row in enumerate(number_pixels):
            for j, pixel in enumerate(row):
                if pixel == '1':
                    # Draw a scaled pixel (square)
                    for dx in range(scale):  # Width of scaled pixel
                        for dy in range(scale):  # Height of scaled pixel
                            try:
                                self.matrix[x + j*scale + dx, y + i*scale + dy] = color
                            except IndexError:
                                pass




c = ClockScreen((800, 480), 60)
c.run()

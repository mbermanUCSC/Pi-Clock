import numpy as np
import pygame as pg
import time

from clock.Managers import ClockManager, DexcomManager, CalendarManager
from clock.fonts import font1

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

        self.clock_manager = ClockManager()
        # read from pass.txt
        with open('clock/pass.txt') as f:
            lines = f.readlines()
            username = lines[0].strip()
            password = lines[1].strip()
        self.dexcom_manager = DexcomManager(username, password)
        self.calendar_manager = CalendarManager()

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
        self.calendar_manager.update(now)

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
        self.draw_str(time_str, x=50, y=80, color=color, scale=10, spacing=20)

        # draw glucose
        if self.dexcom_manager.data:
            
            glucose_str = '---'
            if self.dexcom_manager.data['glucose_value']:
                glucose_str = str(self.dexcom_manager.data['glucose_value']) + str(self.dexcom_manager.data['trend_arrow'])

            if self.nightmode:
                scale = 15
            else:
                scale = 10
            self.draw_str(glucose_str, x=50, y=360, color=color, scale=scale, spacing=20)


        # everything after this is not drawn in nightmode
        if self.nightmode:
            return
        
        next_event = self.calendar_manager.get_next_event()
        if next_event:
            event_str = next_event.name + ' ' + next_event.start.strftime('%I:%M %p')
            self.draw_str(event_str, x=100, y=240, color=color, scale=2, spacing=20)


        # draw date
        # 0 = Monday, 6 = Sunday
        # day/month no year
        day_int = self.clock_manager.time.weekday()
        date_str = self.clock_manager.time.strftime("%m-%d")
        date_str = str(day_int)+ ' ' + date_str
        self.draw_str(date_str, x=90, y=190, color=color, scale=6, spacing=20)



    def draw_str(self, numbers, x, y, color, scale=1, spacing=10):
        current_x = x
        for number in numbers:
            self.draw_char(number, current_x, y, color, scale)
            # Move to the next character position
            # Assuming each character is 5 pixels wide plus the spacing
            current_x += 5 * scale + spacing


    def draw_char(self, number, x, y, color, scale):
        font_char = font1[number]
        for i, row in enumerate(font_char):
            for j, pixel in enumerate(row):
                if pixel == '1':
                    # for scale size
                    for dx in range(scale):  # Width of scaled pixel
                        for dy in range(scale):  # Height of scaled pixel
                            try:
                                self.matrix[x + j*scale + dx, y + i*scale + dy] = color
                            except IndexError:
                                pass




c = ClockScreen((800, 480), 60)
c.run()

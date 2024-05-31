from pydexcom import Dexcom
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
      try:
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
      except:
            self.data = None

class Event:
      def __init__(self, name, start, end, recurrence):
            self.name = name
            self.start = self.update_time(start)
            self.end = self.update_time(end)
            self.recurrence = recurrence


      def update_time(self, time):
            try:
                  # convert 11:00 into time object
                  datetime_obj = datetime.strptime(time, '%H:%M:%S').time()
            except:
                  datetime_obj = None
            return datetime_obj
      
      def __str__(self):
            return f'{self.name} {self.start} {self.end} {self.recurrence}'
      
      def __repr__(self):
            return self.__str__()

class CalendarManager:
      def __init__(self, update_interval=10000): # 1 second
            self.update_interval = update_interval
            self.timestamp = 0
            self.events = []
      
      def update(self, now):
            if now - self.timestamp < self.update_interval / 1000:
                  return
            
            if len(self.events) == 0:
                 self.events.append(Event('CMPM 169', start='11:40:00', end='13:15:00', recurrence=[1,3]))
                 self.events.append(Event('CMPM 172', start='15:20:00', end='16:55:00', recurrence=[1,3]))
                 self.events.append(Event('CMPM 151', start='17:20:00', end='20:45:00', recurrence=[1]))

      def get_next_event(self):
            # get either the next event or the current event. cyclicle too by so next day events are considered too
            now = datetime.now().time()
            for event in self.events:
                  if event.start <= now <= event.end:
                        # check if event is today
                        if event.recurrence:
                              if datetime.now().weekday() in event.recurrence:
                                    return event
                        else:
                              return event # no recurrence, just return the event

            return None
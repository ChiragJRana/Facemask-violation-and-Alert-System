from pygame import mixer
import os

class Alarm:    
    def __init__(self):
        path = 'alert.mp3'
        mixer.init()
        mixer.music.load(path)
        self.alarm_switch = False
        self.staff_switch = True
        print('The Alarm is Initialized')

    def ring_alarm(self):
        if self.staff_switch:
            if not self.alarm_switch:
                mixer.music.play()
                self.alarm_switch = True
            else: print('The alarm is already on')
        else: print('Staff has turned the system off')
    
    def stop_alarm(self):
        if self.staff_switch:
            if self.alarm_switch :
                mixer.music.stop()
                self.alarm_switch = False
            else: print('The alarm is already off')
        else: print('Staff has turned the system On')

    def work_off(self):
        self.stop_alarm()
        self.staff_switch = False        
        print('Staff turned off the alarm')
        return "you have turned off the alarm"
    def work_on(self):
        self.staff_switch = True
        print('Staff has turned on the alarm.')
        return "you have turned on the alarm."

    def __del__(self):
        mixer.music.stop()

# if __name__ == '__main__':
#     # To test the working of the mixer
#     mixer.init()
#     mixer.music.load('alert.mp3')
#     mixer.music.set_volume(0.7)
#     mixer.music.play()
#     while True: 
      
#         print("Press 'p' to pause, 'r' to resume") 
#         print("Press 'e' to exit the program") 
#         query = input("  ") 
        
#         if query == 'p': 
    
#             # Pausing the music 
#             mixer.music.pause()      
#         elif query == 'r': 
    
#             # Resuming the music 
#             mixer.music.unpause() 
#         elif query == 'e': 
    
#             # Stop the mixer 
#             mixer.music.stop() 
#             break
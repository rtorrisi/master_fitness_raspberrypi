from RFID import RFIDReader
from firebase import Firebase
from HomeScreen import HomeScreen
from ViewerScreen import ViewerScreen
from os import path, environ
from functools import partial 
#environ["KIVY_NO_CONSOLELOG"] = "1"

import kivy
kivy.require('1.11.1')
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.app import App
from kivy.clock import Clock

from config import config

class WorkoutPlansManager:
	def __init__(self, screen_manager, home_screen, viewer_screen):
		self.firebase = Firebase(config)
		self.rfidReader = RFIDReader('/dev/ttyUSB0', handler_function=self.handler)
		self.home_screen = home_screen
		self.viewer_screen = viewer_screen
		self.screen_manager = screen_manager		

	def handler(self, card_no, state):
		print("handler -> card %s (%u)" % (card_no, state))
		
		if state:
			destination_path = "storage_data/"+card_no+".jpg"
			if not path.isfile(destination_path):
				Clock.schedule_once(partial(self.home_screen.setBarVisibility, True))
				Clock.schedule_once(partial(self.home_screen.setBarValue, 50))
				source_path = "users/"+card_no+"/scheda.jpg"
				self.firebase.downloadFile(source_path, destination_path)
				print("downloaded")	
				Clock.schedule_once(partial(self.home_screen.setBarValue, 100))
			else:
				print("file exists")
			
			Clock.schedule_once(partial(self.viewer_screen.setSourcePath, destination_path))
			self.screen_manager.current = 'viewer'

	def run(self):
		self.rfidReader.start()
		
	def stop(self):
		self.rfidReader.stop()		


screen_manager = ScreenManager(transition=NoTransition())
home_screen = HomeScreen(name='home')
viewer_screen = ViewerScreen(name='viewer')

screen_manager.add_widget(home_screen)
screen_manager.add_widget(viewer_screen)

class TestApp(App):
	WPM = WorkoutPlansManager(screen_manager, home_screen, viewer_screen)

	def build(self):
		self.WPM.run()
		return screen_manager

	def stop(self):
		self.WPM.stop()


if __name__ == "__main__":
	TestApp().run()

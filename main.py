from RFID import RFIDReader
from firebase import Firebase
from HomeScreen import HomeScreen
from ViewerScreen import ViewerScreen
from os import path, environ
from functools import partial 
environ["KIVY_NO_CONSOLELOG"] = "1"

import kivy
kivy.require('1.11.1')

from kivy.config import Config
Config.set('graphics', 'width', '1024')
Config.set('graphics', 'height', '600')

from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.app import App
from kivy.clock import Clock

from config import config
import os

class WorkoutPlansManager:
	def __init__(self, screen_manager, home_screen, viewer_screen):
		self.firebase = Firebase(config)
		self.rfidReader = RFIDReader(handler_function=self.handler)
		self.home_screen = home_screen
		self.viewer_screen = viewer_screen
		self.screen_manager = screen_manager		

	def loadViewer(self, user_data):
		Clock.schedule_once(partial(self.viewer_screen.setUserData, self.saveUserData, user_data))
		Clock.schedule_once(partial(self.home_screen.setBarValue, 100))
		self.screen_manager.current = 'viewer'

	def saveUserData(self, card_no, data):
		self.firebase.update("users/"+card_no, data)

	def loadUserData(self, card_no):
		Clock.schedule_once(partial(self.home_screen.setBarVisibility, True))
		source_path = "users/"+card_no+"/scheda.pdf"
		destination_path = "storage_data/"+card_no+"/"+"scheda.pdf"
		Clock.schedule_once(partial(self.home_screen.setBarValue, 25))
		if not path.isfile(destination_path):
			os.system("rm -f storage_data/"+card_no+"/*")
			os.system("mkdir -p storage_data/"+card_no)
			self.firebase.downloadFile(source_path, destination_path)
			Clock.schedule_once(partial(self.home_screen.setBarValue, 50))
			os.system("convert -density 140 "+destination_path+" -quality 50 scheda_%01d.jpg")
		else:
			print("file exists")

		Clock.schedule_once(partial(self.home_screen.setBarValue, 75))
		user_data = self.firebase.get("users/"+card_no).val()
		Clock.schedule_once(partial(self.home_screen.setBarValue, 90))

		return user_data

	def handler(self, card_no):
		print("handler -> card %s" % card_no)
		
		user_data = self.loadUserData(card_no)
		if not user_data:
			print("user not exists")
			Clock.schedule_once(partial(self.home_screen.setBarVisibility, False))
			Clock.schedule_once(partial(self.home_screen.setBarValue, 0))
		else:
			self.loadViewer(user_data)

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

	def __del__(self):
		self.WPM.stop()


if __name__ == "__main__":
	TestApp().run()

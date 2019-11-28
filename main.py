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
	def __init__(self, screen_manager):
		self.firebase = Firebase(config)
		self.rfidReader = RFIDReader(handler_function=self.handler)
		self.home_screen = HomeScreen(name='home', saveFunc=self.saveUserData)
		self.viewer_screen = ViewerScreen(name='viewer')
		self.screen_manager = screen_manager
		self.screen_manager.add_widget(self.home_screen)
		self.screen_manager.add_widget(self.viewer_screen)

	def loadViewer(self, user_data):
		Clock.schedule_once(partial(self.viewer_screen.setUserData, user_data))
		Clock.schedule_once(partial(self.home_screen.setBarValue, 100))
		self.screen_manager.current = 'viewer'

	def saveUserData(self, card_no, data):
		self.firebase.update("users/"+card_no, data)

	def loadUserData(self, card_no):
		try:
			user_data = self.firebase.get("users/"+card_no).val()
		except:
			#no connection
			return -2

		if not user_data:
			#no user
			return -1
			
		Clock.schedule_once(partial(self.home_screen.setBarVisibility, True))
		Clock.schedule_once(partial(self.home_screen.setBarValue, 25))
		
		source_path = "users/"+card_no
		destination_path = "storage_data/"+card_no

		if not path.isfile(destination_path+"/scheda.pdf"):
			os.system("rm -f "+destination_path+"/*")
			os.system("mkdir -p "+destination_path)

			self.firebase.downloadFile(source_path+"/scheda.pdf", destination_path+"/scheda.pdf")
			
			Clock.schedule_once(partial(self.home_screen.setBarValue, 50))
			
			os.system("convert -density 140 "+destination_path+"/scheda.pdf -quality 50 "+destination_path+"/scheda_%01d.jpg")

		Clock.schedule_once(partial(self.home_screen.setBarValue, 75))

		return user_data

	def handler(self, card_no):
		self.screen_manager.current = 'home'
		user_data = self.loadUserData(card_no)
		
		# if user found in firebase
		if user_data != -1 and user_data != -2:
			self.loadViewer(user_data)
		else:
			if user_data == -1:
				text = "Chiedi informazioni in segreteria per usare il totem!"
			else:
				text = "Connessione di rete assente. Contatta la segreteria!"
			self.home_screen.setHintVisibility(text, True)
			Clock.schedule_once(partial(self.home_screen.setHintVisibility, "", False), 5)

	def run(self):
		self.rfidReader.start()

	def stop(self):
		self.rfidReader.stop()


screen_manager = ScreenManager(transition=NoTransition())

class TestApp(App):
	WPM = WorkoutPlansManager(screen_manager)

	def build(self):
		self.WPM.run()
		return screen_manager

	def __del__(self):
		self.WPM.stop()


if __name__ == "__main__":
	TestApp().run()

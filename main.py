from RFID import RFIDReader
from os import path, environ
from firebase import Firebase
#environ["KIVY_NO_CONSOLELOG"] = "1"

import kivy
kivy.require('1.11.1')
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.progressbar import ProgressBar
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.clock import Clock
from functools import partial 

from config import config

from kivy.lang import Builder
Builder.load_file('kivy.kv')

class HomeScreen(Screen):
	progress_bar_visibility = BooleanProperty(False)
	progress_bar_value = NumericProperty(0)

	def setProgressBarVisibility(self, visible, *largs):
		self.progress_bar_visibility = visible

	def setProgressBarValue(self, value, *largs):
		self.progress_bar_value = value
	

class ViewerScreen(Screen):
	src = StringProperty("")

	def setSourcePath(self, path, *largs):
		self.src = path	

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
				Clock.schedule_once(partial(self.home_screen.setProgressBarVisibility, True))
				Clock.schedule_once(partial(self.home_screen.setProgressBarValue, 50))
				source_path = "users/"+card_no+"/scheda.jpg"
				self.firebase.downloadFile(source_path, destination_path)
				print("downloaded")	
				Clock.schedule_once(partial(self.home_screen.setProgressBarValue, 100))
			else:
				print("file exists")
			
			Clock.schedule_once(partial(self.viewer_screen.setSourcePath, destination_path))
			self.screen_manager.current = 'viewer'
		
		else:
			Clock.schedule_once(partial(self.home_screen.setProgressBarValue, 0))
			Clock.schedule_once(partial(self.home_screen.setProgressBarVisibility, False))
			self.screen_manager.current = 'home'		

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

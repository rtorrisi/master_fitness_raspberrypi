from RFID import RFIDReader
from firebase import Firebase
from HomeScreen import HomeScreen
from ViewerScreen import ViewerScreen
from os import path, environ, system
import zipfile
from functools import partial 
from config import config
from remove_old import deleteOldFolders

environ["KIVY_NO_CONSOLELOG"] = "1"
import kivy
kivy.require('1.11.1')

from kivy.config import Config
Config.set("graphics", "show_cursor", 0)
Config.set('graphics', 'width', '1024')
Config.set('graphics', 'height', '600')

from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.app import App
from kivy.clock import Clock

class WorkoutPlansManager:
	def __init__(self, screen_manager):
		self.firebase = Firebase(config)
		self.rfidReader = RFIDReader(handler_function=self.handler)
		self.home_screen = HomeScreen(name='home')
		self.viewer_screen = ViewerScreen(name='viewer', saveFunc=self.saveUserData)
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
			return -2 #firebase error

		if not user_data:
			return -1 #no user
			
		Clock.schedule_once(partial(self.home_screen.setBarVisibility, True))
		Clock.schedule_once(partial(self.home_screen.setBarValue, 25))
		
		source_path = "users/"+card_no
		destination_path = "storage_data/"+card_no
		filename_path = '%s/%s' % (destination_path, user_data['file'])

		if not path.isfile(filename_path):
			os.system("rm -f %s/*" % destination_path)
			os.system("mkdir -p %s" % destination_path)

			try:
				self.firebase.downloadFile(source_path+"/scheda.zip", filename_path)
			except:
				return -2 #firebase error

			Clock.schedule_once(partial(self.home_screen.setBarValue, 50))
			with zipfile.ZipFile(filename_path,"r") as zip_ref:
				for zip_info in zip_ref.infolist():
					if zip_info.filename[-1] == '/':
						continue
					zip_info.filename = os.path.basename(zip_info.filename)
					zip_ref.extract(zip_info, destination_path)
			#os.system("convert -density 140 "+destination_path+"/scheda.pdf -quality 50 "+destination_path+"/scheda_%01d.jpg")

		Clock.schedule_once(partial(self.home_screen.setBarValue, 75))

		return user_data

	def handler(self, card_no):
		self.screen_manager.current = 'home'
		user_data = self.loadUserData(card_no)
		
		# if user found in firebase
		if user_data not in [-1, -2]:
			self.loadViewer(user_data)
		else:
			if user_data == -1:
				text = "Chiedi informazioni in segreteria per usare il totem!"
			else:
				text = "Impossibile scaricare scheda al momento. Contatta la segreteria."
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
	days = 60
	seconds_per_day = 86400
	seconds = days*seconds_per_day
	deleteOldFolders('storage_data', seconds)
	TestApp().run()

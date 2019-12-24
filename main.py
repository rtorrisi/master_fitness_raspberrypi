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

class TestApp(App):

	def __init__(self):
		super(TestApp,self).__init__()
		self.rfidReader = RFIDReader(handler_function=self.handler)
		self.firebase = Firebase(config)
		self.cleanInfoEvent = None
		self.screen_manager = ScreenManager(transition=NoTransition())
		self.home_screen = HomeScreen(name='home')
		self.viewer_screen = ViewerScreen(name='viewer', saveFunc=self.saveUserData)
		self.screen_manager.add_widget(self.home_screen)
		self.screen_manager.add_widget(self.viewer_screen)

	def build(self):
		self.rfidReader.start()
		#self.handler('234234')
		return self.screen_manager

	def __del__(self):
		self.rfidReader.stop()
		
	def loadHome(self, *largs):
		self.screen_manager.current = 'home'

	def loadViewer(self, *largs):
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
		
		source_path = "users/"+card_no
		destination_path = "storage_data/"+card_no
		filename_path = '%s/%s' % (destination_path, user_data['file'])

		if not path.isfile(filename_path):
			system("rm -f %s/*" % destination_path)
			system("mkdir -p %s" % destination_path)

			try:
				self.firebase.downloadFile(source_path+"/scheda.zip", filename_path)
			except:
				return -2 #firebase error

			with zipfile.ZipFile(filename_path,"r") as zip_ref:
				for zip_info in zip_ref.infolist():
					if zip_info.filename[-1] == '/':
						continue
					zip_info.filename = path.basename(zip_info.filename)
					zip_ref.extract(zip_info, destination_path)
			#system("convert -density 140 "+destination_path+"/scheda.pdf -quality 50 "+destination_path+"/scheda_%01d.jpg")

		return user_data

	def loadAll(self, card_no, *largs):
		user_data = self.loadUserData(card_no)
		
		# if user found in firebase
		if user_data not in [-1, -2]:
			Clock.schedule_once(partial(self.viewer_screen.setUserData, user_data), -1)
			Clock.schedule_once(self.loadViewer, 0.5)
		else:
			if user_data == -1:
				self.showHint("Utente non registrato. Chiedi informazioni in segreteria!")
			else:
				self.showHint("Impossibile scaricare file dal server. Contatta la segreteria!")

	def handler(self, card_no):
		Clock.schedule_once(partial(self.home_screen.setHintMessage, "Carico scheda..."), -1)
		Clock.schedule_once(self.loadHome, 0)
		Clock.schedule_once(partial(self.loadAll, card_no), 0.1)

	def showHint(self, text, timeout=6):
		if self.cleanInfoEvent: Clock.unschedule(self.cleanInfoEvent)
		self.home_screen.setHintMessage(text)
		self.cleanInfoEvent = Clock.schedule_once(partial(self.home_screen.setHintMessage, ""), timeout)

if __name__ == "__main__":
	days = 60
	seconds_per_day = 86400
	seconds = days*seconds_per_day
	deleteOldFolders('storage_data', seconds)
	TestApp().run()

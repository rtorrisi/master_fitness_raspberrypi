from RFID import RFIDReader
from firebase import Firebase
from HomeScreen import HomeScreen
from ViewerScreen import ViewerScreen
from os import path, environ, system
import zipfile
import pyqrcode
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
		return self.screen_manager

	def __del__(self):
		self.rfidReader.stop()

	def saveUserData(self, card_no, data):
		self.firebase.update("users/"+card_no, data)

	def getUserData(self, card_no):
		try:
			user_data = self.firebase.get("users/"+card_no).val()
			return user_data
		except Exception:
			raise Exception("Nessuna connessione ad internet. Contatta la segreteria!")

	def getUserRFID(self, user_data):
		try:
			if user_data: return user_data['rfid']
			else: raise Exception('no user')
		except Exception:
			raise Exception("Utente non registrato. Chiedi informazioni in segreteria!")

	def downloadUserFile(self, user_data, rfid, destination_path, filename_path):
		system("rm -f %s/*" % destination_path)
		system("mkdir -p %s" % destination_path)

		try:
			try:
				node = self.firebase.getNode("users/"+rfid+"/scheda.zip")
			except Exception as e:
				raise e
			try:
				node.download(filename_path)
			except Exception as e:
				raise e
		except Exception as e:
			raise e#Exception("Impossibile scaricare file dal server. Contatta la segreteria!")

		try:
			with zipfile.ZipFile(filename_path,"r") as zip_ref:
				for zip_info in zip_ref.infolist():
					if zip_info.filename[-1] == '/':
						continue
					zip_info.filename = path.basename(zip_info.filename)
					zip_ref.extract(zip_info, destination_path)
		except Exception:
			raise Exception("Impossibile estrarre scheda dall'archivio. Contatta la segreteria!")
		
		try:
			qr = pyqrcode.create('https://firebasestorage.googleapis.com/v0/b/master-fitness.appspot.com/o/users%2F'+rfid+'%2Fscheda.pdf?alt=media')
			qr.png(destination_path+'/qr_code.png', scale=4)
		except Exception as e:
			raise Exception("Impossibile creare il QR Code. Contatta la segreteria!")

	def loadViewerScreen(self, card_no, *largs):
		try:
			user_data = self.getUserData(card_no)
			rfid = self.getUserRFID(user_data)
			destination_path = "storage_data/"+rfid
			filename_path = '%s/%s' % (destination_path, user_data['file'])
			fileExists = path.isfile(filename_path)
			if not fileExists: self.downloadUserFile(user_data, rfid, destination_path, filename_path)
			self.viewer_screen.setUserData(user_data)
			self.screen_manager.current = 'viewer'

		except Exception as e:
			self.showHint(str(e))

	def handler(self, card_no):
		Clock.schedule_once(partial(self.home_screen.setHintMessage, "Carico scheda..."), -1)
		self.screen_manager.current = 'home'
		Clock.schedule_once(partial(self.loadViewerScreen, card_no), 0.1)

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

#system("convert -density 140 "+destination_path+"/scheda.pdf -quality 50 "+destination_path+"/scheda_%01d.jpg")
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
		self.viewer_screen = ViewerScreen(name='viewer', firebase=self.firebase)
		self.screen_manager.add_widget(self.home_screen)
		self.screen_manager.add_widget(self.viewer_screen)

	def build(self):
		self.rfidReader.start()
		return self.screen_manager

	def __del__(self):
		self.rfidReader.stop()

	def getUserData(self, rfid):
		try:
			user_data = self.firebase.get("users/"+rfid).val()
			return user_data
		except Exception:
			raise Exception("Nessuna connessione ad internet. Contatta la segreteria!")

	def downloadUserFile(self, rfid, destination_path, filename_path):
		try:
			print("CREATING FOLDERS...")
			system("mkdir -p %s" % destination_path)
			system("rm -f %s/*" % destination_path)
			print("FOLDERS CREATED!")
			print("FIREBASE NODE ACCESSING...")
			node = self.firebase.getNode("users/"+rfid+"/scheda.zip")
			print("NODE DONE!")
			print("DOWNLOADING...")
			node.download(filename_path)
			print("DOWNLOADED!")
		except Exception as e:
			raise Exception("Impossibile scaricare file dal server. "+str(e))

		self.extractUserFile(rfid, destination_path, filename_path)

	def extractUserFile(self, rfid, destination_path, filename_path):
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

	def loadViewerScreen(self, rfid, *largs):
		print("loadViewerScreen")
		try:
			# try to download user data from firebase
			print("GETTING USER DATA...\n...\n")
			user_data = self.getUserData(rfid)
			print("DATA DOWNLOADED!")
			# if user data is not found, raise exception
			if not user_data: raise Exception("Utente non registrato. Chiedi informazioni in segreteria!")
			
			destination_path = "storage_data/"+rfid
			# ex. filename_path: storage_data/0123456789/scheda_2019-12-28_02-06-09.zip
			filename_path = '%s/%s' % (destination_path, user_data['file'])
			# if .zip file doesnt exist download from firebase, else check if hasnt been already unzipped (in case of SCP Secure Copy)
			if not path.isfile(filename_path):
				print("no file found")
				self.downloadUserFile(rfid, destination_path, filename_path)
				print("END downloadUserFile!")
			else:
				schedaName_path = destination_path+'/scheda_0.jpg'
				if not path.isfile(schedaName_path):
					print("not extracted... EXTRACTING...")
					self.extractUserFile(rfid, destination_path, filename_path)
					print("EXTRACTED")
			print("setting user data...")
			self.viewer_screen.setUserData(user_data)
			print("setUserData")
			self.screen_manager.current = 'viewer'

		except Exception as e:
			self.showHint(str(e))

	def handler(self, rfid):
		print("\n\nCarico scheda...")
		Clock.schedule_once(partial(self.home_screen.setHintMessage, "Carico scheda..."), -1)
		self.screen_manager.current = 'home'
		Clock.schedule_once(partial(self.loadViewerScreen, rfid), 0.1)

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
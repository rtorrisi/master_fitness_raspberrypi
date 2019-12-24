from kivy.uix.screenmanager import Screen
from kivy.uix.progressbar import ProgressBar
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.properties import NumericProperty, BooleanProperty
from kivy.graphics import Rectangle

class HomeScreen(Screen):
	def __init__(self,**kwargs):
		super(HomeScreen, self).__init__(**kwargs)
		with self.canvas:
			self.bg = Rectangle(source='app_data/background_home.jpg', pos=self.pos, size=self.size)
		self.bind(pos=self.update_bg)
		self.bind(size=self.update_bg)

		boxlayout = BoxLayout(
			orientation='vertical',
			padding=30
		)
		logo = Image(
			size_hint=(1, 3),
			source='app_data/master_fitness_logo_w.png'
		)
		# img_RFID = Image(
		# 	size_hint=(1, 0.6),
		# 	source='app_data/rfid.png'
		# )
		self.anchorlayout = AnchorLayout(
			size_hint=(1, 0.4),
			anchor_x='center',
			anchor_y='center'
		)
		self.hint = Label(
			size_hint=(1, 1),
			font_size=30,
			italic=True,
			text=""
		)
		self.anchorlayout.add_widget(self.hint)
		boxlayout.add_widget(logo)
		boxlayout.add_widget(self.anchorlayout)
		#boxlayout.add_widget(img_RFID)
		self.add_widget(boxlayout)
	
	def on_leave(self):
		self.setHintMessage("")

	def update_bg(self, *args):
		self.bg.pos = self.pos
		self.bg.size = self.size

	def setHintMessage(self, text, *largs):
		self.hint.text = text

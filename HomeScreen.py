from kivy.uix.screenmanager import Screen
from kivy.uix.progressbar import ProgressBar
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.properties import NumericProperty, BooleanProperty
from kivy.graphics import Rectangle
from kivy.properties import StringProperty
from kivy.clock import Clock

class HomeScreen(Screen):
	src = StringProperty("")

	def __init__(self,**kwargs):
		super(HomeScreen, self).__init__(**kwargs)
		with self.canvas:
			self.bg = Rectangle(source='app_data/background_home.jpg', pos=self.pos, size=self.size)
		self.bind(pos=self.update_bg)
		self.bind(size=self.update_bg)

		self.ads_list = ['app_data/master_fitness_logo_w.png', 'app_data/rt_logo.png', 'app_data/freesound_logo.png']
		self.current_ads_index = 0
		self.ads_event = None
		self.main_ads_timeout = 30
		self.ads_timeout = 10

		boxlayout = BoxLayout(
			orientation='vertical',
			padding=30
		)
		self.ads_logo = Image(
			size_hint=(1, 3),
			source=self.src
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
		boxlayout.add_widget(self.ads_logo)
		boxlayout.add_widget(self.anchorlayout)
		#boxlayout.add_widget(img_RFID)
		self.add_widget(boxlayout)

	def changeAds(self, *largs):
		self.current_ads_index = (self.current_ads_index+1) % len(self.ads_list)
		self.ads_logo.source = self.ads_list[self.current_ads_index]
		self.rescheduleAds()
		
	def on_src(self, instance, value):
		if self.ads_logo:
			self.ads_logo.source = value

	def rescheduleAds(self):
		Clock.unschedule(self.ads_event)
		self.ads_event = Clock.schedule_once(self.changeAds, self.main_ads_timeout if self.current_ads_index == 0 else self.ads_timeout)

	def on_pre_enter(self):
		self.current_ads_index = 0
		self.ads_logo.source = self.ads_list[self.current_ads_index]
		self.rescheduleAds()

	def on_leave(self):
		Clock.unschedule(self.ads_event)
		self.setHintMessage("")

	def update_bg(self, *args):
		self.bg.pos = self.pos
		self.bg.size = self.size

	def setHintMessage(self, text, *largs):
		self.hint.text = text

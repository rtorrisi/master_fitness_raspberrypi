from kivy.uix.screenmanager import Screen
from kivy.uix.progressbar import ProgressBar
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.properties import NumericProperty, BooleanProperty
from kivy.graphics import Rectangle

class HomeScreen(Screen):
	bar_visibility = BooleanProperty(False)
	hint_visibility = BooleanProperty(False)
	bar_value = NumericProperty(0)

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
			size_hint=(1, 1),
			source='app_data/master_fitness_logo_w.png'
		)
		img_RFID = Image(
			size_hint=(1, 0.6),
			source='app_data/rfid.png'
		)
		self.anchorlayout = AnchorLayout(
			size_hint=(1, 0.2),
			anchor_x='center',
			anchor_y='center'
		)
		self.anchorlayout2 = AnchorLayout(
			size_hint=(1, None),
			height='0dp',
			anchor_x='center',
			anchor_y='center'
		)
		self.hint = Label(
			size_hint=(1, 1),
			font_size=20,
			italic=True,
			text=""
		)
		self.progressbar = ProgressBar(
			size_hint=(0.8, None),
			value=0, opacity=0
		)
		self.anchorlayout.add_widget(self.progressbar)
		self.anchorlayout2.add_widget(self.hint)
		boxlayout.add_widget(logo)
		boxlayout.add_widget(self.anchorlayout2)
		boxlayout.add_widget(self.anchorlayout)
		boxlayout.add_widget(img_RFID)
		self.add_widget(boxlayout)
	
	def on_enter(self):
		self.bar_visibility = False
		self.setHintVisibility("", False)
		self.bar_value = 0

	def on_leave(self):
		self.bar_visibility = False
		self.setHintVisibility("", False)
		self.bar_value = 0
		
	def on_bar_visibility(self, instance, value):
		self.progressbar.opacity = 1 if value else 0

	def on_bar_value(self, isinstance, value):
		self.progressbar.value = value

	def update_bg(self, *args):
		self.bg.pos = self.pos
		self.bg.size = self.size

	def setHintVisibility(self, text, visible, *largs):
		self.hint_visibility = visible
		if visible:
			self.hint.text = text
			self.anchorlayout2.size_hint_y=0.2
			self.anchorlayout.size_hint_y=None
			self.anchorlayout.height='0dp'
		else:
			self.hint.text = ""
			self.anchorlayout2.size_hint_y=None
			self.anchorlayout2.height='0dp'
			self.anchorlayout.size_hint_y=0.2

	def setBarVisibility(self, visible, *largs):
		self.bar_visibility = visible

	def setBarValue(self, value, *largs):
		self.bar_value = value

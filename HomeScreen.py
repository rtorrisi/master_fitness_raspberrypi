from kivy.uix.screenmanager import Screen
from kivy.uix.progressbar import ProgressBar
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.properties import NumericProperty, BooleanProperty
from kivy.graphics import Rectangle

class HomeScreen(Screen):
	bar_visibility = BooleanProperty(False)
	bar_value = NumericProperty(0)

	def __init__(self,**kwargs):
		super(HomeScreen, self).__init__(**kwargs)
		with self.canvas:
			self.bg = Rectangle(source='app_data/background.jpg', pos=self.pos, size=self.size)
		self.bind(pos=self.update_bg)
		self.bind(size=self.update_bg)

		boxlayout = BoxLayout(
			orientation='vertical'
		)
		image = Image(
			size_hint=(1, 0.8),
			source='app_data/master_fitness_logo_w.png'
		)
		anchorlayout = AnchorLayout(
			size_hint=(1, 0.2),
			anchor_y='top'
		)
		self.progressbar = ProgressBar(
			size_hint=(0.8, None),
			value=0, opacity=0
		)

		anchorlayout.add_widget(self.progressbar)
		boxlayout.add_widget(image)
		boxlayout.add_widget(anchorlayout)
		self.add_widget(boxlayout)
	
	def on_leave(self):
		self.bar_visibility = False
		self.bar_value = 0
		
	def on_bar_visibility(self, instance, value):
		self.progressbar.opacity = 1 if value else 0

	def on_bar_value(self, isinstance, value):
		self.progressbar.value = value

	def update_bg(self, *args):
		self.bg.pos = self.pos
		self.bg.size = self.size

	def setBarVisibility(self, visible, *largs):
		self.bar_visibility = visible

	def setBarValue(self, value, *largs):
		self.bar_value = value
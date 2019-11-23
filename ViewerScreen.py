from kivy.uix.screenmanager import Screen
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock

from functools import partial 

class LeftPanel(StackLayout):
    def __init__(self,**kwargs):
        super(LeftPanel, self).__init__(**kwargs)
        with self.canvas:
            Color(0, 0, 0, 0.5)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg)
        self.bind(size=self.update_bg)
    
    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

class ViewerScreen(Screen):
    src = StringProperty("")
    
    def __init__(self,**kwargs):
        super(ViewerScreen, self).__init__(**kwargs)
        with self.canvas:
            self.bg = Rectangle(source='app_data/background.jpg', pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg)
        self.bind(size=self.update_bg)
        
        self.event = None
        self.timeout = 5

        boxlayout = BoxLayout(
			orientation='horizontal'
		)
        leftpanel = LeftPanel(
			orientation='tb-lr',
            size_hint=(0.2, 1),
			padding=15
        )
        image = Image(
            size_hint=(1, None),
            height=200,
            source='app_data/master_fitness_logo_w_noaddr.png'
        )
        label1 = Label(
            size_hint=(1, None),
            height=50,
            halign='left',
            text='Scheda di Allenamento',
            font_size=25
        )
        label2 = Label(
            size_hint=(1, None),
            height=50,
            halign='left',
            text='Riccardo Torrisi',
            font_size=20
        )
        button_container = BoxLayout(
            size_hint=(1, 0.67)
        )
        self.close_button = Button(
            size_hint=(1, None),
            height=50,
            background_normal='',
            background_color= (.04, .85, .9, 1),
            text='Chiudi',
            on_press=self.on_press_close_button,
            on_release=self.on_release_close_button
        )
        self.scrollview = ScrollView(
            size_hint=(0.75, 1)
        )
        slider = Slider(
            orientation='vertical',
            size_hint=(0.05, 0.99),
            min=0, max=1, step=0.01, value=1
        )
        self.scrollview.bind(scroll_y=partial(self.slider_change, slider))
        slider.bind(value=partial(self.scroll_change, self.scrollview))

        self.img_view = Image(
            size_hint=(1, None),
            height=8770,
            source=self.src
        )

        leftpanel.add_widget(image)
        leftpanel.add_widget(label1)
        leftpanel.add_widget(label2)
        button_container.add_widget(self.close_button)
        leftpanel.add_widget(button_container)
        self.scrollview.add_widget(self.img_view)
        boxlayout.add_widget(leftpanel)
        boxlayout.add_widget(self.scrollview)
        boxlayout.add_widget(slider)
        self.add_widget(boxlayout)

    def reschedule(self):
        if self.event:
            Clock.unschedule(self.event)
        self.event = Clock.schedule_once(self.go_to_home, self.timeout)

    def on_enter(self):
        self.scrollview.scroll_y = 1
        self.event = Clock.schedule_once(self.go_to_home, self.timeout)

    def on_pre_leave(self):
        print(self.scrollview.scroll_y)
        if self.event:
            Clock.unschedule(self.event)

    def go_to_home(self, *largs):
        self.manager.current = 'home'

    def scroll_change(self, scrlv, instance, value):
        scrlv.scroll_y = value
        self.reschedule()

    def slider_change(self, slider, instance, value):
        if value >= 0:
        #this to avoid 'maximum recursion depth exceeded' error
            slider.value=value
            self.reschedule()

    def on_press_close_button(self, instance):
        self.close_button.background_color = (.05, 0.86, .91, 1)
        self.go_to_home()

    def on_release_close_button(self, instance):
        self.close_button.background_color = (.04, 0.85, .9, 1)


    def on_src(self, instance, value):
        self.img_view.source = value
        self.img_view.reload()

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def setSourcePath(self, path, *largs):
        self.src = path
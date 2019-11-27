from kivy.uix.screenmanager import Screen
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.properties import StringProperty, NumericProperty
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock

from os import path

class BarPanel(BoxLayout):
    def __init__(self,**kwargs):
        super(BarPanel, self).__init__(**kwargs)
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
    label_text = StringProperty("")
    slider_value = NumericProperty(1)
    
    def __init__(self,**kwargs):
        super(ViewerScreen, self).__init__(**kwargs)
        with self.canvas:
            self.bg = Rectangle(source='app_data/background.jpg', pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg)
        self.bind(size=self.update_bg)
        
        self.event = None
        self.user_data = None
        self.page = 0
        self.saveUserDataCallback = None
        self.timeout = 20

        box_layout = BoxLayout(
			orientation='vertical'
		)
        bar_panel = BarPanel(
			orientation='horizontal',
            size_hint=(1, None),
            height=80,
			padding=7
		)
        image = Image(
            size_hint=(None, 1),
            width=150,
            source='app_data/master_fitness_logo_w_noaddr.png'
        )
        self.label = Label(
            size_hint=(1, 1),
            font_size=30,
            italic=True,
            text=self.label_text
        )
        self.close_button = Button(
            size_hint=(None, None),
            width=70,
            height=70,
            valign='center',
            halign='center',
            background_normal='app_data/close_normal.png',
            background_down='app_data/close_down.png',
            border=(0,0,0,0),
            on_press=self.on_press_close_button,
            on_release=self.on_release_close_button
        )
        self.left_button = Button(
            size_hint=(None, None),
            width=70,
            height=70,
            valign='center',
            halign='center',
            background_normal='app_data/left_normal.png',
            background_down='app_data/left_down.png',
            border=(0,0,0,0),
            on_release=self.on_release_left_button
        )
        self.right_button = Button(
            size_hint=(None, None),
            width=70,
            height=70,
            valign='center',
            halign='center',
            background_normal='app_data/right_normal.png',
            background_down='app_data/right_down.png',
            border=(0,0,0,0),
            on_release=self.on_release_right_button
        )
        anchor_layout1 = AnchorLayout(
			#orientation='horizontal',
            size_hint=(1, 0.8),
            anchor_x='right'
		)
        anchor_layout2 = AnchorLayout(
			#orientation='horizontal',
            size_hint=(1, 0.8),
            anchor_x='right'
		)
        self.scrollview = ScrollView(
            size_hint=(1, 1),
            bar_color=[0,0,0,0],
            bar_inactive_color=[0,0,0,0]
        )
        self.slider = Slider(
            orientation='vertical',
            size_hint=(None, 1),
            width=50,
            min=0, max=1, step=0.01, value=self.slider_value,
            cursor_image='app_data/kettlebell.png',
            cursor_size=('45sp', '45sp'),
            background_vertical='app_data/slider.png',
            background_width='3sp',
            padding='30sp'
        )
        self.scrollview.bind(scroll_y=self.slider_change)
        self.slider.bind(value=self.scroll_change)
        self.img_view = Image(
            size_hint=(1, None),
            height=1754,
			nocache=True,
            source=self.src
        )

        bar_panel.add_widget(image)
        bar_panel.add_widget(self.label)
        bar_panel.add_widget(self.left_button)
        bar_panel.add_widget(self.right_button)
        bar_panel.add_widget(self.close_button)
        self.scrollview.add_widget(self.img_view)
        anchor_layout1.add_widget(self.scrollview)
        anchor_layout1.add_widget(self.slider)
        box_layout.add_widget(bar_panel)
        box_layout.add_widget(anchor_layout1)
        self.add_widget(box_layout)

    def reschedule(self):
        Clock.unschedule(self.event)
        self.event = Clock.schedule_once(self.go_to_home, self.timeout)

    def on_enter(self):
        pass

    def on_pre_leave(self):
        Clock.unschedule(self.event)
        if self.saveUserDataCallback and self.user_data :
            self.saveUserDataCallback(self.user_data['rfid'], {"slider": self.slider_value, "page":self.page})

    def go_to_home(self, *largs):
        self.manager.current = 'home'

    def scroll_change(self, instance, value):
        self.slider_value = value
        self.scrollview.scroll_y = value
        self.reschedule()

    def slider_change(self, instance, value):
        if value >= 0:
        #this to avoid 'maximum recursion depth exceeded' error
            self.slider_value = value
            self.reschedule()

    def on_press_close_button(self, instance):
        pass

    def on_release_close_button(self, instance):
        self.go_to_home()

    def on_release_left_button(self, instance):
        self.reschedule()
        page=self.page-1
        if path.isfile("storage_data/"+str(self.user_data['rfid'])+"/scheda_"+str(page)+".jpg"):
            self.page=page
            self.setSourcePath("storage_data/"+str(self.user_data['rfid'])+"_"+str(self.page)+".jpg")
            self.slider_value = 1

    def on_release_right_button(self, instance):
        self.reschedule()
        page=self.page+1
        if path.isfile("storage_data/"+str(self.user_data['rfid'])+"/scheda_"+str(page)+".jpg"):
            self.page=page
            self.setSourcePath("storage_data/"+str(self.user_data['rfid'])+"_"+str(self.page)+".jpg")
            self.slider_value = 1

    def on_src(self, instance, value):
        self.img_view.source = value

    def on_label_text(self, instance, value):
        self.label.text = value

    def on_slider_value(self, isinstance, value):
        self.slider.value = value

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def setSourcePath(self, path, *largs):
        self.src = path

    def setUserData(self, saveUserDataFunc, user_data, *largs):
        if not self.saveUserDataCallback:
            self.saveUserDataCallback = saveUserDataFunc

        if not self.user_data or self.user_data['rfid'] != user_data['rfid']:
            if self.user_data and self.user_data['rfid'] != user_data['rfid']:
                self.saveUserDataCallback(self.user_data['rfid'], {"slider":  self.slider_value, "page": self.page})
            self.user_data = user_data
            self.page = self.user_data['page']
            self.setSourcePath("storage_data/"+str(self.user_data['rfid'])+"/scheda_"+str(self.page)+".jpg")
            self.slider_value = self.user_data['slider']
            self.label_text = "Scheda di "+self.user_data['name']+" "+self.user_data['surname']

        self.reschedule()

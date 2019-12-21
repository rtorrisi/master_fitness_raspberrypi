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
from kivy.effects.scroll import ScrollEffect
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
    
    def __init__(self, saveFunc, **kwargs):
        super(ViewerScreen, self).__init__(**kwargs)
        with self.canvas:
            self.bg = Rectangle(source='app_data/background.jpg', pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg)
        self.bind(size=self.update_bg)
        
        self.event = None
        self.user_data = None
        self.page = 0
        self.default_zoom = [1, 2.79]
        self.num_pages = 0
        self.saveUserDataCallback = saveFunc
        self.timeout = 30

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
            font_size=20,
            italic=True,
            text=self.label_text
        )
        self.labelPage = Label(
            size_hint=(None, 1),
            width=50,
            font_size=30,
            italic=True
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
        self.zoomOut_button = Button(
            size_hint=(None, None),
            width=70,
            height=70,
            valign='center',
            halign='center',
            background_normal='app_data/zoomOut_normal.png',
            background_down='app_data/zoomOut_down.png',
            border=(0,0,0,0),
            on_release=self.on_release_zoomOut_button
        )
        self.zoomIn_button = Button(
            size_hint=(None, None),
            width=70,
            height=70,
            valign='center',
            halign='center',
            background_normal='app_data/zoomIn_normal.png',
            background_down='app_data/zoomIn_down.png',
            border=(0,0,0,0),
            on_release=self.on_release_zoomIn_button
        )
        anchor_layout = AnchorLayout(
            size_hint=(1, 0.8),
            anchor_x='right'
        )
        self.scrollview = ScrollView(
            size_hint=(1, 1),
            bar_color=[0,0,0,0],
            bar_inactive_color=[0,0,0,0],
            effect_cls=ScrollEffect
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
        self.img_view = None #Image(size_hint=(1, None), height=1450, nocache=True, source=self.src)

        bar_panel.add_widget(image)
        bar_panel.add_widget(self.label)
        bar_panel.add_widget(self.zoomOut_button)
        bar_panel.add_widget(self.zoomIn_button)
        bar_panel.add_widget(self.left_button)
        bar_panel.add_widget(self.labelPage)
        bar_panel.add_widget(self.right_button)
        bar_panel.add_widget(self.close_button)
        #self.scrollview.add_widget(self.img_view)
        anchor_layout.add_widget(self.scrollview)
        anchor_layout.add_widget(self.slider)
        box_layout.add_widget(bar_panel)
        box_layout.add_widget(anchor_layout)
        self.add_widget(box_layout)

    def reschedule(self):
        Clock.unschedule(self.event)
        self.event = Clock.schedule_once(self.go_to_home, self.timeout)

    def on_enter(self):
        self.img_view = Image(
            size_hint=(self.default_zoom[0], self.default_zoom[1]),
            allow_stretch = True,
            nocache=True,
            source=self.src
        )
        self.img_view.bind(size_hint=self.on_img_hint_update)
        self.scrollview.add_widget(self.img_view)
        self.page = self.user_data['page']
        self.num_pages = self.user_data['num_pages']
        self.labelPage.text=str(self.page+1)+"/"+str(self.num_pages)
        self.label_text = "Scheda di "+self.user_data['name']+" "+self.user_data['surname']
        self.setSourcePath("storage_data/"+str(self.user_data['rfid'])+"/scheda_"+str(self.page)+".jpg")
        try:
            self.slider_value = self.user_data['slider_y']
            self.scrollview.scroll_x = self.user_data['slider_x']
            zoom = self.user_data['zoom']
            if zoom[0] == 0 and zoom[1] == 0:
                zoom = self.default_zoom
            self.img_view.size_hint = (zoom[0], zoom[1])
        except:
            self.slider_value = 1
            self.scrollview.scroll_x = 0.5
            self.img_view.size_hint = (self.default_zoom[0], self.default_zoom[1])
        self.reschedule()

    def on_pre_leave(self):
        Clock.unschedule(self.event)
        if self.saveUserDataCallback and self.user_data :
            self.saveUserDataCallback(self.user_data['rfid'], {"page": self.page, "zoom": self.img_view.size_hint, "slider_y": self.slider_value, "slider_x": self.scrollview.scroll_x})
    
    def on_leave(self):
        self.scrollview.remove_widget(self.img_view)
        self.img_view = None

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

    def on_release_close_button(self, instance):
        self.go_to_home()

    def on_release_left_button(self, instance):
        self.reschedule()
        page=self.page-1
        if path.isfile("storage_data/"+str(self.user_data['rfid'])+"/scheda_"+str(page)+".jpg"):
            self.page=page
            self.labelPage.text=str(self.page+1)+"/"+str(self.num_pages)
            self.setSourcePath("storage_data/"+str(self.user_data['rfid'])+"/scheda_"+str(self.page)+".jpg")
            self.slider_value = 1

    def on_img_hint_update(self, instance, value):
        scroll_x = self.scrollview.scroll_x
        self.scrollview.scroll_x = scroll_x
        self.reschedule()

    def on_release_zoomOut_button(self, instance):
        if self.img_view.size_hint_x / 1.2 >= 1:
            if self.img_view:
                self.img_view.size_hint = (self.img_view.size_hint_x / 1.2, self.img_view.size_hint_y / 1.2)
                self.img_view.width = 0
        else:
            self.scrollview.scroll_x = 0.5

    def on_release_zoomIn_button(self, instance):
        if self.img_view.size_hint_x * 1.2 <= 3:
            if self.img_view:
                self.img_view.size_hint = (self.img_view.size_hint_x * 1.2, self.img_view.size_hint_y * 1.2)
                self.img_view.width = 0

    def on_release_right_button(self, instance):
        self.reschedule()
        page=self.page+1
        if path.isfile("storage_data/"+str(self.user_data['rfid'])+"/scheda_"+str(page)+".jpg"):
            self.page=page
            self.labelPage.text=str(self.page+1)+"/"+str(self.num_pages)
            self.setSourcePath("storage_data/"+str(self.user_data['rfid'])+"/scheda_"+str(self.page)+".jpg")
            self.slider_value = 1

    def on_src(self, instance, value):
        if self.img_view:
            self.img_view.source = value
        else:
            print("img_view is None")

    def on_label_text(self, instance, value):
        self.label.text = value

    def on_slider_value(self, isinstance, value):
        self.slider.value = value

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def setSourcePath(self, path, *largs):
        self.src = path

    def setUserData(self, user_data, *largs):
        self.user_data = user_data

import kivy

kivy.require('1.10.1')

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.togglebutton import ToggleButton
import cv2


def ListDevices():
    # How many camera devices do we have?
    cam_index = 0
    devices = []
    while True:
        cap = cv2.VideoCapture(cam_index)
        if not cap.read()[0]:
            break
        else:
            devices.append(cam_index)
        cap.release()
        cam_index += 1

    devices = [0, 1, 2]

    return devices


class Settings(GridLayout):
    def __init__(self, **kwargs):
        super(Settings, self).__init__(**kwargs)

        button_group = GridLayout(rows=1)

        devices = ListDevices()

        for idx, cam in enumerate(devices):
            if idx == 0:
                btn = ToggleButton(text='Camera {}'.format(cam), group='cameras', state='down')
                self.SelectedCam = cam
            else:
                btn = ToggleButton(text='Camera {}'.format(cam), group='cameras')
            btn.bind(on_press=self.SelectCam)
            button_group.add_widget(btn)

        self.add_widget(Label(text='Select Camera'))
        self.add_widget(button_group)

        self.cols = 1
        self.add_widget(Label(text='User Name'))
        self.add_widget(Label(text='2 Name'))

    def SelectCam(self, btn):
        cam_number = int(btn.text.split(' ')[1])
        self.SelectedCam = cam_number
        print(cam_number)


class Screen(GridLayout):

    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.cols = 2

        self.add_widget(Settings())
        # self.username = TextInput(multiline=False)
        # self.add_widget(self.username)
        self.add_widget(Label(text='password'))
        self.password = TextInput(password=True, multiline=False)
        self.add_widget(self.password)


class MyApp(App):

    def build(self):
        return Screen()


if __name__ == '__main__':
    MyApp().run()

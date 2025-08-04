import re
import ssl
import urllib.request
from functools import partial

from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivymd.app import MDApp
from kivymd.uix.relativelayout import MDRelativeLayout
from yt_dlp import YoutubeDL

Window.size = (500, 600)


class MyApp(MDApp):

    def __init__(self):
        super().__init__()
        self.link = None
        self.video_info = None
        self.selected_resolution = '480p'  # Default resolution
        self.dropdown_button = Button(text=f"{self.selected_resolution}", size_hint=(None, None), size=(130, 90),
                                      pos=(435, 186),
                                      height=50)
        self.download_button_text = "Download"

    def get_link_info(self, event, layout):
        self.link = self.link_input.text
        self.validate_link = re.match("^https://www.youtube.com/.*", self.link)

        if self.validate_link:

            self.dropdown_button.pos = (435, 186)

            self.error_label.text = ""
            self.error_label.pos_hint = {'center_x': .5, 'center_y': 20}

            try:
                self.error_label.text = ""
                self.error_label.pos_hint = {'center_x': .5, 'center_y': 20}

                # Disable SSL certificate verification
                # ssl_context = ssl.create_default_context()
                # ssl_context.check_hostname = False
                # ssl_context.verify_mode = ssl.CERT_NONE

                # Use SSL context to disable certificate verification
                ydl_opts = {
                    'quiet': True,
                    'format': f'best[ext=mp4]/best',  # Default to MP4 format
                }

                with YoutubeDL(ydl_opts) as ydl:
                    self.video_info = ydl.extract_info(self.link, download=False)
                    # self.video_info = urllib.request.urlopen(self.link, context=ssl_context)

                    if 'entries' in self.video_info:
                        self.video_info = self.video_info['entries'][0]
                    self.author_label.text = f"Author: {self.video_info.get('uploader')}"
                    self.title_label.text = f"Title: {self.video_info.get('title')}"
                    self.views_label.text = f"Views: {self.video_info.get('view_count')}"
                    self.length_label.text = f"Length: {self.video_info.get('duration')} seconds"

                    self.download_button.text = self.download_button_text
                    self.download_button.pos_hint = {'center_x': .5, 'center_y': .23}
                    self.download_button.size_hint = (.2, .05)

                    video_formats = self.video_info.get('formats', [])

                    resolutions = [resolution.get('format_note') for resolution in video_formats if
                                   resolution.get('ext') == 'mp4']
                    res_options = sorted(set(res for res in resolutions if res is not None))

                    # Update the DropDown widget with resolution options
                    self.drop_down.clear_widgets()
                    for res in res_options:
                        btn = Button(text=res, size_hint_y=None, height=30)
                        btn.bind(on_release=lambda btn: self.drop_down.select(btn.text))
                        self.drop_down.add_widget(btn)

                    self.main_button = self.dropdown_button

                    self.main_button.bind(on_release=self.drop_down.open)
                    self.drop_down.bind(on_select=lambda instance, x: setattr(self.main_button, "text", x))

                    layout.add_widget(self.main_button)
            except:
                self.author_label.text = ""
                self.title_label.text = ""
                self.views_label.text = ""
                self.length_label.text = ""
                self.download_button.pos_hint = {'center_x': .5, 'center_y': 30}

                self.dropdown_button.pos = (435, -50)
                self.error_label.text = "Network/Unknown Error"
                self.error_label.pos_hint = {'center_x': .5, 'center_y': .45}

        else:
            self.author_label.text = ""
            self.title_label.text = ""
            self.views_label.text = ""
            self.length_label.text = ""
            self.download_button.pos_hint = {'center_x': .5, 'center_y': 30}

            self.dropdown_button.pos = (435, -50)
            self.error_label.text = "Invalid or Empty Link"
            self.error_label.pos_hint = {'center_x': .5, 'center_y': .45}

    def download(self, event, layout):

        ydl_opts = {
            'quiet': True,
            'format': f'best[ext=mp4]/best',  # Default to MP4 format
        }

        with YoutubeDL(ydl_opts) as ydl:
            self.download_button.text = "Downloading..."
            self.download_button.pos_hint = {'center_x': .5, 'center_y': .23}
            self.download_button.size_hint = (.2, .05)

            self.download_progress_label.text = str(ydl.download(self.link))
            self.download_progress_label.pos_hint = {'center_x': .5, 'center_y': .09}
            self.download_progress_label.color = (0, 0, 1)

            self.download_status_label.text = "Download Complete"

    def build(self):
        layout = MDRelativeLayout(md_bg_color=[210 / 255, 210 / 255, 210 / 255])

        self.img = Image(source='youtube-logo.png', size_hint=(.3, .3), pos_hint={'center_x': .5, 'center_y': 0.90})
        self.youtube_link = Label(text="Enter the YouTube link to get info.",
                                  size_hint=(1, 1), pos_hint={'center_x': .5, 'center_y': .77},
                                  font_size=28, color=(1, 0, 0))
        self.link_input = TextInput(text="", size_hint=(.94, .04), pos_hint={'center_x': 0.5, 'center_y': 0.65},
                                    font_size=28, foreground_color=(0, .5, 0))
        self.link_button = Button(text="Get Link Info", size_hint=(.2, .05),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.57},
                                  font_size=28, background_color=(0, 1, 0))
        self.link_button.bind(on_press=partial(self.get_link_info, layout))

        self.author_label = Label(text="", size_hint=(1, 1), pos_hint={'center_x': .5, 'center_y': .45},
                                  font_size=26, color=(0, 0, 1))
        self.title_label = Label(text="", size_hint=(1, 1), pos_hint={'center_x': .5, 'center_y': .41},
                                 font_size=26, color=(0, 0, 1))
        self.views_label = Label(text="", size_hint=(1, 1), pos_hint={'center_x': .5, 'center_y': .37},
                                 font_size=26, color=(0, 0, 1))
        self.length_label = Label(text="", size_hint=(1, 1), pos_hint={'center_x': .5, 'center_y': .33},
                                  font_size=26, color=(0, 0, 1))
        self.download_button = Button(text="", size_hint=(1, 1), size=(75, 75),
                                      pos_hint={'center_x': .5, 'center_y': 20},
                                      font_size=26, color=(1, 1, 1), bold=True, background_color=(0, 1, 0))

        self.download_button.bind(on_press=partial(self.download, layout))

        self.download_progress_label = Label(text="", size_hint=(1, 1), pos_hint={'center_x': .5, 'center_y': .09},
                                             font_size=24, color=(0, 0, 1))
        self.download_status_label = Label(text="", size_hint=(1, 1), pos_hint={'center_x': .5, 'center_y': .05},
                                           font_size=25, color=(0, .5, 0))

        self.error_label = Label(text="", size_hint=(1, 1), size=(75, 75), pos_hint={'center_x': .5, 'center_y': 20},
                                 font_size=24, color=(1, 0, 0))

        self.drop_down = DropDown()

        layout.add_widget(self.img)
        layout.add_widget(self.youtube_link)
        layout.add_widget(self.link_input)
        layout.add_widget(self.link_button)
        layout.add_widget(self.author_label)
        layout.add_widget(self.title_label)
        layout.add_widget(self.views_label)
        layout.add_widget(self.length_label)
        layout.add_widget(self.download_button)
        layout.add_widget(self.error_label)
        layout.add_widget(self.download_progress_label)
        layout.add_widget(self.download_status_label)

        return layout


if __name__ == "__main__":
    MyApp().run()

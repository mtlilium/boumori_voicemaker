# -*- coding: utf-8 -*-
import json

class UserParams():
    def __init__(self):
        super().__init__()
        self.sample_rate = 24000
        self.sample_width = 2
        self.num_channel = 1

        self.open_config()

    def open_config(self):
        dic_lang = {'Japanese':'ja',
                    'English':'en',
                    'French':'fr',
                    'German':'de',
                    'Latin':'la',
                    'Spanish':'es',
                    'Russian':'ru',
                    'Chinese':'zh-cn'
                    }

        with open('config.json', encoding='utf-8') as f:
            df = json.load(f)
            self.lang = dic_lang[df["lang"]]
            self.default_interval = df["default_interval"]
            self.difficulty = df["difficulty"]
            self.speed = df["speed"]
            self.pitch = df["pitch"]
            self.female = df["female"]
            self.file_path = df["file_path"]
            self.export_name = df["export_name"]

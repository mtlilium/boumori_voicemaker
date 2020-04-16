# -*- coding: utf-8 -*-
import numpy as np
import os
import sys
import re
import gtts
import shutil
import wave
import subprocess
import threading
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.playback import play
from pydub import effects
import pyworld as pw

default_params = {"lang": "Japanese","default_interval": 0.5,"difficulty": 3,"export_name": "result","speed": 1.0,"pitch": 1.0,"female": 1.0}

class BoumoriVoice():


    def __init__(self, serif="こんにちは", params=default_params):
        self.cache = None # AudioSegment
        self.serifs = serif
        self.params = params

        self.output = AudioSegment.silent(0)

    def create_original(self, s):
        size = len(s)
        chrs = []

        gtts.gTTS(text=s, lang=self.params['lang']).save("tmp/original__bit64riff__.wav")
        cmd = f"ffmpeg -y -i " + "tmp/original__bit64riff__.wav " + "-ab 32000 tmp/original.wav"
        subprocess.call(cmd, shell=True, stdout=subprocess.PIPE)
        subprocess.call(f"rm " + "tmp/original__bit64riff__.wav", shell=True)

    def split_original(self, sil_thr=-30):
        # wavファイルのデータ取得
        sound = AudioSegment.from_file("tmp/original.wav", format="wav")

        # wavデータの分割（無音部分で区切る）
        chunks = split_on_silence(sound, min_silence_len=10, silence_thresh=sil_thr, keep_silence=10)

        chunk_list = []
        # 分割したデータ毎にファイルに出力
        for i, chunk in enumerate(chunks):
            if chunk.duration_seconds >= 0.8:
                tmp_len = int(chunk.duration_seconds * 1000)
                mae = chunk[int(tmp_len/8):int(tmp_len/2)]
                ushiro = chunk[int(tmp_len/2.25):]
                chunk_list.append(mae)
                chunk_list.append(ushiro)
            else:
                chunk_list.append(chunk)

        del chunks
        subprocess.call(f"rm " + "tmp/original.wav", shell=True)

        return chunk_list

    def doumolize(self, chunks, pitch=2.0, female=1.8, speed=1.0, during=0.5, difficulty=3):
        # chunk ごとに処理
        element = []
        for index, chunk in enumerate(chunks):
            # numpy.float型の配列じゃないと pyworld 動かない
            chunk = effects.compress_dynamic_range(chunk)
            arr_chunk = np.array(chunk.get_array_of_samples()).astype(np.float)
            if index % 2 == 0:
                data = arr_chunk[int(len(arr_chunk)/(11 - difficulty)):]
            else:
                data = arr_chunk[int(len(arr_chunk)/(7 - difficulty)):]

            fs = chunk.frame_rate

            _f0, t = pw.dio(data, fs)  # 基本周波数の抽出
            f0 = pw.stonemask(data, _f0, t, fs)  # 基本周波数の修正
            sp = pw.cheaptrick(data, f0, t, fs)  # スペクトル包絡の抽出
            ap = pw.d4c(data, f0, t, fs)  # 非周期性指標の抽出

            # pitch
            new_freq = f0*pitch  # 周波数を2倍にすると1オクターブ上がる

            # スペクトル包絡 (gender)
            gender_sp = np.zeros_like(sp)
            for f in range(gender_sp.shape[1]):
                # gender > 1 でより女性的
                gender_sp[:, f] = sp[:, int(f/female)]

            if chunk.duration_seconds > 0.2:
                synthesized = pw.synthesize(new_freq, gender_sp, ap, fs)
            else:
                continue

            sozai = AudioSegment(
                                synthesized.astype("int16").tobytes(),
                                sample_width=chunk.sample_width,
                                frame_rate=chunk.frame_rate,
                                channels=chunk.channels
                                )
            sozai = effects.compress_dynamic_range(sozai)
            element.append(sozai)
            sozai.export("tmp/sozai_"+ str(index)+".wav", format="wav")

        # element[i].duration_seconds が短いと index out of range になります ! (投げやり)
        concated = element[0].fade_in(80).fade_out(50)
        for i in range(1, len(element)):
            concated = concated + element[i].fade_in(100).fade_out(50)

        delay = AudioSegment.silent(1000*speed*during)
        concated = concated + delay

        return concated

    def main(self):

        dur_pattern = '<(.+)>'
        self.output = AudioSegment.silent(0)

        os.makedirs("tmp", exist_ok=True)
        os.makedirs("output", exist_ok=True)

        for index, line in enumerate(self.serifs):
            if line == '':
                continue
            if len(re.findall(dur_pattern, line)) == 0:
                dur = self.params['default_interval']
            else:
                dur = float(re.findall(dur_pattern, line)[0])
            serif = re.sub(dur_pattern, '', line)

            print("===いまから このセリフを 変換するだなも !===")
            print(serif)

            self.create_original(serif)

            chunks = self.split_original() #AudioSegment型

            concated = self.doumolize(chunks,pitch=self.params['pitch'],female=self.params['female'],speed=self.params['speed'],during=dur,difficulty=self.params['difficulty'])

            print("===できたなも!===\n")

            self.output = self.output + concated


        self.output.export("tmp/out.wav", format="wav")

        # 仕上げ
        cmd = f'ffmpeg -y -i tmp/out.wav -filter:a "atempo=' + str(self.params['speed']) + '" -vn output/' + str(self.params['export_name'])
        subprocess.call(cmd, shell=True, stdout=subprocess.PIPE)
        subprocess.call(f"rm " + "tmp/out.wav", shell=True)
        shutil.rmtree('tmp')

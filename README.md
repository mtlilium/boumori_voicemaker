# boumori_voicemaker

# 必要環境

- Python 3.7
- ffmpeg
- gTTS
- pydub
- pyworld

# 使いかた

1. config.json でパラメータの設定
2. tool_main.py を実行

# パラメータの説明

#### speed : 速さ (default = 1.0)
> 0.1 <= speed <= 10.0
>
> 再生スピード

#### pitch : ピッチ (default = 1.0)
> 0.125 <= pitch <= 16.0
>
> 2 倍で 1 オクターブの変化

#### female : 女性らしさ (default = 1.0)
> 1.0 <= female <= 3.0
>  
> フォルマントシフト

#### language : 言語 (default = Japanese)
> GTTS がサポートしている言語ならば扱える

#### default interval : 間隔の指定が無いときの値 (秒)
> 0.0 <= default interval <= 10.0$

#### difficulty : 聞き取りづらさ (default = 3)
> 1 <= difficulty <= 3
>  
> 高い値ほど, 音素が削れて詰まった声になる

# 入力形式

テキストファイルに喋らせたいセリフを打ち込む. 入力方式は

> 文章 <間隔 (秒)>
>
> 文章 <間隔 (秒)>
>
> .....

<> 内は半角でお願いします.

# 紹介記事
[GTTS + 音声処理で某ぶつの森風ボイスメーカーを作りたかったんだなも！](https://ch-random.net/post/94/)

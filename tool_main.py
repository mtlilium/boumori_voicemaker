# -*- coding: utf-8 -*-
from user_params import UserParams
from boumori import BoumoriVoice

def load_txt(file_path):
    with open(file_path, encoding='utf-8') as f:
        s = f.read().split('\n')
    return s

def main():
    user = UserParams()
    s = load_txt(user.file_path)
    boumori = BoumoriVoice(serif=s, params=user.__dict__)
    boumori.main()

if __name__ == '__main__':
    main()

import os
import json
from bs4 import BeautifulSoup
import requests
from http_helper import HttpHelper
from pathlib import Path
import jsonpickle

class Word():
    def __init__(self, text):
        self.text = text
        self.partOfSpeech = {}
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4, ensure_ascii=False)

def save_file(filename, data):
    try:
        with open(filename, 'w+') as f:
            f.write(data)
    except IOError as e:
        print('Error saving file: {0}'.format(e.message))

def go():
    p = Path('../../projects/wiktionary-downloads')
    files = [x for x in p.iterdir()]

    # TEMP_P = Path('../../projects/wiktionary-downloads/zapato.html')
    # TEMP_F_IDX = files.index(TEMP_P)

    # for file in files[TEMP_F_IDX:TEMP_F_IDX+1]:
    for file in [f for f in files  if f.suffix == '.html']:
        name = os.path.splitext(os.path.basename(file))[0]
        with open(file, encoding='utf-8') as f:
            try:
                soup = BeautifulSoup(f.read(), 'html.parser')
                spanish_section = soup.find('span', id='Spanish')
                headwords = soup.findAll('strong', lang='es') #absurdo, absurdo
                parts_of_speech = [] # Adjective, Noun
                parts_of_speech_containers = []
                gender_forms = {}
                words = []
                w = Word(name)

                for h in headwords:
                    # print('Headword: {0}'.format(h.string))
                    pos = h.findParent().findPrevious('h3').find('span')
                    # print('POS: {0}'.format(pos))
                    #parts_of_speech_containers.append(pos)
                    #parts_of_speech.append(pos.string) # Adjective, Noun
                    gender_forms_elems = h.findNextSiblings('i')
                    # print('gender_forms_elems: {0}'.format(gender_forms_elems))
                    # w = Word(h.string)
                    w.partOfSpeech[pos.string] = {}
                    for gf in gender_forms_elems:
                        gender_form_type = gf.string
                        gender_form_text = gf.findNextSibling('b').find('a').string
                        # print('gftype: {0}\ngftext: {1}'.format(gender_form_type, gender_form_text))
                        w.partOfSpeech[pos.string][gender_form_type] = gender_form_text
                    # words.append(w)

                filepath = '../../projects/wiktionary-downloads/{0}.json'.format(w.text)
                # frozen = jsonpickle.encode(w, make_refs=False)
                # print(frozen)
                # for k in w.partOfSpeech:
                #     print('POS: {0}'.format(k))
                #     for v in w.partOfSpeech[k]:
                #         print('Gender Form Type: {0}'.format(v))
                #         print('Gender Form Text: {0}'.format(w.partOfSpeech[k][v]))
                # print(frozen)
                # print(w.toJSON())
                save_file(filepath, w.toJSON())



                # for w in words:
                    # filepath = '../../projects/wiktionary-downloads/{0}.json'.format(w.text)
                    # save_file(filepath, w.toJSON())
                    # print(w.text) # absurdo
                    # for k in w.partOfSpeech:
                    #     print(k) # Adjective
                    #     for v in w.partOfSpeech[k]:
                    #         print(v) # feminine singular
                    #         print(w.partOfSpeech[k][v]) # absurda
            except Exception as e:
                print(e)
                print('Could not parse {0}'.format(file))

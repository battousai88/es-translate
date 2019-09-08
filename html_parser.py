from html.parser import HTMLParser
from bs4 import BeautifulSoup
import json

# Translation html tag names
QUICK_DEFINITION_WRAPPER_CLASS = 'quickdefWrapper--HELyO'
DEFINITION_DIV_CONTAINER_CLASS = 'quickdefsWrapperDesktop--25FVk'
DICTIONARY_RESULTS_DIV_ID = 'dictionary-results-en'
HEADWORD_DIV_ID = 'headword-en'
ANCHOR_CLASS = 'a--1btSh'
DICTIONARY_RESULTS_DIV_CLASS = 'dictionary-results-en'
DICTIONARY_RESULT_ENTRY_TITLE_SPAN_CLASS = 'entryTitle--WGK1Y'
PART_OF_SPEECH_CONTAINER_DIV_CLASS = 'posContainer--2xs-U'
PART_OF_SPEECH_ANCHOR_CLASS = 'href--2RDqa'
POS_TYPE_SPAN = 'noHref--1cchI'
POS_CONTEXT_TITLE_SPAN = 'context--1vspK'
POS_ORDER_TITLE_SPAN = 'order--1TgBO'
POS_INDENT_DIV_CLASS = 'indent--FyTYr'
EXAMPLE_SPANISH_TRANSLATION_EM = 'exampleDesktop--3n1hN'
POS_TRANSLATION_ANCHOR_CLASS = 'neodictTranslation--C2TP2'
NEO_DICT_ENTRY_ID = 'dictionary-neodict-en'
COLLINS_DICT_ENTRY_ID = 'dictionary-collins-en'
HARRAP_DICT_ENTRY_ID = 'dictionary-neoharrap-en'

# Conjugate html tag names
DIV_CLASS_CONJUGATION = 'conjugation'
CONJUGATE_BASICS_DIV_CLASS = 'conj-row conj-basics-row'
CONJUGATION_RESULT_TYPE_ANCHOR = 'conjugation_results'
CONJUGATION_BASIC_WORD_SPAN = 'conj-basic-word'
VERB_TABLE_HEADER_CLASS = 'vtable-header'  # verb types

class SpanishTranslation():
    def __init__(self, text, order, phrase):
        self.text = text
        self.order = order
        self.example_phrase = phrase


class EnglishContext():
    def __init__(self, text, order):
        self.text = text
        self.order = order
        self.spanish_translations = []


class PartOfSpeech():
    def __init__(self, type):
        self.type = type
        self.english_contexts = []


class Word():
    def __init__(self, text):
        self.text = text
        self.quick_translations = []
        self.parts_of_speech = []

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=False, indent=4, ensure_ascii=False)


class ConjugatedWord():
    def __init__(self, headword):
        self.headword = headword


class Conjugation():
    def __init__(self, headword):
        self.headword = headword
        self.quick_conjugations = []
        self.conjugation_results = {}

def save_file(filename, data):
    try:
        with open(filename, 'w+') as f:
            f.write(data)
    except IOError as e:
        print('Error saving file: {0}'.format(e.message))

class DictHtmlParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

    def parse_context(self, indent, part_of_speech):
        pos_order_title = indent.find('span', POS_ORDER_TITLE_SPAN).string
        context_title = indent.find('span', POS_CONTEXT_TITLE_SPAN).string
        context = EnglishContext(context_title, pos_order_title)
        return context

    def parse_translation(self, indent, context):
        pos_order_title = indent.find('span', POS_ORDER_TITLE_SPAN).string
        translation_anchor = indent.find('a', POS_TRANSLATION_ANCHOR_CLASS)

        if translation_anchor is None:
            translation = 'no direct translation'
        else:
            translation = translation_anchor.string
        sibs = indent.find('em', EXAMPLE_SPANISH_TRANSLATION_EM)
        ex_phrase_div = sibs.previous_sibling.previous_sibling.string
        example_phrase = "{0} - {1}".format(ex_phrase_div, sibs.string)
        sp_translation = SpanishTranslation(
            translation, pos_order_title, example_phrase)
        return sp_translation

    def find_verb_type_conjugations(self, conjugation_table):
        verb_type_table_elems = conjugation_table.find(
            'tr', 'vtable-head-row').findAll('span', 'vtable-title-link-text')
        verb_type_names = [n.string for n in verb_type_table_elems] # present, imperfect, etc
        conjugations = {}
        for name in verb_type_names:
            conjugations[name] = {}
        verb_tenses = conjugation_table.findAll('tr', 'vtable-body-row')
        for i,verb_tense in enumerate(verb_tenses): # yo, tu, el/ella/ustd, etc
            pronoun_elem = verb_tense.find('td', 'vtable-pronoun')
            if pronoun_elem and pronoun_elem.string:
                pronoun = pronoun_elem.string
            
            words = verb_tense.findAll('td', 'vtable-word')
            for idx, word in enumerate(words):
                text = word.find('div', 'vtable-word-text')
                if not text:
                    text = word.find('div', 'vtable-word-contents').string
                    if not text:
                        text = word.find(
                            'a', 'sd-track-click vtable-word-text')
                if text:
                    conjugations[verb_type_names[idx]][pronoun] = text.string
                else:
                    print('No vtable-word-text found for {0}'.format(word))

        return conjugations

    def parse_conjugations(self, soup):
        headword = soup.find('div', id='headword-es').string
        conjugated_word = Conjugation(headword)
        conjugation_results_wrapper = soup.find('div', 'conjugation')
        quick_conjugations_elem = soup.findAll('div', CONJUGATE_BASICS_DIV_CLASS)
        quick_conjugations = {}
        for elem in quick_conjugations_elem:
            conjugation_type = elem.find('a').string
            basic_conjugation = elem.find('span', CONJUGATION_BASIC_WORD_SPAN).string
            # conjugated_word.quick_conjugations.append(basic_conjugation)
            quick_conjugations[conjugation_type] = basic_conjugation

        verb_type_headers = conjugation_results_wrapper.findAll('div', VERB_TABLE_HEADER_CLASS)
        conjugation_results = {}
        conjugation_results["quick_conjugations"] = quick_conjugations
        for vtype_header in verb_type_headers:
            vtype_header_name = vtype_header.find('span').string
            conjugation_results[vtype_header_name] = {}
            conj_table_wrapper = vtype_header.findNextSibling('div', 'vtable-wrapper')
            if conj_table_wrapper:
                conj_table = conj_table_wrapper.find('table', 'vtable')
                results = self.find_verb_type_conjugations(conj_table)
                conjugation_results[vtype_header_name] = results
            else:
                print('No conjugation table found for {0}'.format(vtype_header_name))
        
        dump = json.dumps(conjugation_results, default=lambda o: o.__dict__, sort_keys=False, indent=4, ensure_ascii=False)
        save_file('../asalariado.json', dump)

    def parse_conjugation_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        self.parse_conjugations(soup)

    def parse_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        headword = soup.find(id=HEADWORD_DIV_ID).string
        word = Word(headword)
        quick_translations_wrapper = soup.findAll(
            'div', QUICK_DEFINITION_WRAPPER_CLASS)

        for quick_def_divs in quick_translations_wrapper:
            word.quick_translations.append(
                quick_def_divs.find('a', ANCHOR_CLASS).string)

        harrap_dict_entry = soup.find(
            'div', attrs={"id": HARRAP_DICT_ENTRY_ID})
        collins_dict_entry = soup.find(
            'div', attrs={"id": COLLINS_DICT_ENTRY_ID})
        neo_dict_entry = soup.find('div', attrs={"id": NEO_DICT_ENTRY_ID})
        neo_dict_entry_name = neo_dict_entry.find(
            'span', DICTIONARY_RESULT_ENTRY_TITLE_SPAN_CLASS)
        parts_of_speech_containers = neo_dict_entry.findAll(
            'div', PART_OF_SPEECH_CONTAINER_DIV_CLASS)

        for pos in parts_of_speech_containers:
            pos_type_element = pos.find('a', PART_OF_SPEECH_ANCHOR_CLASS)

            if not pos_type_element:
                pos_type_element = pos.find('span', POS_TYPE_SPAN)
            part_of_speech = PartOfSpeech(pos_type_element.string)
            context_def_indents = pos.find('div', POS_INDENT_DIV_CLASS)

            for cdi in context_def_indents:
                context = self.parse_context(cdi, part_of_speech)
                sp_trans_indents = cdi.find('div', POS_INDENT_DIV_CLASS)

                for sp in sp_trans_indents:
                    translation = self.parse_translation(sp, context)
                    context.spanish_translations.append(translation)
                part_of_speech.english_contexts.append(context)
            word.parts_of_speech.append(part_of_speech)

        return word

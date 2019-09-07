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
                          sort_keys=True, indent=4, ensure_ascii=False)


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

    def parse_conjugations(self, soup):
        conjugation_wrapper = soup.find('div', 'conjugation')
        conj_row_basics = soup.findAll('div', CONJUGATE_BASICS_DIV_CLASS)

        print('\n### Conjugation Types ###')
        for row in conj_row_basics:
            conjugation_type = row.find('a').string  # present particible, past particible
            print(conjugation_type)
            basic_conjugation = row.find('span', CONJUGATION_BASIC_WORD_SPAN).string
            print(basic_conjugation)

        verb_types = conjugation_wrapper.findAll('div', VERB_TABLE_HEADER_CLASS)

        print('\n### Verb Types ###')
        for vtype in verb_types:
            name = vtype.find('span').string
            print(name)

        conj_tables = conjugation_wrapper.findAll('table', 'vtable')

        print('\n### Conjugation Tables ###')
        for tb in conj_tables:
            tenses = tb.findAll('td', 'vtable-title')
            print('\n### Verb Tenses ###')
            for tense in tenses:
                print(tense.find('span').string)
            rows = tb.findAll('tr')

            print('\n### Pronouns ###')
            for row in rows:
                pronoun = row.find('td', 'vtable-pronoun')
                if pronoun and pronoun.string:
                    print('\n<<< {0} >>>'.format(pronoun.string))
                words = row.findAll('td', 'vtable-word')
                print('\n### vtable Words ###')
                for word in words:
                    text = word.find('a', 'sd-track-click vtable-word-text')
                    # text = word.find('div', 'vtable-word-text')
                    if text:
                        print(text.string)

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

import argparse
import logging
import string
from pathlib import Path

import pymystem3

from ufal import udpipe  # pylint: disable=no-name-in-module

from russian_tagsets import converters

mystem = pymystem3.Mystem()
mystem_to_ud20 = converters.converter('mystem', 'ud20')


def tag_with_mystem(sent):
    mystemed_words = mystem.analyze(sent.getText())

    root = udpipe.Word(0)
    udpipe_words = [root] # не уверен, но первое слово игнориться

    index = 1
    space_after = False
    
    for w in mystemed_words:
        form = w['text'].strip()

        # Spaces?
        if not form:
            space_after = True
        else:
            udpipe_word = udpipe.Word(index)
            udpipe_word.form = form

            # Common words
            if 'analysis' in w:
                try:
                    w = w['analysis'][0] # TODO: а если больше 1?
                except: 
                    logging.error(w) # TODO: что делать с неразобранным?
                    continue

                grammems = w['gr']
                udpipe_word.lemma = w['lex']
                udpipe_word.upostag, udpipe_word.feats = mystem_to_ud20(grammems).split()
            
            # Punctuation or...?
            else:
                udpipe_word.upostag = 'PUNCT'
                udpipe_words[-1].setSpaceAfter(space_after) 

                # TODO: Not basic punctuation or numbers 
                if form not in string.punctuation:
                    logging.warn(w)
                    
            index += 1
            udpipe_words.append(udpipe_word)
            space_after = False

    # replace with tagged words
    sent.words = udpipe.Words(udpipe_words)


class UDPiper:
    def __init__(self, path):
        """Load given model."""
        self.model = udpipe.Model.load(path)
        if not self.model:
            raise Exception("Cannot load UDPipe model from file '%s'" % path)

    def tokenize(self, text):
        """Tokenize the text and return list of ufal.udpipe.Sentence-s."""
        tokenizer = self.model.newTokenizer(self.model.TOKENIZER_RANGES)
        if not tokenizer:
            raise Exception("The model does not have a tokenizer")
        return self._read(text, tokenizer)

    def read(self, text, in_format):
        """Load text in the given format (conllu|horizontal|vertical) and return list of ufal.udpipe.Sentence-s."""
        input_format = udpipe.InputFormat.newInputFormat(in_format)
        if not input_format:
            raise Exception("Cannot create input format '%s'" % in_format)
        return self._read(text, input_format)

    def _read(self, text, input_format):
        input_format.setText(text)
        error = udpipe.ProcessingError()
        sentences = []

        sentence = udpipe.Sentence()
        while input_format.nextSentence(sentence, error):
            sentences.append(sentence)
            sentence = udpipe.Sentence()

        if error.occurred():
            raise Exception(error.message)

        return sentences

    def tag(self, sentence):
        """Tag the given ufal.udpipe.Sentence (inplace)."""
        self.model.tag(sentence, self.model.DEFAULT)

    def parse(self, sentence):
        """Parse the given ufal.udpipe.Sentence (inplace)."""
        self.model.parse(sentence, self.model.DEFAULT)

    def write(self, sentences, out_format):
        """Write given ufal.udpipe.Sentence-s in the required format (conllu|horizontal|vertical)."""

        output_format = udpipe.OutputFormat.newOutputFormat(out_format)
        output = ''
        for sentence in sentences:
            output += output_format.writeSentence(sentence)
        output += output_format.finishDocument()

        return output

    def process(self, text, text_id='example', mystem=False):
        sentences = self.tokenize(text)

        for s in sentences:
            sent_id = s.getSentId()
            s.setSentId('{}_{}'.format(text_id, sent_id))
            if mystem:
                tag_with_mystem(s)
            else:
                self.tag(s)
            self.parse(s)

        conllu = self.write(sentences, "conllu")
        return conllu

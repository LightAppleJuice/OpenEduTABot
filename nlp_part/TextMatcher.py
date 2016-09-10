#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'a.smirnov'


from settings import settings
from sklearn.neighbors import KNeighborsClassifier
from sklearn.utils.validation import NotFittedError
import re
import numpy as np
import logging


def preprocess_train_data(train_data_in):
    train_data_out = []
    for sent in train_data_in:
        sent = preprocess_sentence(sent)
        train_data_out.append(re.split("\s+", sent))
    return train_data_out


def preprocess_sentence(sent):
    sent = sent.decode('utf-8').lower().encode('utf-8')
    sent = re.sub(r"[/\\\.,\?!\":;\(\)\*#\'\d]", " ", sent)
    sent = re.sub("\-\s+", " ", sent)
    sent = re.sub("[a-z]", "", sent)
    sent = re.sub("\s+", " ", sent)
    sent = sent.strip()
    return sent


class ThemeClassifierError(Exception):
    """просто мой exception"""
    def __init__(self, value):
        self.value = value


class Word2Vec:
    def __init__(self):
        self.w2v = 0  # word2vec model
        self.dict = {}  # word2vec dictionary
        self.num_of_occur = []  # number of occurrences for words in the dictionary
        self.dim = 0  # dimensionality of words vector space
        self.num_words = 0  # the total number of words

    def load_word2vec_model(self, w2v_file):
        """
            loads word2vec model
            w2v_file -- file with word2vec model
            w2v_file: format: first 8 bytes = 2 uints for the number of words and dimensionality of w2v space
                         the rest of the file -- w2v matrix [dim, num_words]
        """
        self.w2v = np.load(w2v_file)
        self.num_words = np.shape(self.w2v)[1]-1
        self.dim = np.shape(self.w2v)[0]

    def covert_from_words_to_vecs(self, word_data):
        """
            convert words from word_data to vectors representations
            :param word_data: lists of words
            :return: np array of vector representations ((dim w2v) x (number of words))
        """

        num_words = len(word_data)
        # in the last column of w2v there is a vector for unknown words
        wordvec_data = np.zeros((self.dim, num_words)) + np.reshape(self.w2v[:, -1], (self.dim, 1))
        for word_num in range(num_words):
            try:
                cur_word_position = self.dict[word_data[word_num]]
                wordvec_data[:, word_num] = self.w2v[:, cur_word_position]
            except KeyError:
                curWord = word_data[word_num]
                logging.debug("Can't find the word " + curWord + " in dictionary. ")
        return wordvec_data

    def load_word2vec_dictionary(self, dict_file):
            """
                loads word2vec dictionary
                dict_file -- file with word2vec dictionary
                dict_file: format: word number_of_occurrences
            """
            with open(dict_file) as dictionary:
                line_num = 0
                if self.num_of_occur:
                    self.num_of_occur = []
                    logging.info("Nonempty vocabulary in Word2Vec Class. That's weird.")
                for line in dictionary:
                    line = re.sub('\s+$', '', line)
                    cur_word, cur_num_of_occur = re.split('\s+', line)
                    self.dict[cur_word] = line_num
                    self.num_of_occur.append(float(cur_num_of_occur))
                    line_num += 1


class SentenceClassifier:
    """ to train and use sentence classifier
        Parameteres:
        nn -- number of neighbours to use in knn classifier
        weight -- specify how to weights votes form nearest nn neighbours
    """

    def __init__(self, neighbours_num=1, weight='uniform'):
        self.nn = neighbours_num
        self.weight = weight
        self.distance = 'cosine'
        self.allowed_weights = ['uniform', 'squared-inverse']
        if weight not in self.allowed_weights:
            logging.warning("Unknown type of weighting for KNN Classifier. Using 'uniform'...")
            self.weight = 'uniform'
        elif weight == "squared-inverse":
            self.weight = lambda x: np.power(np.asarray(x)+1e-5, -2)
        self.KNNClassifier = KNeighborsClassifier(n_neighbors=self.nn, metric=self.distance, weights=self.weight, algorithm='brute')

    def fit_sentence_classifier(self, sentvecs, sent_labels):
        """ 'trains' KNN classifier
            sentvecs -- train data, array with sentences vectors
            sent_labels -- reference labels
        """
        self.KNNClassifier.fit(sentvecs, sent_labels)

    def predict_class_with_KNN(self, sentvecs_ts, reference_labels=None):
        """
            sentvecs_ts -- test data, array with sentences vectors
            reference_labels -- reference labels. to check the quality of classification. optional parameter.
                                in case when reference labels are not provided return accuracy = -1
            return predicted_labels -- predicted labels
            return acc -- average accuracy of classification (or -1 if reference labels are not provided)
        """
        try:
            predicted_labels = self.KNNClassifier.predict(sentvecs_ts)
            probability_matrix = self.KNNClassifier.predict_proba(sentvecs_ts)
            conf_vector = np.sort(probability_matrix, 1)[:, -1]
        except NotFittedError:
            logging.error("Oops! The KNN-classifier hasn't been initialized.")
            raise ThemeClassifierError("Error's occurred. The KNN-classifier hasn't been initialized.")
        if reference_labels:
            correct_classification = np.where(predicted_labels == reference_labels, 1, 0)
            acc = np.mean(correct_classification)
        else:
            acc = -1
        return predicted_labels, conf_vector, acc


class TextClassifier:
    def __init__(self):
        self.config = settings()

        self.logger = logging.getLogger('BotLogger.NLP')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(self.config.log)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        self.logger.info('Loading w2v models')
        self.w2v_model = Word2Vec()
        self.w2v_model.load_word2vec_dictionary(self.config.w2vec_dict)
        self.w2v_model.load_word2vec_model(self.config.w2vec_model)

        self.sentenceClassifier = SentenceClassifier(neighbours_num=1, weight='squared-inverse')  # can predict sentence class

        self.logger.info('Converting tr data to vecs')

        self.tr_data = ["привет", "пока"]
        self.labels_tr = ["1", "2"]
        # self.sentvecs_tr = np.array([self.text_to_vec(sent) for sent in self.tr_data])
        self.sentvecs_tr = [self.text_to_vec(sent) for sent in self.tr_data]

        self.logger.info('Training classifier')
        self.sentenceClassifier.fit_sentence_classifier(self.sentvecs_tr, self.labels_tr)  # "train" nn-classifier
        self.logger.info('Initialized successfully')

    def preprocess_sentence(self, sent):
        sent = sent.decode('utf-8').lower().encode('utf-8')
        sent = re.sub(r"[/\\\.,\?!\":;\(\)\*#\'\d]", " ", sent)
        sent = re.sub("\-\s+", " ", sent)
        sent = re.sub("\s+", " ", sent)
        sent = sent.strip()
        return sent

    def text_to_vec(self, text):
        """
        convert sentence to vector
        :param text: sentence
        :return: vector shape = (1, dim)
        """
        text_proc = self.preprocess_sentence(text)
        if not text_proc:  # :))))
            text_proc = "клмншмидт"
        word_vecs = self.w2v_model.covert_from_words_to_vecs(text_proc.split())
        sent_vec = np.average(word_vecs, axis=1)
        return sent_vec.T

    def give_answer(self, question):
        que_vec = self.text_to_vec(question)
        answer, confidence, acc = self.sentenceClassifier.predict_class_with_KNN([que_vec], )
        return answer

    def add_to_train_data(self, question, answer):
        self.logger.info('Updating intrinsic data representations')
        que_vec = self.text_to_vec(question)
        self.tr_data.append(question)
        self.labels_tr.append(answer)
        self.sentvecs_tr.append(que_vec)
        self.logger.info('Retraining classifier')
        self.sentenceClassifier.fit_sentence_classifier(self.sentvecs_tr, self.labels_tr)  # "train" nn-classifier

    def remove_from_train_data(self, question):
        elmnts_to_del = []
        for i in range(len(self.labels_tr)):
            if self.tr_data[i] == question:
                elmnts_to_del.append(i)
        elmnts_to_del.reverse()
        for i in elmnts_to_del:
            del self.tr_data[i]
            del self.sentvecs_tr[i]
            del self.labels_tr[i]
        self.sentenceClassifier.fit_sentence_classifier(self.sentvecs_tr, self.labels_tr)  # "train" nn-classifier


if __name__ == "__main__":
    text_classifier = TextClassifier()
    print text_classifier.give_answer("привет")[0].decode('utf-8')
    print text_classifier.give_answer("пока")[0].decode('utf-8')
    print text_classifier.give_answer("здравствуй")[0].decode('utf-8')
    print text_classifier.give_answer("до свидания")[0].decode('utf-8')
    print text_classifier.give_answer("чао")[0].decode('utf-8')
    print "Add 3"
    text_classifier.add_to_train_data("здравствуй", "3")
    print text_classifier.give_answer("здравствуй")[0].decode('utf-8')
    print "Remove 1"
    text_classifier.remove_from_train_data("привет")
    print [sent.decode('utf-8') for sent in text_classifier.tr_data]
    print text_classifier.give_answer("привет")[0].decode('utf-8')
    print text_classifier.give_answer("пока")[0].decode('utf-8')
    print text_classifier.give_answer("здравствуй")[0].decode('utf-8')




import numpy as np
from matplotlib import pyplot as plt
from scipy.io import loadmat

from sklearn.mixture import GMM
import pyhsmm

from util import read_align, get_segments

HOGS_PATH = "hogs.mat"

def train_word_init_probs(data, vocab):
    word_init_counts = {word: 0 for word in vocab}

    for chain in data:
        if chain['state_seq'][0] in word_init_counts:
            word_init_counts[chain['state_seq'][0]] = 1
        else:
            word_init_counts[chain['state_seq'][0]] += 1

    return {word: float(count) / len(vocab) for word, count in word_init_counts}

def train_word_trans_probs(data, vocab):
    pass

def train_word_durations(data, vocab):
    pass

def gather_gmm_data(data, vocab):
    """ Returns a dictionary mapping words to their observation data matrices (of shape (num_segments, hogs_dim)) """
    # Collect segments for each word in training data.
    segments = {}
    for chain in data:
        for idx, word in enumerate(chain['state_seq']):
            if word in segments.keys():
                segments[word].add(chain['obs'][idx])
            else:
                segments[word] = {chain['obs'][idx]}

    # Put segments for each word together, so that each word has a single data matrix.
    train_data_gmm = {}
    for word in vocab:
        train_data_gmm[word] = np.vstack((np.asarray(seg) for seg in segments[word])).T

    return train_data_gmm

def train_word_gmms(train_data_gmm):
    pass

def train_hsmm(data):
    """ Trains a HSMM from the given complete data.

        data: Set of observation sequences and state sequences.
            {
                {
                    state_seq: [word_0, word_1, word_2]
                    obs: [[frame_0, frame_1], [frame_2, frame_3, frame_4], [frame_5]],
                },
                {
                    state_seq: [word_0, word_1, word_2]
                    obs: [[frame_0, frame_1], [frame_2, frame_3, frame_4], [frame_5]],
                }
                ...
            }
    """

    vocab = {} # Set of all words in the vocabulary.

    word_init_probs = train_word_init_probs(data, vocab) # Compute initial word probabilities.
    
    word_trans_probs = train_word_trans_probs(data, vocab) # Compute word transition probabilities.
    word_dur_params = train_word_durations(data, vocab) # Learn parameters of word duration distributions.

    # Gather data for training each GMM.
    train_data_gmm = gather_gmm_data(data, vocab)

    # Train word GMMs.
    word_gmms = train_word_gmms(train_data_gmm)

    return word_init_probs, word_trans_probs, word_dur_params, word_gmms



"""Defines project-wide fixtures for unit testing"""

import os
import struct
import numpy as np
import pytest

from shennong.audio import AudioData
from shennong.alignment import AlignmentCollection
from shennong.features import Features, FeaturesCollection
from shennong.features.mfcc import MfccProcessor


@pytest.fixture(scope='session')
def alignment_file():
    return os.path.join(os.path.dirname(__file__), 'data', 'alignment.txt')


@pytest.fixture(scope='session')
def alignments(alignment_file):
    return AlignmentCollection.load(alignment_file)


@pytest.fixture(scope='session')
def wav_file():
    return os.path.join(os.path.dirname(__file__), 'data', 'test.wav')


@pytest.fixture(scope='session')
def audio(wav_file):
    return AudioData.load(wav_file)


@pytest.fixture(scope='session')
def mfcc(audio):
    return MfccProcessor().process(audio)


@pytest.fixture(scope='session')
def wav_file_8k():
    return os.path.join(os.path.dirname(__file__), 'data', 'test.8k.wav')


@pytest.fixture(scope='session')
def audio_8k(wav_file_8k):
    return AudioData.load(wav_file_8k)


@pytest.fixture(scope='session')
def bottleneck_original():
    fea_file = os.path.join(
        os.path.dirname(__file__), 'data', 'test.bottleneck.fea')

    # this is BottleneckFeaturesExtraction.utils.read_htk(file)
    try:
        fh = open(fea_file, 'rb')
    except TypeError:
        fh = fea_file
    try:
        nSamples, sampPeriod, sampSize, parmKind = struct.unpack(
            ">IIHH", fh.read(12))
        m = np.frombuffer(fh.read(nSamples * sampSize), 'i1')
        m = m.view('>f').reshape(nSamples, int(sampSize/4))
    finally:
        if fh is not fea_file:
            fh.close()
    return m


@pytest.fixture(scope='session')
def features_collection():
    # build a collection of 3 random features of same ndims, various
    # nframes
    dim = 10
    feats = FeaturesCollection()
    for n in range(3):
        nframes = np.random.randint(5, 15)
        feats[str(n)] = Features(
            np.random.random((nframes, dim)),
            np.arange(0, nframes))
    return feats

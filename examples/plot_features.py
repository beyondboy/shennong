#!/usr/bin/env python
"""Extract features from a wav file and plot them"""

import argparse
import numpy as np
import matplotlib.pyplot as plt

from shennong.audio import Audio
from shennong.features.processor.filterbank import FilterbankProcessor
from shennong.features.processor.mfcc import MfccProcessor
from shennong.features.processor.plp import PlpProcessor
from shennong.features.processor.rastaplp import RastaPlpProcessor
from shennong.features.processor.bottleneck import BottleneckProcessor
from shennong.features.processor.spectrogram import SpectrogramProcessor


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('wav', help='wav file to compute features on')

    # load the wav file
    wav_file = parser.parse_args().wav
    audio = Audio.load(wav_file)

    # initialize features processors
    processors = {
        'spectrogram': SpectrogramProcessor(sample_rate=audio.sample_rate),
        'filterbank': FilterbankProcessor(sample_rate=audio.sample_rate),
        'mfcc': MfccProcessor(sample_rate=audio.sample_rate),
        'plp': PlpProcessor(sample_rate=audio.sample_rate),
        'rastaplp': RastaPlpProcessor(sample_rate=audio.sample_rate),
        'bottleneck': BottleneckProcessor(weights='BabelMulti')}

    # compute the features for all processors
    features = {k: v.process(audio) for k, v in processors.items()}

    # plot the audio signal and the resulting features
    fig, axes = plt.subplots(nrows=len(processors)+1)
    time = np.arange(0.0, audio.nsamples) / audio.sample_rate
    axes[0].plot(time, audio.data)
    axes[0].set_title('audio')
    axes[0].set_xlim(0.0, audio.duration)

    for n, (k, v) in enumerate(features.items(), start=1):
        axes[n].imshow(v.data.T, aspect='auto')
        axes[n].set_title(k)

    fig.suptitle(wav_file)
    plt.show()


if __name__ == '__main__':
    main()

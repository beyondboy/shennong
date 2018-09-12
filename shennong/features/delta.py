"""Compute time derivatives on existing features

Uses the Kaldi implementation (see [kaldi-delta]_)

    *Features* ---> DeltaProcessor ---> *Features*

Examples
--------

>>> from shennong.audio import AudioData
>>> from shennong.features.mfcc import MfccProcessor
>>> from shennong.features.delta import DeltaProcessor
>>> audio = AudioData.load('./test/data/test.wav')
>>> mfcc = MfccProcessor().process(audio)

Initialize the delta processor to compute first and second order time
derivatives:

>>> processor = DeltaProcessor(order=2)

Compute the deltas from MFCC features. The resulting matrice is the
concatenation of the original features, the first and the second
order:

>>> delta = processor.process(mfcc)
>>> nmfcc = mfcc.shape[1]
>>> delta.shape[1] == nmfcc * 3
True
>>> original = delta.data[:, :nmfcc]
>>> np.array_equal(original, mfcc.data)
True
>>> first_order = delta.data[nmfcc:2*nmfcc]
>>> second_order = delta.data[2*nmfcc:]

References
----------

.. [kaldi-delta] http://kaldi-asr.org/doc/feature-functions_8h.html

"""

import kaldi.feat.functions
import kaldi.matrix
import numpy as np

from shennong.features.processor import FeaturesProcessor
from shennong.features.features import Features


class DeltaProcessor(FeaturesProcessor):
    def __init__(self, order=2, window=2):
        self._options = kaldi.feat.functions.DeltaFeaturesOptions()
        self.order = order
        self.window = window

    @property
    def order(self):
        """Order of delta computation"""
        return self._options.order

    @order.setter
    def order(self, value):
        self._options.order = value

    @property
    def window(self):
        """Parameter controlling window for delta computation

        The actual window size for each delta order is 1 + 2 *
        `window`. The behavior at the edges is to replicate the first
        or last frame.

        """
        return self._options.window

    @window.setter
    def window(self, value):
        if not 0 < value < 1000:
            raise ValueError(
                'window must be in [1, 999], it is {}'.format(value))
        self._options.window = value

    def parameters(self):
        return {
            'order': self.order,
            'window': self.window}

    def labels(self):
        raise ValueError(
            'labels are created from the input features given to `process()`')

    def times(self, nframes):
        raise ValueError(
            'times are created from the input features given to `process()`')

    def process(self, features):
        """Compute deltas on `features` with the specified options

        Parameters
        ----------
        features : Features, shape = [nframes, nlabels]
            The input features on which to compute the deltas

        Returns
        -------
        deltas : Features, shape = [nframes, nlabels * (`order`+1)]
            The computed deltas with as much orders as specified. The
            output features are the concatenation of the input
            `features` and it's time derivative at each orders.

        """
        data = kaldi.matrix.SubMatrix(
            kaldi.feat.functions.compute_deltas(
                self._options, kaldi.matrix.SubMatrix(features.data))).numpy()

        labels = features.labels.tolist()
        for o in range(self.order):
            labels += [l + '_d{}'.format(o+1) for l in features.labels]
        labels = np.asarray(labels)

        return Features(data, labels, features.times, self.parameters())

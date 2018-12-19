"""Test of the module shennong.audio"""

import numpy as np
import pytest

from shennong.audio import AudioData


def test_load(audio):
    assert audio.sample_rate == 16000
    assert audio.nchannels == 1
    assert audio.duration == pytest.approx(1.437, rel=1e-3)
    assert audio.data.shape == (23001,)
    assert audio.nsamples == 23001
    assert audio.dtype == np.int16


def test_load_notwav():
    with pytest.raises(ValueError):
        AudioData.load(__file__)


def test_equal(audio):
    assert audio == audio

    audio2 = AudioData(audio.data, audio.sample_rate)
    assert audio == audio2

    audio2 = AudioData(audio.data, audio.sample_rate + 1)
    assert audio != audio2

    audio2 = AudioData(audio.data * 2, audio.sample_rate)
    assert audio.duration == audio2.duration
    assert audio.sample_rate == audio2.sample_rate
    assert audio != audio2


def test_channels_mono(audio):
    assert audio.nchannels == 1
    assert audio.channel(0) == audio
    with pytest.raises(ValueError):
        audio.channel(1)


def test_channels_stereo():
    data = np.random.random((1000, 2))
    audio2 = AudioData(data, sample_rate=16000)
    assert audio2.nchannels == 2

    audio1 = audio2.channel(0)
    assert audio1.nchannels == 1
    assert all(np.equal(audio1.data, audio2.data[:, 0]))
    assert not all(np.equal(audio1.data, audio2.data[:, 1]))
    assert audio1.duration == audio2.duration

    audio1 = audio2.channel(1)
    assert audio1.nchannels == 1
    assert all(np.equal(audio1.data, audio2.data[:, 1]))
    assert not all(np.equal(audio1.data, audio2.data[:, 0]))

    with pytest.raises(ValueError):
        audio2.channel(2)


@pytest.mark.parametrize('fs', [4000, 8000, 16000, 32000])
def test_resample(audio, fs):
    audio2 = audio.resample(fs)

    assert audio2.nchannels == audio.nchannels
    assert audio2.sample_rate == fs
    assert audio2.nsamples == int(
        audio.nsamples * fs / audio.sample_rate)

"""Test of the module shennong.features.mfcc"""

import tempfile
import numpy as np
import pytest

from kaldi.util.table import SequentialWaveReader
from shennong.audio import AudioData
from shennong.features.mfcc import MfccProcessor


def test_params():
    assert len(MfccProcessor().parameters()) == 21


@pytest.mark.parametrize('num_ceps', [0, 1, 5, 13, 23, 25])
def test_num_ceps(audio, num_ceps):
    proc = MfccProcessor(num_ceps=num_ceps)
    if 0 < proc.num_ceps <= proc.num_bins:
        feat = proc.process(audio)
        assert feat.shape == (142, num_ceps)

        proc.use_energy = False
        feat = proc.process(audio)
        assert feat.shape == (142, num_ceps)
    else:
        with pytest.raises(RuntimeError):
            proc.process(audio)


@pytest.mark.parametrize('num_bins', [0, 1, 5, 23])
def test_num_bins(audio, num_bins):
    proc = MfccProcessor(num_bins=num_bins)
    proc.num_ceps = min(proc.num_ceps, num_bins)
    if 3 <= proc.num_bins:
        feat = proc.process(audio)
        assert feat.shape == (142, proc.num_ceps)

        proc.use_energy = False
        feat = proc.process(audio)
        assert feat.shape == (142, proc.num_ceps)
    else:
        with pytest.raises(RuntimeError):
            proc.process(audio)


def test_htk_compat(audio):
    p1 = MfccProcessor(use_energy=True, htk_compat=False).process(audio)
    p2 = MfccProcessor(use_energy=True, htk_compat=True).process(audio)
    assert p1.data[:, 0] == pytest.approx(p2.data[:, -1], rel=1e-2)

    p1 = MfccProcessor(use_energy=False, htk_compat=False).process(audio)
    p2 = MfccProcessor(use_energy=False, htk_compat=True).process(audio)
    assert p1.data[:, 0] * 2**0.5 == pytest.approx(p2.data[:, -1], rel=1e-2)


def test_output(audio):
    assert MfccProcessor(frame_shift=0.01).process(audio).shape == (142, 13)
    assert MfccProcessor(frame_shift=0.02).process(audio).shape == (71, 13)
    assert MfccProcessor(
        frame_shift=0.02, frame_length=0.05).process(audio).shape == (70, 13)

    # sample rate mismatch
    with pytest.raises(ValueError):
        MfccProcessor(sample_rate=8000).process(audio)

    # only mono signals are accepted
    with pytest.raises(ValueError):
        data = np.random.random((1000, 2))
        stereo = AudioData(data, sample_rate=16000)
        MfccProcessor(sample_rate=stereo.sample_rate).process(stereo)


def test_kaldi_audio(wav_file, audio):
    # make sure we have results when loading a wav file with
    # shennong.AudioData and with the Kaldi code.
    with tempfile.NamedTemporaryFile('w+') as tfile:
        tfile.write('test {}\n'.format(wav_file))
        tfile.seek(0)
        with SequentialWaveReader('scp,t:' + tfile.name) as reader:
            for key, wave in reader:
                audio_kaldi = AudioData(
                    wave.data().numpy().reshape(audio.data.shape),
                    audio.sample_rate)

    assert audio.duration == audio_kaldi.duration
    assert audio.dtype == np.int16
    assert audio_kaldi.dtype == np.float32

    mfcc = MfccProcessor().process(audio)
    mfcc_kaldi = MfccProcessor().process(audio_kaldi)
    assert mfcc.shape == mfcc_kaldi.shape
    assert np.array_equal(mfcc.times, mfcc_kaldi.times)
    assert mfcc.properties == mfcc_kaldi.properties
    assert pytest.approx(mfcc.data, mfcc_kaldi.data)

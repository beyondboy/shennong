"""Test of the module shennong.features.features"""

import numpy as np
import pytest

from shennong.features import Features, FeaturesCollection


def test_init_bad():
    with pytest.raises(ValueError) as err:
        Features(0, 0, properties=0)
    assert 'data must be a numpy array' in str(err)

    with pytest.raises(ValueError) as err:
        Features(np.asarray([0]), 0, properties=0)
    assert 'times must be a numpy array' in str(err)

    with pytest.raises(ValueError) as err:
        Features(np.asarray([0]), np.asarray([0]), properties=0)
    assert 'properties must be a dictionnary' in str(err)

    with pytest.raises(ValueError) as err:
        Features(np.asarray([0]), np.asarray([0]), properties={0: 0})
    assert 'data dimension must be 2' in str(err)

    with pytest.raises(ValueError) as err:
        Features(np.asarray([[0], [0]]), np.asarray([[0], [0]]))
    assert 'times dimension must be 1' in str(err)


def test_tofrom_dict(mfcc):
    a = mfcc._to_dict()
    b = Features._from_dict(a)
    assert b == mfcc

    with pytest.raises(ValueError) as err:
        Features._from_dict({'data': a['data'], 'properties': a['properties']})
    assert 'missing keys: times' in str(err)


def test_equal(mfcc):
    # same object
    assert mfcc == mfcc
    assert mfcc.is_close(mfcc)
    # same data
    mfcc2 = mfcc.copy()
    assert mfcc == mfcc2
    assert mfcc.is_close(mfcc2)
    # not same shape
    mfcc2 = mfcc.concatenate(mfcc)
    assert not mfcc == mfcc2
    assert not mfcc.is_close(mfcc2)
    # not same dtype
    mfcc64 = mfcc.copy(dtype=np.float64)
    assert not mfcc == mfcc64
    assert mfcc.is_close(mfcc64)
    # not same properties
    mfcc2 = Features(mfcc.data, mfcc.times, properties={'foo': 0})
    assert not mfcc == mfcc2
    assert not mfcc.is_close(mfcc2)
    # not same times
    mfcc2 = Features(mfcc.data, mfcc.times + 1, properties=mfcc.properties)
    assert not mfcc == mfcc2
    assert not mfcc.is_close(mfcc2)
    # not same data
    mfcc2 = Features(mfcc.data + 1, mfcc.times, properties=mfcc.properties)
    assert not mfcc == mfcc2
    assert not mfcc.is_close(mfcc2)
    # not same data but close
    mfcc2 = Features(mfcc.data + 1, mfcc.times, properties=mfcc.properties)
    assert not mfcc == mfcc2
    assert mfcc.is_close(mfcc2, atol=1)
    # not same times but close
    mfcc2 = Features(mfcc.data, mfcc.times + 1, properties=mfcc.properties)
    assert not mfcc == mfcc2
    assert mfcc.is_close(mfcc2, atol=1)


def test_copy(mfcc):
    # by copy we allocate new arrays
    mfcc2 = mfcc.copy()
    assert mfcc2 == mfcc
    assert mfcc2 is not mfcc
    assert mfcc2.data is not mfcc.data
    assert mfcc2.times is not mfcc.times
    assert mfcc2.properties is not mfcc.properties

    # by explicit construction the arrays are shared
    mfcc2 = Features(
        mfcc.data, mfcc.times, properties=mfcc.properties, validate=False)
    assert mfcc2 == mfcc
    assert mfcc2 is not mfcc
    assert mfcc2.data is mfcc.data
    assert mfcc2.times is mfcc.times
    assert mfcc2.properties is mfcc.properties


def test_concatenate(mfcc):
    mfcc2 = mfcc.concatenate(mfcc)
    assert mfcc2.nframes == mfcc.nframes
    assert mfcc2.ndims == mfcc.ndims * 2
    assert mfcc2.properties == mfcc.properties

    mfcc2 = Features(mfcc.data, mfcc.times + 1)
    with pytest.raises(ValueError) as err:
        mfcc.concatenate(mfcc2)
    assert 'times are not equal' in str(err)


def test_collection(mfcc):
    assert FeaturesCollection._value_type is Features
    assert FeaturesCollection().is_valid()
    assert FeaturesCollection(mfcc=mfcc).is_valid()
    assert not FeaturesCollection(mfcc=Features(
        np.asarray([0]), 0, validate=False)).is_valid()


def test_collection_isclose():
    f1 = Features(np.random.random((10, 2)), np.random.random((10,)))
    f2 = Features(np.random.random((10, 2)), np.random.random((10,)))

    fc1 = FeaturesCollection(f1=f1, f2=f2)
    fc2 = FeaturesCollection(f1=f1, f2=Features(f2.data+1, f2.times))
    fc3 = FeaturesCollection(f1=f1, f3=f2)

    assert fc1.is_close(fc1)
    assert not fc1.is_close(fc2)
    assert fc1.is_close(fc2, atol=1)
    assert not fc1.is_close(fc3)


def test_partition():
    f1 = Features(np.random.random((10, 2)), np.random.random((10,)))
    f2 = Features(np.random.random((15, 2)), np.random.random((15,)))
    f3 = Features(np.random.random((5, 2)), np.random.random((5,)))
    fc = FeaturesCollection(f1=f1, f2=f2, f3=f3)

    with pytest.raises(ValueError) as err:
        fp = fc.partition({'f1': 'p1', 'f2': 'p1'})
    assert 'following items are not defined in the index: f3' in str(err)

    fp = fc.partition({'f1': 'p1', 'f2': 'p1', 'f3': 'p2'})
    assert sorted(fp.keys()) == ['p1', 'p2']
    assert sorted(fp['p1'].keys()) == ['f1', 'f2']
    assert sorted(fp['p2'].keys()) == ['f3']

    assert fc.is_valid()
    for fc in fp.values():
        assert fc.is_valid()
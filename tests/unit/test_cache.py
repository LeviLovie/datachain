import pytest

from datachain.cache import DataChainCache
from datachain.lib.file import File


@pytest.fixture
def cache(tmp_path):
    return DataChainCache(str(tmp_path / "cache"), str(tmp_path / "tmp"))


def test_simple(cache):
    uid = File(source="s3://foo", path="data/bar", etag="xyz", size=3)
    data = b"foo"
    assert not cache.contains(uid)

    cache.store_data(uid, data)
    assert cache.contains(uid)
    with open(cache.get_path(uid), mode="rb") as f:
        assert f.read() == data

    cache.clear()
    assert not cache.contains(uid)


def test_get_total_size(cache):
    file_info = [
        ("file1", b"foo"),
        ("file2", b"bar"),
        ("file3", b"some file data"),
        ("file4", b"more file data " * 1024),
    ]
    expected_total = sum(len(d) for _, d in file_info)
    for name, data in file_info:
        uid = File(source="s3://foo", path=f"data/{name}", etag="xyz", size=3)
        cache.store_data(uid, data)
    total = cache.get_total_size()
    assert total == expected_total

    cache.clear()
    empty_total = cache.get_total_size()
    assert empty_total == 0


def test_remove(cache):
    uid = File(source="s3://bkt42", path="dir1/dir2/file84", etag="abc", size=3)
    cache.store_data(uid, b"some random string 679")

    assert cache.contains(uid)
    cache.remove(uid)
    assert not cache.contains(uid)

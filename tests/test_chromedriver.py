# -*- coding: utf-8 -*-

import os

import pytest

import webdrivers.chromedriver
from tests.conftest import PLATFORM


@pytest.fixture(scope='function')
def chromedriver():
    driver = webdrivers.chromedriver.Chromedriver()
    yield driver
    driver.remove()


@pytest.fixture(scope='function')
def offline(chromedriver):
    chromedriver.is_site_available = lambda: False
    yield


def test_finds_latest_version(chromedriver):
    old_version = '2.30'
    new_version = '80.00'
    latest_version = chromedriver.latest_version()

    assert latest_version > old_version
    assert latest_version < new_version


def test_download_latest_by_default(chromedriver):
    chromedriver.download()
    cur_ver = chromedriver.current_version()
    latest_ver = chromedriver.latest_version()
    assert cur_ver == latest_ver


def test_download_specified_version_by_float(chromedriver):
    chromedriver.version = 2.29
    chromedriver.download()
    assert '2.29' in chromedriver.current_version().vstring


def test_download_specified_version_by_string(chromedriver):
    chromedriver.version = '73.0.3683.68'
    chromedriver.download()
    assert chromedriver.current_version() == '73.0.3683.68'


def test_update(chromedriver, local_install_dir):
    executable = chromedriver.update()
    assert os.path.dirname(executable) == local_install_dir


def test_remove(chromedriver):
    chromedriver.remove()
    assert chromedriver.current_version() is None


@pytest.mark.usefixtures('offline')
class TestOffline(object):

    def test_latest_version_raises_when_offline(self, chromedriver):
        with pytest.raises(Exception, match='Can not reach site'):
            chromedriver.latest_version()

    def test_download_raises_when_offline(self, chromedriver):
        with pytest.raises(Exception, match='Can not reach site'):
            chromedriver.download()


@pytest.mark.skipif(PLATFORM not in {'linux', 'darwin'},
                    reason='Test group only run on Linux and Mac')
class TestUnix(object):

    def test_update_returns_full_path(self, chromedriver, local_install_dir):
        executable = chromedriver.update()
        assert executable == os.path.join(local_install_dir, "chromedriver")


@pytest.mark.skipif(PLATFORM != 'windows',
                    reason='Test group only run on Windows')
class TestWindows(object):

    def test_update_returns_full_path(self, chromedriver, local_install_dir):
        executable = chromedriver.update()
        assert executable == os.path.join(local_install_dir, "chromedriver.exe")




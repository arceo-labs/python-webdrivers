# -*- coding: utf-8 -*-
import platform
import shutil
import tempfile

import pytest

PLATFORM = platform.system().lower()


@pytest.fixture(scope='function', autouse=True)
def local_install_dir(monkeypatch):
    install_dir = tempfile.mkdtemp()
    monkeypatch.setenv('WEBDRIVERS_INSTALL_DIR', install_dir)
    yield install_dir
    shutil.rmtree(install_dir)

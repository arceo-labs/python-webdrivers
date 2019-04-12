# -*- coding: utf-8 -*-
import errno
import os
from contextlib import contextmanager
import subprocess
from distutils.version import LooseVersion


@contextmanager
def chdir(path):
    old_dir = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(old_dir)


def rmf(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


def sh(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if result.returncode > 0:
        raise Exception(f"Failed to run shell command!\n"
                        f"  command:   {cmd}\n"
                        f"  exit code: {result.returncode}\n"
                        f"  STDOUT:    {result.stdout}\n"
                        f"  STDERR:    {result.stderr}")
    return result.stdout.decode('utf-8')


class HashableVersion(LooseVersion):
    def __init__(self, version=None):
        if version:
            super(HashableVersion, self).__init__(str(version))

    def __hash__(self):
        return hash('.'.join(str(i) for i in self.version))

    def __repr__(self):
        return "HashableVersion ('%s')" % str(self)

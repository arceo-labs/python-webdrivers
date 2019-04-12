# -*- coding: utf-8 -*-
import logging
import os
import platform
import stat
import urllib.request
import zipfile

from webdrivers.util import chdir, rmf, sh, HashableVersion

log = logging.getLogger()


class CommonDriver(object):
    version = None

    def base_url(self):
        raise NotImplementedError("WebDriver extension must implement base_url method")

    def file_name(self):
        raise NotImplementedError("WebDriver extension must implement file_name method")

    def downloads(self):
        raise NotImplementedError("WebDriver extension must implement downloads method")

    def current_version(self):
        raise NotImplementedError(
            "WebDriver extension must implement current_version method"
        )

    def update(self):
        if not self.is_site_available():
            return None

        # Newer not specified or latest not found, so use existing
        if not self.desired_version() and os.path.exists(self.binary()):
            return self.binary()

        # Can't find desired and no existing binary
        if not self.desired_version():
            raise Exception(
                f"Unable to find the latest version of {self.file_name()}; "
                f"try downloading manually from {self.base_url()} and place "
                f"in {self.install_dir()}"
            )

        if self.is_correct_binary():
            log.debug("Expected webdriver version found")
            return self.binary()

        self.remove()  # Remove outdated exe
        return self.download()  # Fetch latest

    def desired_version(self):
        if isinstance(self.version, HashableVersion):
            return self.version
        elif not self.version:
            return self.latest_version()
        else:
            return HashableVersion(self.version)

    def latest_version(self):
        if not self.is_site_available():
            raise Exception("Can not reach site")

        return max(self.downloads().keys())

    def remove(self):
        log.debug(f"Deleting {self.binary()}")
        rmf(self.binary())

    def download(self):
        if not self.is_site_available():
            raise Exception("Can not reach site")

        url = self.downloads()[self.desired_version()]
        filename = os.path.basename(url)

        os.makedirs(self.install_dir(), exist_ok=True)
        with chdir(self.install_dir()):
            rmf(filename)
            with open(filename, "wb") as file:
                file.write(self.get(url))
            if not os.path.exists(filename):
                raise Exception(f"Could not download {url}")
            pass

            log.debug(f"Successfully downloaded {filename}")
            dcf = self.decompress_file(filename)
            log.debug("Decompression complete")
            if dcf:
                log.debug(f"Deleting {filename}")
                rmf(filename)
            if self.responds_to("extract_file"):
                # noinspection PyUnresolvedReferences
                self.extract_file(dcf)

        if not os.path.isfile(self.binary()):
            raise Exception(f"Could not decompress {filename} to get {self.binary()}")

        st = os.stat(self.binary()).st_mode
        st |= stat.S_IRUSR | stat.S_IXUSR  # u+rx
        st |= stat.S_IRGRP | stat.S_IXGRP  # g+rx
        st |= stat.S_IROTH | stat.S_IXOTH  # o+rx
        os.chmod(self.binary(), st)
        log.debug(f"Completed download and processing of {self.binary()}")
        return self.binary()

    def install_dir(self):
        return os.getenv("WEBDRIVERS_INSTALL_DIR") or os.path.abspath(
            os.path.join(os.getenv("HOME"), ".webdrivers")
        )

    def binary(self):
        return os.path.join(self.install_dir(), self.file_name())

    # Protected

    def get(self, url):
        response = self.urlopen(url)
        log.debug(f"Get response: {type(response)} {response.status} {response.msg} ")
        return response.read()

    def urlopen(self, url):
        if self.using_proxy():
            raise NotImplementedError("Proxy support has not yet been implemented")
        else:
            return urllib.request.urlopen(url)

    # Private

    def using_proxy(self):
        # TODO: Implement proxy
        return False

    def is_downloaded(self):
        result = os.path.isfile(self.binary())
        log.debug(f"File is already downloaded: {result}")
        return result

    def is_site_available(self):
        log.debug(f"Looking for Site: {self.base_url()}")
        try:
            self.get(self.base_url())
            log.debug(f"Found Site: {self.base_url()}")
            return True
        except Exception as e:
            log.debug(e)
            return False

    def platform(self):
        host_os = platform.system().lower()
        if host_os == "linux":
            return f"linux{'64' if platform.machine().endswith('64') else '32'}"
        elif host_os == "darwin":
            return "mac"
        else:
            return "win"

    def decompress_file(self, filename):
        if filename.endswith("tar.gz"):
            log.debug("Decompressing tar")
            return self.untargz_file(filename)
        elif filename.endswith("tar.bz2"):
            log.debug("Decompressing bz2")
            sh(f"tar xjf {filename}")
            return filename.rstrip(".tar.bz2")
        elif filename.endswith("zip"):
            log.debug("Decompressing zip")
            return self.unzip_file(filename)
        else:
            log.debug("No Decompression needed")
            return None

    def untargz_file(self, filename):
        raise NotImplementedError

    def unzip_file(self, filename):
        with zipfile.ZipFile(os.path.join(os.getcwd(), filename), "r") as zip_ref:
            zip_ref.extractall(os.getcwd())
            return zip_ref.filelist[0].filename

    def is_correct_binary(self):
        return (
            self.current_version()
            and self.desired_version() == self.current_version()
            and os.path.isfile(self.binary())
        )

    def normalize(self, string):
        if isinstance(string, bytes):
            string = string.decode("utf-8")
        return HashableVersion(string)

    def responds_to(self, symbol):
        op = getattr(self, symbol, None)
        return op and callable(op)

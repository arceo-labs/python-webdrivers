# -*- coding: utf-8 -*-
import logging
import re
import shlex
import urllib.request as request

from lxml import html

from webdrivers.common import CommonDriver
from webdrivers.util import sh

log = logging.getLogger()


class Chromedriver(CommonDriver):
    all_downloads = {}

    def current_version(self):
        log.debug("Checking current version")
        if not self.is_downloaded():
            return None

        ver = sh(f"{self.binary()} --version")
        log.debug(f"Current {self.binary()} version: {ver}")

        # Matches 2.46, 2.46.628411 and 73.0.3683.75
        return self.normalize(re.search(r"\d+\.\d+(\.\d+)?(\.\d+)?", ver).group())

    def latest_version(self):
        if not self.is_site_available():
            raise Exception("Can not reach site")

        # Versions before 70 do not have a LATEST_RELEASE file
        if self.release_version() < self.normalize("70.0.3538"):
            return self.normalize("2.46")

        # Latest webdriver release for installed Chrome version
        release_file = f"LATEST_RELEASE_{self.release_version()}"
        latest_available = self.get(request.urljoin(self.base_url(), release_file))
        log.debug(f"Latest version available: {latest_available}")
        return self.normalize(latest_available)

    # Private

    def file_name(self):
        return "chromedriver.exe" if self.platform() == "win" else "chromedriver"

    def base_url(self):
        return "https://chromedriver.storage.googleapis.com"

    def downloads(self):
        if self.all_downloads:
            log.debug(
                f"Versions previously located on downloads site: {self.all_downloads.keys()}"
            )

        doc = html.fromstring(self.get(self.base_url()))
        items = [
            item.text
            for item in doc.cssselect("Contents Key")
            if self.platform() in item.text
        ]
        ds = dict(
            (
                self.normalize(re.search("^[^/]+", item).group()),
                f"{self.base_url()}/{item}",
            )
            for item in items
        )
        log.debug(f"Versions now located on downloads site: {ds.keys()}")
        self.all_downloads.update(ds)
        return self.all_downloads

    # Returns release version from the currently installed Chrome version
    #
    # @example
    #   73.0.3683.75 -> 73.0.3683
    def release_version(self):
        return re.search(r"\d+\.\d+\.\d+", self.chrome_version()).group()

    def chrome_version(self):
        platform = self.platform()
        if platform == "win":
            ver = self.chrome_on_windows()
        elif platform.startswith("linux"):
            ver = self.chrome_on_linux()
        elif platform == "mac":
            ver = self.chrome_on_mac()
        else:
            raise NotImplementedError("Your OS is not supported by webdrivers plugin.")

        if not ver:
            raise Exception("Failed to find Chrome binary or its version.")

        # Google Chrome 73.0.3683.75 -> 73.0.3683.75
        return re.search(r"\d+\.\d+\.\d+\.\d+", ver).group()

    def chrome_on_windows(self):
        raise NotImplementedError

    def chrome_on_linux(self):
        if self.browser_binary():
            log.debug(f"Browser executable: {self.browser_binary()}")
            return shlex.quote(self.browser_binary())

        # Default to Google Chrome
        executable = sh("which google-chrome").strip()
        log.debug(f"Browser executable: {executable}")
        return sh(f"{executable} --product-version").strip()

    def chrome_on_mac(self):
        if self.browser_binary():
            log.debug(f"Browser executable: {self.browser_binary()}")
            return str(sh(f"{shlex.quote(self.browser_binary())} --version")).strip()

        # Default to Google Chrome
        executable = shlex.quote(
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        )
        log.debug(f"Browser executable: {executable}")
        return str(sh(f"{executable} --version")).strip()

    def browser_binary(self):
        # TODO: Figure out what Ruby impl is doing and mimic that
        return None

# -*- coding: utf-8 -*-
from webdrivers.chromedriver import Chromedriver


def Chrome():
    from selenium.webdriver.chrome import webdriver

    class ChromeWebDriver(webdriver.WebDriver):
        def __init__(self, *args, **kwargs):
            if "executable_path" not in kwargs:
                kwargs["executable_path"] = Chromedriver().update()
            super().__init__(*args, **kwargs)

    return ChromeWebDriver()


def Firefox():
    raise NotImplementedError("Haven't yet implemented Firefox webdriver")


__all__ = ["Chrome", "Firefox"]

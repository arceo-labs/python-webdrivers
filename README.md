# Python Webdrivers

_A shameless Python port of the much better Ruby library: https://github.com/titusfortner/webdrivers_

## Description

`webdrivers` downloads drivers and directs Python-Selenium to use them.  Currently supports:

  * [chromedriver](http://chromedriver.chromium.org/)
  * *COMING SOON!*
    * [geckodriver](https://github.com/mozilla/geckodriver)
  * *Only by demand*
    * [IEDriverServer](https://github.com/SeleniumHQ/selenium/wiki/InternetExplorerDriver)
    * [MicrosoftWebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)

## Usage

_(Recommended)_ Install using pipenv (example assumes `--dev` for testing):
```bash
pipenv install --dev -e git+https://github.com/arceo-labs/python-webdrivers#egg=webdrivers
```

In your project, use the `webdrivers` module instead of `selenium.webdriver` to initialie
your webdriver of choice.  To be more explicit, replace:
```python
from selenium import webdriver

driver = webdriver.Chrome()
```
...with:
```python
import webdrivers

driver = webdrivers.Chrome()
```

That's it!  Use the `driver` like you would a Selenium driver (it's only a shim), and your
browser's driver should be automatically downloaded and updated.


## License

This library is available as open source under the terms of the MIT License, see
[LICENSE.txt](LICENSE.txt) for full details and copyright.

## Contributing

Bug reports and pull requests are welcome here on GitHub.  Run `pipenv run test` and squash the commits
in your PRs.

## Copyright

Copyright (c) 2019 Arceo.ai


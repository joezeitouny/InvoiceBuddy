# InvoiceBuddy

[![Alt text](https://img.shields.io/pypi/v/invoicebuddy.svg?style=flat-square)](https://pypi.python.org/pypi/invoicebuddy/) [![Alt text](https://img.shields.io/github/license/joezeitouny/invoicebuddy)](https://pypi.python.org/pypi/invoicebuddy/)

A tool to help with generating invoices and proposals for freelancers or small businesses.

### Installation

**Requirements:	Python 3.x >= 3.5**

`InvoiceBuddy` can be installed via `pip` or an equivalent via:

```console
$ pip install InvoiceBuddy
```

#### From Source

You can install `InvoiceBuddy` from source just as you would install any other Python package:

```console
$ pip install git+https://github.com/joezeitouny/InvoiceBuddy.git
```

This will allow you to keep up to date with development on GitHub:

```console
$ pip install -U git+https://github.com/joezeitouny/InvoiceBuddy.git
```

### Features

- Ability to generate Excel and / or CSV logs
- Generate GPX file with GPS coordinates combined with timestamps
- Ability to generate a summary log for each session
- Sessions can be tied by the NMEA server, Victron system availability or by a specified time interval

### Usage

```console
$ python -m InvoiceBuddy --config=CONFIGURATION_FILENAME [options]
```

Where CONFIGURATION_FILENAME points to the file where the JSON configuration file is located on your system.

For the full list of available options

```console
$ python -m InvoiceBuddy --help
```

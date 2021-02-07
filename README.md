[![Documentation Status](https://readthedocs.org/projects/mone/badge/?version=latest)](https://mone.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/pearjo/mone.svg?branch=master)](https://travis-ci.org/pearjo/mone)
![Swagger Validator](https://validator.swagger.io/validator?url=https://raw.githubusercontent.com/pearjo/mone/master/mone/www/api/openapi.yaml)

# Mone: your private bookkeeper

If you want to track your spending's but don't want to share all you
financial data, then you're at the right place. Mone provides a
bookkeeper to track and record all your transactions and stores them
in a database over which you have control.

The bookkeeper is intended to be used for double-entry bookkeeping.
So money is like a continuum which neither can be created nor
destroyed. It can only change it's owner or like in the case here: an
account.

## Getting Started

Mone provides an API which is build upon flask and is written for
Python 3.8. The required packages can be install by running:

```bash
pip install -r requirements.txt
```

To install the mone package run:

```bash
python setup.py install
```

The code documentation can be build by running the following:

```bash
cd doc
make html
```

## Usage

Before running the mone app, you need to initialize the database which
is used to store your records. This is done by running:

```bash
FLASK_APP=mone/www flask init-db
```

This creates the directory `instance` including your
database. Finally, the app is run as following:

```bash
FLASK_APP=mone/www flask run
```

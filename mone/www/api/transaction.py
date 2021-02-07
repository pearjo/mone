# Copyright (C) 2020  Joe Pearson
#
# This file is part of Mone.
#
# Mone is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mone is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import logging

from flask import Response, url_for, redirect
import connexion

from mone.www import db
from mone.www.model import Transaction


def delete(uuid: str) -> Response:
    """DELETE /transaction/{uuid}"""
    transaction = Transaction(db.get_book())
    logging.debug('Delete transaction: %s', uuid)
    transaction.delete(uuid)
    return redirect(url_for('.mone_www_book_search', full='true'), 303)


def post() -> Response:
    """POST /transaction"""
    transaction = Transaction(db.get_book())
    logging.debug('Create transaction: %s', transaction)
    transaction.create(connexion.request.get_json())
    return redirect(url_for('.mone_www_book_search', full='true'), 303)


def search() -> dict:
    """GET /transaction"""
    transaction = Transaction(db.get_book())
    return transaction.read()

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
import datetime

import mone.book


class Account():
    def __init__(self, book):
        self.book = book

    def create(self, data):
        acct = mone.book.Account(data['name'],
                                 data['balance'],
                                 data['extern'])
        self.book.add(acct)

    def read(self):
        def to_dict(acct):
            return {'balance': acct.balance,
                    'extern': acct.extern,
                    'name': acct.name,
                    'uuid': acct.uuid}

        return list(map(to_dict, self.book.accounts.values()))

    def delete(self, uuid, replacement):
        self.book.replace(uuid, replacement)


class Budget():
    def __init__(self, book):
        self.book = book

    def create(self, data):
        budget = mone.book.Budget(data['name'],
                                  data['balance'],
                                  data['budget'])
        self.book.add(budget)

    def read(self):
        def to_dict(budget):
            return {'balance': budget.balance,
                    'budget': budget.budget,
                    'name': budget.name,
                    'uuid': budget.uuid}

        return list(map(to_dict, self.book.budgets.values()))

    def delete(self, uuid, replacement):
        self.book.replace(uuid, replacement)


class Book():
    def __init__(self, book):
        self.book = book

    def read(self, full=False):
        response = {'accounts': Account(self.book).read(),
                    'balance': self.book.balance,
                    'budgets': Budget(self.book).read()}
        if full:
            response['transactions'] = Transaction(self.book).read()

        return response


class Transaction():
    def __init__(self, book):
        self.book = book

    def create(self, data):
        transaction = mone.book.Transaction(
            value=data['value'],
            description=data['description'],
            sources=set(data['sources']),
            receiver=set(data['receiver']),
            date=datetime.date.fromisoformat(data['date']),
            tags=set(data['tags'])
        )
        self.book.add(transaction)

    def read(self):
        def to_dict(transaction):
            return {'uuid': transaction.uuid,
                    'date': transaction.date.isoformat(),
                    'description': transaction.description,
                    'receiver': list(transaction.receiver),
                    'sources': list(transaction.sources),
                    'tags': list(transaction.tags),
                    'value': transaction.value}

        return list(map(to_dict, self.book.transactions))

    def delete(self, uuid):
        self.book.remove(uuid)

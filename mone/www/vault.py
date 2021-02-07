# -*- coding: utf-8 -*-

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

"""
A vault to store the book's records
===================================

This module provides classes which extend several of the :mod:`~mone.book`
classes to be stored in a database, aka the vault.

.. currentmodule:: mone.vault

.. autosummary::
   :toctree: generated/

"""

from dataclasses import dataclass, field
import json
import logging
import sqlite3

import mone.book


class StoredAccounts(mone.book.Accounts):
    """Extend :class:`~mone.book.Accounts` to store them in a database."""

    def __init__(self, db) -> None:
        """Stores the accounts in the database *db*. """
        self.db = db
        accounts = self.__fetch__()
        super().__init__(accounts)

    def __delitem__(self, uuid: str) -> None:
        logging.debug('Delete stored account: %s', uuid)
        self.db.execute('DELETE FROM accounts WHERE id=?', (uuid,))
        self.db.commit()
        super().__delitem__(uuid)

    def __fetch__(self) -> mone.book.Accounts:
        results = self.db.execute('SELECT * FROM accounts').fetchall()
        accounts = list(map(lambda d: mone.book.Account.from_dict(json.loads(d[1])),
                            results))
        uuids = map(lambda d: d[0], results)
        return mone.book.Accounts(zip(uuids, accounts))

    def __setitem__(self, uuid: str, account: mone.book.Account) -> None:
        logging.debug('Add stored account: %s', account)
        self.db.execute('INSERT INTO accounts VALUES (?, ?)',
                        [uuid, json.dumps(account.to_dict())])
        self.db.commit()
        super().__setitem__(uuid, account)


class StoredBudgets(mone.book.Accounts):
    """Extend :class:`~mone.book.Accounts` to store budgets in a database."""

    def __init__(self, db) -> None:
        """Stores the budgets in the database *db*. """
        self.db = db
        budgets = self.__fetch__()
        super().__init__(budgets)

    def __delitem__(self, uuid: str) -> None:
        logging.debug('Delete stored budget: %s', uuid)
        self.db.execute('DELETE FROM budgets WHERE id=?', (uuid,))
        self.db.commit()
        super().__delitem__(uuid)

    def __fetch__(self) -> mone.book.Accounts:
        results = self.db.execute('SELECT * FROM budgets').fetchall()
        budgets = list(map(lambda d: mone.book.Budget.from_dict(json.loads(d[1])),
                           results))
        uuids = map(lambda d: d[0], results)
        return mone.book.Accounts(zip(uuids, budgets))

    def __setitem__(self, uuid: str, budget: mone.book.Budget) -> None:
        logging.debug('Add stored budget: %s', budget)
        self.db.execute('INSERT INTO budgets VALUES (?, ?)',
                        [uuid, json.dumps(budget.to_dict())])
        self.db.commit()
        super().__setitem__(uuid, budget)


class StoredTransactions(mone.book.Transactions):
    """Extend :class:`~mone.book.Transactions` to store them in a database."""

    def __init__(self, db) -> None:
        """Stores the transactions in the database *db*. """
        self.db = db
        transactions = self.__fetch__()
        super().__init__(transactions)

    def __fetch__(self) -> mone.book.Transactions:
        # fetch all transactions and return them
        results = self.db.execute('SELECT * FROM transactions').fetchall()
        return mone.book.Transactions(
            map(lambda d: mone.book.Transaction.from_dict(json.loads(d[1])),
                results))

    def append(self, transaction: mone.book.Transaction) -> None:
        """Extend :meth:`~mone.book.Transactions.append` to insert the transaction into
        the database.
        """
        logging.debug('Add stored transaction: %s', transaction)
        self.db.execute('INSERT INTO transactions VALUES (?, ?)',
                        [transaction.uuid,
                         json.dumps(transaction.to_dict())])
        self.db.commit()
        super().append(transaction)

    def overwrite(self, transactions: mone.book.Transactions) -> None:
        """Overwrite the stored transactions with the *transactions*."""
        logging.debug('Overwrite stored transactions!')
        self.db.execute('DELETE FROM transactions')
        self.db.executemany('INSERT INTO transactions VALUES (?, ?)',
                            list(map(lambda t: (t.uuid,
                                                json.dumps(t.to_dict())),
                                     transactions)))
        self.db.commit()

    def remove(self, transaction: mone.book.Transaction) -> None:
        logging.debug('Remove transaction: %s', transaction)
        super().remove(transaction)
        is_str = isinstance(transaction, str)
        uuid = transaction if is_str else transaction.uuid
        self.db.execute('DELETE FROM transactions WHERE id=?', (uuid,))
        self.db.commit()


@dataclass
class Vault():
    """Store accounts, budgets and transactions in a database."""
    db: sqlite3.Connection

    accounts: StoredAccounts = field(init=False)
    """The stored accounts."""

    budgets: StoredBudgets = field(init=False)
    """The stored budgets."""

    transactions: StoredTransactions = field(init=False)
    """The stored transactions."""

    def __post_init__(self):
        self.accounts = StoredAccounts(self.db)
        self.budgets = StoredBudgets(self.db)
        self.transactions = StoredTransactions(self.db)

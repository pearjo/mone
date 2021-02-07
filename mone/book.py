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
A book used for bookkeeping
===========================

This module provides several classes which for together a book, which is used
for bookkeeping. The :class:`BookKeeper` holds all records and manages the
booking of :class:`Transactions` onto :class:`Accounts`. Besides recording
transactions on the accounts, they can also be add to a :class:`Budget` which
can be part of the accounts. The :class:`Budget` accounts can be used to set up
budgets to track spendings on e.g. living costs.

.. currentmodule:: mone.book

.. autosummary::
   :toctree: generated/
"""

from __future__ import annotations

from typing import Any, List, Set, Union
from uuid import uuid1
import csv
import datetime
import io


class Accounts(dict):
    """A dictionary of :class:`Account`.

    Extend :class:`dict` to add some methods helping to manage the accounts.
    The :attr:`balance` is the sum of all account's balances excluding the
    external accounts. A transaction can be :meth:`add()` to another
    account. A single transaction can be removed with :meth:`remove()` from all
    accounts or all transactions can be removed from all accounts by
    :meth:`reset()`. In addition, all accounts can be returned as a list of
    dictionaries by :meth:`to_dict()`.
    """

    def __setitem__(self, key: str, value: Account) -> None:
        if not isinstance(value, Account):
            raise ValueError('can only add Account')

        super().__setitem__(key, value)

    def add(self, transaction: Transaction) -> None:
        """Add the *transaction* to the accounts.

        The transaction is add to all transactions which are a source or
        receiver of the transaction.
        """
        get = self.get
        uuids = transaction.sources | transaction.receiver
        for uuid in uuids:
            acct = get(uuid)
            if acct is not None:
                acct.add(transaction)

    @property
    def balance(self) -> float:
        """The balance of all accounts excluding the external accounts."""
        # filter externals
        accts = filter(lambda a: not a.extern, self.values())
        return sum(map(lambda a: a.balance, accts))

    def remove(self, transaction: Transaction) -> None:
        """Remove the *transaction* from all accounts."""
        for acct in self.values():
            acct.transactions.remove(transaction)

    def reset(self) -> None:
        """Clear all transactions of all accounts to reset them."""
        for acct in self.values():
            acct.transactions.clear()

    def to_dict(self) -> List[dict]:
        """Return a list of accounts as dictionaries.

        .. seealso:: :meth:`Account.to_dict()`
        """
        return [t.to_dict() for t in self.values()]


class Transactions(list):
    """A list of :class:`Transaction`.

    Extend :class:`list` to manage transactions. Only objects of type
    :class:`Transaction` can be appended. However, a list of transactions can
    also be generated from a CSV file, e.g. a bank export of an account's
    transactions, by :meth:`from_csv()`. Transactions can also be generated
    from a list of transactions represented by a dictionary with
    :meth:`from_dict()`. With :meth:`to_dict()`, the list can be returned as
    such a list of transactions as dictionaries. A transaction can be removed
    from the list with :meth:`remove()`.
    """

    def append(self, other) -> None:
        """Extend to check the type of *other*.

        Raise a :class:`TypeError` if *other* is not a :class:`Transaction`.
        """
        if not isinstance(other, Transaction):
            raise TypeError('can only add Transaction')

        super().append(other)

    @classmethod
    def from_csv(cls, file: str, value: int, date: int, description: int,
                 skiprows: int = 0, delimiter: str = ',', thousands: str = '',
                 decimal: str = '.', datefmt: str = '%Y-%M-%d') -> 'Transactions':
        """Return a transactions list from a csv *file*.

        Most banks provide the option to download transactions as csv files from
        which transactions can be read. The *file* must provide the columns
        *value*, *date* and *description*. If the file contains additional
        information you can *skiprows* to the start of the actual data with the
        column indices as defined previous. The columns are delimited by the
        *delimiter*. The value can have a *thousands* and *decimal*
        separator. The format of the date column is defined by *datefmt*.

        .. seealso:: :meth:`datetime.date.strftime()` for more on *datefmt*.
        """

        def strpdate(date_str: str) -> datetime.datetime:
            """Return a datetime object from the parsed *date_str*."""
            return datetime.datetime.strptime(date_str, datefmt).date()

        def strpfloat(float_str: str) -> float:
            """Return a float from the parsed *float_str*."""
            return float(float_str.replace(thousands, '')
                         .replace(decimal, '.'))

        def ptransaction(transaction: list) -> Transaction:
            """Return a Transaction from the parsed *transaction* list."""
            return Transaction(strpfloat(transaction[value]),
                               '',
                               transaction[description],
                               [],
                               [],
                               strpdate(transaction[date]))

        if isinstance(file, str):
            stream = open(file, 'r')
        else:
            stream = io.TextIOWrapper(file.stream._file, 'UTF8', newline=None)

        reader = csv.reader(stream, delimiter=delimiter)
        entries = list(reader)[skiprows:]
        transactions = map(ptransaction, entries)
        stream.close()

        return cls(transactions)

    @classmethod
    def from_dict(cls, dictionary) -> 'Transactions':
        """Return a transactions from a *dictionary*.

        The keys of the each transaction dictionary are the same as for
        :meth:`Transaction.from_dict()`.
        """
        return cls(map(Transaction.from_dict, dictionary))

    def remove(self, transaction: Union[Transaction, str]) -> None:
        """Remove the *transaction* from the list.

        Extend remove to either remove the actual :class:`Transaction` object
        or the transaction identified by it's uuid.
        """
        # get transaction by uuid
        if isinstance(transaction, str):
            transaction = next(filter(lambda t: t.uuid == transaction,
                                      self),
                               None)

        if transaction is not None and transaction in self:
            super().remove(transaction)

    def to_dict(self) -> List[dict]:
        """Return a list with transactions as dictionaries.

        .. seealso:: :meth:`Transaction.to_dict()`
        """
        return [t.to_dict() for t in self]


class Account():
    """An account tracking transactions with a balance.

    The account is used like a bank account our your wallet. It has some money
    in it, the :attr:`balance`, and you can add :attr:`transactions` which
    either add money to the account or worst, remove some from it.

    A :class:`Transaction` can be :meth:`add()` to the account which returns
    the new balance, or the addition of two accounts can also be returned by
    :meth:`add()`. An account can be represented as a dictionary by
    :meth:`to_dict()` or can be created from such a dict by :meth:`from_dict`.

    Often you have transactions which are going out of your pocket into the
    pockets (or accounts) of someone else. To track such transactions, an
    account can be :attr:`extern`, which then represents the pocket of someone
    else. Usually it should be sufficient to have one external account, but one
    can add as many external accounts as necessary. Accounts marked as
    :attr:`extern` don't pay into the :attr:`Accounts.balance`. The following
    example should illustrate the use of accounts::

       >>> from mone.book import Account, Accounts, Transaction
       >>>
       >>> # We have one bank account with an initial balance of 10000 and an
       >>> # empty external account.
       >>> bank = Account('Bank Account', 10000)
       >>> extern = Account('External Account', extern=True)
       >>>
       >>> # Bundle the accounts in an Accounts object and check our balance.
       >>> accounts = Accounts({bank.uuid: bank, extern.uuid: extern})
       >>> accounts.balance
       10000
       >>>
       >>> # Now lets buy a coffee and pay it with our bank account.
       >>> t = Transaction(5, 'USD', 'Coffee', {bank.uuid}, {extern.uuid})
       >>> accounts.add(t)
       >>>
       >>> # The 5$ went now from our pocket into the coffee shop's pocket and
       >>> # are gone from our perspective.
       >>> accounts.balance
       9995

    """

    def __init__(self, name: str, balance: float = 0.0, extern: bool = False,
                 uuid: str = None) -> None:
        """The account requires a *name* and an initial *balance*.

        Optionally, the *extern* attribute can be set and a *uuid* can be
        provided.
        """

        self.extern = extern
        """*True* if the account is used to track transactions which are going
        out of your pocket. As an example, when you pay something in a store,
        it goes from your pocket into the one of the shop owner. The shop
        owners account is then in our view an external account.
        """

        self.name = name
        """The account name."""

        self.uuid = uuid or str(uuid1())
        """A unique identifier of the account."""

        self.transactions = Transactions()
        """The :class:`Transactions` booked with the account."""

        self._init_balance = balance

    def __add__(self, other) -> float:
        return self.add(other)

    def __radd__(self, other) -> float:
        return self.add(other)

    def __repr__(self) -> str:
        return (f'Account({self.name}, {self.balance}, {self.extern})')

    def add(self, other: Any) -> float:
        """Return addition of account and *other*.

        Same as ``account + other``. The *other* can be an :class:`Account` or a
        :class:`Transaction`.
        """
        if isinstance(other, Account):
            return self.balance + other.balance

        if isinstance(other, Transaction):
            self.transactions.append(other)
            return self.balance

        return self.balance + other

    @property
    def balance(self) -> float:
        """The balance of the account.

        Transactions which are used to rebalance budget accounts are excluded
        from the balance. The balance is the sum of all remaining transactions
        where each value get a negative sign if the account is in that
        transaction's sources.
        """
        def sign(t: Transaction) -> int:
            if ((self.uuid in t.sources and self.uuid in t.receiver)
                    or t.budget_rebalance):
                return 0
            return -1 if self.uuid in t.sources else 1

        return sum(map(lambda t: sign(t) * t.value, self.transactions),
                   start=self._init_balance)

    @classmethod
    def from_dict(cls, data: dict) -> 'Account':
        """Return an account generated from the *data*.

        The *data* dictionary must have the key ``'name'``. The ``'balance'``,
        ``'uuid'`` and ``'extern'`` keys are optional.
        """
        return cls(
            uuid=data.get('uuid'),
            name=data['name'],
            balance=data.get('balance'),
            extern=data.get('extern')
        )

    def history(self, periode: List[datetime.date] =
                [datetime.date.min, datetime.date.max]) -> dict:
        transactions = list(filter(
            lambda t: min(periode) <= t.date <= max(periode),
            self.transactions
        ))
        return {'balance': [t.balance for t in transactions],
                'date': [t.date.isoformat() for t in transactions]}

    def to_dict(self) -> dict:
        """Return the account as dictionary.

        The returned dictionary has the following keys:

        - ``'uuid'`` the unique identifier :attr:`uuid` of the account
        - ``'extern'`` the :attr:`extern` flag of the account
        - ``'name'`` the account :attr:`name`
        - ``'balance'`` the :attr:`balance` of the account

        """
        return {'uuid': self.uuid,
                'extern': self.extern,
                'name': self.name,
                'balance': float(self.balance)}


class BookKeeper():
    """Keep records of all accounts and transactions.

    The bookkeeper is the one, who records all :attr:`transactions` between all
    :attr:`accounts` and :attr:`budgets`. An account, budget or transaction can
    be :meth:`add()` to the book to keep a record of it. The bookkeeper can also
    :meth:`replace()` an account by another account or :meth:`remove()` a
    transaction from all accounts or budgets where it was booked.
    """

    def __init__(self, accounts: Accounts, budgets: Accounts,
                 transactions: Transactions) -> None:
        """Open the book with the *accounts*, *budgets* and *transactions*."""

        self.accounts = accounts
        """The :class:`Accounts` used for bookkeeping."""

        self.budgets = budgets
        """The budgets used for bookkeeping."""

        self.transactions = transactions
        """The :class:`Transactions` which are recorded by the bookkeeper."""

        self.__bookall__()

    def __book__(self, transaction: Transaction) -> None:
        self.accounts.add(transaction)
        self.budgets.add(transaction)

    def __bookall__(self) -> None:
        for transaction in self.transactions:
            self.__book__(transaction)

    def __repr__(self) -> str:
        return f'BookKeeper({self.accounts, self.budgets, self.transactions})'

    def add(self, other: Union[Account, Budget, Transaction]) -> None:
        """Add *other* to the book.

        If *other* is a transaction, the bookkeeper checks if the transaction
        is used to rebalance a budget and sets
        :attr:`~Transaction.budget_rebalance` accordingly before adding it to
        the book.
        """
        if isinstance(other, Account):
            if isinstance(other, Budget):
                self.budgets[other.uuid] = other
            else:
                self.accounts[other.uuid] = other
        elif isinstance(other, Transaction):
            other.budget_rebalance = ((len(other.sources)
                                       == len(other.receiver)
                                       == 1)
                                      and other.receiver.issubset(self.budgets))
            self.transactions.append(other)
            self.__book__(other)

    @property
    def balance(self) -> float:
        """The sum of all :attr:`accounts` balances.

        .. note:: External accounts are excluded from the balance.
        """
        accts = filter(lambda a: type(a) == Account and not a.extern,
                       self.accounts.values())
        return sum(map(lambda a: a.balance, accts))

    def remove(self, transaction: Transaction) -> None:
        """Remove the *transaction* from the book.

        The *transaction* is removed from the :attr:`transactions`,
        :attr:`accounts` and :attr:`budgets`.
        """
        self.transactions.remove(transaction)
        self.accounts.remove(transaction)
        self.budgets.remove(transaction)

    def replace(self, current: str, replacement: str) -> None:
        """Replace the *current* by *replacement*.

        The :class:`Account`, :class:`Budget` or :class:`Transaction` with the
        uuid *current* is replaced by the object of same type with the uuid
        *replacement*. When e.g. an account should be removed from the book
        because it was merged with another account, it can be replaced by the
        other account move all transactions booked with it to the other
        account.
        """
        if current in self.accounts:
            del self.accounts[current]
        elif current in self.budgets:
            del self.budgets[current]

        for transaction in self.transactions:
            transaction.update(current, replacement)

        self.transactions.overwrite(self.transactions)
        self.accounts.reset()
        self.budgets.reset()
        self.__bookall__()

    def to_dict(self, full: bool = False) -> dict:
        """Return the book as dictionary.

        When *full* is true, all transactions are returned additionally. The
        returned dictionary has the keys:

        - ``'accounts'`` a list of all accounts
        - ``'balance'`` the book's balance
        - ``'budgets'`` a list of all budgets

        """
        data = {
            'accounts': self.accounts.to_dict(),
            'budgets': self.budgets.to_dict(),
            'balance': float(self.balance)
        }

        if full:
            data['transactions'] = self.transactions.to_dict()

        return data


class Budget(Account):
    """A budget to better keep track of spendings.

    Extend an :class:`Account` to add a :attr:`budget` and the :attr:`balance`
    shows how much money is left to spend.
    """

    def __init__(self, name: str, budget: float = 0.0,
                 balance: float = 0.0, uuid: str = None) -> None:
        """
        Extend the :class:`Account` to provide a *budget*.
        """

        self.budget = budget
        """The budget."""

        super().__init__(name, balance, uuid=uuid)

    def __repr__(self) -> str:
        return 'Budget(%r, %f, %f)' % (
            self.name, self.budget, self.balance
        )

    @property
    def balance(self) -> float:
        """The money which is left to be spend.

        The budget's balance is the sum of all transactions and the set
        budget.
        """
        def sign(t: Transaction) -> int:
            return -1 if self.uuid in t.sources else 1

        return sum(map(lambda t: sign(t) * t.value,
                       self.transactions),
                   self.budget)

    @classmethod
    def from_dict(cls, data: dict) -> 'Budget':
        return cls(
            uuid=data.get('uuid'),
            name=data.get('name'),
            budget=data.get('budget'),
            balance=data.get('balance'),
        )

    def to_dict(self) -> dict:
        d = super().to_dict()
        d['budget'] = float(self.budget)
        return d


class Transaction():
    """A transaction of money between accounts."""

    def __init__(self, value: float, description: str, sources: Set[str],
                 receiver: Set[str], date: datetime.date =
                 datetime.date.today(), tags: Set[str] = [], budget_rebalance:
                 bool = False, uuid: str = None) -> None:
        """
        The transaction of the *value* and is executed at the defined *date*.
        The *description* gives information about the transaction. The *sources*
        are all accounts from which the *value* is subtracted and *receiver* is
        a list of all accounts to which the *value* is booked. A list of *tags*
        can be add optional to the transaction.
        """
        self.value = abs(value)
        """The value of the transaction.

        The value is always positive since the :attr:`sources` and
        :attr:`receiver` define the direction of the cash flow.
        """

        self.date = date
        """The date when the transaction is booked (value date)."""

        self.description = description
        """A brief description of the transaction."""

        self.budget_rebalance = budget_rebalance

        self.sources = sources
        """A list of account ids from which the :attr:`value` is subtracted."""

        self.receiver = receiver
        """A list of account ids to which the :attr:`value` is add."""

        if not self.sources or not self.receiver:
            raise TypeError('Sources or receiver not defined.')

        self.tags = tags
        """A list of tags to help track the transaction."""

        self.uuid = uuid if uuid else str(uuid1())
        """The transaction's unique identifier."""

    def __repr__(self) -> str:
        return 'Transaction(%f, %r, %r, %r, %r, %r, %r)' % (
            self.value, self.description, self.sources, self.receiver,
            self.date, self.tags, self.budget_rebalance
        )

    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Return a transaction from the dictionary.

        The dictionary *dict* has the same keys as the one returned by
        :meth:`to_dict()`.

        .. seealso:: :meth:`to_dict()` for all keys.
        """
        return cls(
            date=datetime.date.fromisoformat(data.get('date')),
            description=data.get('description'),
            receiver=set(data.get('receiver')),
            sources=set(data.get('sources')),
            tags=set(data.get('tags')),
            value=data.get('value'),
            uuid=data.get('uuid')
        )

    def update(self, current: str, replacement: str) -> None:
        """Update the sources and receiver.

        The *current* account in the sources and receiver is replaced by its
        *replacement*.
        """
        if current in self.receiver:
            self.receiver.remove(current)
            self.receiver.add(replacement)
        if current in self.sources:
            self.sources.remove(current)
            self.sources.add(replacement)

    def to_dict(self) -> dict:
        """Return the transaction as dictionary.

        The dictionary has the following keys:

        - ``'uuid'`` the unique identifier :attr:`uuid`
        - ``'date'`` the date in ISO format
        - ``'description'`` the :attr:`description` of the transaction
        - ``'receiver'`` a list of the receiver's identifier
        - ``'sources'`` a list of the source's identifier
        - ``'tags'`` the list of :attr:`tags`
        - ``'value'`` the value of the transaction
        """
        return {
            'uuid': self.uuid,
            'date': self.date.isoformat(),
            'description': self.description,
            'receiver': list(self.receiver),
            'sources': list(self.sources),
            'tags': list(self.tags),
            'value': self.value,
        }

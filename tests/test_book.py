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

import unittest

import mone.book


class TestAccounts(unittest.TestCase):
    """Test the Accounts."""

    def setUp(self):
        self.account_list = [mone.book.Account('Bank', 10000),
                             mone.book.Account('Extern', extern=True),
                             mone.book.Account('Cash', 1000)]
        self.uuids = list(map(lambda acct: acct.uuid, self.account_list))

        self.accounts = mone.book.Accounts(zip(self.uuids, self.account_list))
        self.transaction = mone.book.Transaction(10, 'Add test',
                                                 sources={self.uuids[0]},
                                                 receiver={self.uuids[1]})

    def test_add(self):
        """Add a transaction and check the new balance."""
        acct_0 = self.account_list[0]

        new_balance = acct_0.balance - self.transaction.value  # acct_0 is source
        self.accounts.add(self.transaction)
        self.assertEqual(acct_0.balance, new_balance)

    def test_balance(self):
        """Compare difference of balances before and after a transaction."""
        init_balance = self.accounts.balance
        self.accounts.add(self.transaction)
        final_balance = self.accounts.balance
        self.assertEqual(abs(final_balance - init_balance),
                         self.transaction.value)

    def test_remove(self):
        """Add one transaction to an account and remove it.

        The balance before adding the transaction and after removing it are
        compared to be equal.
        """
        initial_balance = self.accounts[self.uuids[0]].balance
        self.accounts.add(self.transaction)
        self.accounts.remove(self.transaction)
        self.assertEqual(self.accounts[self.uuids[0]].balance, initial_balance)

    def test_reset(self):
        """Book a transaction to an external account and reset the
        transactions."""
        init_balance = self.accounts.balance
        self.accounts.add(self.transaction)
        self.accounts.reset()
        self.assertEqual(self.accounts.balance, init_balance)


class TestTransactions(unittest.TestCase):
    """Test the book's Transactions."""

    def setUp(self):
        self.transaction_list = [
            mone.book.Transaction(4, 'Coffee', {'account'}, {'shop'}),
            mone.book.Transaction(20, 'Drinks', {'account'}, {'shop'}),
            mone.book.Transaction(40, 'Dinner', {'account'}, {'shop'}),
        ]
        self.transactions = mone.book.Transactions(self.transaction_list)

    def test_append(self):
        """Append not a Transaction and expect a type error."""
        self.assertRaises(TypeError, self.transactions.append, None)

    def test_remove(self):
        """Remove a transaction by it's uuid."""
        self.transactions.remove(self.transaction_list[0].uuid)
        self.assertEqual(len(self.transactions),
                         len(self.transaction_list) - 1)


class TestAccount(unittest.TestCase):
    """Test an Account."""

    def setUp(self):
        self.account = mone.book.Account('My Account', 100)
        self.other = mone.book.Account("Other's Account", 20)

    def test_add(self):
        """Add another account and transaction to an account."""
        self.assertEqual(self.account + self.other, 120)

        # transfer 4 EUR for coffee from account to other
        transaction = mone.book.Transaction(4, 'Coffee',
                                            {self.account.uuid},
                                            {self.other.uuid})
        self.assertEqual(self.account + transaction, 96)

        # return the 4 EUR from other to account since the coffee was for free
        transaction = mone.book.Transaction(4, 'Free Coffee',
                                            {self.other.uuid},
                                            {self.account.uuid})
        self.assertEqual(self.account + transaction, 100)

    def test_balance(self):
        """Add transactions where uuid is in sources, receiver and both."""
        transaction = mone.book.Transaction(10, 'Spend money',
                                            {self.account.uuid},
                                            {self.other.uuid})
        self.account.add(transaction)
        self.assertEqual(self.account.balance, 90)

        transaction = mone.book.Transaction(10, 'Earn money',
                                            {self.other.uuid},
                                            {self.account.uuid})
        self.account.add(transaction)
        self.assertEqual(self.account.balance, 100)

        transaction = mone.book.Transaction(10, 'Shift money around',
                                            {self.account.uuid},
                                            {self.account.uuid})
        self.account.add(transaction)
        self.assertEqual(self.account.balance, 100)


if __name__ == '__main__':
    unittest.main()

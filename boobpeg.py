#!/usr/bin/env python

from weboob.core import Weboob
from weboob.capabilities.bank import CapBank
import logging

logger = logging.getLogger(__name__)

class Boobpeg:
    """ Class that performs requests using weboob capabitilities """

    def __init__(self):
        self.peg_perco_names = ["PERCO INTEGRAL",
                                "PERCO LIBRE",
                                "PERCO PILOTE",
                                "PLAN D'EPARGNE GROUPE"]
        self.weboob = Weboob()
        self.weboob.load_backends(CapBank)
        self.investments = {}

    def retrieve_investments(self, account):
        account_investments = {}
        for investment in list(self.weboob.iter_investment(account)):
            account_investments[investment.code] = str(investment.unitvalue)
        return account_investments

    def update_investments(self):
        accounts = list(self.weboob.iter_accounts())
        for account in accounts:
            if account.label in self.peg_perco_names:
                self.investments.update(self.retrieve_investments(account))

        return self.investments


if __name__ == "__main__":
    from tabulate import tabulate
    boobpeg = Boobpeg()
    investments = boobpeg.update_investments()
    array_investments = []
    for code, value in investments.items():
        array_investments.append([code, value])
    print(tabulate(array_investments, ["code", "unit value"], "pipe"))

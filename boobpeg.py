#!/usr/bin/env python

from weboob.core import Weboob
from weboob.capabilities.bank import CapBank
import logging

logger = logging.getLogger(__name__)


class Boobpeg:
    """ Class that performs requests using weboob capabitilities """

    def __init__(self):
        logger.debug("class init")
        self.peg_perco_names = []
        self.weboob = Weboob()
        self.weboob.load_backends(CapBank)
        self.investments = {}

    def set_peg_perco_names(self, peg_perco_names):
        logger.debug("set_peg_perco_names(): peg_perco_names: %s"
                     % peg_perco_names)
        self.peg_perco_names = ["PERCO INTEGRAL",
                                "PERCO LIBRE",
                                "PERCO PILOTE",
                                "PLAN D'EPARGNE GROUPE"]

    def retrieve_investments(self, account):
        logger.debug("retrieve_investments(): account: %s" % account)
        account_investments = {}
        for investment in list(self.weboob.iter_investment(account)):
            account_investments[investment.code] = str(investment.unitvalue)
        logger.debug("retrieve_investments(): return: %s"
                     % account_investments)
        return account_investments

    def update_investments(self):
        logger.debug("update_investments()")
        accounts = list(self.weboob.iter_accounts())
        for account in accounts:
            if account.label in self.peg_perco_names:
                self.investments.update(self.retrieve_investments(account))

        logger.debug("update_investments(): return: %s" % self.investments)
        return self.investments


if __name__ == "__main__":
    from tabulate import tabulate
    boobpeg = Boobpeg()
    investments = boobpeg.update_investments()
    array_investments = []
    for code, value in investments.items():
        array_investments.append([code, value])
    print(tabulate(array_investments, ["code", "unit value"], "pipe"))

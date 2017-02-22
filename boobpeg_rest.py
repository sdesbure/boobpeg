#!/usr/bin/env python


import json
import os.path
import logging
import sys
from argparse import ArgumentParser
from datetime import datetime
from bottle import run, get
from boobpeg import Boobpeg
from boobmanage import Boobmanage

version = 1.0
parser = ArgumentParser(description='give a REST api in order to retrieve '
                                    'unit values of PEG/PERCO accounts')
parser.add_argument('--config-folder', help="configuration folder",
                    dest="config_folder", default=".")
group = parser.add_mutually_exclusive_group()
group.add_argument("-v", "--verbose", action="store_true")
group.add_argument("-q", "--quiet", action="store_true")

args = parser.parse_args()
level = logging.INFO
if args.verbose:
    level = logging.DEBUG
if args.quiet:
    level = logging.ERROR

LOGGER = logging.getLogger()
LOGGER.setLevel(level)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(level)
formatter = logging.Formatter(
        '%(asctime)s|%(levelname)s|%(name)s|%(message)s')
ch.setFormatter(formatter)
LOGGER.addHandler(ch)

values_file = args.config_folder + '/values.json'
config_file = args.config_folder + '/config.json'
LOGGER.debug("values file location: %s" % values_file)
LOGGER.debug("config file location: %s" % config_file)

boobpeg = None


@get('/')
def index():
    return {"server": "OK", "version": version}


def update_investments_and_return_value(code):
    now = datetime.now()
    investments = boobpeg.update_investments()
    save_file = {
            "date_retrieved": now.strftime("%Y-%m-%d"),
            "codes": investments}
    with open(values_file, 'w') as outfile:
            json.dump(save_file, outfile)
    if code in investments:
        return {"unit_value": investments[code]}
    else:
        return {"error": "code %s unknown" % (code)}


@get('/code/<code>')
def show_code(code):
    if os.path.isfile(values_file):
        values = None
        with open(values_file) as data_file:
            values = json.load(data_file)
        if "date_retrieved" in values:
            now = datetime.now()
            if now.strftime("%Y-%m-%d") == values["date_retrieved"]:
                if "codes" in values and code in values["codes"]:
                    return {"unit_value": values["codes"][code]}
                else:
                    return {"error": "code %s unknown" % (code)}
    return update_investments_and_return_value(code)


if os.path.isfile(config_file):
    LOGGER.debug("opening config.json file in order to retrieve configuration")
    config = None
    boobmanage = Boobmanage()
    with open(config_file) as data_file:
        config = json.load(data_file)
    if "providers" in config:
        for provider in config["providers"]:
            LOGGER.debug('checking if provider "%s" is already configured'
                         % provider)
            if not boobmanage.has_backend(provider):
                LOGGER.debug('provider "%s" not there, adding it' % provider)
                if provider in config["provider_credentials"]:
                    boobmanage.add_backend(
                            provider,
                            config["provider_credentials"][provider])
                else:
                    LOGGER.error('bad configuration file (no credentials for '
                                 'provider "%s", exiting' % provider)
                    exit()
            else:
                LOGGER.debug('provider "%s" already configurer, continuing'
                             % provider)
    else:
        LOGGER.error("bad configuration file (no provider given), exiting")
        exit()
    boobpeg = Boobpeg()
    if "peg_perco_names" in config:
        boobpeg.set_peg_perco_names(config["peg_perco_names"])
    else:
        LOGGER.error('bad configuration file (no peg_perco_names), exiting')
        exit()
    run(host='0.0.0.0', port=8081)
else:
    LOGGER.error('config.json is not present in folder "%s", please create it '
                 'and restart' % args.config_folder)

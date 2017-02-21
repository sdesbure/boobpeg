#!/usr/bin/env python


import json
import os.path
import logging
import sys
from datetime import datetime
from bottle import run, get
from boobpeg import Boobpeg

version = 1.0
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
LOGGER.addHandler(ch)


@get('/')
def index():
    return {"server": "OK", "version": version}


def update_investments_and_return_value(code):
    now = datetime.now()
    boobpeg = Boobpeg()
    investments = boobpeg.update_investments()
    save_file = {
            "date_retrieved": now.strftime("%Y-%m-%d"),
            "codes": investments}
    with open('values.json', 'w') as outfile:
            json.dump(save_file, outfile)
    if investments[code]:
        return {"unit_value": investments[code]}
    else:
        return {"error": "code %s unknown" % (code)}


@get('/code/<code>')
def show_code(code):
    if os.path.isfile("values.json"):
        values = None
        with open('values.json') as data_file:
            values = json.load(data_file)
        if "date_retrieved" in values:
            now = datetime.now()
            if now.strftime("%Y-%m-%d") == values["date_retrieved"]:
                if "codes" in values and code in values["codes"]:
                    return {"unit_value": values["codes"][code]}
                else:
                    return {"error": "code %s unknown" % (code)}
    return update_investments_and_return_value(code)


run(host='0.0.0.0', port=8081)

#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Author: $Author$
Date: $Date$
Revision: $Revision$

Description: Describe module function
"""
import sys
import subprocess

BASE_PORT = 9601
IP = '127.0.0.1'
NAME = 'gameServer'

currencyServerCounts = {
    'CNY'       :   1,
    'USD'       :   0,
    'HKD'       :   0,
    'THB'       :   0,
    'IDR'       :   0,
    'MYR'       :   0,
    'KRW'       :   0,
    'LAK'       :   0,
    'MMK'       :   0,
    'PHP'       :   0,
    'VND'       :   0,
    'VND1'      :   0,
    'JPY'       :   0,
    'TWD'       :   0,
    'SGD'       :   0,
    'GUEST'     :   0,
    'TEST'      :   0,
}

for code, count in currencyServerCounts.iteritems():
    for i in xrange(count):
        subprocess.Popen('python -m run_server -i %s -p %s -c %s -n %s'%(IP, BASE_PORT, code, NAME), shell=True)
        BASE_PORT += 1

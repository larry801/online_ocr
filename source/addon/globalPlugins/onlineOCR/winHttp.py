# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# urllib3 used in this file is Copyright (c) 2008-2019 Andrey Petrov and contributors under MIT license.
import addonHandler
import ui
from logHandler import log
from urllib3.contrib.socks import SOCKSProxyManager
import config
import urllib3
urllib3.disable_warnings()
# import certifi
# import urllib3.contrib.pyopenssl
# urllib3.contrib.pyopenssl.inject_into_urllib3()

oldProxyType = config.conf["onlineOCR"]["proxyType"]
oldProxyAddress = config.conf["onlineOCR"]["proxyAddress"]
_ = lambda x: x
addonHandler.initTranslation()

# Translators: Message announced when network error occurred
internet_error_message = _(u"Recognition failed. Internet connection error.")
# Translators: Message announced when network error occurred
timeout_message = _(u"Internet connection timeout.Recognition failed. ")


def getConnectionPool():
    proxyType = config.conf["onlineOCR"]["proxyType"]
    proxyAddress = config.conf["onlineOCR"]["proxyAddress"]
    msg = u"type:\n{0}\naddress:\n{1}".format(
        proxyType,
        proxyAddress
    )

    if proxyType == u"http":
        pool = urllib3.ProxyManager(
            proxyAddress,
            # cert_reqs='CERT_REQUIRED',
            # ca_certs=certifi.where(),
            timeout=urllib3.Timeout(connect=10, read=10)
        )
        msg += u"\nHTTP proxy\n{0}".format(
            pool
        )
        log.io(msg)
        return pool
    elif proxyType == u"socks":
        pool = SOCKSProxyManager(
            proxyAddress,
            # cert_reqs='CERT_REQUIRED',
            # ca_certs=certifi.where(),
            timeout=urllib3.Timeout(connect=10, read=10)
        )
        msg += u"\nSocks proxy\n{0}".format(
            pool
        )
        log.io(msg)
        return pool
    else:
        pool = urllib3.PoolManager(
            # cert_reqs='CERT_REQUIRED',
            # ca_certs=certifi.where(),
            timeout=urllib3.Timeout(connect=10, read=10)
        )
        msg += u"\nNo proxy\n{0}".format(
            pool
        )
        log.io(msg)
        return pool


httpConnectionPool = getConnectionPool()


def refreshConnectionPool():
    if oldProxyType == config.conf["onlineOCR"]["proxyType"] \
            and oldProxyAddress == config.conf["onlineOCR"]["proxyAddress"]:
        pass
    else:
        global httpConnectionPool
        httpConnectionPool = getConnectionPool()


def doHTTPRequest(callback, method, url, **kwargs):
    """
    Call this method in a separate thread to avoid blocking.
    @param callback:
    @type callback:
    @param method:
    @type method:
    @param url:
    @type url:
    """
    refreshConnectionPool()
    try:
        r = httpConnectionPool.request(method, url, **kwargs)
    except urllib3.exceptions.TimeoutError:
        ui.message(timeout_message)
        return
    except urllib3.exceptions.HTTPError as e:
        log.error(e)
        ui.message(internet_error_message)
        return
    log.io(r.data)
    callback(r.data)


def postContent(callback, url, data, headers=None):
    doHTTPRequest(callback, 'POST', url, fields=data,
                  headers=headers)

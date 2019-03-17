# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# urllib3 used in this file is Copyright (c) 2008-2019 Andrey Petrov and contributors under MIT license.
import addonHandler
import certifi
import urllib3.contrib.pyopenssl
import ui
from logHandler import log
from six import string_types

_ = lambda x: x
addonHandler.initTranslation()
urllib3.contrib.pyopenssl.inject_into_urllib3()
http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where(),
    timeout=urllib3.Timeout(connect=10, read=10)
)
# Translators: Message announced when network error occurred
internet_error_message = _(u"Recognition failed. Internet connection error.")
# Translators: Message announced when network error occurred
timeout_message = _(u"Internet connection timeout.Recognition failed. ")


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
    try:
        if isinstance(url, string_types):
            url = url.encode('utf8')
        r = http.request(method, url, **kwargs)
    except urllib3.exceptions.TimeoutError:
        ui.message(timeout_message)
        return
    except Exception as e:
        log.error(e)
        ui.message(internet_error_message)
        return
    log.io(r.data)
    callback(r.data)


def postContent(callback, url, data, headers=None):
    doHTTPRequest(callback, 'POST', url, fields=data,
                  headers=headers)

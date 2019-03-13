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
# Translators: Message announced when network error occured
internet_error_message = _(u"Recognition failed. Internet connection error.")
timeout_message = _(u"Recognition failed. Internet connection timeout")


def multipartFormData(url, fileObject, callback, headers=None, paramName=None, fileName=None):
    """
    POST multipart formData
    :param fileName:
    :param paramName:
    :param headers:
    :param url:
    :param fileObject:
    :param callback:
    :return:
    """
    if isinstance(url, string_types):
        url = url.encode('utf8')
    try:
        if headers:
            r = http.request(
                'POST',
                url,
                fields={
                    paramName: (fileName, fileObject),
                },
                headers=headers)
        else:
            r = http.request(
                'POST',
                url,
                fields={
                    paramName: (fileName, fileObject),
                })
    except urllib3.exceptions.TimeoutError:
        ui.message(timeout_message)
        return
    except Exception as e:
        log.error(e)
        ui.message(internet_error_message)
        return
    callback(r.data)


def postContent(callback, url, data, headers=None):
    if isinstance(url, string_types):
        url = url.encode('utf8')
    try:
        if headers:
            r = http.request(
                'POST',
                url,
                fields=data,
                headers=headers)
        else:
            r = http.request(
                'POST',
                url,
                fields=data)
    except urllib3.exceptions.TimeoutError:
        ui.message(internet_error_message)
        return
    except Exception as e:
        log.error(e)
        ui.message(internet_error_message)
        return
    callback(r.data)

# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# urllib3 used in this file is Copyright (c) 2008-2019 Andrey Petrov and contributors under MIT license.
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
import addonHandler
import ui
from logHandler import log
from urllib3.contrib.socks import SOCKSProxyManager
import six
import config
import urllib3
import wx
urllib3.disable_warnings()
# import certifi
# import urllib3.contrib.pyopenssl
# urllib3.contrib.pyopenssl.inject_into_urllib3()

oldProxyType = config.conf["onlineOCRGeneral"]["proxyType"]
oldProxyAddress = config.conf["onlineOCRGeneral"]["proxyAddress"]
_ = lambda x: x
addonHandler.initTranslation()


def showMessageInNetworkThread(message):
	wx.CallAfter(ui.message, message)


def getConnectionPool():
	proxyType = config.conf["onlineOCRGeneral"]["proxyType"]
	proxyAddress = config.conf["onlineOCRGeneral"]["proxyAddress"]
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
	global httpConnectionPool, oldProxyType, oldProxyAddress
	if oldProxyType == config.conf["onlineOCRGeneral"]["proxyType"] \
		and oldProxyAddress == config.conf["onlineOCRGeneral"]["proxyAddress"]:
		pass
	else:
		httpConnectionPool = getConnectionPool()
		oldProxyType = config.conf["onlineOCRGeneral"]["proxyType"]
		oldProxyAddress = config.conf["onlineOCRGeneral"]["proxyAddress"]


def doHTTPRequest(callback, method, url, **kwargs):
	"""
	Call this method in a separate thread to avoid blocking.
	@param callback:
	@type callback:
	@param method:
	@type method:
	@param url:
	@type url: bytes
	"""
	refreshConnectionPool()
	try:
		if isinstance(url, bytes) and six.PY3:
			url = url.decode('utf-8')
		r = httpConnectionPool.request(method, url, **kwargs)
	except urllib3.exceptions.TimeoutError as e:
		# Translators: Message announced when network error occurred
		showMessageInNetworkThread(_(u"Internet connection timeout.Recognition failed."))
		callback(None)
		return
	except urllib3.exceptions.HTTPError as e:
		log.error(e)
		# Translators: Message announced when network error occurred
		showMessageInNetworkThread(_(u"Recognition failed. Internet connection error."))
		callback(None)
		return
	log.io(r.data)
	callback(r.data)


def postContent(callback, url, data, headers=None):
	if six.PY2:
		doHTTPRequest(
			callback, b'POST', url, fields=data,
			headers=headers
		)
	elif six.PY3:

		doHTTPRequest(
			callback, 'POST', url, fields=data,
			headers=headers
		)

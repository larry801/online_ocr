# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from .. import onlineOCRHandler
import addonHandler
import hashlib
from six.moves.urllib_parse import urlencode
from six import iterkeys
from logHandler import log

_ = lambda x: x
addonHandler.initTranslation()


class CustomContentRecognizer(onlineOCRHandler.BaseRecognizer):
	name = b"sougouOCR"
	
	# Translators: Description of Online OCR Engine
	description = _("Sougou AI OCR")
	
	uploadBase64EncodeImage = False
	
	def _get_supportedSettings(self):
		return [
			CustomContentRecognizer.AccessTypeSetting(),
			CustomContentRecognizer.APIKeySetting(),
			CustomContentRecognizer.APISecretSetting(),
		]
	
	@classmethod
	def check(cls):
		return True
	
	def process_api_result(self, result):
		import json
		try:
			apiResult = json.loads(result)
			code = apiResult["success"]
			if code != 1:
				# Translators: Error message of sougou API
				return _(u"Sougou API error occurred. Recognition failed")
		except Exception as e:
			log.error(e)
			return False
		try:
			statusText = apiResult["statusText"]
			return statusText
		except:
			return False
	
	def get_domain(self):
		if self._use_own_api_key:
			self.useHttps = False
			return b"api.ai.sogou.com"
		else:
			self.useHttps = True
			return self.NVDAcnDomain
	
	useHttps = True
	
	def get_url(self):
		if self._use_own_api_key:
			return b"pub/ocr"
		else:
			return b"ocr/sougou.php"
	
	@staticmethod
	def calculate_signature(options, app_key):
		"""
		generate signature for API
		@param app_key: API secret key
		@param options: request parameters
		@type options: dict
		@return:
		"""
		encoded_option = ""
		key_sequence = sorted(iterkeys(options), reverse=False)
		for k in key_sequence:
			query = "&" + urlencode({
				k: options[k]
			})
			encoded_option += query
		encoded_option += "&app_key="
		encoded_option += app_key
		encoded_option = encoded_option[1:]
		md5 = hashlib.md5()
		md5.update(encoded_option)
		return md5.hexdigest()
	
	def getHTTPHeaders(self):
		if self._use_own_api_key:
			return {
				b"Authorization": str(self.getSignature(self._api_key, self._api_secret_key, b""))
			}
		else:
			return {}
	
	def getPayload(self, jpegBytes):
		if self._use_own_api_key:
			# use str here to avoid urllib3 decode raw image data as bytes
			fileName = str(self.getImageFileName())
			# The name "pic" is mandated by the API endpoint
			paramName = b"pic"
		else:
			paramName = b'foo'
			fileName = b'foo'
		payloads = {
			paramName: (fileName, jpegBytes)
		}
		return payloads
	
	def convert_to_line_result_format(self, apiResult):
		def extractCoordinate(coord):
			groups = coord.split(',')
			return int(groups[0]), int(groups[1])
		
		lineResult = []
		for items in apiResult[u"result"]:
			rightXCoord, yCoord = extractCoordinate(items[u"frame"][1])
			xCoord, downYCoord = extractCoordinate(items[u"frame"][2])
			lineResult.append([{
				"x": xCoord,
				"y": yCoord,
				"width": rightXCoord - xCoord,
				"height": downYCoord - yCoord,
				"text": items[u"content"],
			}])
		log.io(lineResult)
		return lineResult
	
	@staticmethod
	def extract_text(apiResult):
		words = []
		for items in apiResult[u"result"]:
			words.append(items[u"content"])
			log.io(items[u"content"])
		return u" ".join(words)
	
	@staticmethod
	def getSignature(ak, sk, url, method='POST'):
		import hashlib
		import time
		import hmac
		import base64
		pre = "sac-auth-v1/" + ak + '/' + str(int(time.time())) + "/3600"
		part2 = "\nPOST\napi.ai.sogou.com\n/pub/ocr\n"
		message = bytes(pre + part2)
		signature = hmac.new(bytes(sk), message, digestmod=hashlib.sha256).digest()
		headerSig = pre + '/' + base64.b64encode(signature)
		log.io(headerSig)
		return str(headerSig)
	
	def getFullURL(self):
		from six import string_types
		url = super(CustomContentRecognizer, self).getFullURL()
		fullURL = url
		# Unicode URL cause urllib3 to decode raw image data as if they were unicode.
		if isinstance(fullURL, string_types):
			if not isinstance(fullURL, str):
				fullURL = fullURL.decode('utf8')
		return fullURL
	
	@staticmethod
	def getImageFileName():
		import time
		fNList = []
		ts = "{0:.3f}".format(time.time())
		fNList.append(ts)
		fNList.append('_')
		
		def luhn_residue(digits):
			return sum(
				sum(
					divmod(
						int(d) * (1 + i % 2), 10
					)
				)
				for i, d in enumerate(digits[::-1])
			) % 10
		
		def getIMEI(N):
			import random
			part = ''.join(str(random.randrange(0, 9)) for _ in range(N - 1))
			res = luhn_residue('{}{}'.format(part, 0))
			return '{}{}'.format(part, -res % 10)
		
		import hashlib
		m = hashlib.md5()
		m.update(str(getIMEI(15)))
		fNList.append(m.hexdigest())
		fNList.append('_fyj.jpg')
		return "".join(fNList)

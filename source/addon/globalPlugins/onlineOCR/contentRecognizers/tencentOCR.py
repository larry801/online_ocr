# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from onlineOCRHandler import BaseRecognizer
import addonHandler
import hashlib
from six.moves.urllib_parse import urlencode
from six import iterkeys
from logHandler import log

_ = lambda x: x
addonHandler.initTranslation()


class CustomContentRecognizer(BaseRecognizer):
	name = b"tencentOCR"
	api_domain = b"api.ai.qq.com"
	api_url = "fcgi-bin/ocr/ocr_generalocr"

	# Translators: Description of Online OCR Engine
	description = _(u"Tencent AI OCR")

	maxSize = 1024 * 1024

	minWidth = 5

	minHeight = 5

	def __init__(self):
		self.onResult = None

	@classmethod
	def check(cls):
		return True

	def _get_supportedSettings(self):
		return [
			CustomContentRecognizer.AccessTypeSetting(),
			CustomContentRecognizer.AppIDSetting(),
			CustomContentRecognizer.APIKeySetting(),
		]

	def convert_to_line_result_format(self, apiResult):
		lineResult = []
		if apiResult["ret"] != 0:
			raise RuntimeError("OCR Failed")
		item_list = apiResult["data"]["item_list"]
		for items in item_list:
			lineResult.append([{
				"x": items["itemcoord"][0]["x"],
				"y": items["itemcoord"][0]["y"],
				"width": items["itemcoord"][0]["width"],
				"height": items["itemcoord"][0]["height"],
				"text": items["itemstring"],
			}])
		return lineResult

	@staticmethod
	def calculate_signature(options, app_key):
		"""
		generate signature for API
		@param app_key: API secret key
		@param options: request parameters
		@type options: dict
		@return: signatrue
		@rtype: str
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

	def process_api_result(self, result):
		import json
		apiResult = json.loads(result)
		try:
			if apiResult["ret"] != 0:
				# Translators: Error message of Tencent API
				return _(u"Error occurred on API endpoint")
			else:
				return False
		except KeyError:
			return False

	def getFullURL(self):
		fullURL = super(CustomContentRecognizer, self).getFullURL()
		from six import binary_type
		if isinstance(fullURL, binary_type):
			fullURL = fullURL.encode("utf-8")
		return fullURL

	def create_payload(self, png_string, app_id="", app_secret="", use_nvda_cn=True):
		if use_nvda_cn:
			options = {
				b"image": png_string
			}
		else:
			import time
			import random
			options = {
				b"app_id": app_id,
				b"time_stamp": int(time.time()),
				b"nonce_str": str(random.randint(10000, 99999)),
				b"image": png_string
			}
			sign = self.calculate_signature(options, app_secret)
			sign = sign.upper()
			options[b"sign"] = sign
		log.io(options)
		return options

	def get_domain(self):
		if self._use_own_api_key:
			return self.api_domain
		else:
			return self.NVDAcnDomain

	def get_url(self):
		if self._use_own_api_key:
			return self.api_url
		else:
			return "ocr/tencent.php"

	def getPayload(self, image):
		if self._use_own_api_key:
			return self.create_payload(
				image,
				app_id=self._appID,
				app_secret=self._api_secret_key,
				use_nvda_cn=False)
		else:
			return self.create_payload(image, use_nvda_cn=True)

	@staticmethod
	def extract_text(apiResult):
		lineResult = []
		if apiResult["ret"] != 0:
			raise RuntimeError("OCR Failed")
		item_list = apiResult["data"]["item_list"]
		for items in item_list:
			lineResult.append(items["itemstring"])
		return u" ".join(lineResult)

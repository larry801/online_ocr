# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from onlineOCRHandler import BaseRecognizer
import addonHandler

_ = lambda x: x  # type: callable
addonHandler.initTranslation()


class CustomContentRecognizer(BaseRecognizer):

	def process_api_result(self, result):
		"""

		@param result: raw API result from urllib3
		@type result: str
		@return:
		@rtype: bool or str
		"""
		if len(result) <= 0:
			if self._use_own_api_key:
				# Translators: Error message
				return _(u"Result is empty.Your API quota is used up.")
			else:
				# Translators: Error message
				return _(u"Result is empty.Test quota is used up.")
		groups = result.split('|')
		if groups[1] == "ERROR":
			return groups[2]
		else:
			return False

	@staticmethod
	def extract_text(apiResult):
		"""
		Extract text result from API response
		@param apiResult:
		@type apiResult: str
		@return:
		@rtype: str
		"""
		groups = apiResult.split('|')
		return groups[2]

	def convert_to_line_result_format(self, apiResult):
		return [[{
			"x": 0,
			"y": 0,
			"width": 1,
			"height": 1,
			"text": self.extract_text(apiResult),
		}]]

	@staticmethod
	def convert_to_json(data):
		return data

	def get_domain(self):
		if self._use_own_api_key:
			self.useHttps = False
			return "api.captchadecoder.com"
		else:
			self.useHttps = True
			return self.NVDAcnDomain

	def _get_supportedSettings(self):
		return [
			CustomContentRecognizer.AccessTypeSetting(),
			CustomContentRecognizer.APIKeySetting(),
		]

	name = b"captcha"

	@classmethod
	def check(cls):
		return False

	# Translators: Description of Online OCR Engine
	description = _("Captcha Solving")

	def get_url(self):
		if self._use_own_api_key:
			return "decode"
		else:
			return "ocr/captchaDecode.php"

	def getPayload(self, image):
		fileName = b"captcha"
		if self._use_own_api_key:
			payload = {
				b"key": self._api_key,
				b"method": b"solve",
				b"captcha": (fileName, image),
			}
		else:
			payload = {
				"captcha": (fileName, image),
			}
		return payload

	def getHTTPHeaders(self, imageData):
		if self._use_own_api_key:
			return {
				"Content-type": "application/x-www-form-urlencoded"
			}

	def refreshBalance(self):

		def callback(response):
			self._balance = response

		if self._use_own_api_key:
			self.sendRequest(
				callback,
				b"http://api.captchadecoder.com/decode",
				{
					"key": self._api_key,
					"method": "balance",
				}
			)
		else:
			self.sendRequest(
				callback,
				b"https://www.nvdacn.com/ocr/captchaBalace.php",
				{
					"method": "balance",
				}
			)

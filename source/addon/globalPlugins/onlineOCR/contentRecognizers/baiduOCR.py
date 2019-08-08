# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from onlineOCRHandler import BaseRecognizer
import addonHandler
from logHandler import log
from collections import OrderedDict

_ = lambda x: x  # type: callable
addonHandler.initTranslation()


class CustomContentRecognizer(BaseRecognizer):
	name = b"baiduOCR"

	# Translators: Description of Online OCR Engine
	description = _("Baidu OCR")

	_access_token = ""

	def _get_access_token(self):
		return self._access_token

	def _set_access_token(self, access_token):
		self._access_token = access_token

	text_result = False

	_api_key = " "

	_api_secret_key = " "

	_language = "CHN_ENG"

	minHeight = 15

	minWidth = 15

	def _get_supportedSettings(self):
		return [
			CustomContentRecognizer.AccessTypeSetting(),
			CustomContentRecognizer.LanguageSetting(),
			# Translators: Label for OCR engine settings.
			CustomContentRecognizer.BooleanSetting("detectDirection", _("&Detect image  direction")),
			# Translators: Label for OCR engine settings.
			CustomContentRecognizer.BooleanSetting("recognizeGranularity", _("&Get position of every character")),
			# Translators: Label for OCR engine settings.
			CustomContentRecognizer.BooleanSetting("accurate", _("&Use Accurate API(Slower)")),
			# CustomContentRecognizer.ReadOnlySetting("access_token",
			#                                         # Translators: Label of access token
			#                                         _(u"Access Token"))
			CustomContentRecognizer.APIKeySetting(),
			CustomContentRecognizer.APISecretSetting(),
		]

	_timeout = 100

	def _get_timeout(self):
		return self._timeout

	def _set_timeout(self, timeout):
		self._timeout = timeout

	_accurate = False

	def _get_accurate(self):
		return self._accurate

	def _set_accurate(self, accurate):
		self._accurate = accurate

	_vertexes_location = False

	def _get_vertexes_location(self):
		return self._vertexes_location

	def _set_vertexes_location(self, vertexes_location):
		self._vertexes_location = vertexes_location

	_recognizeGranularity = False

	def _get_recognizeGranularity(self):
		return self._recognizeGranularity

	def _set_recognizeGranularity(self, recognizeGranularity):
		self._recognizeGranularity = recognizeGranularity

	@classmethod
	def check(cls):
		return True

	def refresh_token(self):
		url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={0}&client_secret={1}".format(
			self._api_key,
			self._api_secret_key
		)
		result = self.json_endpoint(url, {})
		log.io(result)
		try:
			self._access_token = result["access_token"]
			self.saveSettings()
		except Exception as e:
			log.error(e)

	def getFullURL(self):
		fullURL = super(CustomContentRecognizer, self).getFullURL()
		from six import binary_type
		if isinstance(fullURL, binary_type):
			fullURL = fullURL.encode("utf-8")
		return fullURL

	# noinspection PyBroadException
	def process_api_result(self, result):
		import json
		apiResult = json.loads(result)
		try:
			code = apiResult["error_code"]
			if code in (110, 111):
				self.refresh_token()
			return self.codeToErrorMessage[code]

		except Exception:
			return False

	codeToErrorMessage = {
		# Translators: Error message of Baidu OCR engine.
		1: _(u"Unknown error"),
		# Translators: Error message of Baidu OCR engine.
		2: _(u"Service temporarily unavailable"),
		# Translators: Error message of Baidu OCR engine.
		3: _(u"Unsupported api endpoints"),
		# Translators: Error message of Baidu OCR engine.
		4: _(u"Open api request limit reached"),
		# Translators: Error message of Baidu OCR engine.
		6: _(u"No permission to access data"),
		# Translators: Error message of Baidu OCR engine.
		14: _(u"IAM Certification failed"),
		# Translators: Error message of Baidu OCR engine.
		17: _(u"Open api daily request limit reached"),
		# Translators: Error message of Baidu OCR engine.
		18: _(u"Open api qps request limit reached"),
		# Translators: Error message of Baidu OCR engine.
		19: _(u"Open api total request limit reached"),
		# Translators: Error message of Baidu OCR engine.
		100: _(u"Invalid parameter"),
		# Translators: Error message of Baidu OCR engine.
		110: _(u"Access token invalid or no longer valid"),
		# Translators: Error message of Baidu OCR engine.
		111: _(u"Access token expired"),
		# Translators: Error message of Baidu OCR engine.
		282000: _(u"internal error"),
		# Translators: Error message of Baidu OCR engine.
		216100: _(u"invalid param"),
		# Translators: Error message of Baidu OCR engine.
		216101: _(u"not enough param"),
		# Translators: Error message of Baidu OCR engine.
		216102: _(u"service not support"),
		# Translators: Error message of Baidu OCR engine.
		216103: _(u"param too long"),
		# Translators: Error message of Baidu OCR engine.
		216110: _(u"appid not exist"),
		# Translators: Error message of Baidu OCR engine.
		216200: _(u"empty image"),
		# Translators: Error message of Baidu OCR engine.
		216201: _(u"image format error"),
		# Translators: Error message of Baidu OCR engine.
		216202: _(u"image size error"),
		# Translators: Error message of Baidu OCR engine.
		216630: _(u"recognize error"),
		# Translators: Error message of Baidu OCR engine.
		216631: _(u"recognize bank card error"),
		# Translators: Error message of Baidu OCR engine.
		216633: _(u"recognize ID card error"),
		# Translators: Error message of Baidu OCR engine.
		216634: _(u"detect error"),
		# Translators: Error message of Baidu OCR engine.
		272000: _(u"structure failed"),
		# Translators: Error message of Baidu OCR engine.
		272001: _(u"classify failed"),
		# Translators: Error message of Baidu OCR engine.
		282003: _(u"missing parameters"),
		# Translators: Error message of Baidu OCR engine.
		282004: _(u"invalid parameter, appId doesn't own this template nor not launch"),
		# Translators: Error message of Baidu OCR engine.
		282005: _(u"batch processing error"),
		# Translators: Error message of Baidu OCR engine.
		282006: _(u"batch task limit reached"),
		# Translators: Error message of Baidu OCR engine.
		282102: _(u"target detect error"),
		# Translators: Error message of Baidu OCR engine.
		282103: _(u"target recognize error"),
		# Translators: Error message of Baidu OCR engine.
		282110: _(u"urls not exit"),
		# Translators: Error message of Baidu OCR engine.
		282111: _(u"url format illegal"),
		# Translators: Error message of Baidu OCR engine.
		282112: _(u"url download timeout"),
		# Translators: Error message of Baidu OCR engine.
		282113: _(u"url response invalid"),
		# Translators: Error message of Baidu OCR engine.
		282114: _(u"url size error"),
		# Translators: Error message of Baidu OCR engine.
		282808: _(u"request id:  not exist"),
		# Translators: Error message of Baidu OCR engine.
		282809: _(u"result type error"),
		# Translators: Error message of Baidu OCR engine.
		282810: _(u"image recognize error"),
	}

	def get_domain(self):
		if self._use_own_api_key:
			return "aip.baidubce.com"
		else:
			return self.NVDAcnDomain

	def get_url(self):
		if self._use_own_api_key:
			if len(self._access_token) < 1:
				self.refresh_token()
			if self.text_result:
				if self._accurate == u"True":
					apiType = "accurate_basic"
				else:
					apiType = "general_basic"
			else:
				if self._accurate == u"True":
					apiType = "accurate"
				else:
					apiType = "general"
			url = "/rest/2.0/ocr/v1/{type}?access_token={token}".format(
				token=self._access_token,
				type=apiType
			)
		else:
			if self.text_result:
				if self._accurate == u"True":
					url = "ocr/baiduAccurate.php"
				else:
					url = "ocr/baiduBasic.php"
			else:
				# if self._accurate:
				#     url = "ocr/baiduAccurateWithPos.php"
				# else:
				# log.info(type(self._accurate))
				# log.info(self._accurate)
				url = "ocr/baidu.php"
		return url

	def getPayload(self, image):
		if self.text_result:
			return self.create_simple_payload(image)
		else:
			return self.create_payload(image)

	def _get_language(self):
		return self._language

	_detectLanguage = False

	def _get_detectLanguage(self):
		return self._detectLanguage

	def _set_detectLanguage(self, detectLanguage):
		self._detectLanguage = detectLanguage

	_detectDirection = False

	def _get_detectDirection(self):
		return self._detectDirection

	def _set_detectDirection(self, detectDirection):
		self._detectDirection = detectDirection

	def _set_language(self, language):
		self._language = language

	def _get_availableLanguages(self):
		languages = OrderedDict({
			# Translators: Text language for OCR
			"CHN_ENG": _("Chinese and English"),
			"ENG": _("English"),
			"POR": _("Portuguese"),
			"FRE": _("French"),
			"GER": _("German"),
			"ITA": _("Italian"),
			"SPA": _("Spanish"),
			"RUS": _("Russian"),
			"JAP": _("Japanese"),
			"KOR": _("Korean")
		})
		return self.generate_string_settings(languages)

	def create_payload(self, png_string):
		if self._recognizeGranularity:
			recognize_granularity = "small"
		else:
			recognize_granularity = "big"
		payload = {
			b"image": png_string,
			b"detect_direction": self.pyBool2json(self._detectDirection),
			b"detect_language": self.pyBool2json(self._detectLanguage),
			b"language_type": self._language,
			b"recognize_granularity": recognize_granularity,
			b"vertexes_location": self.pyBool2json(self._recognizeGranularity),
			b"probability": "false",
		}
		return payload

	def create_simple_payload(self, png_string):
		payload = {
			b"image": png_string,
			b"detect_direction": self.pyBool2json(self._detectDirection),
			b"detect_language": self.pyBool2json(self._detectLanguage),
			b"language_type": self._language,
			b"probability": "false",
		}
		return payload

	def convert_to_line_result_format(self, apiResult):
		lineResult = []
		if self._recognizeGranularity:
			for words in apiResult["words_result"]:
				wordResult = []
				for items in words["chars"]:
					wordResult.append({
						"x": items["location"]["left"],
						"y": items["location"]["top"],
						"width": items["location"]["width"],
						"height": items["location"]["height"],
						"text": items["char"],
					})
				lineResult.append(wordResult)
		else:
			for items in apiResult["words_result"]:
				lineResult.append([{
					"x": items["location"]["left"],
					"y": items["location"]["top"],
					"width": items["location"]["width"],
					"height": items["location"]["height"],
					"text": items["words"],
				}])
		log.io(lineResult)
		return lineResult

	@staticmethod
	def extract_text(apiResult):
		words = []
		for items in apiResult["words_result"]:
			words.append(items["words"])
		log.io(words)
		return u" ".join(words)

	@staticmethod
	def convert_to_json(data):
		import json
		data = data.decode("utf-8", errors="ignore")
		return json.loads(data)

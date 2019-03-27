# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from __future__ import unicode_literals
from .. import onlineOCRHandler
import addonHandler
from collections import OrderedDict

from logHandler import log

_ = lambda x: x
addonHandler.initTranslation()


class CustomContentRecognizer(onlineOCRHandler.BaseRecognizer):
	name = b"azureOCR"

	# Translators: Description of Online OCR Engine
	description = _("Microsoft Azure OCR")

	def _get_supportedSettings(self):
		return [
			CustomContentRecognizer.AccessTypeSetting(),
			CustomContentRecognizer.LanguageSetting(),
			CustomContentRecognizer.StringSettings(
				"region",
				# Translators: Label for engine settings
				_(u"Azure resource Region")
			),
			CustomContentRecognizer.APIKeySetting(),

		]

	_api_key = ""

	_type_of_api_access = "free"

	maxHeight = 4200

	maxWidth = 4200

	maxSize = 4 * 1024 * 1024  # 4 mega bytes

	_region = ""
	
	def getPayloadForHyperLink(self, url):
		import json
		return json.dumps({
			"url": url,
		})

	@classmethod
	def check(cls):
		return True

	def _get_region(self):
		return self._region

	def _set_region(self, region):
		self._region = region

	def _get_availableRegions(self):
		regions = OrderedDict({
			# Translators: Regions for azure ocr resource
			"canadacentral.api.cognitive.microsoft.com": _(u"Canada Central"),
			# Translators: Regions for azure ocr resource
			"westeurope.api.cognitive.microsoft.com": _(u"West Europe"),
			# Translators: Regions for azure ocr resource
			"eastus2.api.cognitive.microsoft.com": _(u"East US 2"),
			# Translators: Regions for azure ocr resource
			"southeastasia.api.cognitive.microsoft.com": _(u"Southeast Asia"),
			# Translators: Regions for azure ocr resource
			"centralindia.api.cognitive.microsoft.com": _(u"Central India"),
			# Translators: Regions for azure ocr resource
			"southcentralus.api.cognitive.microsoft.com": _(u"South Central US"),
			# Translators: Regions for azure ocr resource
			"australiaeast.api.cognitive.microsoft.com": _(u"Australia East"),
			# Translators: Regions for azure ocr resource
			"westus2.api.cognitive.microsoft.com": _(u"West US 2"),
			# Translators: Regions for azure ocr resource
			"eastasia.api.cognitive.microsoft.com": _(u"East Asia"),
			# Translators: Regions for azure ocr resource
			"eastus.api.cognitive.microsoft.com": _(u"East US"),
			# Translators: Regions for azure ocr resource
			"westus.api.cognitive.microsoft.com": _(u"West US"),
			# Translators: Regions for azure ocr resource
			"northeurope.api.cognitive.microsoft.com": _(u"North Europe"),
			# Translators: Regions for azure ocr resource
			"japaneast.api.cognitive.microsoft.com": _(u"Japan East"),
			# Translators: Regions for azure ocr resource
			"uksouth.api.cognitive.microsoft.com": _(u"UK South"),
			# Translators: Regions for azure ocr resource
			"westcentralus.api.cognitive.microsoft.com": _(u"West Central US"),
			# Translators: Regions for azure ocr resource
			"brazilsouth.api.cognitive.microsoft.com": _(u"Brazil South"),
			# Translators: Regions for azure ocr resource
			"chinanorth.api.cognitive.azure.cn": _(u"China North"),
			# Translators: Regions for azure ocr resource
			"chinaeast2.api.cognitive.azure.cn": _(u"China East 2"),
		})
		return self.generate_string_settings(regions)

	def get_domain(self):
		if self._use_own_api_key:
			return self._region
		else:
			return self.NVDAcnDomain

	def get_url(self):
		if self._use_own_api_key:
			return b"vision/v1.0/ocr"
		else:
			return b"ocr/msocr.php"

	def getPayload(self, jpegBytes):
		if self._use_own_api_key:
			fileName = b'ocr.png'
			paramName = fileName
		else:
			paramName = b'foo'
			fileName = b'foo'
		payloads = {
			paramName: (fileName, jpegBytes)
		}
		return payloads

	def getHTTPHeaders(self):
		if self._use_own_api_key:
			return {
				'Ocp-Apim-Subscription-Key': self._api_key
			}
		else:
			return {}

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

	_language = b"unk"

	def _get_language(self):
		return self._language

	def _set_language(self, language):
		self._language = language

	def _get_availableLanguages(self):
		languages = OrderedDict({
			# Translators: Text language for OCR
			b"unk": _(u"Auto Detect"),
			# Translators: Text language for OCR
			b"zh-Hans": _(u"Chinese Simplified"),
			# Translators: Text language for OCR
			b"zh-Hant": _(u"Chinese Traditional"),
			# Translators: Text language for OCR
			b"cs": _(u"Czech"),
			# Translators: Text language for OCR
			b"da": _(u"Danish"),
			# Translators: Text language for OCR
			b"nl": _(u"Dutch"),
			# Translators: Text language for OCR
			b"en": _(u"English"),
			# Translators: Text language for OCR
			b"fi": _(u"Finnish"),
			# Translators: Text language for OCR
			b"fr": _(u"French"),
			# Translators: Text language for OCR
			b"de": _(u"German"),
			# Translators: Text language for OCR
			b"el": _(u"Greek"),
			# Translators: Text language for OCR
			b"hu": _(u"Hungarian"),
			# Translators: Text language for OCR
			b"it": _(u"Italian"),
			# Translators: Text language for OCR
			b"ja": _(u"Japanese"),
			# Translators: Text language for OCR
			b"ko": _(u"Korean"),
			# Translators: Text language for OCR
			"nb": _(u"Norwegian"),
			# Translators: Text language for OCR
			b"pl": _(u"Polish"),
			# Translators: Text language for OCR
			b"pt": _(u"Portuguese"),
			# Translators: Text language for OCR
			b"ru": _(u"Russian"),
			# Translators: Text language for OCR
			b"es": _(u"Spanish"),
			# Translators: Text language for OCR
			b"sv": _(u"Swedish"),
			# Translators: Text language for OCR
			b"tr": _(u"Turkish"),
			# Translators: Text language for OCR
			b"ar": _(u"Arabic"),
			# Translators: Text language for OCR
			b"ro": _(u"Romanian"),
			# Translators: Text language for OCR
			b"sr-Cyrl": _(u"Cyrillic Serbian"),
			# Translators: Text language for OCR
			b"sr-Latn": _(u"Latin Serbian"),
			# Translators: Text language for OCR
			b"sk": _(u"Slovak"),
		})
		return self.generate_string_settings(languages)

	def getFullURL(self):
		from six import string_types
		url = super(CustomContentRecognizer, self).getFullURL()
		queryString = b"?language={0}&detectOrientation={1}".format(
			self._language,
			self.pyBool2json(self._detectDirection)
		)
		fullURL = url + queryString
		# Unicode URL cause urllib3 to decode raw image data as if they were unicode.
		if isinstance(fullURL, string_types):
			if not isinstance(fullURL, str):
				fullURL = fullURL.decode('utf8')
		return fullURL

	def serializeImage(self, PILImage):
		from io import BytesIO
		import ui
		imgBuf = BytesIO()
		PILImage.save(imgBuf, "PNG")
		imageContent = imgBuf.getvalue()
		if len(imageContent) > self.maxSize:
			# Translators: Reported when error occurred during image serialization
			errorMsg = _(u"Image content size is too big")
			ui.message(errorMsg)
			return False
		else:
			return imageContent

	def process_api_result(self, result):
		import json
		apiResult = json.loads(result)
		try:
			statusText = apiResult["message"]
			return statusText
		except KeyError:
			pass
		try:
			code = apiResult["code"]
			if code == 305:
				# Translators: Error message of Microsoft Cognitive API
				return _(u"Your quota is not adequate")
		except KeyError:
			return False

	def convert_to_line_result_format(self, apiResult):
		def extractCoordinate(coord):
			groups = coord.split(',')
			return int(groups[0]), int(groups[1]), int(groups[2]), int(groups[3])

		lineResult = []
		resultSets = apiResult["regions"]
		for result in resultSets:
			for line in result["lines"]:
				currentLine = []
				for word in line['words']:
					x, y, w, h = extractCoordinate(word["boundingBox"])
					currentLine.append({
						"x": x,
						"y": y,
						"width": w,
						"height": h,
						"text": word["text"]
					})
				lineResult.append(currentLine)
		log.io(lineResult)
		return lineResult

	@staticmethod
	def extract_text(apiResult):
		words = []
		resultSets = apiResult["regions"]
		for result in resultSets:
			for line in result["lines"]:
				for word in line['words']:
					words.append(word["text"])
		return u" ".join(words)

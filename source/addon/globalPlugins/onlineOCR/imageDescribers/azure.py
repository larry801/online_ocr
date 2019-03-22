# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from ..OnlineImageDescriberHandler import BaseDescriber
import addonHandler
from collections import OrderedDict
from logHandler import log

_ = lambda x: x
addonHandler.initTranslation()


class MLDescriber(BaseDescriber):
	name = b"azure"
	
	# Translators: Description of Online OCR Engine
	description = _("Microsoft Azure Image describer")
	
	def _get_supportedSettings(self):
		return [
			BaseDescriber.AccessTypeSetting(),
			BaseDescriber.LanguageSetting(),
			BaseDescriber.NumericSettings(
				"maxCandidates",
				_(u"Max number of candidates")
			),
			BaseDescriber.StringSettings(
				"region",
				# Translators: Label for engine settings
				_(u"Azure resource Region")
			),
			BaseDescriber.APIKeySetting(),
		
		]
	
	_api_key = ""
	
	_type_of_api_access = "free"
	
	maxHeight = 4200
	
	maxWidth = 4200
	
	maxSize = 4 * 1024 * 1024  # 4 mega bytes
	
	_region = ""
	
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
			return self.nvda_cn_domain
	
	def get_url(self):
		if self._use_own_api_key:
			return b"vision/v2.0/describe"
		else:
			return b"ocr/msdesc.php"
	
	def getPayload(self, jpegBytes):
		if self._use_own_api_key:
			fileName = b'img.png'
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
	
	_maxCandidates = 1
	
	def _get_maxCandidates(self):
		return self._maxCandidates
	
	def _set_maxCandidates(self, maxCandidates):
		self._maxCandidates = maxCandidates
	
	_language = b"en"
	
	def _get_language(self):
		return self._language
	
	def _set_language(self, language):
		self._language = language
	
	def _get_availableLanguages(self):
		languages = OrderedDict({
			# Translators: Text language for OCR
			b"zh": _(u"Simplified Chinese"),
			# Translators: Text language for OCR
			b"en": _(u"English"),
			# Translators: Text language for OCR
			b"ja": _(u"Japanese"),
			# Translators: Text language for OCR
			b"pt": _(u"Portuguese"),
			# Translators: Text language for OCR
			b"es": _(u"Spanish"),
		})
		return self.generate_string_settings(languages)
	
	def getFullURL(self):
		from six import string_types
		url = self.get_url()
		domain = self.get_domain()
		if self.useHttps:
			protocol = b"https:/"
		else:
			protocol = b"http:/"
		fullURL = b"/".join([
			protocol,
			domain,
			url
		])
		queryString = b"?language={0}&maxCandidates={1}".format(
			self._language,
			self._maxCandidates
		)
		fullURL = fullURL + queryString
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
			return False
	
	def convert_to_line_result_format(self, apiResult):
		from contentRecog import SimpleTextResult
		return SimpleTextResult(self.extract_text(apiResult))
	
	@staticmethod
	def extract_text(apiResult):
		words = []
		tags = apiResult["description"]["tags"]
		tagCode = _("Tags:")
		words.append(tagCode)
		for result in tags:
			words.append(result)
		captionsCode = _("Captions:")
		words.append(captionsCode)
		for captions in apiResult["description"]["captions"]:
			words.append(captions["text"])
		return u" ".join(words)

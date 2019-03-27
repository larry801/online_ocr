# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from __future__ import unicode_literals
from .. import onlineOCRHandler
from logHandler import log
from collections import OrderedDict
import addonHandler

_ = lambda x: x
addonHandler.initTranslation()


class CustomContentRecognizer(onlineOCRHandler.BaseRecognizer):
	api_domain = "api.ocr.space"
	api_url = "parse/image"

	@classmethod
	def check(cls):
		return True

	@staticmethod
	def extract_text(apiResult):
		lineResult = []
		resultSets = apiResult["ParsedResults"]
		for result in resultSets:
			lineResult.append(result["ParsedText"])
		log.io(lineResult)
		return u" ".join(lineResult)

	def convert_to_line_result_format(self, apiResult):
		lineResult = []
		resultSets = apiResult["ParsedResults"]
		for result in resultSets:
			for line in result["TextOverlay"]["Lines"]:
				currentLine = []
				for word in line['Words']:
					currentLine.append({
						"x": word["Left"],
						"y": word["Top"],
						"width": word["Width"],
						"height": word["Height"],
						"text": word["WordText"],
					})
				lineResult.append(currentLine)
		log.io(lineResult)
		return lineResult

	name = b"ocrSpace"

	# Translators: Description of Online OCR Engine
	description = _("OCR Space")

	_api_key = ""

	def _get_supportedSettings(self):
		return [
			CustomContentRecognizer.AccessTypeSetting(),
			CustomContentRecognizer.LanguageSetting(),
			# Translators: Label for OCR engine settings.
			CustomContentRecognizer.BooleanSetting("scale", _("Scale image for better quality")),
			# Translators: Label for OCR engine settings.
			CustomContentRecognizer.BooleanSetting("detectOrientation", _("Detect image orientation")),
			# Translators: Label for OCR engine settings.
			CustomContentRecognizer.BooleanSetting("isTable", _("Optimize for table recognition")),
			CustomContentRecognizer.APIKeySetting(),
		]

	_isTable = None

	def _get_isTable(self):
		return self._isTable

	def _set_isTable(self, isTable):
		self._isTable = isTable

	_detectOrientation = None

	def _get_detectOrientation(self):
		return self._detectOrientation

	def _set_detectOrientation(self, detectOrientation):
		self._detectOrientation = detectOrientation

	_scale = False

	def _get_scale(self):
		return self._scale

	def _set_scale(self, scale):
		self._scale = scale

	_language = "eng"

	def _get_language(self):
		return self._language

	def _set_language(self, language):
		self._language = language

	def _get_availableLanguages(self):
		languages = OrderedDict({
			# Translators: Text language for OCR
			"ara": _("Arabic"),
			# Translators: Text language for OCR
			"bul": _("Bulgarian"),
			# Translators: Text language for OCR
			"chs": _("Chinese(Simplified)"),
			# Translators: Text language for OCR
			"cht": _("Chinese(Traditional)"),
			# Translators: Text language for OCR
			"hrv": _("Croatian"),
			# Translators: Text language for OCR
			"cze": _("Czech"),
			# Translators: Text language for OCR
			"dan": _("Danish"),
			# Translators: Text language for OCR
			"dut": _("Dutch"),
			# Translators: Text language for OCR
			"eng": _("English"),
			# Translators: Text language for OCR
			"fin": _("Finnish"),
			# Translators: Text language for OCR
			"fre": _("French"),
			# Translators: Text language for OCR
			"ger": _("German"),
			# Translators: Text language for OCR
			"gre": _("Greek"),
			# Translators: Text language for OCR
			"hun": _("Hungarian"),
			# Translators: Text language for OCR
			"kor": _("Korean"),
			# Translators: Text language for OCR
			"ita": _("Italian"),
			# Translators: Text language for OCR
			"jpn": _("Japanese"),
			# Translators: Text language for OCR
			"pol": _("Polish"),
			# Translators: Text language for OCR
			"por": _("Portuguese"),
			# Translators: Text language for OCR
			"rus": _("Russian"),
			# Translators: Text language for OCR
			"slv": _("Slovenian"),
			# Translators: Text language for OCR
			"spa": _("Spanish"),
			# Translators: Text language for OCR
			"swe": _("Swedish"),
			# Translators: Text language for OCR
			"tur": _("Turkish")
		})
		return self.generate_string_settings(languages)

	def getPayload(self, png_string, text_only=False):
		base64_image = "data:image/png;base64," + png_string
		if text_only:
			isOverlayRequired = False
		else:
			isOverlayRequired = True
		payload = {
			b"base64Image": base64_image,
			b"filetype": "PNG",
			b"isTable": self.pyBool2json(self._isTable),
			b"detectOrientation": self.pyBool2json(self._detectOrientation),
			b"language": self._language,
			b"isOverlayRequired": self.pyBool2json(isOverlayRequired),
			b"scale": self.pyBool2json(self._scale),
		}
		if self._use_own_api_key:
			payload[b"apikey"] = self._api_key
		return payload

	def get_domain(self):
		if self._use_own_api_key:
			self.useHttps = True
			return self.api_domain
		else:
			self.useHttps = True
			return self.NVDAcnDomain

	def get_url(self):
		if self._use_own_api_key:
			return self.api_url
		else:
			return "ocr/ocrSpace.php"

	def process_api_result(self, result):
		import json
		apiResult = json.loads(result)
		try:
			code = apiResult["OCRExitCode"]
			return self.codeToErrorMessage[code]
		except KeyError:
			return False

	def getFullURL(self):
		fullURL = super(CustomContentRecognizer, self).getFullURL()
		from six import binary_type
		if isinstance(fullURL, binary_type):
			fullURL = fullURL.encode("utf-8")
		return fullURL

	codeToErrorMessage = {
		# Translators: Report when API error occurred
		3: _(u"Image parsing failed."),
		# Translators: Report when API error occurred
		4: _(u"A fatal error occurs during parsing )."),
	}

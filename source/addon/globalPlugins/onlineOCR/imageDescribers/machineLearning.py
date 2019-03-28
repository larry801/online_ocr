# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from ..onlineOCRHandler import BaseDescriber
import addonHandler
from collections import OrderedDict
from logHandler import log

_ = lambda x: x
addonHandler.initTranslation()


class MLDescriber(BaseDescriber):

	name = b"machineLearning"

	description = _(u"Machine Learning Engine by Oliver Edholm")

	@classmethod
	def check(cls):
		return True

	def _get_supportedSettings(self):
		return [
			MLDescriber.AccessTypeSetting(),
			MLDescriber.LanguageSetting(),
		]

	def convert_to_line_result_format(self, apiResult):
		return [[{
			"x": 0,
			"y": 0,
			"width": 1,
			"height": 1,
			"text": self.extract_text(apiResult),
		}]]
	
	_type_of_api_access = "own_key"

	def _get_availableAccesstypes(self):
		accessTypes = OrderedDict({
			# Translators: Label for OCR engine settings.
			"free": _("Use proxy on nvdacn.com"),
			# Translators: Label for OCR engine settings.
			"own_key": _("Access directly"),
		})
		return self.generate_string_settings(accessTypes)

	def get_url(self):
		if self._use_own_api_key:
			return b"function-2/interpret_image"
		else:
			return b"ocr/imageDesc.php"

	def get_domain(self):
		if self._use_own_api_key:
			return b"us-central1-icon-classifier.cloudfunctions.net"
		else:
			return self.NVDAcnDomain

	def getPayload(self, image):
		if self._use_own_api_key:
			return image
		else:
			return {
				"locale": self._language,
				"b64": image,
			}

	def process_api_result(self, result):
		pass

	@staticmethod
	def extract_text(apiResult):
		return apiResult["result"]

	_language = b"en"

	def _get_language(self):
		return self._language

	def _set_language(self, language):
		self._language = language

	def _get_availableLanguages(self):
		languages = OrderedDict({
			# Translators: Text language for image description
			b"zh-CN": _(u"Chinese Simplified"),
			# Translators: Text language for image description
			b"bg": _(u"Bulgarian"),
			# Translators: Text language for image description
			b"ca": _(u"Catalan"),
			# Translators: Text language for image description
			b"cs": _(u"Czech"),
			# Translators: Text language for image description
			b"da": _(u"Danish"),
			# Translators: Text language for image description
			b"de": _(u"German"),
			# Translators: Text language for image description
			b"el": _(u"Greek"),
			# Translators: Text language for image description
			b"en": _(u"English"),
			# Translators: Text language for image description
			b"es": _(u"Spanish"),
			# Translators: Text language for image description
			b"fi": _(u"Finnish"),
			# Translators: Text language for image description
			b"fr": _(u"French"),
			# Translators: Text language for image description
			b"id": _(u"Indonesian"),

			# Translators: Text language for image description
			b"hu": _(u"Hungarian"),
			# Translators: Text language for image description
			b"it": _(u"Italian"),
			# Translators: Text language for image description
			b"ja": _(u"Japanese"),
			# Translators: Text language for image description
			b"ko": _(u"Korean"),
			# Translators: Text language for image description
			b"lt": _(u"Lithuanian"),
			# Translators: Text language for image description
			b"lv": _(u"Latvian"),
			# Translators: Text language for image description
			b"nb_r": _(u"Norwegian"),
			# Translators: Text language for image description
			b"nl": _(u"Dutch"),
			# Translators: Text language for image description
			b"pl": _(u"Polish"),
			# Translators: Text language for image description
			b"pt": _(u"Portuguese"),
			# Translators: Text language for image description
			b"ro": _(u"Romanian"),
			# Translators: Text language for image description
			b"ru": _(u"Russian"),
			# Translators: Text language for image description
			b"sk": _(u"Slovak"),
			# Translators: Text language for image description
			b"sl": _(u"Slovenian"),
			# Translators: Text language for image description
			b"sr": _(u"Serbian"),
			# Translators: Text language for image description
			b"sv": _(u"Swedish"),
			# Translators: Text language for image description
			b"tg": _(u"Tajik"),
			# Translators: Text language for image description
			b"tr": _(u"Turkish"),
			# Translators: Text language for image description
			b"uk": _(u"Ukrainian"),
			# Translators: Text language for image description
			b"vi": _(u"Turkish"),
		})
		return self.generate_string_settings(languages)

	def sendRequest(self, callback, fullURL, payloads, headers=None):
		if self._use_own_api_key:
			fullURL = "https://us-central1-icon-classifier.cloudfunctions.net/function-2/interpret_image?locale={0}&b64={1}".format(
				self._language,
				payloads
			)
			from ..winHttp import doHTTPRequest
			from threading import Thread
			self.networkThread = Thread(
				target=doHTTPRequest,
				args=(
					callback,
					'GET',
					fullURL,
				)
			)
			self.networkThread.start()
		else:
			super(MLDescriber, self).sendRequest(
				callback,
				fullURL,
				payloads,
				headers=headers
			)

# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from . import azureAnalyse
import addonHandler
from collections import OrderedDict
from logHandler import log
from colors import RGB
from struct import unpack

_ = lambda x: x
addonHandler.initTranslation()


class CustomContentRecognizer(azureAnalyse.CustomContentRecognizer):
	name = b"azureAnalyseNarrator"

	# Translators: Description of Online OCR Engine
	description = _("Microsoft Narrator Image Analyser")

	def _get_supportedSettings(self):
		return [
			self.StringSettings(
				"detail",
				_(u"Detect Details")),
			self.CheckListSetting(
				"feature",
				# Translators: Label for engine settings
				_("Configure visual features to extract")
			),
		]

	@classmethod
	def check(cls):
		return False

	def getHTTPHeaders(self, imageData):
		return {
			b'Ocp-Apim-Subscription-Key': b'5365b76c568743ffa7ae0dc192e16879'
		}

	def get_domain(self):
		return b'narrator.azure-api.net'

	def get_url(self):
		return b'/captionapi/analyze'


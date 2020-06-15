# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from . import azure
import six
import addonHandler
from collections import OrderedDict
from logHandler import log
from colors import RGB
from struct import unpack

_ = lambda x: x
addonHandler.initTranslation()


class CustomContentRecognizer(azure.CustomContentRecognizer):
	name = b"azureAnalyse"
	
	# Translators: Description of Online OCR Engine
	description = _("Microsoft Azure Image Analyser")
	
	uploadBase64EncodeImage = False
	
	_feature = ["Tags", "Description"]
	
	def _get_feature(self):
		return self._feature
	
	def _set_feature(self, feature):
		self._feature = feature
	
	def _get_availableFeatures(self):
		return self.generate_string_settings(self.features)
	
	def _get_supportedSettings(self):
		return [
			self.AccessTypeSetting(),
			self.StringSettings(
				"detail",
				_(u"Detect Details")),
			self.CheckListSetting(
				"feature",
				# Translators: Label for engine settings
				_("Configure visual features to extract")
			),
			self.APIKeySetting(),
			self.StringSettings(
				"region",
				# Translators: Label for engine settings
				_(u"Azure resource Region")
			),
		]
	
	features = OrderedDict({
		# Translators: Description of visual features
		"Adult": _(u"Detect adult content."),
		# Translators: Description of visual features
		"Brands": _(u"Detects various brands within an image, including the approximate location. "),
		"Categories":
			# Translators: Description of visual features
			_(u"Categorizes image content according to a taxonomy defined in documentation."),
		"Description":
			# Translators: Description of visual features
			_(u"Describes the image content with a complete sentence in supported languages."),
		"Color":
			# Translators: Description of visual features
			_(u"Determines the accent color, dominant color, and whether an image is black&white."),
		"Tags":
			# Translators: Description of visual features
			_(u"Tags the image with a detailed list of words related to the image content."),
		"Faces":
			# Translators: Description of visual features
			_(u"Detects if faces are present. If present, generate coordinates, gender and age."),
		"ImageType":
			# Translators: Description of visual features
			_(u"Detects if image is clip art or a line drawing."),
		"Objects": _(
			# Translators: Description of visual features
			"Detects various objects within an image, including the approximate location. The Objects argument is only available in English.")
	})
	
	def getFeatures(self):
		visualFeatures = []
		for i in self._feature:
			visualFeatures.append(i)
		return str(",".join(visualFeatures))
	
	@classmethod
	def check(cls):
		return True
	
	_detail = "Celebrities,Landmarks"
	
	def _get_detail(self):
		return self._detail
	
	def _set_detail(self, detail):
		self._detail = detail
	
	def _get_availableDetails(self):
		details = OrderedDict({
			# Translators: Regions for azure ocr resource
			"Celebrities": _(u"identifies celebrities if detected in the image."),
			"Landmarks": _(u"identifies landmarks if detected in the image."),
			"Celebrities,Landmarks": _(u"identifies landmarks and celebrities if detected in the image."),
		})
		return self.generate_string_settings(details)
	
	def get_url(self):
		if self._use_own_api_key:
			return b"vision/v2.0/analyze"
		else:
			return b"ocr/msAnalyse.php"
	
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
		if six.PY2:
			queryString = b"?visualFeatures={2}&language={0}&details={1}".format(
				self._language,
				self._detail,
				self.getFeatures(),
			)
		else:
			queryString = "?visualFeatures={2}&language={0}&details={1}".format(
				self._language,
				self._detail,
				self.getFeatures(),
			)
			queryString = queryString.encode('utf-8')
		fullURL = fullURL + queryString
		# Unicode URL cause urllib3 to decode raw image data as if they were unicode.
		if isinstance(fullURL, string_types):
			if not isinstance(fullURL, str):
				log.io("Decode URL to str")
				return str(fullURL)
			else:
				return fullURL
	
	def extract_text(self, apiResult):
		entries = []
		if "categories" in apiResult:
			# Translators: Result label for azure image analyzer
			entries.append(_(u"Categories:"))
			# Translators: Result label for azure image analyzer
			entries.append("{number} categories detected.".format(
				number=len(apiResult["categories"])
			))
			for category in apiResult["categories"]:
				entries.append(category["name"])
				if "detail" in category:
					if "celebrities" in category["detail"]:
						# Translators: Result label for azure image analyzer
						entries.append("{number} celebrities detected.".format(
							number=len(category["detail"]["celebrities"])
						))
						for celebrity in category["detail"]["celebrities"]:
							entries.append(celebrity["name"])
					if "landmarks" in category["detail"]:
						# Translators: Result label for azure image analyzer
						entries.append("{number} landmarks detected.".format(
							number=len(category["detail"]["landmarks"])
						))
						for landmark in category["detail"]["landmarks"]:
							entries.append(landmark["name"])
		if "adult" in apiResult:
			# Translators: Result label for azure image analyzer
			entries.append(_(u"Adult content detection:"))
			if apiResult["adult"]["isAdultContent"]:
				# Translators: Result label for azure image analyzer
				entries.append(_(u"This image contains adult content"))
			else:
				# Translators: Result label for azure image analyzer
				entries.append(_(u"This image does not contain adult content"))
			if apiResult["adult"]["isRacyContent"]:
				# Translators: Result label for azure image analyzer
				entries.append(_(u"This image contains racy content"))
			else:
				# Translators: Result label for azure image analyzer
				entries.append(_(u"This image does not contain racy content"))
		if "color" in apiResult:
			# Translators: Result label for azure image analyzer
			entries.append(_(u"Color detection:"))
			# Translators: Result label for azure image analyzer
			colorMsg = _(
				u"Dominant foreground color is {foreGroundColor}.\n Dominant background color is {backGroundColor}.")
			entries.append(colorMsg.format(
				foreGroundColor=apiResult["color"]["dominantColorForeground"],
				backGroundColor=apiResult["color"]["dominantColorBackground"],
			))
			hexAccentColor = apiResult["color"]["accentColor"]
			r, g, b = unpack("BBB", hexAccentColor.decode("hex"))
			rgbAccentColor = RGB(r, g, b)
			# Translators: Result label for azure image analyzer
			entries.append(_("Accent color is {color}, its hex code is {hex}.".format(
				hex=apiResult["color"]["accentColor"],
				color=rgbAccentColor.name
			)))
			# Translators: Result label for azure image analyzer
			entries.append(_("Dominant colors:"))
			for color in apiResult["color"]["dominantColors"]:
				entries.append(color)
			if apiResult["color"]["isBWImg"]:
				# Translators: Result label for azure image analyzer
				entries.append(_(u"The image is black and white."))
			else:
				# Translators: Result label for azure image analyzer
				entries.append(_(u"The image is not black and white."))
		if "tags" in apiResult and len(apiResult["tags"]) > 0:
			# Translators: Result label for azure image analyzer
			entries.append("{number} tags detected.".format(
				number=len(apiResult["tags"])
			))
			for tag in apiResult["tags"]:
				entries.append(tag["name"])
		if "imageType" in apiResult:
			# Translators: Result label for azure image analyzer
			entries.append(_(u"Detected image type:"))
			if apiResult["imageType"]["clipArtType"] == 0:
				# Translators: Result label for azure image analyzer
				entries.append(_(u"The image is not a clip-art."))
			elif apiResult["imageType"]["clipArtType"] == 1:
				# Translators: Result label for azure image analyzer
				entries.append(_(u"Cannot tell whether is image is clip-art"))
			elif apiResult["imageType"]["clipArtType"] == 2:
				# Translators: Result label for azure image analyzer
				entries.append(_(u"The image is Normal-clip-art"))
			elif apiResult["imageType"]["clipArtType"] == 3:
				# Translators: Result label for azure image analyzer
				entries.append(_(u"The image is Good-clip-art"))
			if apiResult["imageType"]["lineDrawingType"] == 1:
				# Translators: Result label for azure image analyzer
				entries.append(_(u"The image is a lineDrawing"))
			else:
				# Translators: Result label for azure image analyzer
				entries.append(_(u"The image is not a lineDrawing"))
		if "description" in apiResult:
			# Translators: Result label for azure image analyzer
			entries.append("{number} results available.".format(
				number=len(apiResult["description"]["captions"])
			))
			for desc in apiResult["description"]["captions"]:
				entries.append(desc["text"])
		if "objects" in apiResult and len(apiResult["objects"]) > 0:
			# Translators: Result label for azure image analyzer
			entries.append(_(u"{number} objects detected.".format(
				number=len(apiResult["objects"])
			)))
			resultSets = apiResult["objects"]
			if self.text_result:
				for result in resultSets:
					entries.append(result["object"])
		if "brands" in apiResult and len(apiResult["brands"]) > 0:
			# Translators: Result label for azure image analyzer
			entries.append(_(u"{number} brands detected.".format(
				number=len(apiResult["brands"])
			)))
			resultSets = apiResult["brands"]
			if self.text_result:
				for result in resultSets:
					entries.append(result["name"])
		if "faces" in apiResult and len(apiResult["faces"]) > 0:
			# Translators: Result label for azure image analyzer
			entries.append(_(u"{number} faces detected.".format(
				number=len(apiResult["faces"])
			)))
			if self.text_result:
				resultSets = apiResult["faces"]
				for result in resultSets:
					entries.append(
						self.getFaceDescription(result)
					)
		return u"\r\n".join(entries)
	
	def convert_to_line_result_format(self, apiResult):
		lineResult = [[{
			"x": 0,
			"y": 0,
			"width": 1,
			"height": 1,
			"text": self.extract_text(apiResult),
		}]]
		if "categories" in apiResult:
			for category in apiResult["categories"]:
				if "detail" in category:
					entries = []
					if "celebrities" in category["detail"]:
						for result in category["detail"]["celebrities"]:
							entries.append({
								"x": result["faceRectangle"]["x"],
								"y": result["faceRectangle"]["y"],
								"width": result["faceRectangle"]["w"],
								"height": result["faceRectangle"]["h"],
								"text": result["name"]
							})
					if len(entries) > 0:
						lineResult.append(entries)
		if "objects" in apiResult and len(apiResult["objects"]) > 0:
			objectResult = []
			resultSets = apiResult["objects"]
			for result in resultSets:
				objectResult.append({
					"x": result["rectangle"]["x"],
					"y": result["rectangle"]["y"],
					"width": result["rectangle"]["w"],
					"height": result["rectangle"]["h"],
					"text": result["object"]
				})
			lineResult.append(objectResult)
		if "brands" in apiResult and len(apiResult["brands"]) > 0:
			brandResult = []
			resultSets = apiResult["brands"]
			for result in resultSets:
				brandResult.append({
					"x": result["rectangle"]["x"],
					"y": result["rectangle"]["y"],
					"width": result["rectangle"]["w"],
					"height": result["rectangle"]["h"],
					"text": result["name"]
				})
			lineResult.append(brandResult)
		if "faces" in apiResult and len(apiResult["faces"]) > 0:
			faceResult = []
			resultSets = apiResult["faces"]
			for result in resultSets:
				faceResult.append({
					"x": result["faceRectangle"]["x"],
					"y": result["faceRectangle"]["y"],
					"width": result["faceRectangle"]["w"],
					"height": result["faceRectangle"]["h"],
					"text": self.getFaceDescription(result)
				})
			lineResult.append(faceResult)
		log.io(lineResult)
		return lineResult
	
	@staticmethod
	def getFaceDescription(faceObj):
		entries = [
			# Translators: Result label for azure image analyzer
			_("Face:"),
			# Translators: Result label for azure image analyzer
			_("Age:"),
			str(faceObj["age"]),
			# Translators: Result label for azure image analyzer
			_("Gender:"),
			faceObj["gender"]
		]
		return " ".join(entries)

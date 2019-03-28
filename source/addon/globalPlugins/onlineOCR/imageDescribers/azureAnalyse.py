# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from . import azure
import addonHandler
from collections import OrderedDict
from logHandler import log
from colors import RGB
from struct import unpack

_ = lambda x: x
addonHandler.initTranslation()


class MLDescriber(azure.MLDescriber):
	name = b"azureAnalyse"
	
	# Translators: Description of Online OCR Engine
	description = _("Microsoft Azure Image Analyser")
	
	uploadBase64EncodeImage = False
	
	_adult = False
	
	def _get_adult(self):
		return self._adult
	
	def _set_adult(self, adult):
		self._adult = adult
	
	_faces = False
	
	def _get_faces(self):
		return self._faces
	
	def _set_faces(self, faces):
		self._faces = faces
	
	_brands = False
	
	def _get_brands(self):
		return self._brands
	
	def _set_brands(self, brands):
		self._brands = brands
	
	_categories = False
	
	def _get_categories(self):
		return self._categories
	
	def _set_categories(self, categories):
		self._categories = categories
	
	_imageDescription = True
	
	def _get_imageDescription(self):
		return self._imageDescription
	
	def _set_imageDescription(self, imageDescription):
		self._imageDescription = imageDescription
	
	_color = False
	
	def _get_color(self):
		return self._color
	
	def _set_color(self, color):
		self._color = color
	
	_tags = False
	
	def _get_tags(self):
		return self._tags
	
	def _set_tags(self, tags):
		self._tags = tags
	
	_imageType = False
	
	def _get_imageType(self):
		return self._imageType
	
	def _set_imageType(self, imageType):
		self._imageType = imageType
	
	_imageObjects = False
	
	def _get_imageObjects(self):
		return self._imageObjects
	
	def _set_imageObjects(self, imageObjects):
		self._imageObjects = imageObjects
	
	def _get_supportedSettings(self):
		return [
			MLDescriber.AccessTypeSetting(),
			
			MLDescriber.StringSettings(
				"detail",
				_(u"Detect Details")),
			MLDescriber.BooleanSetting(
				"adult",
				_(u"Detect adult content."),
			), MLDescriber.BooleanSetting(
				"brands",
				_(u"Detects various brands within an image, including the approximate location. ")
			), MLDescriber.BooleanSetting(
				"categories",
				_(u"Categorizes image content according to a taxonomy defined in documentation.")
			), MLDescriber.BooleanSetting(
				"imageDescription",
				_(u"Describes the image content with a complete sentence in supported languages.")
			), MLDescriber.BooleanSetting(
				"color",
				_(u"Determines the accent color, dominant color, and whether an image is black&white.")
			), MLDescriber.BooleanSetting(
				"tags",
				_(u"Tags the image with a detailed list of words related to the image content.")
			), MLDescriber.BooleanSetting(
				"faces",
				_(u"Describes the image content with a complete sentence in supported languages.")
			), MLDescriber.BooleanSetting(
				"imageType",
				_(u"Detects if image is clip art or a line drawing.")
			), MLDescriber.BooleanSetting(
				"imageObjects",
				_(
					u"Detects various objects within an image, including the approximate location. The Objects argument is only available in English.")
			),
			
			MLDescriber.APIKeySetting(),
			MLDescriber.StringSettings(
				"region",
				# Translators: Label for engine settings
				_(u"Azure resource Region")
			),
		]
	
	@classmethod
	def check(cls):
		return True
	
	_detail = ""
	
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
	
	def _get_visualFeature(self):
		features = []
		if self._adult:
			features.append(b"Adult")
		if self._brands:
			features.append(b"Brands")
		if self._categories:
			features.append(b"Categories")
		if self._color:
			features.append(b"Color")
		if self._imageDescription:
			features.append(b"Description")
		if self._faces:
			features.append(b"Faces")
		if self._imageType:
			features.append(b"ImageType")
		if self._imageObjects:
			features.append(b"Objects")
		if self._tags:
			features.append(b"Tags")
		if len(features) <= 0:
			features.append(b"Description")
			features.append(b"Tags")
		return b','.join(features)
	
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
		queryString = b"?visualFeatures={2}&language={0}&details={1}".format(
			self._language,
			self._detail,
			self.visualFeature,
		)
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
			# Translators: Result from azure image analyzer
			entries.append(_(u"Categories:"))
			entries.append("\n")
			for cats in apiResult["categories"]:
				entries.append(cats["name"])
				entries.append("\n")
		if "adult" in apiResult:
			# Translators: Result from azure image analyzer
			entries.append(_(u"Adult content detection:"))
			entries.append("\n")
			if apiResult["adult"]["isAdultContent"]:
				# Translators: Result from azure image analyzer
				entries.append(_(u"This image contains adult content"))
			else:
				# Translators: Result from azure image analyzer
				entries.append(_(u"This image does not contain adult content"))
			entries.append("\n")
			if apiResult["adult"]["isRacyContent"]:
				# Translators: Result from azure image analyzer
				entries.append(_(u"This image contains racy content"))
			else:
				# Translators: Result from azure image analyzer
				entries.append(_(u"This image does not contain racy content"))
			entries.append("\n")
		if "color" in apiResult:
			# Translators: Result from azure image analyzer
			entries.append(_(u"Color detection:"))
			entries.append("\n")
			# Translators: Result from azure image analyzer
			colorMsg = _(
				u"Dominant foreground color is {foreGroundColor}.\n Dominant background color is {backGroundColor}.")
			entries.append(colorMsg.format(
				foreGroundColor=apiResult["color"]["dominantColorForeground"],
				backGroundColor=apiResult["color"]["dominantColorBackground"],
			))
			entries.append("\n")
			hexAccentColor = apiResult["color"]["accentColor"]
			r, g, b = unpack("BBB", hexAccentColor.decode("hex"))
			rgbAccentColor = RGB(r, g, b)
			# Translators: Result from azure image analyzer
			entries.append(_("Accent color is {color}, its hex code is {hex}.".format(
				hex=apiResult["color"]["accentColor"],
				color=rgbAccentColor.name
			)))
			entries.append("\n")
			# Translators: Result from azure image analyzer
			entries.append(_("Dominant colors:"))
			entries.append("\n")
			for color in apiResult["color"]["dominantColors"]:
				entries.append(color)
				entries.append("\n")
			if apiResult["color"]["isBWImg"]:
				# Translators: Result from azure image analyzer
				entries.append(_(u"The image is black and white."))
			else:
				# Translators: Result from azure image analyzer
				entries.append(_(u"The image is not black and white."))
			entries.append("\n")
		if "tags" in apiResult and len(apiResult["tags"]) > 0:
			# Translators: Result from azure image analyzer
			entries.append(_(u"Tags:"))
			entries.append("\n")
			for tag in apiResult["tags"]:
				entries.append(tag["name"])
				entries.append("\n")
		if "imageType" in apiResult:
			# Translators: Result from azure image analyzer
			entries.append(_(u"Detected image type:"))
			entries.append("\n")
			if apiResult["imageType"]["clipArtType"] == 0:
				# Translators: Result from azure image analyzer
				entries.append(_(u"The image is not a clip-art."))
			elif apiResult["imageType"]["clipArtType"] == 1:
				# Translators: Result from azure image analyzer
				entries.append(_(u"Cannot tell whether is image is clip-art"))
			elif apiResult["imageType"]["clipArtType"] == 2:
				# Translators: Result from azure image analyzer
				entries.append(_(u"The image is Normal-clip-art"))
			elif apiResult["imageType"]["clipArtType"] == 3:
				# Translators: Result from azure image analyzer
				entries.append(_(u"The image is Good-clip-art"))
			entries.append("\n")
			if apiResult["imageType"]["lineDrawingType"] == 1:
				# Translators: Result from azure image analyzer
				entries.append(_(u"The image is a lineDrawing"))
			else:
				# Translators: Result from azure image analyzer
				entries.append(_(u"The image is not a lineDrawing"))
			entries.append("\n")
		if "description" in apiResult:
			# Translators: Result from azure image analyzer
			entries.append(_(u"Descriptions of this image:"))
			entries.append("\n")
			for desc in apiResult["description"]["captions"]:
				entries.append(desc["text"])
				entries.append("\n")
		if "objects" in apiResult and len(apiResult["objects"]) > 0:
			# Translators: Result from azure image analyzer
			entries.append(_(u"{number} objects detected.".format(
				number=len(apiResult["objects"])
			)))
			entries.append("\n")
			resultSets = apiResult["objects"]
			if self.text_result:
				for result in resultSets:
					entries.append(result["object"])
					entries.append("\n")
		if "brands" in apiResult and len(apiResult["brands"]) > 0:
			# Translators: Result from azure image analyzer
			entries.append(_(u"{number} brands detected.".format(
				number=len(apiResult["brands"])
			)))
			entries.append("\n")
			resultSets = apiResult["brands"]
			if self.text_result:
				for result in resultSets:
					entries.append(result["name"])
					entries.append("\n")
		if "faces" in apiResult and len(apiResult["faces"]) > 0:
			# Translators: Result from azure image analyzer
			entries.append(_(u"{number} faces detected.".format(
				number=len(apiResult["faces"])
			)))
			entries.append("\n")
			if self.text_result:
				resultSets = apiResult["faces"]
				for result in resultSets:
					entries.append(
						self.getFaceDescription(result)
					)
					entries.append("\n")
		return u" ".join(entries)
	
	def convert_to_line_result_format(self, apiResult):
		lineResult = [[{
			"x": 0,
			"y": 0,
			"width": 1,
			"height": 1,
			"text": self.extract_text(apiResult),
		}]]
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
			# Translators: Result from azure image analyzer
			_("Face:"),
			# Translators: Result from azure image analyzer
			_("Age:"),
			str(faceObj["age"]),
			# Translators: Result from azure image analyzer
			_("Gender:"),
			faceObj["gender"]
		]
		return " ".join(entries)

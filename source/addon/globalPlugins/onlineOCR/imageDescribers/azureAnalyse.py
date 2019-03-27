# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from . import azure
import addonHandler
from collections import OrderedDict
from logHandler import log

_ = lambda x: x
addonHandler.initTranslation()


class MLDescriber(azure.MLDescriber):
	name = b"azureAnalyse"
	
	# Translators: Description of Online OCR Engine
	description = _("Microsoft Azure Image Analyser")
	
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
			), MLDescriber.APIKeySetting(),
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
			features.append("Adult")
		if self._brands:
			features.append("Brands")
		if self._categories:
			features.append("Categories")
		if self._color:
			features.append("Color")
		if self._imageDescription:
			features.append("Description")
		if self._faces:
			features.append("Faces")
		if self._imageType:
			features.append("ImageType")
		if self._imageObjects:
			features.append("Objects")
		if self._tags:
			features.append("Tags")
		if len(features) <= 0:
			features.append("Description")
			features.append("Tags")
		return ','.join(features)
		
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
			self._maxCandidates,
			self.visualFeature,
		)
		fullURL = fullURL + queryString
		# Unicode URL cause urllib3 to decode raw image data as if they were unicode.
		if isinstance(fullURL, string_types):
			if not isinstance(fullURL, str):
				fullURL = fullURL.decode('utf8')
		return fullURL

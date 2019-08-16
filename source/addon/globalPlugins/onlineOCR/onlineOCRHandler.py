# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# urllib3 used in this file is Copyright (c) 2008-2019 Andrey Petrov and contributors under MIT license.
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

from abc import ABC
from threading import Thread

import gui
import six
from configobj import Section
from io import BytesIO
import json
from contentRecog import LinesWordsResult, ContentRecognizer, RecogImageInfo
import base64
import wx
import config
from six import iterkeys
from gui.guiHelper import BoxSizerHelper
import addonHandler
from logHandler import log
import ui
from collections import OrderedDict
from gui.settingsDialogs import SettingsPanel
from six.moves.urllib_parse import urlencode
from abstractEngine import AbstractEngineHandler, AbstractEngineSettingsPanel, AbstractEngine
import imageDescribers
import contentRecognizers
from PIL import Image
from PIL.Image import LANCZOS
_ = lambda x: x
addonHandler.initTranslation()

COLUMN_SPLIT_TYPES = [
	# Translators: Column split mode shown in online image describer settings dialog.
	("no", _("Do not split")),
	("two", _("Split to two columns")),
	("three", _("Split to three columns")),
]

ENGINE_TYPES = [
	# Translators: One of the engine types in online OCR settings panel.
	("onlineOCR", _(u"Online OCR Engines")),
	("onlineImageDescriber", _(u"Online Image Describer Engines")),
	("win10OCR", _(u"Windows 10 Offline OCR Engine")),
]

TARGET_TYPES = [
	# Translators: One of the proxy types in online OCR settings panel.
	("wholeDesktop", _(u"The whole desktop")),
	# Translators: One of the proxy types in online OCR settings panel.
	("clipboardImage", _(u"Image data or image file in clipboard")),
	# Translators: One of the proxy types  in online OCR settings panel.
	("foreGroundWindow", _(u"Current foreground window")),
	("navigatorObject", _(u"Navigator object")),
	("clipboardURL", _(u"Image path or url in clipboard")),
]


class BaseRecognizer(ContentRecognizer, AbstractEngine, ABC):
	"""
	Abstract base BaseRecognizer
	"""
	
	# Translators: Description of Online OCR Engine
	description = ""
	isURLSupported = False
	NVDAcnDomain = b"www.nvdacn.com"
	configSectionName = "onlineOCR"
	networkThread = None  # type: Thread
	useHttps = True
	
	pixels = None
	originalImage = None
	onResult = None
	imageInfo = None
	_compression = 9
	
	def _get_compression(self):
		return self._compression
	
	def _set_compression(self, compression):
		self._compression = compression
	
	_quality = 75
	
	def _get_quality(self):
		return self._quality
	
	def _set_quality(self, quality):
		self._quality = quality
	
	@classmethod
	def ImageQualitySetting(cls):
		return BaseRecognizer.NumericSettings(
			"quality",
			# Translators: Label for image quality settings in settings panel
			_("Upload image quality")
		)
	
	_api_key = ""
	
	_api_secret_key = ""
	
	_appID = ""
	
	def _get_appID(self):
		return self._appID
	
	def _set_appID(self, appID):
		self._appID = appID
	
	text_result = False
	
	minHeight = 50
	
	maxHeight = 4096
	
	minWidth = 50
	
	maxWidth = 4096
	
	maxPixels = 10000000
	
	maxSize = 4 * 1024 * 1024  # 4 mega bytes
	
	@classmethod
	def CopyToClipboardSetting(cls):
		return BaseRecognizer.BooleanSetting(
			"clipboard",
			# Translators: Label in settings dialog
			_(u"Copy result text to clipboard after recognition")
		)
	
	_clipboard = False
	
	def _get_clipboard(self):
		return self._clipboard
	
	def _set_clipboard(self, clipboard):
		self._clipboard = clipboard
	
	@staticmethod
	def pyBool2json(boolean):
		"""
		Convert python boolean to "true" or "false"
		@param boolean:
		@type boolean: bool
		@return:
		@rtype: bytes
		"""
		if boolean:
			return b"true"
		else:
			return b"false"
	
	def _get_supportedSettings0(self):
		raise NotImplementedError
	
	def _get_apiKey(self):
		return self._api_key
	
	def _set_apiKey(self, key):
		self._api_key = key
	
	def _get_apiSecret(self):
		return self._api_secret_key
	
	def _set_apiSecret(self, key):
		self._api_secret_key = key
	
	def json_endpoint(self, url, payloads):
		json_data = self.convert_to_json(
			self.post_to_url(url, payloads)
		)
		return json_data
	
	@staticmethod
	def capture_again(imageInfo):
		"""
		Capture image using ImageGrab instead of bitmap
		@param imageInfo: Information about the image for recognition.
		@type imageInfo: L{RecogImageInfo}
		@return: Captured image
		@rtype: L{Image}
		"""
		from PIL import ImageGrab
		img = ImageGrab.grab(bbox=(
			imageInfo.screenLeft,
			imageInfo.screenTop,
			imageInfo.screenLeft + imageInfo.recogWidth,
			imageInfo.screenTop + imageInfo.recogHeight
		))
		img.resize((
			imageInfo.recogWidth * imageInfo.resizeFactor,
			imageInfo.recogHeight * imageInfo.resizeFactor
		))
		return img
	
	def convert_to_line_result_format(self, apiResult):
		"""
		Convert API result to NVDA compatible ones
		@param apiResult:
		@type apiResult: dict
		@return: Recognition result
		@rtype: L{LinesWordsResult}
		"""
		raise NotImplementedError
	
	@property
	def _use_own_api_key(self):
		if self._type_of_api_access == "own_key":
			return True
		else:
			return False
	
	@staticmethod
	def post_to_url(url, payloads):
		# noinspection PyUnresolvedReferences
		import urllib3
		http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=10, read=100))
		response = http.request("POST", url=url, fields=payloads)
		text = response.data
		return text
	
	@staticmethod
	def form_encode(options):
		"""
		generate www-form
		@param options: request parameters
		@type options: dict
		@return:
		"""
		encoded_option = ""
		key_sequence = sorted(iterkeys(options), reverse=False)
		for k in key_sequence:
			query = "&" + urlencode({
				k: options[k]
			})
			encoded_option += query
		payload = encoded_option[1:]
		if config.conf["onlineOCR"]["verboseDebugLogging"]:
			log.io(payload)
		return payload
	
	@staticmethod
	def convert_to_json(data):
		return json.loads(data)
	
	def get_url(self):
		raise NotImplementedError
	
	def get_domain(self):
		raise NotImplementedError
	
	def getFullURL(self):
		"""

		@return:
		@rtype:
		"""
		url = self.get_url()
		if six.PY3 and isinstance(url, str):
			url = url.encode('utf-8')
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
		return fullURL
	
	def getPayload(self, image):
		"""
		Get payload from image and engine settings
		@param image: ImageContent to convert
		@type image: str
		@return: A dictionary for urllib3
		"""
		raise NotImplementedError
	
	# noinspection PyBroadException
	@staticmethod
	def processCURLError(result):
		"""
		process error message from php curl
		@param result:
		@type result:
		@return:
		@rtype: bool or str
		"""
		try:
			import json
			apiResult = json.loads(result)
			code = apiResult["errmsg"]
			if code in range(1, 61):
				log.error(result)
				# Translators: Reported when error occurred during image conversion
				errorMessage = _(u"Error occurred on Proxy server. Please try again or use your own API key instead")
				return errorMessage
		except (KeyError, ValueError):
			return False
	
	resizeUpperLimit = 5
	resizeLowerLimit = 0.2
	asymptoticResizeFactor = 0.8
	
	def checkAndResizeImage(self, image):
		"""
		Check Image Size to meet requirement of API
		@param image:
		@type image: PIL.Image.Image
		@return: Resized image
		@rtype: PIL.Image.Image or bool
		"""
		isImageValid = True
		width = image.width
		height = image.height
		msg = u"Original size\nwidth:\n{w}\nheight:\n{h}".format(
			w=width,
			h=height
		)
		if width >= height:
			aspectRatio = width / height
		else:
			aspectRatio = height / width
		widthStatus = 0
		heightStatus = 0
		if aspectRatio > (self.maxHeight / self.minWidth):
			isImageValid = False
			# Translators: Reported when error occurred during image resizing
			errorMsg = _(u"Image aspect ratio is too big. Cannot resize properly for this engine.")
		else:
			if self.minWidth <= width <= self.maxWidth:
				widthResizeFactor = 1
			elif width < self.minWidth:
				widthResizeFactor = (float(self.minWidth) / width) + 1
			else:
				widthResizeFactor = (float(self.maxWidth) / width) + 1
			if self.minHeight <= height <= self.maxHeight:
				heightResizeFactor = 1
			elif height < self.minHeight:
				heightResizeFactor = (float(self.minHeight) / height) + 1
			else:
				heightResizeFactor = (float(self.maxHeight) / height) + 1
			msg += u"\nwidthResizeFactor:\n{0}\nheightResizeFactor:\n{1}".format(
				widthResizeFactor,
				heightResizeFactor
			)
			# Translators: Reported when error occurred during image conversion
			errorMsg = _(u"Error occurred when converting images")
			
			if widthResizeFactor >= self.resizeUpperLimit:
				# Translators: Reported when image size is not valid
				errorMsg = _(u"Image width is too big for this engine")
				isImageValid = False
			
			if heightResizeFactor <= self.resizeLowerLimit:
				isImageValid = False
				# Translators: Reported when error occurred during image conversion
				errorMsg = _(u"Image height is too small for this engine")
			
			if widthResizeFactor >= self.resizeUpperLimit:
				# Translators: Reported when image size is not valid
				errorMsg = _(u"Image width is too big for this engine")
				isImageValid = False
			if heightResizeFactor <= self.resizeLowerLimit:
				isImageValid = False
				# Translators: Reported when error occurred during image conversion
				errorMsg = _(u"Image height is too small for this engine")
		self.imageInfo.resizeFactor = int(max(widthResizeFactor, heightResizeFactor))
		if isImageValid:
			image = self.getResizedImage()
			width = image.width
			height = image.height
			msg += u"\nSize after resizing\nwidth:\n{w}\nheight:\n{h}".format(
				w=width,
				h=height
			)
			log.io(msg)
			if width * height > self.maxPixels:
				pixelCount = image.width * image.height
				while pixelCount >= self.maxPixels and image.width >= self.minWidth and image.height >= self.minHeight:
					self.imageInfo.resizeFactor = self.imageInfo.resizeFactor * self.asymptoticResizeFactor
					image = self.getResizedImage()
					if config.conf["onlineOCR"]["verboseDebugLogging"]:
						msg = "newWidth\n{0}\nnewHeight\n{1}\npixelCount\n{2}".format(
							image.width,
							image.height,
							pixelCount
						)
						log.io(msg)
				if image.width * image.height > self.maxPixels:
					isImageValid = False
					# Translators: Reported when error occurred during image resizing
					ui.message(_(u"Image has too many pixels."))
					return False
				else:
					return self.getResizedImage()
			else:
				return self.getResizedImage()
		else:
			log.io(msg)
			ui.message(errorMsg)
			return False
	
	def getHTTPHeaders(self):
		"""
		Generate HTTP Header for request
		@return:
		@rtype:
		"""
		return {}
	
	def getConvertedImage(self, pixels, imageInfo):
		"""
		Convert RGBQUAD image to PIL format
		@param pixels:
		@type pixels:
		@param imageInfo:
		@return:
		@rtype: PIL.Image.Image
		"""
		width = imageInfo.recogWidth
		height = imageInfo.recogHeight
		img = Image.frombytes("RGBX", (width, height), pixels, "raw", "BGRX")
		img = img.convert("RGB")
		self.originalImage = img
		return img
	
	def getResizedImage(self):
		"""
		Get resized image object for upload
		@return: resized image
		@rtype: PIL.Image.Image
		"""
		return self.originalImage.resize(
			(
				int(self.imageInfo.recogWidth * self.imageInfo.resizeFactor),
				int(self.imageInfo.recogHeight * self.imageInfo.resizeFactor)
			),
			resample=LANCZOS
		)
	
	def getPayloadForHyperLink(self, url):
		raise NotImplementedError
	
	def recognizeHyperLink(self, link, onResult):
		"""
		Setup data for recognition then send request
		@param link:
		@param onResult: Result callback for result viewer
		@return: None
		"""
		if self.networkThread:
			# Translators: Error message
			ui.message(_(u"There is another recognition ongoing. Please wait."))
			return
		
		payloads = self.getPayloadForHyperLink(link)
		fullURL = self.getFullURL()
		headers = self.getHTTPHeaders()
		
		if config.conf["onlineOCR"]["verboseDebugLogging"]:
			log.io(type(fullURL))
			msg = u"{0}\n{1}\n{2}".format(
				fullURL,
				headers,
				payloads,
			)
			log.io(msg)
		self.sendRequest(self.callback, fullURL, payloads, headers)
	
	@staticmethod
	def showMessageInNetworkThread(message):
		wx.CallAfter(ui.message, message)
		
	@staticmethod
	def showBrowseableMessageInNetworkThread(message):
		# Translators: the Title of recognition result pop up window.
		wx.CallAfter(ui.browseableMessage, message, _(u"Image recognition result"))

	def cleanUp(self):
		self.onResult = None
		self.imageInfo = None
		self.originalImage = None
		self.networkThread = None
	
	def callback(self, result):
		if not self.networkThread:
			# Recognition has been cancelled
			return
		# Translators: Message added before recognition result
		# when user do not use result viewer
		result_prefix = _(u"Recognition result:")
		# Network error occurred
		if not result:
			self.cleanUp()
			return
		if not self._use_own_api_key:
			curl_error_message = self.processCURLError(result)  # type: str
			if curl_error_message:
				self.showMessageInNetworkThread(curl_error_message)
				self.cleanUp()
				return
		apiErrorMessage = self.process_api_result(result)  # type: str
		if apiErrorMessage:
			self.showMessageInNetworkThread(apiErrorMessage)
			self.cleanUp()
			return
		try:
			result = self.convert_to_json(result)
		except ValueError as e:
			# Translators: Reported when api result is invalid
			self.showMessageInNetworkThread(_(u"Recognition failed. Result is invalid."))
			self.cleanUp()
			return
		
		try:
			ocrResult = self.extract_text(result)
			if ocrResult.isspace():
				# Translators: Reported when recognition result is empty
				self.showMessageInNetworkThread(_(u"Recognition result is blank. There may be no text on this image."))
				self.cleanUp()
				return
			resultText = result_prefix + ocrResult
			if config.conf["onlineOCR"]["copyToClipboard"]:
				import api
				api.copyToClip(resultText)
			if self.text_result:
				if config.conf["onlineOCR"]["useBrowseableMessage"]:
					self.showBrowseableMessageInNetworkThread(resultText)
				else:
					self.showMessageInNetworkThread(resultText)
			else:
				self.onResult(LinesWordsResult(
					self.convert_to_line_result_format(result),
					self.imageInfo))
		except (KeyError, ValueError):
			# Translators: Reported when api result is invalid
			self.showMessageInNetworkThread(_(u"Recognition failed. Result is invalid."))
		finally:
			self.cleanUp()

	def recognize(self, pixels, imageInfo, onResult):
		"""
		Setup data for recognition then send request
		@param pixels:
		@param imageInfo:
		@param onResult: Result callback for result viewer
		@return: None
		"""
		if self.networkThread:
			# Translators: Error message
			ui.message(_(u"There is another recognition ongoing. Please wait."))
			return
		self.pixels = pixels
		self.onResult = onResult
		self.imageInfo = imageInfo
		imageObject = self.prepareImageObject(pixels, imageInfo)
		if not imageObject:
			return
		imageContent = self.prepareImageContent(imageObject)
		if not imageContent:
			return
		payloads = self.getPayload(imageContent)
		fullURL = self.getFullURL()
		headers = self.getHTTPHeaders()
		if config.conf["onlineOCR"]["verboseDebugLogging"]:
			log.io(type(fullURL))
			msg = u"{0}\n{1}\n{2}".format(
				fullURL,
				headers,
				payloads,
			)
			log.io(msg)
		self.sendRequest(self.callback, fullURL, payloads, headers)
	
	def sendRequest(self, callback, fullURL, payloads, headers=None):
		"""
		Send async network request
		@param headers: HTTP Headers
		@type headers:  dict
		@param callback:
		@type callback:
		@param fullURL: URL
		@type fullURL: str
		@param payloads: data for API
		@type payloads: dict
		"""
		from winHttp import postContent
		self.networkThread = Thread(
			target=postContent,
			args=(
				callback,
				fullURL,
				payloads,
				headers
			)
		)
		self.networkThread.start()
	
	def prepareImageObject(self, pixels, imageInfo):
		imageObject = self.getConvertedImage(pixels, imageInfo)
		imageObject = self.checkAndResizeImage(imageObject)
		if not imageObject:
			ui.message(imageObject)
			return
		else:
			return imageObject
	
	def cancel(self):
		if self.networkThread:
			self.networkThread = None
			self.cleanUp()
	
	def terminate(self):
		self.cancel()

	def process_api_result(self, result):
		raise NotImplementedError
	
	@staticmethod
	def extract_text(apiResult):
		raise NotImplementedError
	
	_type_of_api_access = "free"
	
	def _get_accessType(self):
		return self._type_of_api_access
	
	def _set_accessType(self, type_of_api_access):
		self._type_of_api_access = type_of_api_access
	
	def _get_availableAccesstypes(self):
		accessTypes = OrderedDict({
			# Translators: Label for OCR engine settings.
			"free": _("Use public API quota"),
			# Translators: Label for OCR engine settings.
			"own_key": _("Use api key registered by yourself"),
		})
		return self.generate_string_settings(accessTypes)
	
	@classmethod
	def AccessTypeSetting(cls):
		return AbstractEngine.StringSettings(
			"accessType",
			# Translators: Label for OCR engine settings.
			_(u"API Access Type")
		)
	
	@classmethod
	def BalanceSetting(cls):
		return AbstractEngine.ReadOnlySetting(
			"balance",
			# Translators: Label of OCR API quota balance control
			_(u"API quota Balance")
		)
	
	_balance = -1
	
	def _get_balance(self):
		return self._balance
	
	def _set_balance(self, balance):
		self._balance = balance
	
	def prepareImageContent(self, image):
		imageContent = self.serializeImage(image)
		imageSize = len(imageContent)
		newImage = None
		while imageSize >= self.maxSize and image.width >= self.minWidth and image.height >= self.minHeight:
			self.imageInfo.resizeFactor = self.imageInfo.resizeFactor * self.asymptoticResizeFactor
			newImage = self.getResizedImage()
			imageContent = self.serializeImage(newImage)
			imageSize = len(imageContent)
			if config.conf["onlineOCR"]["verboseDebugLogging"]:
				msg = "newWidth\n{0}\nnewHeight\n{1}\nsize\n{2}".format(
					newImage.width,
					newImage.height,
					imageSize
				)
				log.io(msg)
		
		if imageSize > self.maxSize:
			# Translators: Reported when error occurred during image serialization
			ui.message(_(u"Image content is too big to upload."))
			if config.conf["onlineOCR"]["verboseDebugLogging"]:
				newImage = self.getResizedImage()
				msg = "newWidth\n{0}\nnewHeight\n{1}\nsize\n{2}".format(
					newImage.width,
					newImage.height,
					imageSize
				)
				log.io(msg)
			return False
		else:
			if self.uploadBase64EncodeImage:
				return base64.standard_b64encode(imageContent)
			else:
				return imageContent
	
	uploadBase64EncodeImage = True
	
	def serializeImage(self, PILImage):
		"""
		Serialize image to bytes array
		@param PILImage: image object
		@type PILImage: PIL.Image.Image
		@return: image in bytes form
		@rtype: bool or bytes
		"""
		imageBuffer = BytesIO()
		PILImage.save(
			imageBuffer, "PNG",
			compression_level=self._compression,
			quality=self._quality,
			optimize=True
		)
		imageContent = imageBuffer.getvalue()
		return imageContent


class CustomOCRHandler(AbstractEngineHandler):
	engineClass = BaseRecognizer
	engineClassName = "BaseRecognizer"
	engineAddonName = "onlineOCR"
	enginePackageName = "contentRecognizers"
	enginePackage = contentRecognizers
	configSectionName = "onlineOCR"
	defaultEnginePriorityList = ["azureOCR"]
	mandatoryClassName = "CustomContentRecognizer"
	configSpec = {
		"engine": "string(default=auto)",
		"copyToClipboard": "boolean(default=false)",
		"swapRepeatedCountEffect": "boolean(default=false)",
		"useBrowseableMessage": "boolean(default=false)",
		"verboseDebugLogging": "boolean(default=false)",
		"proxyType": 'option("noProxy", "http", "socks", default="noProxy")',
		"proxyAddress": 'string(default="")',
	}


class OnlineOCRPanel(AbstractEngineSettingsPanel):
	title = _(u"Online OCR")
	handler = CustomOCRHandler


class BaseDescriber(BaseRecognizer):
	"""
	Abstract base BaseDescriber for image description
	"""
	
	configSectionName = "onlineImageDescriber"


class OnlineImageDescriberHandler(AbstractEngineHandler):
	engineClass = BaseDescriber
	mandatoryClassName = "CustomContentRecognizer"
	engineClassName = "BaseDescriber"
	engineAddonName = "onlineImageDescriber"
	enginePackageName = "imageDescribers"
	enginePackage = imageDescribers
	configSectionName = "onlineImageDescriber"
	defaultEnginePriorityList = ["machineLearning"]
	configSpec = {
		"engine": "string(default=auto)",
		"copyToClipboard": "boolean(default=false)",
		"swapRepeatedCountEffect": "boolean(default=false)",
		"verboseDebugLogging": "boolean(default=false)",
		"proxyType": 'option("noProxy", "http", "socks", default="noProxy")',
		"proxyAddress": 'string(default="")',
	}


class OnlineImageDescriberPanel(AbstractEngineSettingsPanel):
	title = _(u"Online Image Describer")
	handler = OnlineImageDescriberHandler


class CustomOCRPanel(SettingsPanel):
	useBrowseableMessageCheckBox = None  # type: wx.CheckBox
	proxyAddressTextCtrl = None  # type: wx.TextCtrl
	swapRepeatedCountEffectCheckBox = None  # type: wx.CheckBox
	verboseDebugLoggingCheckBox = None  # type: wx.CheckBox
	targetTypeList = None  # type: wx.Choice
	engineTypeList = None  # type: wx.Choice
	proxyTypeList = None  # type: wx.Choice
	copyToClipboardCheckBox = None  # type: wx.CheckBox
	notifyIfResizeRequiredCheckBox = None  # type:wx.CheckBox
	columnSplitModeList = None  # type: wx.Choice

	title = _(u"General")
	handler = CustomOCRHandler
	configSpec = {
		"copyToClipboard": "boolean(default=false)",
		"swapRepeatedCountEffect": "boolean(default=false)",
		"useBrowseableMessage": "boolean(default=false)",
		"verboseDebugLogging": "boolean(default=false)",
		"engineType": 'option("win10OCR", "onlineOCR", "onlineImageDescriber", default="onlineOCR")',
		"targetType": 'option("navigatorObject", "clipboardImage", "clipboardURL", "wholeDesktop", "foreGroundWindow", default="navigatorObject")',
		"proxyType": 'option("noProxy", "http", "socks", default="noProxy")',
		"proxyAddress": 'string(default="")',
		"notifyIfResizeRequired": "boolean(default=true)",
		"columnSplitMode": 'option("no", "two", "three", default="no")'
	}

	PROXY_TYPES = [
		# Translators: One of the proxy types in online OCR settings panel.
		("noProxy", _(u"Do not use proxy")),
		# Translators: One of the proxy types in online OCR settings panel.
		("http", _(u"Use HTTP proxy")),
		# Translators: One of the proxy types  in online OCR settings panel.
		("socks", _(u"Use socks proxy")),
	]
	configSection = None  # type: Section

	def makeSettings(self, sizer):
		settingsSizerHelper = BoxSizerHelper(self, sizer=sizer)

		try:
			self.configSection = config.conf["onlineOCRGeneral"]
		except KeyError:
			config.conf["onlineOCRGeneral"] = {}
			config.conf.spec["onlineOCRGeneral"] = self.configSpec
			self.configSection = config.conf["onlineOCRGeneral"]
		log.debug("Set config section {0}".format(self.configSection.dict()))

		# Translators: This is the label for a checkbox in the
		# online OCR settings panel.
		copyToClipboardText = _("&Copy recognition result to the clipboard")
		self.copyToClipboardCheckBox = settingsSizerHelper.addItem(wx.CheckBox(self, label=copyToClipboardText))
		self.copyToClipboardCheckBox.SetValue(
			config.conf["onlineOCRGeneral"]["copyToClipboard"]
		)
		
		# Translators: This is the label for a checkbox in the
		# online OCR settings panel.
		useBrowseableMessageText = _("&Use browseable message for text result")
		self.useBrowseableMessageCheckBox = settingsSizerHelper.addItem(wx.CheckBox(self, label=useBrowseableMessageText))
		self.useBrowseableMessageCheckBox.SetValue(
			config.conf["onlineOCRGeneral"]["useBrowseableMessage"]
		)
		
		# Translators: This is the label for a checkbox in the
		# online OCR settings panel.
		swapRepeatedCountEffectText = _("&Swap the effect of repeated gesture with none repeated ones.")
		self.swapRepeatedCountEffectCheckBox = settingsSizerHelper.addItem(
			wx.CheckBox(self, label=swapRepeatedCountEffectText))
		self.swapRepeatedCountEffectCheckBox.SetValue(
			config.conf["onlineOCRGeneral"]["swapRepeatedCountEffect"]
		)
		# Translators: This is the label for a checkbox in the
		# online OCR settings panel.
		verboseDebugLoggingText = _("&Enable more verbose logging for debug purposes")
		self.verboseDebugLoggingCheckBox = settingsSizerHelper.addItem(wx.CheckBox(self, label=verboseDebugLoggingText))
		self.verboseDebugLoggingCheckBox.SetValue(
			config.conf["onlineOCRGeneral"]["verboseDebugLogging"]
		)

		# Translators: The label for a list in the
		# online OCR settings panel.
		targetTypeText = _("Recognition &target:")
		targetTypeChoices = [
			desc for (name, desc) in TARGET_TYPES
		]
		self.targetTypeList = settingsSizerHelper.addLabeledControl(
			targetTypeText,
			wx.Choice,
			choices=targetTypeChoices
		)
		curTargetType = config.conf["onlineOCRGeneral"]["targetType"]
		for index, (name, desc) in enumerate(TARGET_TYPES):
			if name == curTargetType:
				self.targetTypeList.SetSelection(index)
				break

		# Translators: The label for a list in the
		# online OCR settings panel.
		engineTypeText = _("&Recognition Engine Type:")
		engineTypeChoices = [
			desc for (name, desc) in ENGINE_TYPES
		]
		self.engineTypeList = settingsSizerHelper.addLabeledControl(
			engineTypeText,
			wx.Choice,
			choices=engineTypeChoices
		)
		curEngineType = config.conf["onlineOCRGeneral"]["engineType"]
		for index, (name, desc) in enumerate(ENGINE_TYPES):
			if name == curEngineType:
				self.engineTypeList.SetSelection(index)
				break

				# Translators: This is the label for a checkbox in the
		# online OCR settings panel.
		notifyIfResizeRequiredText = _("&Notify if image resizing is requried.")
		self.notifyIfResizeRequiredCheckBox = settingsSizerHelper.addItem(
			wx.CheckBox(self, label=notifyIfResizeRequiredText)
		)
		self.notifyIfResizeRequiredCheckBox.SetValue(
			config.conf["onlineOCR"]["imageProcessing"]["notifyIfResizeRequired"]
		)

		# Translators: The label for a list in the
		# online OCR settings panel.
		self.columnSplitModeList = settingsSizerHelper.addLabeledControl(
			_("Column &split mode:"),
			wx.Choice,
			choices=[desc for (name, desc) in COLUMN_SPLIT_TYPES]
		)
		curColMode = config.conf["onlineOCR"]["imageProcessing"]["columnSplitMode"]
		for index, (name, desc) in enumerate(COLUMN_SPLIT_TYPES):
			if name == curColMode:
				self.columnSplitModeList.SetSelection(index)
				break

		# Translators: The label for a list in the
		# online OCR settings panel.
		proxyTypeText = _("Proxy &Type")
		proxyTypeChoices = [
			desc for (name, desc) in self.PROXY_TYPES
		]
		self.proxyTypeList = settingsSizerHelper.addLabeledControl(
			proxyTypeText, wx.Choice, choices=proxyTypeChoices)
		curTargetType = config.conf["onlineOCRGeneral"]["proxyType"]
		for index, (name, desc) in enumerate(self.PROXY_TYPES):
			if name == curTargetType:
				self.proxyTypeList.SetSelection(index)
				break

		proxyAddressLabelText = _("Proxy &address:")
		self.proxyAddressTextCtrl = settingsSizerHelper.addLabeledControl(proxyAddressLabelText, wx.TextCtrl)

	def onSave(self):
		config.conf["onlineOCRGeneral"]["copyToClipboard"] = self.copyToClipboardCheckBox.GetValue()
		config.conf["onlineOCRGeneral"]["verboseDebugLogging"] = self.verboseDebugLoggingCheckBox.GetValue()
		config.conf["onlineOCRGeneral"]["useBrowseableMessage"] = self.useBrowseableMessageCheckBox.GetValue()
		config.conf["onlineOCRGeneral"][
			"swapRepeatedCountEffect"] = self.swapRepeatedCountEffectCheckBox.GetValue()
		config.conf["onlineOCRGeneral"]["engineType"] = ENGINE_TYPES[
			self.engineTypeList.GetSelection()
		][0]
		config.conf["onlineOCRGeneral"]["targetType"] = TARGET_TYPES[
			self.targetTypeList.GetSelection()
		][0]
		config.conf["onlineOCRGeneral"]["proxyType"] = self.PROXY_TYPES[self.proxyTypeList.GetSelection()][
			0]
		config.conf["onlineOCRGeneral"]["proxyAddress"] = self.proxyAddressTextCtrl.GetValue()
		config.conf["onlineOCR"]["imageProcessing"]["notifyIfResizeRequired"] = self.notifyIfResizeRequiredCheckBox.GetValue()
		config.conf["onlineOCR"]["imageProcessing"]["columnSplitMode"] = COLUMN_SPLIT_TYPES[self.columnSplitModeList.GetSelection()][0]

	def isValid(self):
		oldProxy = config.conf["onlineOCRGeneral"]["proxyAddress"]
		oldProxyType = config.conf["onlineOCRGeneral"]["proxyType"]
		newProxyType = self.PROXY_TYPES[
			self.proxyTypeList.GetSelection()
		][0]
		if newProxyType != u"noProxy":
			# Translators: Reported when save proxy settings in online ocr panel
			ui.message(_(u"Checking your proxy settings"))
			config.conf["onlineOCRGeneral"]["proxyType"] = newProxyType
			config.conf["onlineOCRGeneral"]["proxyAddress"] = self.proxyAddressTextCtrl.GetValue()
			from .winHttp import httpConnectionPool, refreshConnectionPool
			try:
				refreshConnectionPool()
				log.io(httpConnectionPool)
				r = httpConnectionPool.request(
					b'GET',
					b"http://www.example.com"
				)
				msg = u"pool:\n{0}\nHeaders:\n{1}\nResponse:\n{2}".format(
					httpConnectionPool,
					r.headers,
					r.data,
				)
				log.io(msg)
				gui.messageBox(
					# Translators: Reported when proxy verification fails in online ocr settings panel
					caption=_(u"Proxy is valid, settings is saved."),
					message=_(r.data),
				)
				return True
			except Exception as e:
				config.conf["onlineOCRGeneral"]["proxyType"] = oldProxyType
				config.conf["onlineOCRGeneral"]["proxyAddress"] = oldProxy
				refreshConnectionPool()
				
				gui.messageBox(
					# Translators: Reported when proxy verification fails in online ocr settings panel
					caption=_(u"Proxy is not valid, please check your proxy type and address."),
					message=_(e),
				)
				return False
		else:
			return True


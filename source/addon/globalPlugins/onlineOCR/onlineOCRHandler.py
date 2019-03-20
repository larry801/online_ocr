# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# urllib3 used in this file is Copyright (c) 2008-2019 Andrey Petrov and contributors under MIT license.
from __future__ import unicode_literals
from threading import Thread
import gui
import os
import sys
from io import BytesIO
import json
from contentRecog import LinesWordsResult, ContentRecognizer, RecogImageInfo
import base64
import wx
import config
from six import iterkeys
from .abstractEngine import AbstractEngineHandler, AbstractEngineSettingsPanel, AbstractEngine, BooleanEngineSetting
import addonHandler
from . import contentRecognizers
from logHandler import log
import ui
from collections import OrderedDict

try:
	from urllib import urlencode
except ImportError:
	from urllib.urllib_parse import urlencode
from six import binary_type


def safeJoin(a, b):
	"""
	join pathes safely without unicode error
	@param a:
	@type a: str
	@param b:
	@type b: unicode
	@return:
	@rtype:
	"""
	if isinstance(a, binary_type):
		# In Python2
		return os.path.join(a, b.encode("mbcs"))
	else:
		# In Python3
		return os.path.join(a, b)


contribPath = safeJoin(
	os.path.dirname(os.path.dirname(__file__)),
	u"_contrib",
)
sys.path.insert(0, contribPath)
log.io(sys.path)
from PIL import Image

_ = lambda x: x
addonHandler.initTranslation()


class BaseRecognizer(ContentRecognizer, AbstractEngine):
	"""
	Abstract base BaseRecognizer
	"""

	# Translators: Description of Online OCR Engine
	description = ""

	nvda_cn_domain = b"www.nvdacn.com"
	configSectionName = "onlineOCR"
	networkThread = None  # type: Thread
	useHttps = True

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

	def _get_supportedSettings(self):
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

	def rgb_quad_to_png(self, pixels, imageInfo, resizeFactor=None):
		"""
		@param pixels: The pixels of the image as a two dimensional array of RGBQUADs.
			For example, to get the red value for the coordinate (1, 2):
			pixels[2][1].rgbRed
			This can be treated as raw bytes in BGRA8 format;
			i.e. four bytes per pixel in the order blue, green, red, alpha.
			However, the alpha channel should be ignored.
		@type pixels: Two dimensional array (y then x) of L{winGDI.RGBQUAD}
		@param imageInfo: Information about the image for recognition.
		@type imageInfo: L{RecogImageInfo}
		@rtype: L{Image}
		@param resizeFactor:
		@type resizeFactor:
		"""
		width = imageInfo.recogWidth
		height = imageInfo.recogHeight
		img = Image.frombytes("RGBX", (width, height), pixels, "raw", "BGRX")
		img = img.convert("RGB")
		if resizeFactor:
			img = img.resize((width * resizeFactor,
			                  height * resizeFactor))
		png_buffer = BytesIO()
		img.save(png_buffer, "PNG")
		return png_buffer.getvalue()

	@staticmethod
	def post_to_url(url, payloads):
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
	def processCURLError(self, result):
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
		resizeFactor = int(max(widthResizeFactor, heightResizeFactor))
		if isImageValid:
			image = image.resize((
				int(width * resizeFactor),
				int(height * resizeFactor)
			))
			width = image.width
			height = image.height
			msg += u"\nSize after resizing\nwidth:\n{w}\nheight:\n{h}".format(
				w=width,
				h=height
			)
			log.io(msg)
			if width * height > self.maxPixels:
				isImageValid = False
				# Translators: Reported when error occurred during image resizing
				errorMsg = _(u"Image has too many pixels.")
				ui.message(errorMsg)
				return False
			else:
				return image
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

	def get_converted_image(self, pixels, imageInfo):
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
		return img

	def recognize(self, pixels, imageInfo, onResult):
		"""
		Setup data for recognition then send request
		@param pixels:
		@param imageInfo:
		@param onResult: Result callback for result viewer
		@return: None
		"""

		def callback(result):
			self.networkThread = None
			# Translators: Reported when api result is invalid
			failed_message = _(u"Recognition failed. Result is invalid.")
			# Translators: Message added before recognition result
			# when user do not use result viewer
			result_prefix = _(u"Recognition result:")
			log.io(result)
			if not self._use_own_api_key:
				curl_error_message = self.processCURLError(result)  # type: str
				if curl_error_message:
					ui.message(curl_error_message)
					return
			api_error_message = self.process_api_result(result)  # type: str
			if api_error_message:
				ui.message(api_error_message)
				return
			try:
				result = self.convert_to_json(result)
			except ValueError as e:
				ui.message(failed_message)
				return

			try:
				ocrResult = self.extract_text(result)
				if ocrResult.isspace():
					# Translators: Reported when recognition result is empty
					ocrResult = _(u"blank. There may be no text on this image.")
				resultText = result_prefix + ocrResult
				if config.conf[self.configSectionName]["copyToClipboard"]:
					import api
					api.copyToClip(resultText)
				if self.text_result:
					ui.message(resultText)
				else:
					onResult(LinesWordsResult(self.convert_to_line_result_format(result), imageInfo))
			except Exception as e:
				log.error(e)
				log.error(result)
				ui.message(failed_message)

		if self.networkThread:
			# Translators: Error message
			ui.message(_(u"There is another recognition ongoing. Please wait."))
			return
		PILImage = self.get_converted_image(pixels, imageInfo)
		PILImage = self.checkAndResizeImage(PILImage)
		if PILImage is False:
			ui.message(PILImage)
			return
		imageContent = self.serializeImage(PILImage)
		if not imageContent:
			return
		payloads = self.getPayload(imageContent)
		fullURL = self.getFullURL()
		headers = self.getHTTPHeaders()
		msg = u"{0}\n{1}\n{2}\n{3}".format(
			callback,
			fullURL,
			headers,
			payloads,
		)
		if config.conf["onlineOCR"]["verboseDebugLogging"]:
			log.io(msg)
		self.sendRequest(callback, fullURL, payloads, headers)

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
		from .winHttp import postContent
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

	def cancel(self):
		self.networkThread = None

	def terminate(self):
		self.networkThread = None

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
			"free": _("Use public api quota"),
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

	def serializeImage(self, PILImage):
		"""

		@param PILImage:
		@type PILImage:
		@return:
		@rtype: bool or str
		"""
		imgBuf = BytesIO()
		PILImage.save(imgBuf, "PNG")
		imageContent = imgBuf.getvalue()
		if len(imageContent) > self.maxSize:
			# Translators: Reported when error occurred during image serialization
			errorMsg = _(u"Image content size is too big")
			ui.message(errorMsg)
			return False
		else:
			return base64.standard_b64encode(imageContent)


class CustomOCRHandler(AbstractEngineHandler):
	engineClass = BaseRecognizer
	engineClassName = "BaseRecognizer"
	engineAddonName = "onlineOCR"
	enginePackageName = "contentRecognizers"
	enginePackage = contentRecognizers
	configSectionName = "onlineOCR"
	defaultEnginePriorityList = ["azureOCR"]
	configSpec = {
		"engine": "string(default=auto)",
		"copyToClipboard": "boolean(default=false)",
		"swapRepeatedCountEffect": "boolean(default=false)",
		"verboseDebugLogging": "boolean(default=false)",
		"proxyType": 'option("noProxy", "http", "socks", default="noProxy")',
		"proxyAddress": 'string(default="")',
	}


class CustomOCRPanel(AbstractEngineSettingsPanel):
	testEngineButton = None  # type: wx.Button
	proxyAddressTextCtrl = None  # type: wx.TextCtrl
	swapRepeatedCountEffectCheckBox = None  # type: wx.CheckBox
	verboseDebugLoggingCheckBox = None  # type: wx.CheckBox
	proxyTypeList = None  # type: wx.Choice
	copyToClipboardCheckBox = None  # type: wx.CheckBox
	title = _(u"Online OCR")
	handler = CustomOCRHandler

	PROXY_TYPES = [
		# Translators: One of the proxy types in online OCR settings panel.
		("noProxy", _(u"Do not use proxy")),
		# Translators: One of the proxy types in online OCR settings panel.
		("http", _(u"Use HTTP proxy")),
		# Translators: One of the proxy types  in online OCR settings panel.
		("socks", _(u"Use socks proxy")),
	]

	def makeGeneralSettings(self, settingsSizerHelper):
		# Translators: This is the label for a checkbox in the
		# online OCR settings panel.
		copyToClipboardText = _("&Copy result to clipboard after recognition")
		self.copyToClipboardCheckBox = settingsSizerHelper.addItem(wx.CheckBox(self, label=copyToClipboardText))
		self.copyToClipboardCheckBox.SetValue(
			config.conf[self.handler.configSectionName]["copyToClipboard"])
		# Translators: This is the label for a checkbox in the
		# online OCR settings panel.
		swapRepeatedCountEffectText = _("&Swap the effect of repeated gesture with none repeated ones.")
		self.swapRepeatedCountEffectCheckBox = settingsSizerHelper.addItem(
			wx.CheckBox(self, label=swapRepeatedCountEffectText))
		self.swapRepeatedCountEffectCheckBox.SetValue(
			config.conf[self.handler.configSectionName]["swapRepeatedCountEffect"])
		# Translators: This is the label for a checkbox in the
		# online OCR settings panel.
		verboseDebugLoggingText = _("&Enable more verbose logging for debug purpose")
		self.verboseDebugLoggingCheckBox = settingsSizerHelper.addItem(wx.CheckBox(self, label=verboseDebugLoggingText))
		self.verboseDebugLoggingCheckBox.SetValue(
			config.conf[self.handler.configSectionName]["verboseDebugLogging"])
		# Translators: The label for a list in the
		# online OCR settings panel.
		proxyTypeText = _("Proxy &Type")
		proxyTypeChoices = [
			desc for (name, desc) in self.PROXY_TYPES
		]
		self.proxyTypeList = settingsSizerHelper.addLabeledControl(proxyTypeText, wx.Choice, choices=proxyTypeChoices)
		curType = config.conf[self.handler.configSectionName]["proxyType"]
		for index, (name, desc) in enumerate(self.PROXY_TYPES):
			if name == curType:
				self.proxyTypeList.SetSelection(index)
				break
		# Translators: The label for a TextCtrl in the
		# online OCR settings panel.
		proxyAddressLabelText = _(u"Proxy &Address")
		self.proxyAddressTextCtrl = settingsSizerHelper.addLabeledControl(proxyAddressLabelText,
		                                                                  wx.TextCtrl)
		self.proxyAddressTextCtrl.SetValue(config.conf[self.handler.configSectionName]["proxyAddress"])

	def onSave(self):
		super(CustomOCRPanel, self).onSave()
		config.conf[self.handler.configSectionName]["copyToClipboard"] = self.copyToClipboardCheckBox.GetValue()
		config.conf[self.handler.configSectionName]["verboseDebugLogging"] = self.verboseDebugLoggingCheckBox.GetValue()
		config.conf[self.handler.configSectionName]["swapRepeatedCountEffect"] = self.swapRepeatedCountEffectCheckBox.GetValue()
		config.conf[self.handler.configSectionName]["proxyType"] = self.PROXY_TYPES[self.proxyTypeList.GetSelection()][
			0]
		config.conf[self.handler.configSectionName]["proxyAddress"] = self.proxyAddressTextCtrl.GetValue()

	def isValid(self):
		oldProxy = config.conf[self.handler.configSectionName]["proxyAddress"]
		oldProxyType = config.conf[self.handler.configSectionName]["proxyType"]
		newProxyType = self.PROXY_TYPES[
			self.proxyTypeList.GetSelection()
		][0]
		if newProxyType != u"noProxy":
			# Translators: Reported when save proxy settings in online ocr panel
			ui.message(_(u"Checking your proxy settings"))
			config.conf[self.handler.configSectionName]["proxyType"] = newProxyType
			config.conf[self.handler.configSectionName]["proxyAddress"] = self.proxyAddressTextCtrl.GetValue()
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
					caption=_(u"Proxy is valid, , settings is saved."),
					message=_(r.data),
				)
				return True
			except Exception as e:
				config.conf[self.handler.configSectionName]["proxyType"] = oldProxyType
				config.conf[self.handler.configSectionName]["proxyAddress"] = oldProxy
				refreshConnectionPool()

				gui.messageBox(
					# Translators: Reported when proxy verification fails in online ocr settings panel
					caption=_(u"Proxy is not valid, please check your proxy type and address."),
					message=_(e),
				)
				return False
		else:
			return True

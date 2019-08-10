# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""onlineOCR:
A global plugin that add online ocr to NVDA
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from inputCore import InputGesture
import addonHandler
import globalPluginHandler
import gui
import globalVars
import config
import winUser
from contentRecog import RecogImageInfo
from contentRecog.recogUi import _recogOnResult
from scriptHandler import script
from logHandler import log
import ui
import winKernel
import scriptHandler
import inputCore
from ctypes import windll, create_unicode_buffer, c_uint32, wstring_at
from . import onlineOCRHandler
from PIL import ImageGrab, Image
from onlineOCRHandler import (
	CustomOCRPanel, OnlineImageDescriberHandler, CustomOCRHandler
)
from LayeredGesture import category_name, secondaryGestureMap
_ = lambda x: x
# We need to initialize translation and localization support:
addonHandler.initTranslation()


CONFIGURABLE_RECOGNITION_TARGETS = {
	# Translators: Target type for recognition
	"clipboard": _("Clipboard"),
	"foreGroundWindow": _("Foreground window"),
	"wholeDesktop": _("The whole desktop"),
	"navigatorObject": _("Navigator Objcect")
}


def PILImageToPixels(image):
	"""
	Convert PIL Image into pixels and imageInfo
	@param image: Image to convert
	@type image Image.Image
	@return:
	@rtype: tuple
	"""
	imageInfo = RecogImageInfo(0, 0, image.width, image.height, 1)
	pixels = image.tobytes("raw", "BGRX")
	return pixels, imageInfo


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self):
		super(GlobalPlugin, self).__init__()
		if globalVars.appArgs.secure:
			return
		if config.isAppX:
			return
		CustomOCRHandler.initialize()
		self.handler = CustomOCRHandler
		msg = u"OCR engine:\n{0}\n".format(self.handler.currentEngine)

		OnlineImageDescriberHandler.initialize()
		self.descHandler = OnlineImageDescriberHandler
		msg += u"Describe handler:\n{0}\n".format(self.descHandler.currentEngine)
		log.debug(msg)
		self.prevCaptureFunc = None
		self.capture_function_installed = False
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(CustomOCRPanel)

	def captureFunction(self, gesture: InputGesture):
		"""
		Implement sequential gestures
		@param gesture:
		@type gesture: inputCore.InputGesture
		@return:
		@rtype:
		"""
		gestureIdentifiers = gesture._get_identifiers()
		msg = u"Name\n{0}\nidentifiers\n{2}\nisModifier\n{1}".format(
			gesture._get_displayName(),
			gesture.isModifier,
			gestureIdentifiers
		)
		log.io(msg)
		if not gesture.isModifier:
			secondaryGestureMap.getScriptsForGesture(gesture)
			if 'kb:c' in gestureIdentifiers:
				self.script_describeClipboardImage(gesture)
				self.removeCaptureFunction()
			elif 'kb:d' in gestureIdentifiers:
				self.script_describeNavigatorObject(gesture)
				self.removeCaptureFunction()
			elif 'kb:d' in gestureIdentifiers:
				self.script_recognizeClipboardImageWithOnlineOCREngine(gesture)
				self.removeCaptureFunction()
			elif 'kb:d' in gestureIdentifiers:
				self.script_recognizeWithOnlineOCREngine(gesture)
				self.removeCaptureFunction()
	
	def addCaptureFunction(self):
		log.io("Capture function added.")
		self.prevCaptureFunc = inputCore.manager._captureFunc
		inputCore.manager._captureFunc = self.captureFunction
		self.capture_function_installed = True

	def removeCaptureFunction(self):
		inputCore.manager._captureFunc = self.prevCaptureFunc
		msg = u"Capture function removed"
		self.capture_function_installed = False
		log.io(msg)
	
	# Translators: Online Image Describer command name in input gestures dialog
	image_describe = _(
		"Describe the content of the current navigator object with online image describer.")
	
	# Translators: Online Image Describer command name in input gestures dialog
	@script(
		description=image_describe,
		category=category_name,
		gestures=["kb:NVDA+Alt+P"])
	def script_describeNavigatorObject(self, gesture: InputGesture):
		from contentRecog import recogUi
		engine = OnlineImageDescriberHandler.getCurrentEngine()
		repeatCount = scriptHandler.getLastScriptRepeatCount()
		textResultWhenRepeatGesture = not config.conf["onlineOCR"]["swapRepeatedCountEffect"]
		if repeatCount == 0:
			engine.text_result = textResultWhenRepeatGesture
			recogUi.recognizeNavigatorObject(engine)
		elif repeatCount == 1:
			engine.text_result = not textResultWhenRepeatGesture
	
	# Translators: OCR command name in input gestures dialog
	describe_clipboard_msg = _(
		"Describe clipboard images with online image describer.")
	
	# Translators: Reported when PIL cannot grab image from clipboard
	noImageMessage = _(u"No image in clipboard")
	
	@script(
		description=describe_clipboard_msg,
		category=category_name,
		gestures=["kb:Control+Shift+NVDA+P"])
	def script_describeClipboardImage(self, gesture: InputGesture):
		"""

		@type gesture: InputGesture
		"""
		engine = OnlineImageDescriberHandler.getCurrentEngine()
		repeatCount = scriptHandler.getLastScriptRepeatCount()
		textResultWhenRepeatGesture = not config.conf["onlineOCR"]["swapRepeatedCountEffect"]
		if repeatCount == 0:
			engine.text_result = textResultWhenRepeatGesture
			clipboardImage = self.getImageFromClipboard()
			if clipboardImage:
				imageInfo = RecogImageInfo(0, 0, clipboardImage.width, clipboardImage.height, 1)
				pixels = clipboardImage.tobytes("raw", "BGRX")
				# Translators: Reporting when content recognition begins.
				ui.message(_("Recognizing"))
				engine.recognize(pixels, imageInfo, _recogOnResult)
			else:
				ui.message(self.noImageMessage)
		elif repeatCount >= 1:
			engine.text_result = not textResultWhenRepeatGesture
	
	# Translators: OCR command name in input gestures dialog
	full_ocr_msg = _(
		"Recognizes the content of the current navigator object with online OCR engine.")
	
	# Translators: OCR command name in input gestures dialog
	@script(
		description=full_ocr_msg,
		category=category_name,
		gestures=["kb:NVDA+Alt+R"]
	)
	def script_recognizeWithOnlineOCREngine(self, gesture: InputGesture):
		from contentRecog import recogUi
		engine = onlineOCRHandler.CustomOCRHandler.getCurrentEngine()
		repeatCount = scriptHandler.getLastScriptRepeatCount()
		textResultWhenRepeatGesture = not config.conf["onlineOCR"]["swapRepeatedCountEffect"]
		if repeatCount == 0:
			engine.text_result = textResultWhenRepeatGesture
			recogUi.recognizeNavigatorObject(engine)
		elif repeatCount == 1:
			engine.text_result = not textResultWhenRepeatGesture
	
	# Translators: OCR command name in input gestures dialog
	clipboard_ocr_msg = _(
		"Recognizes the text in clipboard images with online OCR engine.")
	
	@script(
		description=clipboard_ocr_msg,
		category=category_name,
		gestures=["kb:Control+Shift+NVDA+R"]
	)
	def script_recognizeClipboardImageWithOnlineOCREngine(self, gesture: InputGesture):
		engine = onlineOCRHandler.CustomOCRHandler.getCurrentEngine()
		repeatCount = scriptHandler.getLastScriptRepeatCount()
		textResultWhenRepeatGesture = not config.conf["onlineOCR"]["swapRepeatedCountEffect"]
		if repeatCount == 0:
			engine.text_result = textResultWhenRepeatGesture
			clipboardImage = self.getImageFromClipboard()
			if clipboardImage:
				imageInfo = RecogImageInfo(0, 0, clipboardImage.width, clipboardImage.height, 1)
				pixels = clipboardImage.tobytes("raw", "BGRX")
				# Translators: Reporting when content recognition (e.g. OCR) begins.
				ui.message(_("Recognizing"))
				engine.recognize(pixels, imageInfo, _recogOnResult)
			else:
				ui.message(self.noImageMessage)
		elif repeatCount >= 1:
			engine.text_result = not textResultWhenRepeatGesture

	@script(
		# Translators: Online Image Describer command name in input gestures dialog
		description=_("Cancel current recognition if there is any."),
		category=category_name,
		gestures=[]
	)
	def script_cancelCurrentRecognition(self, gesture: InputGesture):
		ocrEngine = CustomOCRHandler.getCurrentEngine()
		describeEngine = OnlineImageDescriberHandler.getCurrentEngine()
		if ocrEngine.networkThread:
			# Translators: Reported when cancelling recognition
			ui.message(_("OCR cancelled"))
			ocrEngine.cancel()
		elif describeEngine.networkThread:
			# Translators: Reported when cancelling recognition
			ui.message(_("Image describe cancelled"))
			describeEngine.cancel()
		else:
			# Translators: Reported when cancelling recognition
			ui.message(_("There is no recognition ongoing."))

	@script(
		# Translators: Online Image Describer command name in input gestures dialog
		description=_("Cycle through types of recognition target"),
		category=category_name,
		gestures=[]
	)
	def script_cycleRecognitionTarget(self, gestures):
		"""

		@type gestures: InputGesture
		"""
		curLevel = config.conf
		for target in CONFIGURABLE_RECOGNITION_TARGETS:
			if target > curLevel:
				break
		else:
			target = CONFIGURABLE_RECOGNITION_TARGETS[0]
		name = 0
		# Translators: Reported when the user cycles through speech symbol levels
		# which determine target of content recognition
		# %s will be replaced with the symbol level; e.g. none, some, most and all.
		ui.message(_("Recognition target: %s") % name)

	@staticmethod
	def enumerateClipboardFormat():
		formats = []
		fmt = 0
		with winUser.openClipboard(gui.mainFrame.Handle):
			while True:
				fmt = windll.user32.EnumClipboardFormats(fmt)
				if fmt == 0:
					break
				formats.append(fmt)
		return formats
	
	@classmethod
	def getImageFromClipboard(cls):
		CF_DIB = 8
		CF_HDROP = 15
		CF_UNICODETEXT = 13
		clipboardImage = None
		formats = cls.enumerateClipboardFormat()
		if CF_DIB in formats:
			clipboardImage = ImageGrab.grabclipboard()
		elif CF_HDROP in formats:
			try:
				filePathList = []
				with winUser.openClipboard(gui.mainFrame.Handle):
					rawData = windll.user32.GetClipboardData(CF_HDROP)

					if not rawData:
						ui.message(_("Error occurred while getting pasted file."))
					rawData = winKernel.HGLOBAL(rawData, autoFree=False)
					with rawData.lock() as addr:
						fileCount = windll.shell32.DragQueryFileW(
							c_uint32(addr),
							c_uint32(0xFFFFFFFF),
							c_uint32(0),
							c_uint32(0)
						)
						for c in range(fileCount):
							BUFFER_SIZE = 4096
							filePath = create_unicode_buffer(BUFFER_SIZE)
							windll.shell32.DragQueryFileW(
								c_uint32(addr),
								c_uint32(c),
								c_uint32(filePath),
								c_uint32(BUFFER_SIZE)
							)
							filePathList.append(wstring_at(filePath, size=BUFFER_SIZE).rstrip('\x00'))
					log.debug("filePathList\n{0}".format(filePathList))
					for fileName in filePathList:
						# TODO Add a prompt for users to choose from
						import os
						if os.path.isfile(fileName):
							clipboardImage = Image.open(rawData[0])
							clipboardImage = clipboardImage.convert("RGB")
							break
			except TypeError as e:
				log.io(e)
		elif CF_UNICODETEXT in formats:
			# TODO extract url or file path from text then grab an image from it.
			try:
				from api import getClipData
				import os
				text = getClipData()
				if os.path.exists(text):
					if os.path.isfile(text):
						clipboardImage = Image.open(text)
					else:
						# Translators: Reported when text in clipboard is not a valid path
						ui.message(_(u"Text in clipboard is the name of a directory."))
				else:
					# Translators: Reported when text in clipboard is not a valid path
					ui.message(_(u"Text in clipboard is not a valid path."))
			except IOError:
				# Translators: Reported when cannot get content of the path specified
				errMsg = _("The file specified in clipboard is not an image")
				ui.message(errMsg)

		return clipboardImage

	def terminate(self):
		OnlineImageDescriberHandler.terminate()
		CustomOCRHandler.terminate()

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
import addonHandler
import globalPluginHandler
import gui
import globalVars
import config
from .onlineOCRHandler import (
	CustomOCRPanel, OnlineImageDescriberHandler, CustomOCRHandler
)
from contentRecog import RecogImageInfo
from contentRecog.recogUi import _recogOnResult
from scriptHandler import script
from logHandler import log
import ui
import scriptHandler
from PIL import ImageGrab, Image
import inputCore
from .LayeredGesture import category_name, addonGestureMap
_ = lambda x: x
# We need to initialize translation and localization support:
addonHandler.initTranslation()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	
	def PILImageToPixels(self, image):
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
	
	def __init__(self):
		super(GlobalPlugin, self).__init__()
		if globalVars.appArgs.secure:
			return
		if config.isAppX:
			return
		from . import onlineOCRHandler
		onlineOCRHandler.CustomOCRHandler.initialize()
		self.handler = onlineOCRHandler.CustomOCRHandler
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(CustomOCRPanel)
		
		OnlineImageDescriberHandler.initialize()
		self.descHandler = OnlineImageDescriberHandler
		self.prevCaptureFunc = None
		self.capture_function_installed = False
		
	def captureFunction(self, gesture):
		"""
		Implement sequential gestures
		@param gesture:
		@type gesture: inputCore.InputGesture
		@return:
		@rtype:
		"""
		gestureIdentifiers = gesture.identifiers
		msg = u"Name\n{0}\nidentifiers\n{2}\nisModifier\n{1}".format(
			gesture.displayName,
			gesture.isModifier,
			gestureIdentifiers
		)
		log.io(msg)
		if not gesture.isModifier:
			addonGestureMap.getScriptsForGesture(gesture)
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
	def script_describeNavigatorObject(self, gesture):
		from contentRecog import recogUi
		engine = OnlineImageDescriberHandler.getCurrentEngine()
		repeatCount = scriptHandler.getLastScriptRepeatCount()
		textResultWhenRepeatGesture = not config.conf["onlineImageDescriber"]["swapRepeatedCountEffect"]
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
	def script_describeClipboardImage(self, gesture):
		engine = OnlineImageDescriberHandler.getCurrentEngine()
		repeatCount = scriptHandler.getLastScriptRepeatCount()
		textResultWhenRepeatGesture = not config.conf["onlineImageDescriber"]["swapRepeatedCountEffect"]
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
	def script_recognizeWithOnlineOCREngine(self, gesture):
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
	def script_recognizeClipboardImageWithOnlineOCREngine(self, gesture):
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
	
	@staticmethod
	def enumerateClipboardFormat():
		import win32clipboard
		formats = []
		win32clipboard.OpenClipboard(None)
		fmt = 0
		while True:
			fmt = win32clipboard.EnumClipboardFormats(fmt)
			if fmt == 0:
				break
			formats.append(fmt)
		return formats
	
	@classmethod
	def getImageFromClipboard(cls):
		import win32clipboard
		clipboardImage = None
		formats = cls.enumerateClipboardFormat()
		if win32clipboard.CF_DIB in formats:
			clipboardImage = ImageGrab.grabclipboard()
		elif win32clipboard.CF_HDROP in formats:
			try:
				win32clipboard.OpenClipboard()
				rawData = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
				log.info(rawData)
				if isinstance(rawData, tuple):
					clipboardImage = Image.open(rawData[0])
					clipboardImage = clipboardImage.convert("RGB")
			except TypeError as e:
				log.io(e)
			finally:
				win32clipboard.CloseClipboard()
		elif win32clipboard.CF_TEXT in formats:
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
			except IOError as e:
				# Translators: Reported when cannot get content of the path specified
				errMsg = _("The file specified in clipboard is not an image")
				ui.message(errMsg)

		return clipboardImage

	def terminate(self):
		OnlineImageDescriberHandler.terminate()
		CustomOCRHandler.terminate()

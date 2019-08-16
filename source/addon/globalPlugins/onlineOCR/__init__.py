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
import api
from ctypes.wintypes import RECT
from contentRecog import uwpOcr
from contentRecog import RecogImageInfo
from contentRecog import recogUi
from scriptHandler import script
from logHandler import log
import ui
import wx
import winKernel
import scriptHandler
from ctypes import windll, create_unicode_buffer, c_uint32, wstring_at, byref
from six import binary_type
from six import PY2
import sys
import os
import winVersion
from gui.settingsDialogs import UwpOcrPanel, NVDASettingsDialog


def safeJoin(a, b):
	"""
	join path safely without unicode error
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


if PY2:
	contribPathName = u"_contrib"
else:
	contribPathName = u"_py3_contrib"
contribPath = safeJoin(
	os.path.dirname(os.path.dirname(__file__)),
	contribPathName,
)
sys.path.insert(0, contribPath)
sys.path.insert(0, os.path.dirname(__file__))
from PIL import ImageGrab, Image
from onlineOCRHandler import (
	CustomOCRPanel, OnlineImageDescriberHandler, CustomOCRHandler,
	OnlineImageDescriberPanel, OnlineOCRPanel,
	TARGET_TYPES, ENGINE_TYPES, COLUMN_SPLIT_TYPES
)
from LayeredGesture import category_name
_ = lambda x: x
# We need to initialize translation and localization support:
addonHandler.initTranslation()


class OCRMultiCategorySettingsDialog(NVDASettingsDialog):
	# Translators: This is the label for the NVDA settings dialog.
	title = _("Online Image Describer Settings")
	categoryClasses = [
		CustomOCRPanel,
		OnlineOCRPanel,
		OnlineImageDescriberPanel,
	]
	if winVersion.isUwpOcrAvailable():
		categoryClasses.append(UwpOcrPanel)


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
		self.ocrHandler = CustomOCRHandler
		msg = u"OCR engine:\n{0}\n".format(self.ocrHandler.currentEngine)

		OnlineImageDescriberHandler.initialize()
		self.descHandler = OnlineImageDescriberHandler
		msg += u"Describe ocrHandler:\n{0}\n".format(self.descHandler.currentEngine)
		log.debug(msg)
		if winVersion.isUwpOcrAvailable():
			self.uwpOCREngine = uwpOcr.UwpOcr()
		self.ocrSettingMenuItem = gui.mainFrame.sysTrayIcon.preferencesMenu.Append(
			wx.ID_NEW,
			# Translators: The label for the menu item to open online image settings dialog.
			_("Open &OnlineImageDescriber settings"),
			_("Open settings dialog for OnlineImageDescriber")
		)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.openSettingsDialog, self.ocrSettingMenuItem)

	@staticmethod
	def openSettingsDialog(evt):
		frame = gui.mainFrame
		if gui.isInMessageBox:
			return
		frame.prePopup()
		d = OCRMultiCategorySettingsDialog(frame)
		d.CenterOnScreen()
		d.Show()
		frame.postPopup()

	# Translators: Online Image Describer command name in input gestures dialog
	image_describe = _(
		"Describe the content of the current navigator object with online image describer.")
	
	# Translators: Online Image Describer command name in input gestures dialog
	@script(
		description=image_describe,
		category=category_name,
		gestures=["kb:NVDA+Alt+P"])
	def script_describeNavigatorObject(self, gesture: InputGesture):
		self.startRecognition("navigatorObject", "onlineImageDescribe")
	
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
		self.startRecognition("clipboardImage", "onlineImageDescribe")
	
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
		self.startRecognition("navigatorObject", "onlineOCR")
	
	# Translators: OCR command name in input gestures dialog
	clipboard_ocr_msg = _(
		"Recognizes the text in clipboard images with online OCR engine.")
	
	@script(
		description=clipboard_ocr_msg,
		category=category_name,
		gestures=["kb:Control+Shift+NVDA+R"]
	)
	def script_recognizeClipboardImageWithOnlineOCREngine(self, gesture: InputGesture):
		self.startRecognition("clipboardImage", "onlineOCR")

	@script(
		# Translators: Online Image Describer command name in input gestures dialog
		description=_("Cancel current recognition if there is any."),
		category=category_name,
		gestures=[]
	)
	def script_cancelCurrentRecognition(self, gesture: InputGesture):
		ocrEngine = self.ocrHandler.getCurrentEngine()
		describeEngine = self.descHandler.getCurrentEngine()
		if ocrEngine.networkThread:
			# Translators: Reported when cancelling recognition
			ui.message(_("OCR cancelled"))
			ocrEngine.cancel()
		elif describeEngine.networkThread:
			# Translators: Reported when cancelling recognition
			ui.message(_("Image describe cancelled"))
			describeEngine.cancel()
		elif winVersion.isUwpOcrAvailable() and recogUi._activeRecog:
			# Translators: Reported when cancelling recognition
			ui.message(_("OCR cancelled"))
			uwpOcr.UwpOcr.cancel(self.uwpOCREngine)
			recogUi._activeRecog = None
		else:
			# Translators: Reported when cancelling recognition
			ui.message(_("There is no recognition ongoing."))

	@script(
		# Translators: Online Image Describer command name in input gestures dialog
		description=_("Recognize image according to engine and target in settings"),
		category=category_name,
		gestures=["kb:NVDA+R"]
	)
	def script_recognizeAccordingToSettings(self, gestures: InputGesture):
		current_target = config.conf["onlineOCR"]["general"]["targetType"]
		current_engine_type = config.conf["onlineOCR"]["general"]["engineType"]
		self.startRecognition(
			current_target,
			current_engine_type
		)

	@staticmethod
	def cycleThroughSettings(config_section, config_name, config_list):
		current_target = config_section[config_name]
		available_targets = [name for (name, desc) in config_list]
		current_target_index = available_targets.index(current_target)
		available_target_names = [name for (name, desc) in config_list]
		for target in available_targets:
			target_index = available_targets.index(target)
			if target_index > current_target_index:
				current_target_index = target_index
				current_target = available_targets[current_target_index]
				break
		else:
			current_target_index = 0
			current_target = available_targets[0]
		name = available_target_names[current_target_index]
		config_section[config_name] = current_target
		return name

	@script(
		# Translators: Online Image Describer command name in input gestures dialog
		description=_("Cycle through types of recognition target"),
		category=category_name,
		gestures=[]
	)
	def script_cycleRecognitionEngineType(self, gestures: InputGesture):
		name = self.cycleThroughSettings(
			config.conf["onlineOCR"]["general"],
			"engineType",
			ENGINE_TYPES
		)
		# Translators: Reported when the user cycles through recognition engine type
		# %s will be replaced with the engine type: e.g. Online OCR Windows 10 Offline OCR
		ui.message(_("Recognition engine type: %s") % name)

	@script(
		# Translators: Online Image Describer command name in input gestures dialog
		description=_("Cycle through types of recognition target"),
		category=category_name,
		gestures=[]
	)
	def script_cycleRecognitionTarget(self, gestures: InputGesture):
		name = self.cycleThroughSettings(
			config.conf["onlineOCR"]["general"],
			"targetType",
			TARGET_TYPES
		)
		# Translators: Reported when the user cycles through target types
		# which determine target of content recognition
		# %s will be replaced with the target type: e.g. Clipboard image, foreground window
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
							return clipboardImage
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

	def getImageFromTarget(self, current_target):
		if current_target == "navigatorObject":
			nav = api.getNavigatorObject()
			# Translators: Reported when content recognition (e.g. OCR) is attempted,
			# but the content is not visible.
			notVisibleMsg = _("Content is not visible")
			try:
				left, top, width, height = nav.location
			except TypeError:
				log.debugWarning("Object returned location %r" % nav.location)
				ui.message(notVisibleMsg)
				return
			# Translators: Reporting when content recognition (e.g. OCR) begins.
			ui.message(_("Recognizing"))
			return ImageGrab.grab((left, top, width, height), True)
		elif current_target == "clipboardImage":
			return self.getImageFromClipboard()
		elif current_target == "clipboardURL":
			return None
		elif current_target == "foreGroundWindow":
			foregroundWindow = winUser.getForegroundWindow()
			desktopWindow = winUser.getDesktopWindow()
			foregroundRect = RECT()
			desktopRect = RECT()
			winUser.user32.GetWindowRect(foregroundWindow, byref(foregroundRect))
			winUser.user32.GetWindowRect(desktopWindow, byref(desktopRect))
			left = max(foregroundRect.left, desktopRect.left)
			right = min(foregroundRect.right, desktopRect.right)
			top = max(foregroundRect.top, desktopRect.top)
			bottom = min(foregroundRect.bottom, desktopRect.bottom)
			if right <= left or bottom <= top:
				ui.message(_("Current window position is invalid."))
				return
			from locationHelper import RectLTRB
			windowRectLTRB = RectLTRB(
				left=left,
				right=right,
				top=top,
				bottom=bottom
			)
			return ImageGrab.grab((
				windowRectLTRB.top,
				windowRectLTRB.left,
				windowRectLTRB.width,
				windowRectLTRB.height
			), True)
		elif current_target == "wholeDesktop":
			return ImageGrab.grab(include_layered_windows=True)
		else:
			# Translators: Reported when target is not correct.
			ui.message(_("Unknown target: %s" % current_target))
			return None

	def getCurrentEngine(self, current_engine_type):
		if winVersion.isUwpOcrAvailable() and current_engine_type == "win10OCR":
			engine = self.uwpOCREngine
		elif current_engine_type == "onlineOCR":
			engine = self.ocrHandler.getCurrentEngine()
		elif current_engine_type == "onlineImageDescriber":
			engine = self.descHandler.getCurrentEngine()
		else:
			engine = None
		return engine

	def startRecognition(self, current_target, current_engine_type):
		recognizeImage = self.getImageFromTarget(current_target)
		if not recognizeImage:
			return
		engine = self.getCurrentEngine(current_engine_type)
		if not engine:
			return
		repeatCount = scriptHandler.getLastScriptRepeatCount()
		textResultWhenRepeatGesture = not config.conf["onlineOCR"]["swapRepeatedCountEffect"]
		if repeatCount == 0:
			engine.text_result = textResultWhenRepeatGesture
			imageInfo = RecogImageInfo(0, 0, recognizeImage.width, recognizeImage.height, 1)
			pixels = recognizeImage.tobytes("raw", "BGRX")
			# Translators: Reported when content recognition begins.
			ui.message(_("Recognizing"))
			engine.recognize(pixels, imageInfo, recogUi._recogOnResult)
		elif repeatCount == 1:
			engine.text_result = not textResultWhenRepeatGesture

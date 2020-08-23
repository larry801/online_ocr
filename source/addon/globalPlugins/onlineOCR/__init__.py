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
import six
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
	SOURCE_TYPES, ENGINE_TYPES, COLUMN_SPLIT_TYPES
)
from LayeredGesture import category_name
_ = lambda x: x
# We need to initialize translation and localization support:
addonHandler.initTranslation()

generalConfigSpec = {
	"copyToClipboard": "boolean(default=false)",
	"swapRepeatedCountEffect": "boolean(default=false)",
	"useBrowseableMessage": "boolean(default=false)",
	"verboseDebugLogging": "boolean(default=false)",
	"engineType": 'option("win10OCR", "onlineOCR", "onlineImageDescriber", default="onlineOCR")',
	"sourceType": 'option("navigatorObject", "clipboardImage", "clipboardURL", "wholeDesktop", "foreGroundWindow", default="navigatorObject")',
	"proxyType": 'option("noProxy", "http", "socks", default="noProxy")',
	"proxyAddress": 'string(default="")',
	"notifyIfResizeRequired": "boolean(default=true)",
	"columnSplitMode": 'option("no", "two", "three", default="no")'
}


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
		config.conf.spec["onlineOCRGeneral"] = generalConfigSpec
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
	def script_describeNavigatorObject(self, gesture):
		self.startRecognition("navigatorObject", "onlineImageDescriber")
	
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
		"""
		@type gesture
		"""
		self.startRecognition("clipboardImage", "onlineImageDescribe")
	
	# Translators: OCR command name in input gestures dialog
	full_ocr_msg = _(
		"Recognizes the content of the current navigator object with online OCR engine.")
	
	# Translators: OCR command name in input gestures dialog
	@script(
		description=full_ocr_msg,
		category=category_name,
		gestures=[]
	)
	def script_recognizeWithOnlineOCREngine(self, gesture):
		self.startRecognition("navigatorObject", "onlineOCR")
	
	# Translators: OCR command name in input gestures dialog
	clipboard_ocr_msg = _(
		"Recognizes the text in clipboard images with online OCR engine.")
	
	@script(
		description=clipboard_ocr_msg,
		category=category_name,
		gestures=[]
	)
	def script_recognizeClipboardImageWithOnlineOCREngine(self, gesture):
		self.startRecognition("clipboardImage", "onlineOCR")

	@script(
		# Translators: Online Image Describer command name in input gestures dialog
		description=_("Show previous recognition result, if any."),
		category=category_name,
		gestures=[]
	)
	def script_showPreviousResult(self, gesture):
		import recogHistory
		result = recogHistory.getPreviousResult()
		if result:
			engine = result["engine"]
			engine.text_result = False
			engine.showResult(result["response"])
		else:
			# Translators: Reported when there is no previous result.
			ui.message(_("No previous result"))

	@script(
		# Translators: Online Image Describer command name in input gestures dialog
		description=_("Cancel current recognition if there is any."),
		category=category_name,
		gestures=[]
	)
	def script_cancelCurrentRecognition(self, gesture):
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
		description=_("Recognize image according to engine and source in settings"),
		category=category_name,
		gestures=["kb:NVDA+Alt+R"]
	)
	def script_recognizeAccordingToSettings(self, gestures):
		current_source = config.conf["onlineOCRGeneral"]["sourceType"]
		current_engine_type = config.conf["onlineOCRGeneral"]["engineType"]
		self.startRecognition(
			current_source,
			current_engine_type
		)

	@staticmethod
	def cycleThroughSettings(config_section, config_name, config_list):
		current_source = config_section[config_name]
		available_sources = [name for (name, desc) in config_list]
		current_source_index = available_sources.index(current_source)
		available_source_names = [name for (name, desc) in config_list]
		for source in available_sources:
			source_index = available_sources.index(source)
			if source_index > current_source_index:
				current_source_index = source_index
				current_source = available_sources[current_source_index]
				break
		else:
			current_source_index = 0
			current_source = available_sources[0]
		name = available_source_names[current_source_index]
		config_section[config_name] = current_source
		return name

	@script(
		# Translators: Online Image Describer command name in input gestures dialog
		description=_("Cycle through types of recognition source"),
		category=category_name,
		gestures=[]
	)
	def script_cycleRecognitionEngineType(self, gestures):
		name = self.cycleThroughSettings(
			config.conf["onlineOCRGeneral"],
			"engineType",
			ENGINE_TYPES
		)
		# Translators: Reported when the user cycles through recognition engine type
		# %s will be replaced with the engine type: e.g. Online OCR Windows 10 Offline OCR
		ui.message(_("Recognition engine type: %s") % name)

	@script(
		# Translators: Online Image Describer command name in input gestures dialog
		description=_("Cycle through types of recognition source"),
		category=category_name,
		gestures=[]
	)
	def script_cycleRecognitionTarget(self, gestures):
		name = self.cycleThroughSettings(
			config.conf["onlineOCRGeneral"],
			"sourceType",
			SOURCE_TYPES
		)
		# Translators: Reported when the user cycles through source types
		# which determine source of content recognition
		# %s will be replaced with the source type: e.g. Clipboard image, foreground window
		ui.message(_("Recognition source: %s") % name)

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

	def getImageFromSource(self, current_source):
		if current_source == "clipboardImage":
			recognizeImage = self.getImageFromClipboard()
			imageInfo = RecogImageInfo(0, 0, recognizeImage.width, recognizeImage.height, 1)
			return imageInfo, recognizeImage
		elif current_source == "clipboardURL":
			return None
		elif current_source == "foreGroundWindow":
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
			imageInfo = RecogImageInfo(
				windowRectLTRB.left,
				windowRectLTRB.top,
				windowRectLTRB.width,
				windowRectLTRB.height,
				1
			)
			recognizeImage = ImageGrab.grab((
				windowRectLTRB.top,
				windowRectLTRB.left,
				windowRectLTRB.width,
				windowRectLTRB.height
			))
			return imageInfo, recognizeImage
		elif current_source == "wholeDesktop":
			recognizeImage = ImageGrab.grab()
			imageInfo = RecogImageInfo(0, 0, recognizeImage.width, recognizeImage.height, 1)
			return imageInfo, recognizeImage
		else:
			# Translators: Reported when source is not correct.
			ui.message(_("Unknown source: %s" % current_source))
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

	def startRecognition(self, current_source, current_engine_type):
		engine = self.getCurrentEngine(current_engine_type)
		repeatCount = scriptHandler.getLastScriptRepeatCount()
		textResultWhenRepeatGesture = not config.conf["onlineOCRGeneral"]["swapRepeatedCountEffect"]
		if repeatCount == 0:
			if not engine:
				ui.message(_("Cannot get recognition engine"))
				return
			engine.text_result = textResultWhenRepeatGesture
			if current_source == "navigatorObject":
				recogUi.recognizeNavigatorObject(engine)
				return
			else:
				imageInfo, recognizeImage = self.getImageFromSource(current_source)
				if not recognizeImage:
					ui.message(_("Clipboard URL source is not implemented."))
					return
				pixels = recognizeImage.tobytes("raw", "BGRX")
				# Translators: Reported when content recognition begins.
				ui.message(_("Recognizing"))
				engine.recognize(pixels, imageInfo, recogUi._recogOnResult)
		elif repeatCount == 1:
			engine.text_result = not textResultWhenRepeatGesture

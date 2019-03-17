# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""onlineOCR:
A global plugin that add online ocr to NVDA
"""
from __future__ import unicode_literals
import addonHandler
import globalPluginHandler
import gui
import globalVars
import config
from onlineOCRHandler import CustomOCRPanel
from contentRecog import RecogImageInfo
from scriptHandler import script
from logHandler import log
import ui
from PIL import ImageGrab, Image
import scriptHandler

_ = lambda x: x
# We need to initialize translation and localization support:
addonHandler.initTranslation()
category_name = _(u"Online OCR")


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
        self.lastNavigatorObject = None
        self.autoOCREnabled = False
        from . import onlineOCRHandler
        onlineOCRHandler.CustomOCRHandler.initialize()
        self.handler = onlineOCRHandler.CustomOCRHandler
        gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(CustomOCRPanel)

    # Translators: OCR command name in input gestures dialog
    full_ocr_msg = _(
        "Recognizes the content of the current navigator object with online OCR engine.Then open a virtual result document.")

    # Translators: OCR command name in input gestures dialog
    @script(description=full_ocr_msg,
            category=category_name,
            gestures=["kb:NVDA+shift+r"])
    def script_recognizeWithCustomOcr(self, gesture):
        from contentRecog import recogUi
        engine = onlineOCRHandler.CustomOCRHandler.getCurrentEngine()
        repeatCount = scriptHandler.getLastScriptRepeatCount()
        if repeatCount == 0:
            engine.text_result = True
            recogUi.recognizeNavigatorObject(engine)
        elif repeatCount == 1:
            engine.text_result = False

    # # Translators: OCR command name in input gestures dialog
    # textMsg = _("Recognizes the text of the current navigator object with captcha engine.Then read result.If pressed twice, open a virtual result document.")
    #
    # @script(description=textMsg, category=category_name,
    #         gestures=["kb:NVDA+shift+c"])
    # def script_recognizeCaptcha(self, gesture):
    #     from contentRecog import recogUi
    #     engine = onlineOCRHandler.CustomOCRHandler.getEngineInstance(b"captcha")
    #     repeatCount = scriptHandler.getLastScriptRepeatCount()
    #     if repeatCount == 0:
    #         engine.text_result = True
    #         recogUi.recognizeNavigatorObject(engine)
    #     elif repeatCount >= 1:
    #         engine.text_result = False

    # Translators: OCR command name in input gestures dialog
    clipboard_ocr_msg = _("Recognizes the text in clipboard images with online OCR engine.Then read result.If pressed twice, open a virtual result document.")

    # Translators: Reported when PIL cannot grab image from clipboard
    noImageMessage = _(u"No image in clipboard")

    @script(description=clipboard_ocr_msg,
            category=category_name,
            gestures=["kb:NVDA+alt+r"])
    def script_recognizeClipboardTextWithCustomOcr(self, gesture):
        engine = onlineOCRHandler.CustomOCRHandler.getCurrentEngine()
        repeatCount = scriptHandler.getLastScriptRepeatCount()
        if repeatCount == 0:
            engine.text_result = True
            from PIL import ImageGrab, Image
            clipboardImage = ImageGrab.grabclipboard()
            if clipboardImage:
                imageInfo = RecogImageInfo(0, 0, clipboardImage.width, clipboardImage.height, 1)
                pixels = clipboardImage.tobytes("raw", "BGRX")
                engine.recognize(pixels, imageInfo, None)
            else:
                import win32clipboard
                try:
                    win32clipboard.OpenClipboard()
                    rawData = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
                    log.info(rawData)
                    if isinstance(rawData, tuple):
                        clipboardImage = Image.open(rawData[0])
                        imageInfo = RecogImageInfo(0, 0, clipboardImage.width, clipboardImage.height, 1)
                        clipboardImage = clipboardImage.convert("RGB")
                        pixels = clipboardImage.tobytes("raw", "RGBX")
                        engine.recognize(pixels, imageInfo, None)
                    else:
                        raise RuntimeError
                    win32clipboard.CloseClipboard()
                except RuntimeError as e:
                    log.error(e)
                    ui.message(self.noImageMessage)
        elif repeatCount >= 1:
            engine.text_result = False

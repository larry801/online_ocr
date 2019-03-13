# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from __future__ import unicode_literals
from threading import Thread
import os
import sys
from io import BytesIO
import json
from contentRecog import LinesWordsResult, ContentRecognizer, RecogImageInfo
import base64

try:
    from urllib import urlencode
except ImportError:
    from urllib.urllib_parse import urlencode
from six import iterkeys
from .abstractEngine import AbstractEngineHandler, AbstractEngineSettingsPanel, AbstractEngine, BooleanEngineSetting
import addonHandler
from . import contentRecognizers
from logHandler import log
import ui
from collections import OrderedDict

Base_Dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(Base_Dir, "_contrib"))
from PIL import Image

_ = lambda x: x
addonHandler.initTranslation()


class BaseRecognizer(ContentRecognizer, AbstractEngine):
    """
    Abstract base BaseRecognizer
    """
    nvda_cn_domain = "www.nvdacn.com"
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

    maxSize = 4 * 1024 * 1024  # 4 mega bytes

    @classmethod
    def CopyToClipboardSetting(cls):
        return BaseRecognizer.BooleanSetting(
            "clipboard",
            # Translators: Label in settings
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
        :param boolean:
        :type boolean: bool
        :return:
        """
        if boolean:
            return "true"
        else:
            return "false"

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
        Use ImageGrab instead of bitmap
        @param imageInfo: Information about the image for recognition.
        @type imageInfo: L{RecogImageInfo}
        @return: L{Image}
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
        raise NotImplementedError

    @property
    def _use_own_api_key(self):
        if self._type_of_api_access == "own_key":
            return True
        else:
            return False

    def rgb_quad_to_png(self, pixels, imageInfo, resizeFactor=None):
        """
        :param pixels: The pixels of the image as a two dimensional array of RGBQUADs.
            For example, to get the red value for the coordinate (1, 2):
            pixels[2][1].rgbRed
            This can be treated as raw bytes in BGRA8 format;
            i.e. four bytes per pixel in the order blue, green, red, alpha.
            However, the alpha channel should be ignored.
        :type pixels: Two dimensional array (y then x) of L{winGDI.RGBQUAD}
        :param imageInfo: Information about the image for recognition.
        :type imageInfo: L{RecogImageInfo}
        :return: L{Image}
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
        :param options: request parameters
        :type options: dict
        :return:
        """
        encoded_option = ""
        key_sequence = sorted(iterkeys(options), reverse=False)
        for k in key_sequence:
            query = "&" + urlencode({
                k: options[k]
            })
            encoded_option += query
        payload = encoded_option[1:]
        log.io(payload)
        return payload

    @staticmethod
    def convert_to_json(data):
        return json.loads(data)

    def get_url(self):
        raise NotImplementedError

    def get_domain(self):
        raise NotImplementedError

    def get_payload(self, base64Image):
        raise NotImplementedError

    def checkAndResizeImage(self, pixels, imageInfo):
        pass

    def get_converted_image(self, pixels, imageInfo):
        isImageValid = True
        errorMsg = _(u"Unknown error")
        if self.minWidth > imageInfo or self.minHeight > imageInfo.screenHeight:
            resizeFactor = 5
        else:
            resizeFactor = None
        imageContent = self.rgb_quad_to_png(pixels, imageInfo, resizeFactor)

        if self.maxHeight < imageInfo.screenHeight:
            isImageValid = False
            errorMsg = _(u"Image height is too big")

        if self.maxWidth < imageInfo.screenWidth:
            isImageValid = False
            errorMsg = _(u"Image Width is too big")
        if len(imageContent) > self.maxSize:
            isImageValid = False
            errorMsg = _(u"Image size is too big")
        if isImageValid:
            return base64.standard_b64encode(imageContent)
        else:
            ui.message(errorMsg)
            return False

    def recognize(self, pixels, imageInfo, onResult):
        """
        Setup data for recognition then send request
        :param pixels:
        :param imageInfo:
        :param onResult: Result callback for result viewer
        :return: None
        """

        def callback(result):
            failed_message = _(u"Recognition failed. Result is invalid.")
            result_prefix = _(u"Recognition result:")
            log.io(result)
            api_error_message = self.process_api_result(result)  # type: str
            if api_error_message:
                ui.message(api_error_message)
                return
            try:
                result = self.convert_to_json(result)
            except Exception as e:
                log.error(e)
                log.error(result)
                ui.message(failed_message)
                return
            try:
                resultText = result_prefix + self.extract_text(result)
                if self._clipboard:
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
            self.networkThread = None

        if self.networkThread:
            # Translators: Error message
            ui.message(_(u"Only one recognition can be performed at a time."))
            return
        url = self.get_url()
        domain = self.get_domain()
        imageContent = self.get_converted_image(pixels, imageInfo)
        if not imageContent:
            return
        payloads = self.get_payload(imageContent)
        if self.useHttps:
            protocol = "https:/"
        else:
            protocol = "http:/"
        fullURL = "/".join([
            protocol,
            domain,
            url
        ])
        msg = u"{0}\n{1}\n{2}\n{3}".format(
            callback,
            domain,
            fullURL,
            payloads
        )
        log.io(msg)
        self.sendRequest(callback, fullURL, payloads)

    def sendRequest(self, callback, fullURL, payloads):
        """
        Send async network request
        :param callback:
        :param fullURL:
        :param payloads:
        :return:
        """
        from . import winHttp
        self.networkThread = Thread(
            target=winHttp.postContent,
            args=(
                callback,
                fullURL,
                payloads
            )
        )
        self.networkThread.start()


    @staticmethod
    def extract_text(apiResult):
        pass


    def cancel(self):
        self.networkThread = None


    def terminate(self):
        pass


    def process_api_result(self, result):
        return ""


    _type_of_api_access = "free"


    def _get_accessType(self):
        return self._type_of_api_access


    def _set_accessType(self, type_of_api_access):
        self._type_of_api_access = type_of_api_access


    def _get_availableAccesstypes(self):
        accessTypes = OrderedDict({
            # Translators: How to access online OCR API
            "free": _("Use public api quota"),
            "own_key": _("Use api key registered by yourself"),
        })
        return self.generate_string_settings(accessTypes)


    @classmethod
    def AccessTypeSetting(cls):
        return AbstractEngine.StringSettings(
            "accessType",
            _(u"API Access Type")
        )


    @classmethod
    def BalanceSetting(cls):
        return AbstractEngine.ReadOnlySetting(
            "balance",
            # Translators: Label of OCR API balance control
            _(u"API Balance")
        )


    _balance = -1


    def _get_balance(self):
        return self._balance


    def _set_balance(self, balance):
        self._balance = balance


class CustomOCRHandler(AbstractEngineHandler):
    engineClass = BaseRecognizer
    engineClassName = "BaseRecognizer"
    engineAddonName = "onlineOCR"
    enginePackageName = "contentRecognizers"
    enginePackage = contentRecognizers
    configSectionName = "onlineOCR"
    defaultEnginePriorityList = ["ocrSpace"]


class CustomOCRPanel(AbstractEngineSettingsPanel):
    title = _(u"Online OCR")
    handler = CustomOCRHandler

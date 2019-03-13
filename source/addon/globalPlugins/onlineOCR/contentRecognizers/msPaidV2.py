# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from .. import onlineOCRHandler
import addonHandler
from contentRecog import LinesWordsResult
from logHandler import log
from collections import OrderedDict
import config

_ = lambda x: x
addonHandler.initTranslation()


class CustomContentRecognizer(onlineOCRHandler.BaseRecognizer):
    name = "msPaidV2"

    description = _("Version 2 Paid Microsoft OCR")

    _appID = "5c58426317b54d00577a90ab"

    _api_key = "p959qmy7t92aj29gjwr1l2ypq"

    _type_of_api_access = "own_key"

    def _get_supportedSettings(self):
        return [
            CustomContentRecognizer.AppIDSetting(),
            CustomContentRecognizer.APIKeySetting(),
            CustomContentRecognizer.BalanceSetting(),
        ]

    def refreshBalance(self):
        if self.checkChineseStoreAccess():
            from config import conf
            self._balance = int(
                conf["chinese_nvda_store"]["accountBalance"]
            )
            self.saveSettings()
        else:
            result = self.post_to_url("https://www.nvdacn.com/ocr/userInfo.php",
                                      {
                                          "userId": self._appID,
                                          "sessionToken": self._api_key,
                                      })
            log.io(result)
            import json
            result = json.loads(result)
            try:
                self._balance = result["ocrBalance"]
                self.saveSettings()
            except Exception as e:
                log.error(e)

    _language = "unk"

    def _get_language(self):
        return self._language

    def _set_language(self, language):
        self._language = language

    def _get_availableLanguages(self):
        languages = OrderedDict({
            # Translators: Text language for OCR
            "unk": _(u"Auto Detect"),
            "zh-Hans": _(u"Chinese Simplified"),
            "zh-Hant": _(u"Chinese Traditional"),
            "cs": _(u"Czech"),
            "da": _(u"Danish"),
            "nl": _(u"Dutch"),
            "en": _(u"English"),
            "fi": _(u"Finnish"),
            "fr": _(u"French"),
            "de": _(u"German"),
            "el": _(u"Greek"),
            "hu": _(u"Hungarian"),
            "it": _(u"Italian"),
            "ja": _(u"Japanese"),
            "ko": _(u"Korean"),
            "nb": _(u"Norwegian"),
            "pl": _(u"Polish"),
            "pt": _(u"Portuguese"),
            "ru": _(u"Russian"),
            "es": _(u"Spanish"),
            "sv": _(u"Swedish"),
            "tr": _(u"Turkish"),
            "ar": _(u"Arabic"),
            "ro": _(u"Romanian"),
            "sr-Cyrl": _(u"SerbianCyrillic"),
            "sr-Latn": _(u"SerbianLatin"),
            "sk": _(u"Slovak"),
        })
        return self.generate_string_settings(languages)

    def get_payload(self, base64Image):
        if int(self._balance) < 0:
            self.refreshBalance()
        if self.checkChineseStoreAccess():
            payload = {
                "image": base64Image,
                "userId": config.conf["chinese_nvda_store"]["accountSessionToken"],
                "sessionToken": config.conf["chinese_nvda_store"]["accountSessionToken"],
                "language": self._language,
            }
            from config import conf
            balance = int(
                conf["chinese_nvda_store"]["accountBalance"]
            )
            conf["chinese_nvda_store"]["accountBalance"] = balance - 1
        else:
            payload = {
                "image": base64Image,
                "userId": self.appID,
                "sessionToken": self.apiKey,
                "language": self._language,
            }
            balance = int(self._balance)
            self._balance = balance - 1
            self.saveSettings()
        return payload

    def get_url(self):
        return "ocr/msPaidV2.php"

    def get_domain(self):
        return self.nvda_cn_domain

    def get_full_url(self):
        return "https://www.nvdacn.com/ocr/msPaidV2.php"

    @classmethod
    def check(cls):
        return True
        # return cls.checkChineseStoreAccess()

    def process_api_result(self, result):
        import json
        apiResult = json.loads(result)
        try:
            statusText = apiResult["message"]
            return statusText
        except:
            pass
        try:
            code = apiResult["code"]
            if code == 305:
                # Translators: Error message of Microsoft Cognitive API
                return _(u"Your quota is not adequate")
        except:
            return False

    def convert_to_line_result_format(self, apiResult):
        def extractCoordinate(coord):
            groups = coord.split(',')
            return int(groups[0]), int(groups[1]), int(groups[2]), int(groups[3])

        lineResult = []
        resultSets = apiResult["regions"]
        for result in resultSets:
            for line in result["lines"]:
                currentLine = []
                for word in line['words']:
                    x, y, w, h = extractCoordinate(word["boundingBox"])
                    currentLine.append({
                        "x": x,
                        "y": y,
                        "width": w,
                        "height": h,
                        "text": word["text"]
                    })
                lineResult.append(currentLine)
        log.io(lineResult)
        return lineResult

    @staticmethod
    def extract_text(apiResult):
        words = []
        resultSets = apiResult["regions"]
        for result in resultSets:
            for line in result["lines"]:
                for word in line['words']:
                    words.append(word["text"])
        return u" ".join(words)

    def get_converted_image(self, pixels, imageInfo):
        if self.minWidth > imageInfo or self.minHeight > imageInfo.screenHeight:
            resizeFactor = 5
        else:
            resizeFactor = None
        from PIL import ImageGrab
        img = ImageGrab.grab(bbox=(
            imageInfo.screenLeft,
            imageInfo.screenTop,
            imageInfo.screenLeft + imageInfo.recogWidth,
            imageInfo.screenTop + imageInfo.recogHeight
        ))
        if resizeFactor:
            img = img.resize(resizeFactor)
        from io import BytesIO
        jpg_buffer = BytesIO()
        img.save(jpg_buffer, "jpeg")
        return jpg_buffer.getvalue()

    def recognize(self, pixels, imageInfo, onResult):
        """
        Recognize
        """
        imageContent = self.get_converted_image(pixels, imageInfo)
        if not imageContent:
            return
        payloads = self.get_payload(imageContent)

        def callback(result):
            import ui
            failed_message = _(u"Recognition failed. Result is invalid.")
            internet_error_message = _(u"Recognition failed. Internet connection error.")
            result_prefix = _(u"Recognition result:")
            log.io(result)
            if self.processWinHttpError(result):
                ui.message(internet_error_message)
                return
            api_error_message = self.process_api_result(result)
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
                if self.text_result:
                    ui.message(result_prefix + self.extract_text(result))
                else:
                    onResult(LinesWordsResult(self.convert_to_line_result_format(result), imageInfo))
            except Exception as e:
                log.error(e)
                log.error(result)
                ui.message(failed_message)

        from ..winHttp import postMultipartFormData
        postMultipartFormData(
            "http://localhost:3480/msPaidV2.php",
            # "https://www.nvdacn.com/ocr/msPaidV2.php",
            imageContent,
            callback,
            paramName=self._appID,
            fileName=self._api_key)

# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from __future__ import unicode_literals
from .. import onlineOCRHandler
from logHandler import log
from collections import OrderedDict
import addonHandler

_ = lambda x: x
addonHandler.initTranslation()


class CustomContentRecognizer(onlineOCRHandler.BaseRecognizer):
    api_domain = "api.ocr.space"
    api_url = "parse/image"

    @classmethod
    def check(cls):
        return True

    @staticmethod
    def extract_text(apiResult):
        lineResult = []
        resultSets = apiResult["ParsedResults"]
        for result in resultSets:
            lineResult.append(result["ParsedText"])
        log.io(lineResult)
        return u" ".join(lineResult)

    def convert_to_line_result_format(self, apiResult):
        lineResult = []
        resultSets = apiResult["ParsedResults"]
        for result in resultSets:
            for line in result["TextOverlay"]["Lines"]:
                currentLine = []
                for word in line['Words']:
                    currentLine.append({
                        "x": word["Left"],
                        "y": word["Top"],
                        "width": word["Width"],
                        "height": word["Height"],
                        "text": word["WordText"],
                    })
                lineResult.append(currentLine)
        log.io(lineResult)
        return lineResult

    name = b"ocrSpace"

    description = _("OCR Space")

    _api_key = ""

    def _get_supportedSettings(self):
        return [
            CustomContentRecognizer.AccessTypeSetting(),
            CustomContentRecognizer.LanguageSetting(),
            # Translators: Label for OCR engine settings.
            CustomContentRecognizer.BooleanSetting("scale", _("Scale image for better quality")),
            CustomContentRecognizer.BooleanSetting("detectOrientation", _("Detect image orientation")),
            CustomContentRecognizer.BooleanSetting("isTable", _("Optimize for table recognition")),
            CustomContentRecognizer.APIKeySetting(),
        ]

    _isTable = None

    def _get_isTable(self):
        return self._isTable

    def _set_isTable(self, isTable):
        self._isTable = isTable

    _detectOrientation = None

    def _get_detectOrientation(self):
        return self._detectOrientation

    def _set_detectOrientation(self, detectOrientation):
        self._detectOrientation = detectOrientation

    _scale = False

    def _get_scale(self):
        return self._scale

    def _set_scale(self, scale):
        self._scale = scale

    _language = "eng"

    def _get_language(self):
        return self._language

    def _set_language(self, language):
        self._language = language

    def _get_availableLanguages(self):
        languages = OrderedDict({
            # Translators: Text language for OCR
            "ara": _("Arabic"),
            "bul": _("Bulgarian"),
            "chs": _("Chinese(Simplified)"),
            "cht": _("Chinese(Traditional)"),
            "hrv": _("Croatian"),
            "cze": _("Czech"),
            "dan": _("Danish"),
            "dut": _("Dutch"),
            "eng": _("English"),
            "fin": _("Finnish"),
            "fre": _("French"),
            "ger": _("German"),
            "gre": _("Greek"),
            "hun": _("Hungarian"),
            "kor": _("Korean"),
            "ita": _("Italian"),
            "jpn": _("Japanese"),
            "pol": _("Polish"),
            "por": _("Portuguese"),
            "rus": _("Russian"),
            "slv": _("Slovenian"),
            "spa": _("Spanish"),
            "swe": _("Swedish"),
            "tur": _("Turkish")
        })
        return self.generate_string_settings(languages)

    def get_payload(self, png_string, text_only=False):
        base64_image = "data:image/png;base64," + png_string
        if text_only:
            isOverlayRequired = False
        else:
            isOverlayRequired = True
        payload = {
            "base64Image": base64_image,
            "filetype": "PNG",
            "isTable": self.pyBool2json(self._isTable),
            "detectOrientation": self.pyBool2json(self._detectOrientation),
            "language": self._language,
            "isOverlayRequired": self.pyBool2json(isOverlayRequired)
        }
        if self._use_own_api_key:
            payload["apikey"] = self._api_key
        return payload

    def get_domain(self):
        if self._use_own_api_key:
            return self.api_domain
        else:
            return self.nvda_cn_domain

    def get_url(self):
        if self._use_own_api_key:
            return self.api_url
        else:
            return "ocr/ocrSpace.php"

    def process_api_result(self, result):
        import json
        apiResult = json.loads(result)
        try:
            code = apiResult["OCRExitCode"]
            return self.codeToErrorMessage[code]
        except KeyError:
            return False

    codeToErrorMessage = {
        3: _(u"Image parsing failed."),
        4: _(u"A fatal error occurs during parsing )."),
    }

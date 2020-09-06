# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from onlineOCRHandler import BaseRecognizer
import addonHandler
import hashlib, hmac, json, os, sys, time
from datetime import datetime
from six.moves.urllib_parse import urlencode
from six import iterkeys
from logHandler import log
from collections import OrderedDict

_ = lambda x: x
addonHandler.initTranslation()


class CustomContentRecognizer(BaseRecognizer):
    name = b"tencentCloudOCR"
    api_domain = b"ocr.tencentcloudapi.com"
    api_url = ""
    # Translators: Description of Online OCR Engine
    description = _(u"Tencent Cloud OCR")
    maxSize = 7 * 1024 * 1024

    minWidth = 20

    minHeight = 15

    def __init__(self):
        self.onResult = None

    @classmethod
    def check(cls):
        return True

    uploadBase64EncodeImage = True

    def _get_supportedSettings(self):
        return [
            CustomContentRecognizer.AccessTypeSetting(),
            CustomContentRecognizer.AppIDSetting(),
            CustomContentRecognizer.APIKeySetting(),
            CustomContentRecognizer.LanguageSetting(),
        ]

    _language = "auto"

    def _get_language(self):
        return self._language

    def _set_language(self, language):
        self._language = language

    _region = "na-toronto"

    def _get_region(self):
        return self._region

    def _set_region(self, region):
        self._region = region

    def _get_availableRegions(self):
        regions = OrderedDict({
            "ap-beijing": _("Beijing, China"),
            "ap-guangzhou": _("Guangzhou, China"),
            "ap-shanghai": _("Shanghai, China"),
            "ap-hongkong": _("Hong Kong, China"),
            "na-toronto": _("Toronto, Canada"),
        })
        return regions

    def _get_availableLanguages(self):
        languages = OrderedDict({
            # Translators: Text language for OCR
            "zh": _("Chinese and English"),
            # Translators: Text language for OCR
            "auto": _("Detect automatically"),
            # Translators: Text language for OCR
            "jpa": _("Japanese"),
            # Translators: Text language for OCR
            "kor": _("Korean"),

            # Translators: Text language for OCR
            "spa": _("Spanish"),
            # Translators: Text language for OCR
            "fre": _("French"),
            # Translators: Text language for OCR
            "ger": _("German"),
            # Translators: Text language for OCR
            "por": _("Portuguese"),

            # Translators: Text language for OCR
            "vie": _("Vietnamese"),
            # Translators: Text language for OCR
            "may": _("Malay Language"),
            # Translators: Text language for OCR
            "rus": _("Russian"),
            # Translators: Text language for OCR
            "ita": _("Italian"),

            # Translators: Text language for OCR
            "hol": _("Dutch"),
            # Translators: Text language for OCR
            "swe": _("Swedish"),
            # Translators: Text language for OCR
            "fin": _("Finnish"),
            # Translators: Text language for OCR
            "dan": _("Danish"),

            # Translators: Text language for OCR
            "nor": _("Norwegian"),
            # Translators: Text language for OCR
            "hun": _("Hungarian"),
            # Translators: Text language for OCR
            "tha": _("Tai"),
            # Translators: Text language for OCR
            "lat": _("Latin"),
        })
        return self.generate_string_settings(languages)

    def get_domain(self):
        if self._use_own_api_key:
            return b'ocr.tencentcloudapi.com'
        else:
            return b"www.nvdacn.com"

    def get_url(self):
        if self._use_own_api_key:
            return b''
        else:
            return b'/ocr/tencentCloudOCR.php'

    def getPayload(self, image):
        return {
            "ImageBase64": image,
            "LanguageType": self._language
        }

    def getHTTPHeaders(self, imageData):
        if self._use_own_api_key:
            service = "ocr"
            host = "ocr.tencentcloudapi.com"
            endpoint = "https://" + host
            region = self._region
            action = "GeneralBasicOCR"
            version = '2018-11-19'
            algorithm = "TC3-HMAC-SHA256"
            timestamp = int(time.time())
            date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")
            params = self.getPayload(imageData)
            http_request_method = "POST"
            canonical_uri = "/"
            canonical_querystring = ""
            ct = "application/json; charset=utf-8"
            payload = json.dumps(params)
            canonical_headers = "content-type:%s\nhost:%s\n" % (ct, host)
            signed_headers = "content-type;host"
            hashed_request_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            canonical_request = (http_request_method + "\n" +
                                 canonical_uri + "\n" +
                                 canonical_querystring + "\n" +
                                 canonical_headers + "\n" +
                                 signed_headers + "\n" +
                                 hashed_request_payload)
            credential_scope = date + "/" + service + "/" + "tc3_request"
            hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
            string_to_sign = (algorithm + "\n" +
                              str(timestamp) + "\n" +
                              credential_scope + "\n" +
                              hashed_canonical_request)
            secret_date = self.sign(("TC3" + self._api_key).encode("utf-8"), date)
            secret_service = self.sign(secret_date, service)
            secret_signing = self.sign(secret_service, "tc3_request")
            signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

            return {
                'Authorization': signature,
                'Content-Type': 'application/json; charset=utf-8',
                'X-TC-Action': action,
                'X-TC-Timestamp': str(timestamp),
                'X-TC-Version': version,
                'X-TC-Region': region,
            }
        else:
            return {}

    @staticmethod
    def sign(key, msg):
        return hmac.new(
            key,
            msg.encode("utf-8"),
            hashlib.sha256
        ).digest()

    def process_api_result(self, result):
        try:
            rep = self.convert_to_json(result)["Response"]
        except KeyError:
            log.debugWarning(result)
            return _("Cannot convert to json")
        if "Error" in rep:
            return rep["Error"]["Message"]
        else:
            return False

    def convert_to_line_result_format(self, apiResult):
        lineResult = []
        height = apiResult["Response"]["TextDetections"][0]["ItemPolygon"]["Y"]
        wordResult = []
        for words in apiResult["Response"]["TextDetections"]:
            newHeight = words["ItemPolygon"]["Y"]
            if newHeight > height:
                height = newHeight
                lineResult.append(wordResult)
                wordResult = []
            wordResult.append({
                "x": words["ItemPolygon"]["X"],
                "y": words["ItemPolygon"]["Y"],
                "width": words["ItemPolygon"]["Width"],
                "height": words["ItemPolygon"]["Height"],
                "text": words["DetectedText"],
            })
        lineResult.append(wordResult)
        log.io(lineResult)
        return lineResult

    def extract_text(self, apiResult):
        words = []
        for items in apiResult["Response"]["TextDetections"]:
            words.append(items["DetectedText"])
        log.io(words)
        return u" ".join(words)

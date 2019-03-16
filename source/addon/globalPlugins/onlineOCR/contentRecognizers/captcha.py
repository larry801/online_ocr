# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from __future__ import unicode_literals
from .. import onlineOCRHandler
import addonHandler
from logHandler import log
from collections import OrderedDict

_ = lambda x: x  # type: callable
addonHandler.initTranslation()


class CustomContentRecognizer(onlineOCRHandler.BaseRecognizer):

    def process_api_result(self, result):
        """

        @param result: raw API result from urllib3
        @type result: str
        @return:
        @rtype: bool or str
        """
        groups = result.split('|')
        if groups[1] == "ERROR":
            return groups[2]
        else:
            return False

    def convert_to_line_result_format(self, apiResult):
        pass

    def get_domain(self):
        if self._use_own_api_key:
            self.useHttps = False
            return "api.captchadecoder.com"
        else:
            self.useHttps = True
            return self.nvda_cn_domain

    def _get_supportedSettings(self):
        return [
            CustomContentRecognizer.AccessTypeSetting(),
            CustomContentRecognizer.APIKeySetting(),
            CustomContentRecognizer.BalanceSetting(),
        ]

    name = b"captcha"

    # Translators: Description of Online OCR Engine
    description = _("Captcha Solving")

    def get_url(self):
        if self._use_own_api_key:
            return "decode"
        else:
            return "ocr/captchaDecode.php"

    def getPayload(self, image):
        fileName = "captcha.png"
        if self._use_own_api_key:
            payload = {
                "key": self._api_key,
                "method": "solve",
                "captcha": (fileName, image),
            }
        else:
            payload = {
                "captcha": (fileName, image),
            }
        return payload

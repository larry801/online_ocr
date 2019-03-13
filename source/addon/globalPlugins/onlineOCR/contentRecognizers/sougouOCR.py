# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from .. import onlineOCRHandler
import addonHandler
from contentRecog import LinesWordsResult, ContentRecognizer, RecogImageInfo
import hashlib
from six.moves.urllib_parse import urlencode
from six import iterkeys
from logHandler import log

_ = lambda x: x
addonHandler.initTranslation()


class CustomContentRecognizer(onlineOCRHandler.BaseRecognizer):
    name = "sougouOCR"

    description = _("Sougou AI OCR")

    def _get_supportedSettings(self):
        return []

    @classmethod
    def check(cls):
        return True

    def process_api_result(self, result):
        import json
        try:
            apiResult = json.loads(result)
            code = apiResult["success"]
            if code != 1:
                # Translators: Error message of sougou API
                return _(u"Sougou API error occurred. Recognition failed")
        except Exception as e:
            log.error(e)
            return False
        try:
            statusText = apiResult["statusText"]
            return statusText
        except:
            return False

    def get_converted_image(self, pixels, imageInfo):
        from PIL import ImageGrab
        img = ImageGrab.grab(bbox=(
            imageInfo.screenLeft,
            imageInfo.screenTop,
            imageInfo.screenLeft + imageInfo.recogWidth,
            imageInfo.screenTop + imageInfo.recogHeight
        ))
        from io import BytesIO
        jpg_buffer = BytesIO()
        img.save(jpg_buffer, "jpeg")
        return jpg_buffer.getvalue()

    def get_domain(self):
        if self._use_own_api_key:
            return "api.ai.sogou.com"
        else:
            return self.nvda_cn_domain

    useHttps = False

    def get_url(self):
        if self._use_own_api_key:
            return "pub/ocr"
        else:
            return "ocr/sougou.php"

    @staticmethod
    def calculate_signature(options, app_key):
        """
        generate signature for API
        :param app_key: API secret key
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
        encoded_option += "&app_key="
        encoded_option += app_key
        encoded_option = encoded_option[1:]
        md5 = hashlib.md5()
        md5.update(encoded_option)
        return md5.hexdigest()

    def get_payload(self, base64Image):
        return base64Image

    def sendRequest(self, callback, fullURL, payloads):
        from ..winHttp import multipartFormData
        from threading import Thread

        if self._use_own_api_key:
            fileName = self.getImageFileName()
            paramName = fileName
            headers = {
                "Authorization": self.getSignature(self._api_key, self._api_secret_key, "")
            }
            fullURL = "https://api.cognitive.azure.cn/vision/v1.0/describe"
        else:
            headers = None
            fullURL = "https://www.nvdacn.com/ocr/msdesc.php"
            paramName = 'foo'
            fileName = 'foo'
        self.networkThread = Thread(
            target=multipartFormData,
            args=(
                fullURL,
                payloads,
                callback,
                headers,
                paramName,
                fileName
            )
        )
        self.networkThread.start()

    def convert_to_line_result_format(self, apiResult):
        def extractCoordinate(coord):
            groups = coord.split(',')
            return int(groups[0]), int(groups[1])

        lineResult = []
        for items in apiResult[u"result"]:
            rightXCoord, yCoord = extractCoordinate(items[u"frame"][1])
            xCoord, downYCoord = extractCoordinate(items[u"frame"][2])
            lineResult.append([{
                "x": xCoord,
                "y": yCoord,
                "width": rightXCoord - xCoord,
                "height": downYCoord - yCoord,
                "text": items[u"content"],
            }])
        log.io(lineResult)
        return lineResult

    @staticmethod
    def extract_text(apiResult):
        words = []
        for items in apiResult[u"result"]:
            words.append(items[u"content"])
            log.io(items[u"content"])
        return u" ".join(words)

    @staticmethod
    def getSignature(ak, sk, url, method='POST'):
        import hashlib
        import time
        import hmac
        import base64
        pre = "sac-auth-v1/" + ak + '/' + str(int(time.time())) + "/3600"
        part2 = "\nPOST\napi.ai.sogou.com\n/pub/ocr\n"
        message = bytes(pre + part2)
        signature = hmac.new(bytes(sk), message, digestmod=hashlib.sha256).digest()
        headerSig = pre + '/' + base64.b64encode(signature)
        log.io(headerSig)
        return headerSig

    @staticmethod
    def getImageFileName():
        import time
        fNList = []
        ts = str(time.time())
        fNList.append(ts)
        fNList.append('_')

        def luhn_residue(digits):
            return sum(sum(divmod(int(d) * (1 + i % 2), 10))
                       for i, d in enumerate(digits[::-1])) % 10

        def getImei(N):
            import random
            part = ''.join(str(random.randrange(0, 9)) for _ in range(N - 1))
            res = luhn_residue('{}{}'.format(part, 0))
            return '{}{}'.format(part, -res % 10)

        import hashlib
        m = hashlib.md5()
        m.update(str(getImei(15)))
        fNList.append(m.hexdigest())
        fNList.append('_fyj.jpg')
        return "".join(fNList)

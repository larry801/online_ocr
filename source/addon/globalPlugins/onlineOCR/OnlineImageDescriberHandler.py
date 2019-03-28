# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# coding=utf-8
# urllib3 used in this file is Copyright (c) 2008-2019 Andrey Petrov and contributors under MIT license.
from __future__ import unicode_literals
from .abstractEngine import (
    AbstractEngineHandler, AbstractEngineSettingsPanel
)
from onlineOCRHandler import  BaseRecognizer
import addonHandler
from . import imageDescribers
from logHandler import log


_ = lambda x: x
addonHandler.initTranslation()


class BaseDescriber(BaseRecognizer):
    """
    Abstract base BaseDescriber for image description
    """

    configSectionName = "onlineImageDescriber"
    
    
class OnlineImageDescriberHandler(AbstractEngineHandler):
    engineClass = BaseDescriber
    engineClassName = "BaseDescriber"
    engineAddonName = "onlineImageDescriber"
    enginePackageName = "imageDescribers"
    enginePackage = imageDescribers
    configSectionName = "onlineImageDescriber"
    defaultEnginePriorityList = ["machineLearning"]
    configSpec = {
        "engine": "string(default=auto)",
        "copyToClipboard": "boolean(default=false)",
        "swapRepeatedCountEffect": "boolean(default=false)",
        "verboseDebugLogging": "boolean(default=false)",
        "proxyType": 'option("noProxy", "http", "socks", default="noProxy")',
        "proxyAddress": 'string(default="")',
    }


class OnlineImageDescriberPanel(AbstractEngineSettingsPanel):
    title = _(u"Online Image Describer")
    handler = OnlineImageDescriberHandler

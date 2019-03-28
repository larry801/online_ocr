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




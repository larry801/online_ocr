# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from __future__ import unicode_literals
from __future__ import absolute_import
import gui
import wx
from gui.settingsDialogs import InputGesturesDialog
from inputCore import (
	GlobalGestureMap,
	_AllGestureMappingsRetriever,
)
import addonHandler
from logHandler import log
from baseObject import ScriptableObject
import baseObject
import os
import globalVars
from .onlineOCRHandler import safeJoin

_ = lambda x: x
# We need to initialize translation and localization support:
addonHandler.initTranslation()
# Translators: Name of addon script category
category_name = _(u"Online Image Describer")
# Translators: Name of script prefix category
SCRCAT_PREFIX = _("Prefix for sequential gesture")
# class AddonGestureMap(GlobalGestureMap):
#
# 	def load(self, filename):
# 		self.fileName = filename
# 		try:
# 			conf = configobj.ConfigObj(filename, file_error=True, encoding="UTF-8")
# 		except (configobj.ConfigObjError, UnicodeDecodeError) as e:
# 			log.warning("Error in gesture map '%s': %s" % (filename, e))
# 			self.lastUpdateContainedError = True
# 			return
# 		self.update(conf)
#

secondaryGestureMap = None


class AddonGestureMapRetriever(_AllGestureMappingsRetriever):

	def addObj(self, obj, isAncestor=False):
		"""

		@param obj:
		@type obj: ScriptableObject
		@param isAncestor:
		@type isAncestor:
		@return:
		@rtype:
		"""
		scripts = {}
		for cls in obj.__class__.__mro__:
			for scriptName, script in cls.__dict__.iteritems():
				if not scriptName.startswith("script_"):
					continue
				if isAncestor and not getattr(script, "canPropagate", False):
					continue
				scriptName = scriptName[7:]
				try:
					scriptInfo = self.scriptInfo[cls, scriptName]
				except KeyError:
					scriptInfo = self.makeNormalScriptInfo(cls, scriptName, script)
					if not scriptInfo:
						continue
					self.addResult(scriptInfo)
				scripts[script] = scriptInfo
		for gesture, script in obj._gestureMap.iteritems():
			try:
				scriptInfo = scripts[script.__func__]
			except KeyError:
				continue
			key = (scriptInfo.cls, gesture)
			if key in self.handledGestures:
				continue
			self.handledGestures.add(key)

	def __init__(self, obj, ancestors):
		self.results = {}
		self.scriptInfo = {}
		self.handledGestures = set()

		self.addGlobalMap(secondaryGestureMap)
		import braille
		gmap = braille.handler.display.gestureMap
		if gmap:
			self.addGlobalMap(gmap)
		if isinstance(braille.handler.display, baseObject.ScriptableObject):
			self.addObj(braille.handler.display)

		# Global plugins.
		import globalPluginHandler
		for plugin in globalPluginHandler.runningPlugins:
			self.addObj(plugin)


def loadAddonGestureMap():
	global secondaryGestureMap
	if not secondaryGestureMap:
		secondaryGestureMap = GlobalGestureMap()
		mapPath = safeJoin(globalVars.appArgs.configPath, u"onlineImageDescriberGestures.ini")
		defaultMapPath = safeJoin(os.path.dirname(__file__), u"defaultGestures.ini")
		if os.path.exists(mapPath):
			secondaryGestureMap.load(mapPath)
		else:
			secondaryGestureMap.load(defaultMapPath)
			secondaryGestureMap.fileName = mapPath
			secondaryGestureMap.save()


class LayeredGestureDialog(InputGesturesDialog):

	def makeSettings(self, settingsSizer):
		super(LayeredGestureDialog, self).makeSettings(settingsSizer)
		self.gestures = AddonGestureMapRetriever(
			gui.mainFrame.prevFocus,
			gui.mainFrame.prevFocusAncestors).results
		newResult = {}
		for x in self.gestures:
			if x == category_name:
				newResult[x] = self.gestures[x]
		self.gestures = newResult
		self.tree.DeleteChildren(self.treeRoot)
		self.populateTree()

	def onOk(self, evt):
		log.io(self.pendingAdds)
		log.io(self.pendingRemoves)
		for gesture, module, className, scriptName in self.pendingRemoves:
			try:
				secondaryGestureMap.remove(gesture, module, className, scriptName)
			except ValueError:
				# The user wants to unbind a gesture they didn't define.
				secondaryGestureMap.add(gesture, module, className, None)

		for gesture, module, className, scriptName in self.pendingAdds:
			try:
				# The user might have unbound this gesture,
				# so remove this override first.
				secondaryGestureMap.remove(gesture, module, className, None)
			except ValueError:
				pass
			secondaryGestureMap.add(gesture, module, className, scriptName)

		if self.pendingAdds or self.pendingRemoves:
			# Only save if there is something to save.
			try:
				secondaryGestureMap.save()
			except:
				log.debugWarning("", exc_info=True)
				# Translators: An error displayed when saving user defined input gestures fails.
				gui.messageBox(
					_(u"Error saving user defined gestures - probably read only file system."),
					_(u"Error"), wx.OK | wx.ICON_ERROR)

		super(InputGesturesDialog, self).onOk(evt)


def onAddonInputGestureDialog(evt):
	from gui import mainFrame
	mainFrame._popupSettingsDialog(LayeredGestureDialog)

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
import configobj
import addonHandler
from logHandler import log
from baseObject import ScriptableObject
import os
import globalVars
from .onlineOCRHandler import safeJoin
import inputCore

_ = lambda x: x
# We need to initialize translation and localization support:
addonHandler.initTranslation()
# Translators: Name of addon script category
category_name = _(u"Online Image Describer")


class AddonCommands(ScriptableObject):
	pass



class AddonGestureMap(GlobalGestureMap):

	def load(self, filename):
		self.fileName = filename
		try:
			conf = configobj.ConfigObj(filename, file_error=True, encoding="UTF-8")
		except (configobj.ConfigObjError, UnicodeDecodeError) as e:
			log.warning("Error in gesture map '%s': %s" % (filename, e))
			self.lastUpdateContainedError = True
			return
		self.update(conf)

	def __init__(self):
		super(AddonGestureMap, self).__init__()
		allEntries = inputCore.manager.getAllGestureMappings(
			obj=gui.mainFrame.prevFocus, ancestors=gui.mainFrame.prevFocusAncestors
		)
		log.info(allEntries)
		# addonEntries = allEntries[category_name]
		# self.fileName = safeJoin(
		# 	globalVars.appArgs.configPath,
		# 	"onlineImageDescriberGestures.ini"
		# )
		# log.debug(addonEntries)
		# if os.path.exists(self.fileName):
		# 	self.load(self.fileName)
		# else:
		# 	self.save()


class AddonGestureMapRetriever(_AllGestureMappingsRetriever):

	def __init__(self):
		self.results = {}
		self.scriptInfo = {}
		self.handledGestures = set()
		self.addGlobalMap(addonGestureMap)

	def addGlobalPluginObj(self, obj, isAncestor=False):
		pass


addonGestureMap = AddonGestureMap()
defaultAddonGestureMap = AddonGestureMap()


def loadAddonGestureMap():
	global addonGestureMap, defaultAddonGestureMap
	if not addonGestureMap:
		mapPath = safeJoin(globalVars.appArgs.configPath, u"onlineImageDescriberGestures.ini")
		if os.path.exists(mapPath):
			addonGestureMap.load(mapPath)
		else:
			allEntries = inputCore.manager.getAllGestureMappings(
				obj=gui.mainFrame.prevFocus, ancestors=gui.mainFrame.prevFocusAncestors
			)
			addonEntries = allEntries[category_name]
			entries = {
				category_name: allEntries[category_name]
			}
			addonGestureMap.add(entries)
			addonGestureMap.save()


class LayeredGestureDialog(InputGesturesDialog):

	def makeSettings(self, settingsSizer):
		super(LayeredGestureDialog, self).makeSettings(settingsSizer)
		log.io(self.gestures)
		self.gestures = AddonGestureMapRetriever().results
		log.io(self.gestures)
		allEntries = inputCore.manager.getAllGestureMappings(
			obj=gui.mainFrame.prevFocus, ancestors=gui.mainFrame.prevFocusAncestors
		)
		addonEntries = allEntries[category_name]
		log.debug(addonEntries)

	def onOk(self, evt):
		log.io(self.pendingAdds)
		log.io(self.pendingRemoves)
		for gesture, module, className, scriptName in self.pendingRemoves:
			try:
				addonGestureMap.remove(gesture, module, className, scriptName)
			except ValueError:
				# The user wants to unbind a gesture they didn't define.
				addonGestureMap.add(gesture, module, className, None)

		for gesture, module, className, scriptName in self.pendingAdds:
			try:
				# The user might have unbound this gesture,
				# so remove this override first.
				addonGestureMap.remove(gesture, module, className, None)
			except ValueError:
				pass
			addonGestureMap.add(gesture, module, className, scriptName)

		if self.pendingAdds or self.pendingRemoves:
			# Only save if there is something to save.
			try:
				addonGestureMap.save()
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

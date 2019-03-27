# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
import gui
import wx
from gui.settingsDialogs import InputGesturesDialog
from inputCore import (
	GlobalGestureMap, _AllGestureMappingsRetriever
)
import addonHandler
from logHandler import log
import os
import globalVars
from onlineOCRHandler import safeJoin
import inputCore
_ = lambda x: x
# We need to initialize translation and localization support:
addonHandler.initTranslation()
# Translators: Name of addon script category
category_name = _(u"Online Image Describer")


class AddonGestureMap(GlobalGestureMap):
	
	def __init__(self):
		addonEntries = inputCore.manager.getAllGestureMappings(
			obj=gui.mainFrame.prevFocus, ancestors=gui.mainFrame.prevFocusAncestors
		)
		# super(AddonGestureMap, self).__init__(entries={
		# 	category_name: addonEntries[category_name]
		# })
		# self.add(
		# 	"kb:a",
		# 	"globalPlugins.onlineOCR",
		# 	"GlobalPlugin",
		# 	"describeNavigatorObject"
		# )


class AddonGestureMapRetriever(_AllGestureMappingsRetriever):
	
	def __init__(self):
		self.results = {}
		self.scriptInfo = {}
		self.handledGestures = set()
		self.addGlobalMap(addonGestureMap)


addonGestureMap = AddonGestureMap()


def loadAddonGestureMap():
	global addonGestureMap
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

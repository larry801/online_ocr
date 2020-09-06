# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
import six
from gui.nvdaControls import CustomCheckListBox
import wx
import winUser


class EngineSettingChanger(object):
	"""Functor which acts as callback for GUI events."""
	
	def __init__(self, setting, engine):
		self.engine = engine
		self.setting = setting
	
	def __call__(self, evt):
		evt.Skip()  # allow other handlers to also process this event.
		val = evt.GetSelection()
		setattr(self.engine, self.setting.name, val)


class TextInputEngineSettingChanger(EngineSettingChanger):
	"""Same as L{EngineSettingChanger} but handles TextCtrl events."""
	
	def __call__(self, evt):
		setattr(self.engine, self.setting.name, evt.GetString())


class StringEngineSettingChanger(EngineSettingChanger):
	"""Same as L{EngineSettingChanger} but handles combobox events."""
	
	def __init__(self, setting, engine, panel):
		self.panel = panel
		super(StringEngineSettingChanger, self).__init__(setting, engine)
	
	def __call__(self, evt):
		if six.PY2:
			newValue = getattr(self.panel, "_%ss" % self.setting.name)[evt.GetSelection()].ID
		elif six.PY3:
			newValue = list(getattr(self.panel, "_%ss" % self.setting.name))[evt.GetSelection()].id
		setattr(
			self.engine, self.setting.name, newValue
		)


class VoiceSettingsSlider(wx.Slider):
	
	def __init__(self, *args, **kwargs):
		super(VoiceSettingsSlider, self).__init__(*args, **kwargs)
		self.Bind(wx.EVT_CHAR, self.onSliderChar)
	
	def SetValue(self, i):
		i = int(i)
		super(VoiceSettingsSlider, self).SetValue(i)
		evt = wx.CommandEvent(wx.wxEVT_COMMAND_SLIDER_UPDATED, self.GetId())
		evt.SetInt(i)
		self.ProcessEvent(evt)
		# HACK: Win events don't seem to be sent for certain explicitly set values,
		# so send our own win event.
		# This will cause duplicates in some cases, but NVDA will filter them out.
		winUser.user32.NotifyWinEvent(
			winUser.EVENT_OBJECT_VALUECHANGE, self.Handle, winUser.OBJID_CLIENT,
			winUser.CHILDID_SELF)
	
	def onSliderChar(self, evt):
		key = evt.KeyCode
		if key == wx.WXK_UP:
			newValue = min(self.Value + self.LineSize, self.Max)
		elif key == wx.WXK_DOWN:
			newValue = max(self.Value - self.LineSize, self.Min)
		elif key == wx.WXK_PAGEUP:
			newValue = min(self.Value + self.PageSize, self.Max)
		elif key == wx.WXK_PAGEDOWN:
			newValue = max(self.Value - self.PageSize, self.Min)
		elif key == wx.WXK_HOME:
			newValue = self.Max
		elif key == wx.WXK_END:
			newValue = self.Min
		else:
			evt.Skip()
			return
		self.SetValue(newValue)


class CheckListEngineSettingChanger(EngineSettingChanger):
	
	def __init__(self, setting, engine, checkListBox):
		"""
		EngineSettingChanger for CheckListBoxSettings
		@param setting:
		@type setting:
		@param engine:
		@type engine:
		@param checkListBox: ListBox of settings
		@type checkListBox:  CustomCheckListBox
		"""
		super(CheckListEngineSettingChanger, self).__init__(setting, engine)
		self.checkList = checkListBox
	
	def __call__(self, evt):
		itemIndices = self.checkList.GetCheckedStrings()
		availableSettings = getattr(self.engine, "available%ss" % self.setting.name.capitalize())
		if six.PY2:
			descToParamID = {
				availableSettings[x].name: availableSettings[x].ID
				for x in availableSettings
			}
		elif six.PY3:
			descToParamID = {
				availableSettings[x].displayName: availableSettings[x].id
				for x in availableSettings
			}
		result = [descToParamID[x] for x in itemIndices]
		setattr(self.engine, self.setting.name, result)
		evt.Skip()


class EngineSetting(object):
	"""
	Represents an engine setting such as language or region
	"""
	configSpec = "string(default=None)"
	
	def __init__(self, name, displayNameWithAccelerator, availableInEngineSettingsRing=True, displayName=None):
		self.name = name
		self.displayNameWithAccelerator = displayNameWithAccelerator
		if not displayName:
			# Strip accelerator from displayNameWithAccelerator.
			displayName = displayNameWithAccelerator.replace("&", "")
		self.displayName = displayName
		self.availableInEngineSettingsRing = availableInEngineSettingsRing


class TextInputEngineSetting(EngineSetting):
	"""
	Represents an engine setting such as API_KEY or API_SECRET.
	"""
	pass


class ReadOnlyEngineSetting(EngineSetting):
	"""
	Represents a read only engine setting such as remaining API quota
	"""
	pass


class NumericEngineSetting(EngineSetting):
	"""Represents a numeric engine setting such as image quality."""
	configSpec = "integer(default=50,min=0,max=100)"
	
	def __init__(
		self, name, displayNameWithAccelerator, availableInEngineSettingsRing=True, minStep=1, normalStep=5,
		largeStep=10, displayName=None):
		"""
		@param minStep: Specifies the minimum step between valid values for each numeric setting. For example, if L{minStep} is set to 10, setting values can only be multiples of 10; 10, 20, 30, etc.
		@type minStep: int
		@param normalStep: Specifies the step between values that a user will normally prefer. This is used in the settings ring.
		@type normalStep: int
		@param largeStep: Specifies the step between values if a large adjustment is desired. This is used for pageUp/pageDown on sliders in the Voice Settings dialog.
		@type largeStep: int
		@note: If necessary, the step values will be normalised so that L{minStep} <= L{normalStep} <= L{largeStep}.
		"""
		super(NumericEngineSetting, self).__init__(
			name, displayNameWithAccelerator,
			availableInEngineSettingsRing=availableInEngineSettingsRing,
			displayName=displayName)
		self.minStep = minStep
		self.normalStep = max(normalStep, minStep)
		self.largeStep = max(largeStep, self.normalStep)


class BooleanEngineSetting(EngineSetting):
	"""Represents a boolean engine setting such as whether to detect language automatically.
	"""
	configSpec = "boolean(default=False)"
	
	def __init__(self, name, displayNameWithAccelerator, availableInEngineSettingsRing=False, displayName=None):
		super(BooleanEngineSetting, self).__init__(
			name,
			displayNameWithAccelerator,
			availableInEngineSettingsRing=availableInEngineSettingsRing,
			displayName=displayName
		)


class CheckListEngineSetting(EngineSetting):
	"""
	Represents an engine setting for a series of optional features
	with sequence, such as entries in a weather forecast
	"""
	configSpec = "list(default=None)"


class ButtonEngineSetting(EngineSetting):
	"""
	Represents an engine setting which should be changed
	in another dialog activated by a button
	"""
	configSpec = "list(default=None)"

# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
import pkgutil
import baseObject
from gui.settingsDialogs import SettingsPanel, SettingsDialog
from gui import guiHelper
import gui
import wx
from synthDriverHandler import StringParameterInfo
from wx.lib.expando import ExpandoTextCtrl
import winUser
import config
import addonHandler
import inspect
from logHandler import log

_ = lambda x: x
addonHandler.initTranslation()


# noinspection PyBroadException
class AbstractEngineHandler(object):
    """
    Handlers for OCR / Translation / Weather Data Provider Engines
    Following properties must be specified before use.
    engineAddonName
    enginePackageName
    enginePackage
    configSectionName
    engineClass
    engineClassName
    You should also provide defaultEnginePriorityList if you need fallback behaviour like SynthEngine in NVDA.
    """

    engine_list = None
    engineAddonName = None
    enginePackageName = None
    enginePackage = None
    configSectionName = None
    engineClass = None
    engineClassName = None

    currentEngine = None
    engine_class_list = None
    defaultEnginePriorityList = ['empty']

    @classmethod
    def initialize(cls):
        cls.init_config()
        cls.get_engine_list()
        try:
            engine_name = config.conf[cls.configSectionName]["engine"]
            cls.set_current_engine(engine_name)
        except:
            pass

    @classmethod
    def init_config(cls):
        try:
            conf = config.conf[cls.configSectionName]
        except KeyError:
            config.conf[cls.configSectionName] = {}
            config.conf[cls.configSectionName]["engine"] = cls.defaultEnginePriorityList[0]

    @classmethod
    def get_engine_list(cls):
        cls.init_config()
        if cls.engine_list:
            return cls.engine_list
        else:
            cls.engine_list = []
            cls.engine_class_list = []
        # The engine that should be placed at the end of the list.
        lastEngine = None
        for loader, name, isPkg in pkgutil.iter_modules(cls.enginePackage.__path__):
            if name.startswith('_'):
                continue
            try:
                engine = cls.get_engine(name)
            except:
                log.error("Error while importing  %s" % name, exc_info=True)
                continue
            try:
                if engine.check():
                    if engine.name == "empty":
                        lastEngine = (engine.name, engine.description)
                    else:
                        cls.engine_list.append((engine.name, engine.description))
                        cls.engine_class_list.append(engine)
                else:
                    log.debugWarning("Engine '%s' doesn't pass the check, excluding from list" % name)
            except:
                log.error("", exc_info=True)
        cls.engine_list.sort(key=lambda s: s[1].lower())
        if lastEngine:
            cls.engine_list.append(lastEngine)
        return cls.engine_list

    @classmethod
    def set_current_engine(cls, name, isFallback=False):
        if name == 'auto':
            name = cls.defaultEnginePriorityList[0]
        if cls.currentEngine:
            cls.currentEngine.cancel()
            cls.currentEngine.terminate()
            prevEngineName = cls.currentEngine.name
            cls.currentEngine = None
        else:
            prevEngineName = None
        try:
            new_engine = cls.get_engine_instance(name)
            cls.currentEngine = new_engine
            if not isFallback:
                config.conf[cls.configSectionName]["engine"] = name
            log.info("Loaded engine %s" % name)
            return True
        except:
            log.error("setSynth", exc_info=True)
            if prevEngineName:
                # There was a previous engine, so switch back to that one.
                cls.set_current_engine(prevEngineName, isFallback=True)
            else:
                # There was no previous engine, so fallback to the next available default synthesizer that has not been tried yet.
                try:
                    nextIndex = cls.defaultEnginePriorityList.index(name) + 1
                except ValueError:
                    nextIndex = 0
                if nextIndex < len(cls.defaultEnginePriorityList):
                    newName = cls.defaultEnginePriorityList[nextIndex]
                    cls.set_current_engine(newName, isFallback=True)
            return False

    @classmethod
    def get_engine_instance(cls, name):
        new_engine = cls.get_engine(str(name))()
        if config.conf[cls.configSectionName].isSet(name):
            new_engine.loadSettings()
        else:
            config.conf[cls.configSectionName][name] = {}
            new_engine.saveSettings()
        return new_engine

    @classmethod
    def get_engine(cls, name):
        engine_module = cls.import_class(cls.enginePackageName, name)
        for items in dir(engine_module):
            obj = getattr(engine_module, items)
            if inspect.isclass(obj) and issubclass(obj, cls.engineClass):
                return obj

    @classmethod
    def get_current_engine(cls):
        return cls.currentEngine

    @classmethod
    def import_class(cls, module_name, class_name):
        imported_module = __import__(module_name, globals(), locals(), [class_name])
        return getattr(imported_module, class_name)

    def handle_post_config_profile_switch(self):
        pass


class EngineSetting(object):
    """
    Represents an engine setting such as voice or variant.
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
    pass


class NumericEngineSetting(EngineSetting):
    """Represents a numeric synthesizer setting such as rate, volume or pitch."""
    configSpec = "integer(default=50,min=0,max=100)"

    def __init__(self, name, displayNameWithAccelerator, availableInEngineSettingsRing=True, minStep=1, normalStep=5,
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
        super(NumericEngineSetting, self).__init__(name, displayNameWithAccelerator,
                                                   availableInEngineSettingsRing=availableInEngineSettingsRing,
                                                   displayName=displayName)
        self.minStep = minStep
        self.normalStep = max(normalStep, minStep)
        self.largeStep = max(largeStep, self.normalStep)


class BooleanEngineSetting(EngineSetting):
    """Represents a boolean synthesiser setting such as rate boost.
    """
    configSpec = "boolean(default=False)"

    def __init__(self, name, displayNameWithAccelerator, availableInEngineSettingsRing=False, displayName=None):
        super(BooleanEngineSetting, self).__init__(name, displayNameWithAccelerator,
                                                   availableInEngineSettingsRing=availableInEngineSettingsRing,
                                                   displayName=displayName)


class AbstractEngine(baseObject.AutoPropertyObject):
    """Abstract base engine for external service like OCR Translation and so on.
    Each engine should be a separate Python module in the enginePackage of handler containing a
    class which inherits from this base class.

    At a minimum, engines must set L{name} and L{description} and override the L{check} method.
    Other methods should be overridden as appropriate.
    L{supportedSettings} should be set as appropriate for the settings supported by the engine.
    There are factory functions to create L{EngineSetting} instances for common settings; e.g. L{APIKeySetting} .
    Each setting is retrieved and set using attributes named after the setting;
    e.g. the L{apiKey} attribute is used for the L{apiKey} setting.
    These will usually be properties.
    @var supportedSettings: The settings supported by the engine.
    @type supportedSettings: list or tuple of L{EngineSetting}
    """
    #: The name of the engine; must be the original module file name.
    #: @type: str
    name = "empty"  # type: str
    #: A description of the engine.
    #: @type: str
    description = ""

    @classmethod
    def AppIDSetting(cls):
        """Factory function for creating a language setting."""
        # Translators: Label for a setting in voice settings dialog.
        return TextInputEngineSetting("appID", _("App &ID"))

    @classmethod
    def APIKeySetting(cls):
        """Factory function for creating a language setting."""
        # Translators: Label for a setting in voice settings dialog.
        return TextInputEngineSetting("apiKey", _("API &Key"))

    @classmethod
    def APISecretSetting(cls):
        """Factory function for creating a language setting."""
        # Translators: Label for a setting in voice settings dialog.
        return TextInputEngineSetting("apiSecret", _("API &Secret Key"))

    @classmethod
    def LanguageSetting(cls):
        """Factory function for creating a language setting."""
        # Translators: Label for a setting in voice settings dialog.
        return EngineSetting("language", _("Recognition Language"))

    @classmethod
    def NumericSettings(cls, name, label):
        """Factory function for creating a language setting."""
        # Translators: Label for a setting in voice settings dialog.
        return NumericEngineSetting(name, label)

    @classmethod
    def StringSettings(cls, name, label):
        """Factory function for creating a language setting."""
        # Translators: Label for a setting in voice settings dialog.
        return EngineSetting(name, label)

    @classmethod
    def BooleanSetting(cls, name, desc):
        return BooleanEngineSetting(name, desc)

    @classmethod
    def ReadOnlySetting(cls, name, desc):
        return ReadOnlyEngineSetting(name, desc)

    def _get_supportedSettings(self):
        raise NotImplementedError

    @staticmethod
    def generate_string_settings(settings_dict):
        """
        Generate StringSettings from dict
        :type settings_dict: dict
        :param settings_dict:
        :return:
        """
        return {x: StringParameterInfo(x, settings_dict[x]) for x in settings_dict.keys()}

    @classmethod
    def check(cls):
        return False

    def cancel(self):
        """
        Cancel current operation.
        :return:
        """
        pass

    def terminate(self):
        """
        Clean up resources before exit.
        :return:
        """
        pass

    def saveSettings(self):
        conf = config.conf[self.configSectionName][self.name]
        for setting in self.supportedSettings:
            conf[setting.name] = getattr(self, setting.name)
        # config.conf.save()

    def loadSettings(self, onlyChanged=False):
        c = config.conf[self.configSectionName][self.name]
        for s in self.supportedSettings:
            try:
                val = c[s.name]
            except KeyError:
                continue
            if val is None:
                continue
            if onlyChanged and getattr(self, s.name) == val:
                continue
            setattr(self, s.name, val)


class AbstractEngineSettingsPanel(SettingsPanel):
    """
    Settings panel of external services.
    handler must be specified before use.
    """
    name = _("Engine")
    engineNameCtrl = None  # type: ExpandoTextCtrl
    engineSettingPanel = None  # type: SpecificEnginePanel
    handler = AbstractEngineHandler  # type: AbstractEngineHandler

    def makeGeneralSettings(self, settingsSizer):
        pass

    def makeSettings(self, settingsSizer):
        settingsSizerHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
        # Translators: A label for the engines on the engine panel.
        engineLabel = _("&Engines")
        engineBox = wx.StaticBox(self, label=engineLabel)
        engineGroup = guiHelper.BoxSizerHelper(self, sizer=wx.StaticBoxSizer(engineBox, wx.HORIZONTAL))
        settingsSizerHelper.addItem(engineGroup)

        # Use a ExpandoTextCtrl because even when readonly it accepts focus from keyboard, which
        # standard readonly TextCtrl does not. ExpandoTextCtrl is a TE_MULTILINE control, however
        # by default it renders as a single line. Standard TextCtrl with TE_MULTILINE has two lines,
        # and a vertical scroll bar. This is not necessary for the single line of text we wish to
        # display here.
        engineDesc = self.handler.get_current_engine().description
        self.engineNameCtrl = ExpandoTextCtrl(self, size=(self.scaleSize(250), -1), value=engineDesc,
                                              style=wx.TE_READONLY)
        self.engineNameCtrl.Bind(wx.EVT_CHAR_HOOK, self._enterTriggersOnChangeEngine)

        # Translators: This is the label for the button used to change engines,
        # it appears in the context of a engine group on the speech settings panel.
        changeEngineBtn = wx.Button(self, label=_("C&hange..."))
        engineGroup.addItem(
            guiHelper.associateElements(
                self.engineNameCtrl,
                changeEngineBtn
            )
        )
        changeEngineBtn.Bind(wx.EVT_BUTTON, self.onChangeEngine)
        self.engineSettingPanel = SpecificEnginePanel(self, self.handler)
        settingsSizerHelper.addItem(self.engineSettingPanel)
        self.makeGeneralSettings(settingsSizer)

    def _enterTriggersOnChangeEngine(self, evt):
        if evt.KeyCode == wx.WXK_RETURN:
            self.onChangeEngine(evt)
        else:
            evt.Skip()

    def onChangeEngine(self, evt):
        change_engine = EnginesSelectionDialog(self, self.handler, multiInstanceAllowed=True)
        ret = change_engine.ShowModal()
        if ret == wx.ID_OK:
            self.Freeze()
            # trigger a refresh of the settings
            self.onPanelActivated()
            self._sendLayoutUpdatedEvent()
            self.Thaw()

    def updateCurrentEngine(self):
        engine_description = self.handler.get_current_engine().description
        self.engineNameCtrl.SetValue(engine_description)

    def onPanelActivated(self):
        # call super after all panel updates have been completed, we do not want the panel to show until this is complete.
        self.engineSettingPanel.onPanelActivated()
        super(AbstractEngineSettingsPanel, self).onPanelActivated()

    def onPanelDeactivated(self):
        self.engineSettingPanel.onPanelDeactivated()
        super(AbstractEngineSettingsPanel, self).onPanelDeactivated()

    def onDiscard(self):
        self.engineSettingPanel.onDiscard()

    def onSave(self):
        self.engineSettingPanel.onSave()


class EnginesSelectionDialog(SettingsDialog):
    """

    """
    engineNames = []  # type: list
    engineList = None  # type: wx.Choice
    handler = None
    # Translators: This is the label for the synthesizer selection dialog
    title = _("Select Engines")

    def __init__(self, parent, handler, multiInstanceAllowed=True):
        self.handler = handler
        super(EnginesSelectionDialog, self).__init__(parent, multiInstanceAllowed=multiInstanceAllowed)

    def makeSettings(self, settingsSizer):
        settingsSizerHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
        # Translators: This is a label for the select
        # synthesizer combobox in the synthesizer dialog.
        engineListLabelText = _("&Engines:")
        self.engineList = settingsSizerHelper.addLabeledControl(engineListLabelText, wx.Choice, choices=[])
        self.updateEngineList()

    def postInit(self):
        # Finally, ensure that focus is on the engine list
        self.engineList.SetFocus()

    def updateEngineList(self):
        handler = self.handler  # type: AbstractEngineHandler
        driverList = handler.engine_list
        self.engineNames = [x[0] for x in driverList]
        options = [x[1] for x in driverList]
        self.engineList.Clear()
        self.engineList.AppendItems(options)
        try:
            index = self.engineNames.index(handler.get_current_engine().name)
            self.engineList.SetSelection(index)
        except:
            pass

    def onOk(self, evt):
        handler = self.handler  # type: AbstractEngineHandler
        if not self.engineNames:
            # The list of engines has not been populated yet, so we didn't change anything in this panel
            return
        newEngineName = self.engineNames[self.engineList.GetSelection()]
        if not handler.get_engine(newEngineName):
            # Translators: This message is presented when
            # NVDA is unable to load the selected engine.
            gui.messageBox(_("Could not load the %s engine.") % newEngineName, _("Engine Error"),
                           wx.OK | wx.ICON_WARNING, self)
            return
        handler.set_current_engine(newEngineName)
        if self.IsModal():
            # Hack: we need to update the engine in our parent window before closing.
            # Otherwise, NVDA will report the old engine even though the new engine is reflected visually.
            self.Parent.updateCurrentEngine()
        super(EnginesSelectionDialog, self).onOk(evt)


class EngineSettingChanger(object):
    """Functor which acts as callback for GUI events."""

    def __init__(self, setting, engine):
        self.engine = engine
        self.setting = setting

    def __call__(self, evt):
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
        setattr(self.engine, self.setting.name,
                getattr(self.panel, "_%ss" % self.setting.name)[evt.GetSelection()].ID)


class VoiceSettingsSlider(wx.Slider):

    def __init__(self, *args, **kwargs):
        super(VoiceSettingsSlider, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_CHAR, self.onSliderChar)

    def SetValue(self, i):
        super(VoiceSettingsSlider, self).SetValue(i)
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_SLIDER_UPDATED, self.GetId())
        evt.SetInt(i)
        self.ProcessEvent(evt)
        # HACK: Win events don't seem to be sent for certain explicitly set values,
        # so send our own win event.
        # This will cause duplicates in some cases, but NVDA will filter them out.
        winUser.user32.NotifyWinEvent(winUser.EVENT_OBJECT_VALUECHANGE, self.Handle, winUser.OBJID_CLIENT,
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


class SpecificEnginePanel(SettingsPanel):
    sizerDict = None  # type: dict
    lastControl = None  # type: wx.Window
    # Translators: This is the label for the voice settings panel.
    title = _("Voice")
    handler = None  # type: AbstractEngineHandler

    def __init__(self, parent, handler, ):
        self.handler = handler
        super(SpecificEnginePanel, self).__init__(parent)

    @classmethod
    def _setSliderStepSizes(cls, slider, setting):
        slider.SetLineSize(setting.minStep)
        slider.SetPageSize(setting.largeStep)

    def makeSettingControl(self, setting):
        """Constructs appropriate GUI controls for given L{EngineSetting} such as label and slider.
        @param setting: Setting to construct controls for
        @type setting: L{NumericEngineSetting}
        @returns: WXSizer containing newly created controls.
        @rtype: L{wx.BoxSizer}
        """
        engine = self.handler.get_current_engine()
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, wx.ID_ANY, label="%s:" % setting.displayNameWithAccelerator)
        slider = VoiceSettingsSlider(self, wx.ID_ANY, minValue=0, maxValue=100)
        setattr(self, "%sSlider" % setting.name, slider)
        slider.Bind(wx.EVT_SLIDER, EngineSettingChanger(setting, engine))
        self._setSliderStepSizes(slider, setting)
        slider.SetValue(getattr(engine, setting.name))
        sizer.Add(label)
        sizer.Add(slider)
        if self.lastControl:
            slider.MoveAfterInTabOrder(self.lastControl)
        self.lastControl = slider
        return sizer

    def makeStringSettingControl(self, setting):
        """Same as L{makeSettingControl} but for string settings. Returns sizer with label and combobox."""

        labelText = "%s:" % setting.displayNameWithAccelerator
        engine = self.handler.get_current_engine()
        setattr(self, "_%ss" % setting.name, getattr(engine, "available%ss" % setting.name.capitalize()).values())
        l = getattr(self, "_%ss" % setting.name)
        labeledControl = guiHelper.LabeledControlHelper(self, labelText, wx.Choice, choices=[x.name for x in l])
        lCombo = labeledControl.control
        setattr(self, "%sList" % setting.name, lCombo)
        try:
            cur = getattr(engine, setting.name)
            i = [x.ID for x in l].index(cur)
            lCombo.SetSelection(i)
        except ValueError:
            pass
        lCombo.Bind(wx.EVT_CHOICE, StringEngineSettingChanger(setting, engine, self))
        if self.lastControl:
            lCombo.MoveAfterInTabOrder(self.lastControl)
        self.lastControl = lCombo
        return labeledControl.sizer

    def makeBooleanSettingControl(self, setting):
        """Same as L{makeSettingControl} but for boolean settings. Returns checkbox."""
        engine = self.handler.get_current_engine()
        checkbox = wx.CheckBox(self, wx.ID_ANY, label=setting.displayNameWithAccelerator)
        setattr(self, "%sCheckbox" % setting.name, checkbox)
        checkbox.Bind(wx.EVT_CHECKBOX,
                      lambda evt: setattr(self.handler.get_current_engine(), setting.name, evt.IsChecked()))
        value = getattr(engine, setting.name)
        if value == u"False" or value == "False":
            value = False
        else:
            value = True
        checkbox.SetValue(value)
        if self.lastControl:
            checkbox.MoveAfterInTabOrder(self.lastControl)
        self.lastControl = checkbox
        return checkbox

    def makeTextInputSettingControl(self, setting):
        """
        Same as L{makeSettingControl} but for TextInputSetting
        :param setting:
        :type setting: TextInputEngineSetting
        :return:
        """
        labelText = "%s:" % setting.displayNameWithAccelerator
        engine = self.handler.get_current_engine()
        labeledControl = guiHelper.LabeledControlHelper(self, labelText, wx.TextCtrl)
        textCtrl = labeledControl.control
        setattr(self, "%sTextCtrl" % setting.name, textCtrl)
        textCtrl.SetValue(getattr(engine, setting.name))
        # textCtrl.Bind(wx.EVT_TEXT_PASTE, TextInputEngineSettingChanger(setting, engine))
        textCtrl.Bind(wx.EVT_TEXT, TextInputEngineSettingChanger(setting, engine))
        if self.lastControl:
            textCtrl.MoveAfterInTabOrder(self.lastControl)
        self.lastControl = textCtrl
        return labeledControl.sizer

    def makeReadOnlySettingsControl(self, setting):
        """
        Same as L{makeSettingControl} but for ReadOnly
        :param setting: setting to use
        :type setting: ReadOnlyEngineSetting
        :return:
        """
        labelText = "%s:" % setting.displayNameWithAccelerator
        engine = self.handler.get_current_engine()
        labeledControl = guiHelper.LabeledControlHelper(self, labelText, ExpandoTextCtrl,
                                                        style=wx.TE_READONLY)
        expandoTextCtrl = labeledControl.control
        setattr(self, "%sExpandoTextCtrl" % setting.name, expandoTextCtrl)
        expandoTextCtrl.SetValue(str(getattr(engine, setting.name)))
        if self.lastControl:
            expandoTextCtrl.MoveAfterInTabOrder(self.lastControl)
        self.lastControl = expandoTextCtrl
        return labeledControl.sizer

    def onPanelActivated(self):
        engine = self.handler.get_current_engine()
        if engine.name is not self._synth.name:
            if gui._isDebug():
                log.debug("refreshing voice panel")
            self.sizerDict.clear()
            self.settingsSizer.Clear(delete_windows=True)
            self.makeSettings(self.settingsSizer)
        super(SpecificEnginePanel, self).onPanelActivated()

    def makeSettings(self, settingsSizer):
        self.sizerDict = {}
        self.lastControl = None
        # Create controls for engine Settings
        self.updateVoiceSettings()

    def updateVoiceSettings(self, changedSetting=None):
        """Creates, hides or updates existing GUI controls for all of supported settings."""
        engine = self._synth = self.handler.get_current_engine()
        log.info(engine)
        # firstly check already created options
        from six import iteritems
        for name, sizer in iteritems(self.sizerDict):
            if name == changedSetting:
                # Changing a setting shouldn't cause that setting itself to disappear.
                continue
            if not engine.isSupported(name):
                self.settingsSizer.Hide(sizer)
        # Create new controls, update already existing
        settings = engine.supportedSettings
        for setting in settings:
            if setting.name == changedSetting:
                # Changing a setting shouldn't cause that setting's own values to change.
                continue
            if setting.name in self.sizerDict:  # update a value
                self.settingsSizer.Show(self.sizerDict[setting.name])
                if isinstance(setting, NumericEngineSetting):
                    getattr(self, "%sSlider" % setting.name).SetValue(getattr(engine, setting.name))
                elif isinstance(setting, BooleanEngineSetting):
                    getattr(self, "%sCheckbox" % setting.name).SetValue(getattr(engine, setting.name))
                elif isinstance(setting, TextInputEngineSetting):
                    getattr(self, "%sTextCtrl" % setting.name).SetValue(getattr(engine, setting.name))
                elif isinstance(setting, ReadOnlyEngineSetting):
                    getattr(self, "%sExpandoTextCtrl" % setting.name).SetValue(getattr(engine, setting.name))
                else:
                    l = getattr(self, "_%ss" % setting.name)
                    lCombo = getattr(self, "%sList" % setting.name)
                    try:
                        cur = getattr(engine, setting.name)
                        i = [x.ID for x in l].index(cur)
                        lCombo.SetSelection(i)
                    except ValueError:
                        pass
            else:  # create a new control
                if isinstance(setting, NumericEngineSetting):
                    settingMaker = self.makeSettingControl
                elif isinstance(setting, BooleanEngineSetting):
                    settingMaker = self.makeBooleanSettingControl
                elif isinstance(setting, TextInputEngineSetting):
                    settingMaker = self.makeTextInputSettingControl
                elif isinstance(setting, ReadOnlyEngineSetting):
                    settingMaker = self.makeReadOnlySettingsControl
                else:
                    settingMaker = self.makeStringSettingControl
                s = settingMaker(setting)
                if isinstance(s, tuple):
                    self.sizerDict[setting.name] = s[0]
                    self.sizerDict[setting.name + "Label"] = s[1]

                    self.settingsSizer.Insert(len(self.sizerDict) - 2, s[0], border=10, flag=wx.BOTTOM)
                    self.settingsSizer.Insert(len(self.sizerDict) - 1, s[1], border=10, flag=wx.BOTTOM)
                else:
                    self.sizerDict[setting.name] = s
                    self.settingsSizer.Insert(len(self.sizerDict) - 1, s, border=10, flag=wx.BOTTOM)
        # Update graphical layout of the dialog
        self.settingsSizer.Layout()

    def onDiscard(self):
        engine = self.handler.get_current_engine()
        # unbind change events for string settings as wx closes combo boxes on cancel
        for setting in engine.supportedSettings:
            if isinstance(setting, (NumericEngineSetting, BooleanEngineSetting, TextInputEngineSetting)):
                continue
            getattr(self, "%sList" % setting.name).Unbind(wx.EVT_CHOICE)
        # restore settings
        engine.loadSettings()
        super(SpecificEnginePanel, self).onDiscard()

    def onSave(self):
        engine = self.handler.get_current_engine()
        engine.saveSettings()

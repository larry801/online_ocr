    # self.testEngineButton = settingsSizerHelper.addItem(
    # 	wx.Button(
    # 		self,
    # 		# Translators: This is the label for a button in the
    # 		# online OCR settings panel.
    # 		label=_(u"Test this OCR engine by recognizing a sample image with five numbers 12345.")
    # 	)
    # )
    # from LayeredGesture import onAddonInputGestureDialog
    # self.testEngineButton.Bind(
    # 	wx.EVT_BUTTON,
    # 	onAddonInputGestureDialog)
		
		
    # Prefix gesture is commented out
	# # Translators:
	# prefix_name = _(u"Prefix of sequential gesture in online image describer addon")
	# 
	# @script(
	# 	description=prefix_name,
	# 	category=category_name,
	# 	gestures=[]
	# )
	# def script_startGestureSequence(self, gesture):
	# 	self.addCaptureFunction()
	# 	# Translators: Reported when prefix gesture pressed
	# 	ui.message(_("Online image describer layer entered"))
	
	### TwoPhase gestures
This addon also provide another way to invoke gestures.
Press a prefix gesture followed by another gesture.
Press question mark to get help.

ERROR - stderr (17:54:43.986):
Exception in thread Thread-16:
Traceback (most recent call last):
  File "threading.pyc", line 801, in __bootstrap_inner
  File "threading.pyc", line 754, in run
  File "C:\Users\John\AppData\Roaming\nvda\addons\onlineOCR\globalPlugins\onlineOCR\winHttp.py", line 115, in postContent
  File "C:\Users\John\AppData\Roaming\nvda\addons\onlineOCR\globalPlugins\onlineOCR\winHttp.py", line 95, in doHTTPRequest
  File "C:\Users\John\AppData\Roaming\nvda\addons\wpn\globalPlugins\_contrib\urllib3\request.py", line 72, in request
  File "C:\Users\John\AppData\Roaming\nvda\addons\wpn\globalPlugins\_contrib\urllib3\request.py", line 150, in request_encode_body
  File "C:\Users\John\AppData\Roaming\nvda\addons\wpn\globalPlugins\_contrib\urllib3\poolmanager.py", line 322, in urlopen
  File "C:\Users\John\AppData\Roaming\nvda\addons\wpn\globalPlugins\_contrib\urllib3\connectionpool.py", line 600, in urlopen
  File "C:\Users\John\AppData\Roaming\nvda\addons\wpn\globalPlugins\_contrib\urllib3\connectionpool.py", line 354, in _make_request
  File "httplib.pyc", line 1042, in request
  File "httplib.pyc", line 1082, in _send_request
  File "httplib.pyc", line 1038, in endheaders
  File "httplib.pyc", line 880, in _send_output
UnicodeDecodeError: 'ascii' codec can't decode byte 0x89 in position 131: ordinal not in range(128)

treat image bytes as unicode
url is unicode?


	def featureChanger(self, evt):
		import wx
		import gui
		order = self._feature
		items = self.features.values()
		if len(order) != len(items):
			order = range(len(items))
		dlg = wx.RearrangeDialog(
			gui.mainFrame,
			# Translators: Notice in rearrange dialog
			_("You can also uncheck the items you don't want to detect."),
			# Translators: Notice in rearrange dialog
			_("Sort the features"),
			order, items)
		if dlg.ShowModal() == wx.ID_OK:
			self._feature = dlg.GetOrder()
			self.saveSettings()

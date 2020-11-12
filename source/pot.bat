del onlineOCR.pot
scons pot && msgmerge -U  addon\locale\zh_CN\LC_MESSAGES\nvda.po  onlineOCR.pot && start addon\locale\zh_CN\LC_MESSAGES\nvda.po
pause

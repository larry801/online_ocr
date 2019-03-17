# -*- coding: UTF-8 -*-

# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

# Full getext (please don't change)
_ = lambda x: x

# Add-on information variables
addon_info = {
    # for previously unpublished addons, please follow the community guidelines at:
    # https://bitbucket.org/nvdaaddonteam/todo/raw/master/guideLines.txt
    # add-on Name, internal for nvda
    "addon_name": "onlineOCR",
    # Add-on summary, usually the user visible name of the addon.
    # Translators: Summary for this add-on to be shown on installation and add-on information.
    "addon_summary": _("Online OCR"),
    # Add-on description: can span multiple lines with """ syntax """
    # Translators: Long description to be shown for this add-on on add-on information from add-ons manager
    "addon_description": _("Add online OCR engines to NVDA"),
    # version
    "addon_version": "0.4-dev",
    # Author(s)
    "addon_author": "Larry Wang <larry.wang.801@gmail.com>",
    # URL for the add-on documentation support

    "addon_url": None,

    # Documentation file name
    "addon_docFileName": "readme.html",
    "addon_minimumNVDAVersion": "2018.3.0",
    "addon_lastTestedNVDAVersion": "2019.1.0",
    "addon_updateChannel": "dev",
}

import os.path

# Define the python files that are the sources of your add-on.
# You can use glob expressions here, they will be expanded.
pythonSources = [
    os.path.join("addon", "globalPlugins", "onlineOCR", "*.py"),
r".\addon\globalPlugins\onlineOCR\**\*.py"
]

# Files that contain strings for translation. Usually your python sources
i18nSources = pythonSources + ["buildVars.py"]

# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory, not to the root directory of your addon sources.
excludedFiles = []

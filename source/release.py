# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
import buildVars
import subprocess

version = buildVars.addon_info["addon_version"]
subprocess.call([
	"git",
	"tag",
	'-m',
	'"{0}"'.format(version),
	version
])
subprocess.call([
	"git", "push", "--tags"
])

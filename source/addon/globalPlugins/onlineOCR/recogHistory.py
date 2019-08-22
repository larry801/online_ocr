# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

history = []
MAX_HISTORY = 20


def historyAppend(image, result):
	history.append({
		"image": image,
		"result": result
	})
	if len(history) > MAX_HISTORY:
		history.pop(0)

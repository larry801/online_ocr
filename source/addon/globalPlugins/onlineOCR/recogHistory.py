# coding=utf-8
# Copyright (C) 2019 Larry Wang <larry.wang.801@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

history = []
MAX_HISTORY = 20


def historyAppend(engine, image, response):
	history.append({
		"engine": engine,
		"image": image,
		"response": response
	})
	if len(history) > MAX_HISTORY:
		history.pop(0)


def getPreviousResult():
	if len(history) > 0:
		return history[-1]

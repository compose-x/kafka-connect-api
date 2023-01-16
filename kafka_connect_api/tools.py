#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2020-2022 John Mille <john@compose-x.io>

KEYISSET = lambda x, y: isinstance(y, dict) and x in y.keys() and y[x]

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

if os.environ['QT_API'] == 'pyqt':
    from PyQt4.QtNetwork import *
else:
    from PySide.QtNetwork import *
# -*- coding: utf-8 -*-
import re


def is_almost_same(origin, trans):
    pattern = re.compile(ur'[^\w\u4e00-\u9fa5]+')
    seg1 = pattern.split(origin)
    print(seg1)
    origin = unicode.lower(u''.join(seg1))
    seg2 = pattern.split(trans)
    print(seg2)
    trans = unicode.lower(u''.join(seg2))
    return origin == trans


def is_english(text):
    text = text.encode("utf8")
    pattern = re.compile(ur'^[a-zA-Z]+$')
    if pattern.match(text):
        return True
    return False


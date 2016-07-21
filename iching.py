# -*- coding: utf-8 -*-
"""
A simple model I Ching.

All data and probabilities taken from Wikipedia at:
    * https://en.wikipedia.org/wiki/I_Ching_divination and
    * https://en.wikipedia.org/wiki/List_of_hexagrams_of_the_I_Ching
"""

from __future__ import unicode_literals

import random
import warnings

from blur.rand import weighted_choice

hexagrams = {
    # number: (character, name, english_name)
    1:  ('䷀', '乾',   'Force'),
    2:  ('䷁', '坤',   'Field'),
    3:  ('䷂', '屯',   'Sprouting'),
    4:  ('䷃', '蒙',   'Enveloping'),
    5:  ('䷄', '需',   'Attending'),
    6:  ('䷅', '訟',   'Arguing'),
    7:  ('䷆', '師',   'Leading'),
    8:  ('䷇', '比',   'Grouping'),
    9:  ('䷈', '小畜', 'Small Accumulating'),
    10: ('䷉', '履',   'Treading'),
    11: ('䷊', '泰',   'Pervading'),
    12: ('䷋', '否',   'Obstruction'),
    13: ('䷌', '同人', 'Concording People'),
    14: ('䷍', '大有', 'Great Possessing'),
    15: ('䷎', '謙',   'Humbling'),
    16: ('䷏', '豫',   'Providing-For'),
    17: ('䷐', '隨',   'Following'),
    18: ('䷑', '蠱',   'Correcting'),
    19: ('䷒', '臨',   'Nearing'),
    20: ('䷓', '觀',   'Viewing'),
    21: ('䷔', '噬嗑', 'Gnawing Bite'),
    22: ('䷕', '賁',   'Adorning'),
    23: ('䷖', '剝',   'Stripping'),
    24: ('䷗', '復',   'Returning'),
    25: ('䷘', '無妄',  'Without Embroiling'),
    26: ('䷙', '大畜',  'Great Accumulating'),
    27: ('䷚', '頤',   'Swallowing'),
    28: ('䷛', '大過',  'Great Exceeding'),
    29: ('䷜', '坎',   'Gorge'),
    30: ('䷝', '離',   'Radiance'),
    31: ('䷞', '咸',   'Conjoining'),
    32: ('䷟', '恆',   'Persevering'),
    33: ('䷠', '遯',   'Retiring'),
    34: ('䷡', '大壯',  'Great Invigorating'),
    35: ('䷢', '晉',   'Prospering'),
    36: ('䷣', '明夷',  'Darkening of the Light'),
    37: ('䷤', '家人',  'Dwelling People'),
    38: ('䷥', '睽',   'Polarising'),
    39: ('䷦', '蹇',   'Limping'),
    40: ('䷧', '解',   'Taking Apart'),
    41: ('䷨', '損',   'Diminishing'),
    42: ('䷩', '益',   'Augmenting'),
    43: ('䷪', '夬',   'Displacement'),
    44: ('䷫', '姤',   'Coupling'),
    45: ('䷬', '萃',   'Clustering'),
    46: ('䷭', '升',   'Ascending'),
    47: ('䷮', '困',   'Confining'),
    48: ('䷯', '井',   'Welling'),
    49: ('䷰', '革',   'Skinning'),
    50: ('䷱', '鼎',   'Holding'),
    51: ('䷲', '震',   'Shake'),
    52: ('䷳', '艮',   'Bound'),
    53: ('䷴', '漸',   'Infiltrating'),
    54: ('䷵', '歸妹',  'Converting the Maiden'),
    55: ('䷶', '豐',   'Abounding'),
    56: ('䷷', '旅',   'Sojourning'),
    57: ('䷸', '巽',   'Ground'),
    58: ('䷹', '兌',   'Open'),
    59: ('䷺', '渙',   'Dispersing'),
    60: ('䷻', '節',   'Articulating'),
    61: ('䷼', '中孚',  'Center Returning'),
    62: ('䷽', '小過',  'Small Exceeding'),
    63: ('䷾', '既濟',  'Already Fording'),
    64: ('䷿', '未濟',  'Not Yet Fording')
}

_hexagram_dict = {
    (1, 1, 1,   1, 1, 1): 1,
    (1, 1, 1,   0, 0, 0): 11,
    (1, 1, 1,   1, 0, 0): 34,
    (1, 1, 1,   0, 1, 0): 5,
    (1, 1, 1,   0, 0, 1): 26,
    (1, 1, 1,   0, 1, 1): 9,
    (1, 1, 1,   1, 0, 1): 14,
    (1, 1, 1,   1, 1, 0): 43,

    (0, 0, 0,   1, 1, 1): 12,
    (0, 0, 0,   0, 0, 0): 2,
    (0, 0, 0,   1, 0, 0): 16,
    (0, 0, 0,   0, 1, 0): 8,
    (0, 0, 0,   0, 0, 1): 23,
    (0, 0, 0,   0, 1, 1): 20,
    (0, 0, 0,   1, 0, 1): 35,
    (0, 0, 0,   1, 1, 0): 45,

    (1, 0, 0,   1, 1, 1): 25,
    (1, 0, 0,   0, 0, 0): 24,
    (1, 0, 0,   1, 0, 0): 51,
    (1, 0, 0,   0, 1, 0): 3,
    (1, 0, 0,   0, 0, 1): 27,
    (1, 0, 0,   0, 1, 1): 42,
    (1, 0, 0,   1, 0, 1): 21,
    (1, 0, 0,   1, 1, 0): 17,

    (0, 1, 0,   1, 1, 1): 6,
    (0, 1, 0,   0, 0, 0): 7,
    (0, 1, 0,   1, 0, 0): 40,
    (0, 1, 0,   0, 1, 0): 29,
    (0, 1, 0,   0, 0, 1): 4,
    (0, 1, 0,   0, 1, 1): 59,
    (0, 1, 0,   1, 0, 1): 64,
    (0, 1, 0,   1, 1, 0): 47,

    (0, 0, 1,   1, 1, 1): 33,
    (0, 0, 1,   0, 0, 0): 15,
    (0, 0, 1,   1, 0, 0): 62,
    (0, 0, 1,   0, 1, 0): 39,
    (0, 0, 1,   0, 0, 1): 52,
    (0, 0, 1,   0, 1, 1): 53,
    (0, 0, 1,   1, 0, 1): 56,
    (0, 0, 1,   1, 1, 0): 31,

    (0, 1, 1,   1, 1, 1): 44,
    (0, 1, 1,   0, 0, 0): 46,
    (0, 1, 1,   1, 0, 0): 32,
    (0, 1, 1,   0, 1, 0): 48,
    (0, 1, 1,   0, 0, 1): 18,
    (0, 1, 1,   0, 1, 1): 57,
    (0, 1, 1,   1, 0, 1): 50,
    (0, 1, 1,   1, 1, 0): 28,

    (1, 0, 1,   1, 1, 1): 13,
    (1, 0, 1,   0, 0, 0): 36,
    (1, 0, 1,   1, 0, 0): 55,
    (1, 0, 1,   0, 1, 0): 63,
    (1, 0, 1,   0, 0, 1): 22,
    (1, 0, 1,   0, 1, 1): 37,
    (1, 0, 1,   1, 0, 1): 30,
    (1, 0, 1,   1, 1, 0): 49,

    (1, 1, 0,   1, 1, 1): 10,
    (1, 1, 0,   0, 0, 0): 19,
    (1, 1, 0,   1, 0, 0): 54,
    (1, 1, 0,   0, 1, 0): 60,
    (1, 1, 0,   0, 0, 1): 41,
    (1, 1, 0,   0, 1, 1): 61,
    (1, 1, 0,   1, 0, 1): 38,
    (1, 1, 0,   1, 1, 0): 58,
}


def get_hexagram(method='THREE COIN'):
    """
    Return one or two hexagrams using any of a variety of divination methods.

    The ``NAIVE`` method simply returns a uniformally random ``int`` between
    ``1`` and ``64``.

    All other methods return a ``tuple`` of two ``int`` where the first
    represents the starting hexagram and the second represents the 'moving to'
    hexagram.

    Args:
        method (Optional[str]): THREE COIN, YARROW, NAIVE

    Returns: tuple(int) or int

    Raises: ValueError if ``method`` is invalid
    """
    if method == 'THREE COIN':
        weights = [('MOVING YANG', 2),
                   ('MOVING YIN',  2),
                   ('STATIC YANG', 6),
                   ('STATIC YIN',  6)]
    elif method == 'YARROW':
        weights = [('MOVING YANG', 8),
                   ('MOVING YIN',  2),
                   ('STATIC YANG', 11),
                   ('STATIC YIN',  17)]
    elif method == 'NAIVE':
        return random.randint(1, 64)
    else:
        raise ValueError

    hexagram_1 = []
    hexagram_2 = []

    for i in range(6):
        roll = weighted_choice(weights)
        if roll == 'MOVING YANG':
            hexagram_1.append(1)
            hexagram_2.append(0)
        elif roll == 'MOVING YIN':
            hexagram_1.append(0)
            hexagram_2.append(1)
        elif roll == 'STATIC YANG':
            hexagram_1.append(1)
            hexagram_2.append(1)
        else:  # roll == 'STATIC YIN'
            hexagram_1.append(0)
            hexagram_2.append(0)
    # Convert hexagrams lists into tuples
    hexagram_1 = tuple(hexagram_1)
    hexagram_2 = tuple(hexagram_2)
    return (_hexagram_dict[hexagram_1],
            _hexagram_dict[hexagram_2])

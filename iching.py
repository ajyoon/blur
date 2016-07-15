# -*- coding: utf-8 -*-
"""
A simple model I Ching

All data and probabilities taken from Wikipedia at:
https://en.wikipedia.org/wiki/I_Ching_divination and
https://en.wikipedia.org/wiki/List_of_hexagrams_of_the_I_Ching
"""

from __future__ import unicode_literals

import random
import warnings

from blur.rand import weighted_option

hexagrams = {
    # number: (character, name, english name)
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
    Return one or two hexagrams using any of a variety of divination methods

    The ``NAIVE`` method simply returns a uniformally random ``int`` between
    ``1`` and ``64``.

    All other methods return a tuple of two ``int`` where the first represents
    the starting hexagram and the second represents the 'moving to' hexagram.

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
        roll = weighted_option(weights)
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

###############################################################################
#   Extended descriptions of hexagrams
#   All information copied from wikipedia at:
#   https://en.wikipedia.org/wiki/List_of_hexagrams_of_the_I_Ching
###############################################################################
descriptions = {
    1:  'Hexagram 1 is named 乾 (qián), "Force". Other variations include "the creative", "strong action", "the key", and "god". Its inner (lower) trigram is ☰ (乾 qián) force = (天) heaven, and its outer (upper) trigram is the same.',
    2:  'Hexagram 2 is named 坤 (kūn), "Field". Other variations include "the receptive", "acquiescence", and "the flow". Its inner trigram is ☷ (坤 kūn) field = (地) earth, and its outer trigram is identical.',
    3:  'Hexagram 3 is named 屯 (zhūn), "Sprouting". Other variations include "difficulty at the beginning", "gathering support", and "hoarding". Its inner trigram is ☳ (震 zhèn) shake = (雷) thunder, and its outer trigram is ☵ (坎 kǎn) gorge = (水) water.',
    4:  'Hexagram 4 is named 蒙 (méng), "Enveloping". Other variations include "youthful folly", "the young shoot", and "discovering". Its inner trigram is ☵ (坎 kǎn) gorge = (水) water. Its outer trigram is ☶ (艮 gèn) bound = (山) mountain.',
    5:  'Hexagram 5 is named 需 (xū), "Attending". Other variations include "waiting", "moistened", and "arriving". Its inner trigram is ☰ (乾 qián) force = (天) heaven, and its outer trigram is ☵ (坎 kǎn) gorge = (水) water.',
    6:  'Hexagram 6 is named 訟 (sòng), "Arguing". Other variations include "conflict" and "lawsuit". Its inner trigram is ☵ (坎 kǎn) gorge = (水) water, and its outer trigram is ☰ (乾 qián) force = (天) heaven.',
    7:  'Hexagram 7 is named 師 (shī), "Leading". Other variations include "the army" and "the troops". Its inner trigram is ☵ (坎 kǎn) gorge = (水) water, and its outer trigram is ☷ (坤 kūn) field = (地) earth.',
    8:  'Hexagram 8 is named 比 (bǐ), "Grouping". Other variations include "holding together" and "alliance". Its inner trigram is ☷ (坤 kūn) field = (地) earth, and its outer trigram is ☵ (坎 kǎn) gorge = (水) water.',
    9:  'Hexagram 9 is named 小畜 (xiǎo chù), "Small Accumulating". Other variations include "the taming power of the small" and "small harvest". Its inner trigram is ☰ (乾 qián) force = (天) heaven, and its outer trigram is ☴ (巽 xùn) ground = (風) wind.',
    10: 'Hexagram 10 is named 履 (lǚ), "Treading". Other variations include "treading (conduct)" and "continuing". Its inner trigram is ☱ (兌 duì) open = (澤) swamp, and its outer trigram is ☰ (乾 qián) force = (天) heaven.',
    11: 'Hexagram 11 is named 泰 (tài), "Pervading". Other variations include "peace" and "greatness". Its inner trigram is ☰ (乾 qián) force = (天) heaven, and its outer trigram is ☷ (坤 kūn) field = (地) earth.',
    12: 'Hexagram 12 is named 否 (pǐ), "Obstruction". Other variations include "standstill (stagnation)" and "selfish persons". Its inner trigram is ☷ (坤 kūn) field = (地) earth, and its outer trigram is ☰ (乾 qián) force = (天) heaven.',
    13: 'Hexagram 13 is named 同人 (tóng rén), "Concording People". Other variations include "fellowship with men" and "gathering men". Its inner trigram is ☲ (離 lí) radiance = (火) fire, and its outer trigram is ☰ (乾 qián) force = (天) heaven.',
    14: 'Hexagram 14 is named 大有 (dà yǒu), "Great Possessing". Other variations include "possession in great measure" and "the great possession". Its inner trigram is ☰ (乾 qián) force = (天) heaven, and its outer trigram is ☲ (離 lí) radiance = (火) fire.',
    15: 'Hexagram 15 is named 謙 (qiān), "Humbling". Other variations include "modesty". Its inner trigram is ☶ (艮 gèn) bound = (山) mountain and its outer trigram is ☷ (坤 kūn) field = (地) earth.',
    16: 'Hexagram 16 is named 豫 (yù), "Providing-For". Other variations include "enthusiasm" and "excess". Its inner trigram is ☷ (坤 kūn) field = (地) earth, and its outer trigram is ☳ (震 zhèn) shake = (雷) thunder.',
    17: 'Hexagram 17 is named 隨 (suí), "Following". Its inner trigram is ☳ (震 zhèn) shake = (雷) thunder, and its outer trigram is ☱ (兌 duì) open = (澤) swamp.',
    18: 'Hexagram 18 is named 蠱 (gŭ), "Correcting". Other variations include "work on what has been spoiled (decay)", decaying and "branch".[1] Its inner trigram is ☴ (巽 xùn) ground = (風) wind, and its outer trigram is ☶ (艮 gèn) bound = (山) mountain. Gu is the name of a venom-based poison traditionally used in Chinese witchcraft.',
    19: 'Hexagram 19 is named 臨 (lín), "Nearing". Other variations include "approach" and "the forest". Its inner trigram is ☱ (兌 duì) open = (澤) swamp, and its outer trigram is ☷ (坤 kūn) field = (地) earth.',
    20: 'Hexagram 20 is named 觀 (guān), "Viewing". Other variations include "contemplation (view)" and "looking up". Its inner trigram is ☷ (坤 kūn) field = (地) earth, and its outer trigram is ☴ (巽 xùn) ground = (風) wind.',
    21: 'Hexagram 21 is named 噬嗑 (shì kè), "Gnawing Bite". Other variations include "biting through" and "biting and chewing". Its inner trigram is ☳ (震 zhèn) shake = (雷) thunder, and its outer trigram is ☲ (離 lí) radiance = (火) fire.',
    22: 'Hexagram 22 is named 賁 (bì), "Adorning". Other variations include "grace" and "luxuriance". Its inner trigram is ☲ (離 lí) radiance = (火) fire, and its outer trigram is ☶ (艮 gèn) bound = (山) mountain.',
    23: 'Hexagram 23 is named 剝 (bō), "Stripping". Other variations include "splitting apart" and "flaying". Its inner trigram is ☷ (坤 kūn) field = (地) earth, and its outer trigram is ☶ (艮 gèn) bound = (山) mountain.',
    24: 'Hexagram 24 is named 復 (fù), "Returning". Other variations include "return (the turning point)". Its inner trigram is ☳ (震 zhèn) shake = (雷) thunder, and its outer trigram is ☷ (坤 kūn) field = (地) earth.',
    25: 'Hexagram 25 is named 無妄 (wú wàng), "Without Embroiling". Other variations include "innocence (the unexpected)" and "pestilence". Its inner trigram is ☳ (震 zhèn) shake = (雷) thunder, and its outer trigram is ☰ (乾 qián) force = (天) heaven.',
    26: 'Hexagram 26 is named 大畜 (dà chù), "Great Accumulating". Other variations include "the taming power of the great", "great storage", and "potential energy." Its inner trigram is ☰ (乾 qián) force = (天) heaven, and its outer trigram is ☶ (艮 gèn) bound = (山) mountain.',
    27: 'Hexagram 27 is named 頤 (yí), "Swallowing". Other variations include "the corners of the mouth (providing nourishment)", "jaws" and "comfort/security". Its inner trigram is ☳ (震 zhèn) shake = (雷) thunder, and its outer trigram is ☶ (艮 gèn) bound = (山) mountain.',
    28: 'Hexagram 28 is named 大過 (dà guò), "Great Exceeding". Other variations include "preponderance of the great", "great surpassing" and "critical mass." Its inner trigram is ☴ (巽 xùn) ground = (風) wind, and its outer trigram is ☱ (兌 duì) open = (澤) swamp.',
    29: 'Hexagram 29 is named 坎 (kǎn), "Gorge". Other variations include "the abyss" (in the oceanographic sense) and "repeated entrapment". Its inner trigram is ☵ (坎 kǎn) gorge = (水) water, and its outer trigram is identical.',
    30: 'Hexagram 30 is named 離 (lí), "Radiance". Other variations include "the clinging, fire" and "the net". Its inner trigram is ☲ (離 lí) radiance = (火) fire, and its outer trigram is identical. The origin of the character has its roots in symbols of long-tailed birds such as the peacock or the legendary phoenix.',
    31: 'Hexagram 31 is named 咸 (xián), "Conjoining". Other variations include "influence (wooing)" and "feelings". Its inner trigram is ☶ (艮 gèn) bound = (山) mountain, and its outer trigram is ☱ (兌 duì) open = (澤) swamp.',
    32: 'Hexagram 32 is named 恆 (héng), "Persevering". Other variations include "duration" and "constancy". Its inner trigram is ☴ (巽 xùn) ground = (風) wind, and its outer trigram is ☳ (震 zhèn) shake = (雷) thunder.',
    33: 'Hexagram 33 is named 遯 (dùn), "Retiring". Other variations include "retreat" and "yielding". Its inner trigram is ☶ (艮 gèn) bound = (山) mountain, and its outer trigram is ☰ (乾 qián) force = (天) heaven.',
    34: 'Hexagram 34 is named 大壯 (dà zhuàng), "Great Invigorating". Other variations include "the power of the great" and "great maturity". Its inner trigram is ☰ (乾 qián) force = (天) heaven, and its outer trigram is ☳ (震 zhèn) shake = (雷) thunder.',
    35: 'Hexagram 35 is named 晉 (jìn), "Prospering". Other variations include "progress" and "aquas". Its inner trigram is ☷ (坤 kūn) field = (地) earth, and its outer trigram is ☲ (離 lí) radiance = (火) fire.',
    36: 'Hexagram 36 is named 明夷 (míng yí), “Darkening of the Light.” Other variations are "brilliance injured" and "intelligence hidden". Its inner trigram is ☲ (離 lí) radiance = (火) fire, and its outer trigram is ☷ (坤 kūn) field = (地) earth.',
    37: 'Hexagram 37 is named 家人 (jiā rén), "Dwelling People". Other variations include "the family (the clan)" and "family members". Its inner trigram is ☲ (離 lí) radiance = (火) fire, and its outer trigram is ☴ (巽 xùn) ground = (風) wind.',
    38: 'Hexagram 38 is named 睽 (kuí), "Polarising". Other variations include "opposition" and "perversion". Its inner trigram is ☱ (兌 duì) open = (澤) swamp, and its outer trigram is ☲ (離 lí) radiance = (火) fire.',
    39: 'Hexagram 39 is named 蹇 (jiǎn), "Limping". Other variations include "obstruction" and "afoot". Its inner trigram is ☶ (艮 gèn) bound = (山) mountain, and its outer trigram is ☵ (坎 kǎn) gorge = (水) water.',
    40: 'Hexagram 40 is named 解 (xiè), "Taking-Apart". Other variations include "deliverance" and "untangled". Its inner trigram is ☵ (坎 kǎn) gorge = (水) water, and its outer trigram is ☳ (震 zhèn) shake = (雷) thunder.',
    41: 'Hexagram 41 is named 損 (sǔn), "Diminishing". Other variations include "decrease". Its inner trigram is ☱ (兌 duì) open = (澤) swamp, and its outer trigram is ☶ (艮 gèn) bound = (山) mountain.',
    42: 'Hexagram 42 is named 益 (yì), "Augmenting". Other variations include "increase". Its inner trigram is ☳ (震 zhèn) shake = (雷) thunder, and its outer trigram is ☴ (巽 xùn) ground = (風) wind.',
    43: 'Hexagram 43 is named 夬 (guài), "Displacement" Other variations include "resoluteness", "parting", and "break-through". Its inner trigram is ☰ (乾 qián) force = (天) heaven, and its outer trigram is ☱ (兌 duì) open = (澤) swamp.',
    44: 'Hexagram 44 is named 姤 (gòu), "Coupling". Other variations include "coming to meet" and "meeting". Its inner trigram is ☴ (巽 xùn) ground = (風) wind, and its outer trigram is ☰ (乾 qián) force = (天) heaven.',
    45: 'Hexagram 45 is named 萃 (cuì), "Clustering". Other variations include "gathering together (massing)" and "finished". Its inner trigram is ☷ (坤 kūn) field = (地) earth, and its outer trigram is ☱ (兌 duì) open = (澤) swamp.',
    46: 'Hexagram 46 is named 升 (shēng), "Ascending". Other variations include "pushing upward". Its inner trigram is ☴ (巽 xùn) ground = (風) wind, and its outer trigram is ☷ (坤 kūn) field = (地) earth.',
    47: 'Hexagram 47 is named 困 (kùn), "Confining". Other variations include "oppression (exhaustion)" and "entangled". Its inner trigram is ☵ (坎 kǎn) gorge = (水) water, and its outer trigram is ☱ (兌 duì) open = (澤) swamp.',
    48: 'Hexagram 48 is named 井 (jǐng), "Welling". Other variations include "the well". Its inner trigram is ☴ (巽 xùn) ground = (風) wind, and its outer trigram is ☵ (坎 kǎn) gorge = (水) water.',
    49: 'Hexagram 49 is named 革 (gé), "Skinning". Other variations including "revolution (molting)" and "the bridle". Its inner trigram is ☲ (離 lí) radiance = (火) fire, and its outer trigram is ☱ (兌 duì) open = (澤) swamp.',
    50: 'Hexagram 50 is named 鼎 (dǐng), "Holding". Other variations include "the cauldron". Its inner trigram is ☴ (巽 xùn) ground = (風) wind, and its outer trigram is ☲ (離 lí) radiance = (火) fire.',
    51: 'Hexagram 51 is named 震 (zhèn), "Shake". Other variations include "the arousing (shock, thunder)" and "thunder". Both its inner and outer trigrams are ☳ (震 zhèn) shake = (雷) thunder.',
    52: 'Hexagram 52 is named 艮 (gèn), "Bound". Other variations include "keeping still, mountain" and "stilling". Both its inner and outer trigrams are ☶ (艮 gèn) bound = (山) mountain.',
    53: 'Hexagram 53 is named 漸 (jiàn), "Infiltrating". Other variations include "development (gradual progress)" and "advancement". Its inner trigram is ☶ (艮 gèn) bound = (山) mountain, and its outer trigram is ☴ (巽 xùn) ground = (風) wind.',
    54: 'Hexagram 54 is named 歸妹 (guī mèi), "Converting the Maiden". Other variations include "the marrying maiden" and "returning maiden". Its inner trigram is ☱ (兌 duì) open = (澤) swamp, and its outer trigram is ☳ (震 zhèn) shake = (雷) thunder.',
    55: 'Hexagram 55 is named 豐 (fēng), "Abounding". Other variations include "abundance" and "fullness". Its inner trigram is ☲ (離 lí) radiance = (火) fire, and its outer trigram is ☳ (震 zhèn) shake = (雷) thunder.',
    56: 'Hexagram 56 is named 旅 (lǚ), "Sojourning". Other variations include "the wanderer" and "traveling". Its inner trigram is ☶ (艮 gèn) bound = (山) mountain, and its outer trigram is ☲ (離 lí) radiance = (火) fire.',
    57: 'Hexagram 57 is named 巽 (xùn), "Ground". Other variations include "the gentle (the penetrating, wind)" and "calculations". Both its inner and outer trigrams are ☴ (巽 xùn) ground = (風) wind.',
    58: 'Hexagram 58 is named 兌 (duì), "Open". Other variations include "the joyous, lake" and "usurpation". Both its inner and outer trigrams are ☱ (兌 duì) open = (澤) swamp.',
    59: 'Hexagram 59 is named 渙 (huàn), "Dispersing". Other variations include "dispersion (dissolution)" and "dispersal". Its inner trigram is ☵ (坎 kǎn) gorge = (水) water, and its outer trigram is ☴ (巽 xùn) ground = (風) wind.',
    60: 'Hexagram 60 is named 節 (jié), "Articulating". Other variations include "limitation" and "moderation". Its inner trigram is ☱ (兌 duì) open = (澤) swamp, and its outer trigram is ☵ (坎 kǎn) gorge = (水) water.',
    61: 'Hexagram 61 is named 中孚 (zhōng fú), "Center Returning". Other variations include "inner truth" and "central return". Its inner trigram is ☱ (兌 duì) open = (澤) swamp, and its outer trigram is ☴ (巽 xùn) ground = (風) wind.',
    62: 'Hexagram 62 is named 小過 (xiǎo guò), "Small Exceeding". Other variations include "preponderance of the small" and "small surpassing". Its inner trigram is ☶ (艮 gèn) bound = (山) mountain, and its outer trigram is ☳ (震 zhèn) shake = (雷) thunder.',
    63: 'Hexagram 63 is named 既濟 (jì jì), "Already Fording". Other variations include "after completion" and "already completed" or "already done" . Its inner trigram is ☲ (離 lí) radiance = (火) fire, and its outer trigram is ☵ (坎 kǎn) gorge = (水) water.',
    64: 'Hexagram 64 is named 未濟 (wèi jì), "Not Yet Fording". Other variations include "before completion" and "not yet completed". Its inner trigram is ☵ (坎 kǎn) gorge = (水) water, and its outer trigram is ☲ (離 lí) radiance = (火) fire.'
}

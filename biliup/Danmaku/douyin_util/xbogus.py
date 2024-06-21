import hashlib
import base64
import math
import random


class ByteDance:
    @staticmethod
    def md5(string) -> str:
        return hashlib.md5(bytearray(string)).hexdigest()

    @staticmethod
    def decode(hex_str) -> list:
        return list(bytes.fromhex(hex_str))


_0x9fb121 = []
_0x207cc5 = []
_0x191fa5 = []

_0x216650 = {
    'kNoMove': 0x2,
    'kNoClickTouch': 0x4,
    'kNoKeyboardEvent': 0x8,
    'kMoveFast': 0x10,
    'kKeyboardFast': 0x20,
    'kFakeOperations': 0x40
}

_0xe06992 = {
    'ubcode': 0x0,
}

def _0x26d461():
    _0x499168 = 0
    _0x462d0a = [0, 0]
    _0x136148 = [0, 0]
    _0x17d8e6 = 1
    _0x499168 |= _0x216650['kFakeOperations']
    if 0 == len(_0x9fb121):
        _0x17d8e6 |= 2
        _0x499168 |= _0x216650['kNoMove']
    else:
        if _0x462d0a[-0x17f8 + -0x1eae + 0x36a6] > 0xbab + -0x1fb9 + 0x3 * 0x6c0:
            _0x17d8e6 |= (0x20 * -0x5c + 0xb22 + 0x6e)
            _0x499168 |= _0x216650['kMoveFast']
    if 0 == len(_0x207cc5):
        _0x17d8e6 |= 4
        _0x499168 |= _0x216650['kNoClickTouch']
    if 0 == len(_0x191fa5):
        _0x17d8e6 |= 8
        _0x499168 |= _0x216650['kNoKeyboardEvent']
    else:
        index = 0x16ee + -0x1 * 0x1e99 + 0x7ab
        if _0x136148[index] > (0x1 * 0xb77 + -0x82 + -0xaf5 + 0.5):
            _0x17d8e6 |= (0x176a + 0x183 + 0x7 * -0x38b)
            _0x499168 |= _0x216650['kKeyboardFast']
    _0xe06992['ubcode'] = _0x499168
    return _0xe06992['ubcode']


def _0x1633f2(a, b, c, d, e):
    Uint8Array = []
    d_md5 = ByteDance.md5(d)
    _0x26d461()
    _0x6caf = {
        'bogusIndex': 0,
        'envcode': 1,
    }
    _0x6caf['bogusIndex'] += 1
    _0xeefda2 = 0 | a << 6 | b << 5 | (1 & math.floor(100 * random.random())) << 4 | 0
    array0 = 63 & _0x6caf['bogusIndex']
    Uint8Array[0] = c << 6 | array0
    Uint8Array[1] = _0x6caf['envcode'] >> 8 & 255
    Uint8Array[2] = 255 & _0x6caf['envcode']
    Uint8Array[3] = _0xe06992['ubcode']
    _0x13f487 = ByteDance.decode(ByteDance.md5(ByteDance.decode(d_md5)))
    Uint8Array[4] = _0x13f487[14],
    Uint8Array[5] = _0x13f487[15];
    _0x136ce1 = ByteDance.decode(ByteDance.md5(ByteDance.decode(e)))
    Uint8Array[6] = _0x136ce1[14]
    Uint8Array[7] = _0x136ce1[15]
    Uint8Array[8] = 255 & math.floor(255 * random.random())
    return _0x4145f8(_0xeefda2, Uint8Array)

def _0x4145f8(a, b):
    pass
    _0x37237c = ""
    _0x37237c += chr(a)
    return chr(a)

# dict = {
#     # _0x1633f2(1, false, 0, null, "2f5d497b88accae9df4c90bcba019ffa")
#     'X-Bogus': _0x1633f2(1, False, 0, "", "2f5d497b88accae9df4c90bcba019ffa")
# };



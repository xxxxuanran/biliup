from biliup.common.tars import tarscore
from ..packet.__util import auto_decode_fields

@auto_decode_fields
class HuyaMultiStreamInfo(tarscore.struct):

    __tars_class__ = "HUYA.MultiStreamInfo"

    def __init__(self):
        self.sDisplayName: tarscore.string = ""
        self.iBitRate: tarscore.int32 = 0
        self.iCodecType: tarscore.int32 = 0
        self.iCompatibleFlag: tarscore.int32 = 0
        self.iHEVCBitRate: tarscore.int32 = -1
        self.iEnable: tarscore.int32 = 1
        self.iEnableMethod: tarscore.int32 = 0
        self.sEnableUrl: tarscore.string = ""
        self.sTipText: tarscore.string = ""
        self.sTagText: tarscore.string = ""
        self.sTagUrl: tarscore.string = ""
        self.iFrameRate: tarscore.int32 = 0
        self.iSortValue: tarscore.int32 = 0

    @staticmethod
    def writeTo(oos: tarscore.TarsOutputStream, value):
        oos.write(tarscore.string, 0, value.sDisplayName)
        oos.write(tarscore.int32, 1, value.iBitRate)
        oos.write(tarscore.int32, 2, value.iCodecType)
        oos.write(tarscore.int32, 3, value.iCompatibleFlag)
        oos.write(tarscore.int32, 4, value.iHEVCBitRate)
        oos.write(tarscore.int32, 5, value.iEnable)
        oos.write(tarscore.int32, 6, value.iEnableMethod)
        oos.write(tarscore.string, 7, value.sEnableUrl)
        oos.write(tarscore.string, 8, value.sTipText)
        oos.write(tarscore.string, 9, value.sTagText)
        oos.write(tarscore.string, 10, value.sTagUrl)
        oos.write(tarscore.int32, 11, value.iFrameRate)
        oos.write(tarscore.int32, 12, value.iSortValue)

    @staticmethod
    def readFrom(ios: tarscore.TarsInputStream):
        value = HuyaMultiStreamInfo()
        value.sDisplayName = ios.read(tarscore.string, 0, False)
        value.iBitRate = ios.read(tarscore.int32, 1, False)
        value.iCodecType = ios.read(tarscore.int32, 2, False)
        value.iCompatibleFlag = ios.read(tarscore.int32, 3, False)
        value.iHEVCBitRate = ios.read(tarscore.int32, 4, False)
        value.iEnable = ios.read(tarscore.int32, 5, False)
        value.iEnableMethod = ios.read(tarscore.int32, 6, False)
        value.sEnableUrl = ios.read(tarscore.string, 7, False)
        value.sTipText = ios.read(tarscore.string, 8, False)
        value.sTagText = ios.read(tarscore.string, 9, False)
        value.sTagUrl = ios.read(tarscore.string, 10, False)
        value.iFrameRate = ios.read(tarscore.int32, 11, False)
        value.iSortValue = ios.read(tarscore.int32, 12, False)
        return value

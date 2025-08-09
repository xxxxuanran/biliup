from biliup.common.tars import tarscore
from ..packet.__util import auto_decode_fields

@auto_decode_fields
class HuyaStreamSettingNotice(tarscore.struct):

    __tars_class__ = "HUYA.StreamSettingNotice"

    def __init__(self):
        self.lPresenterUid: tarscore.int64 = 0
        self.iBitRate: tarscore.int32 = 0
        self.iResolution: tarscore.int32 = 0
        self.iFrameRate: tarscore.int32 = 0
        self.lLiveId: tarscore.int64 = 0
        self.sDisplayName: tarscore.string = ""
        self.iScreenType: tarscore.int32 = 0
        self.sVideoLayout: tarscore.string = ""
        self.iLowDelayMode: tarscore.int32 = 0

    @staticmethod
    def writeTo(oos: tarscore.TarsOutputStream, value):
        oos.write(tarscore.int64, 0, value.lPresenterUid)
        oos.write(tarscore.int32, 1, value.iBitRate)
        oos.write(tarscore.int32, 2, value.iResolution)
        oos.write(tarscore.int32, 3, value.iFrameRate)
        oos.write(tarscore.int64, 4, value.lLiveId)
        oos.write(tarscore.string, 5, value.sDisplayName)
        oos.write(tarscore.int32, 6, value.iScreenType)
        oos.write(tarscore.string, 7, value.sVideoLayout)
        oos.write(tarscore.int32, 8, value.iLowDelayMode)

    @staticmethod
    def readFrom(ios: tarscore.TarsInputStream):
        value = HuyaStreamSettingNotice()
        value.lPresenterUid = ios.read(tarscore.int64, 0, False)
        value.iBitRate = ios.read(tarscore.int32, 1, False)
        value.iResolution = ios.read(tarscore.int32, 2, False)
        value.iFrameRate = ios.read(tarscore.int32, 3, False)
        value.lLiveId = ios.read(tarscore.int64, 4, False)
        value.sDisplayName = ios.read(tarscore.string, 5, False)
        value.iScreenType = ios.read(tarscore.int32, 6, False)
        value.sVideoLayout = ios.read(tarscore.string, 7, False)
        value.iLowDelayMode = ios.read(tarscore.int32, 8, False)
        return value


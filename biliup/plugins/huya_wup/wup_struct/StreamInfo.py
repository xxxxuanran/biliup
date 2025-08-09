from biliup.common.tars import tarscore
from ..packet.__util import auto_decode_fields

@auto_decode_fields
class HuyaStreamInfo(tarscore.struct):

    __tars_class__ = "Huya.StreamInfo"

    # 定义类级别的复合类型
    vctcls_string = tarscore.vctclass(tarscore.string)
    mapcls_string_string = tarscore.mapclass(tarscore.string, tarscore.string)

    def __init__(self):
        self.sCdnType: tarscore.string = ""
        self.iIsMaster: tarscore.int32 = 0
        self.lChannelId: tarscore.int64 = 0
        self.lSubChannelId: tarscore.int64 = 0
        self.lPresenterUid: tarscore.int64 = 0
        self.sStreamName: tarscore.string = ""
        self.sFlvUrl: tarscore.string = ""
        self.sFlvUrlSuffix: tarscore.string = ""
        self.sFlvAntiCode: tarscore.string = ""
        self.sHlsUrl: tarscore.string = ""
        self.sHlsUrlSuffix: tarscore.string = ""
        self.sHlsAntiCode: tarscore.string = ""
        self.iLineIndex: tarscore.int32 = 0
        self.iIsMultiStream: tarscore.int32 = 0
        self.iPCPriorityRate: tarscore.int32 = 0
        self.iWebPriorityRate: tarscore.int32 = 0
        self.iMobilePriorityRate: tarscore.int32 = 0
        self.vFlvIPList = HuyaStreamInfo.vctcls_string()
        self.iIsP2PSupport: tarscore.int32 = 0
        self.sP2pUrl: tarscore.string = ""
        self.sP2pUrlSuffix: tarscore.string = ""
        self.sP2pAntiCode: tarscore.string = ""
        self.lFreeFlag: tarscore.int64 = 0
        self.iIsHEVCSupport: tarscore.int32 = 0
        self.vP2pIPList = HuyaStreamInfo.vctcls_string()
        self.mpExtArgs = HuyaStreamInfo.mapcls_string_string()
        self.lTimespan: tarscore.int64 = 0
        self.lUpdateTime: tarscore.int64 = 0

    @staticmethod
    def writeTo(oos: tarscore.TarsOutputStream, value):
        oos.write(tarscore.string, 0, value.sCdnType)
        oos.write(tarscore.int32, 1, value.iIsMaster)
        oos.write(tarscore.int64, 2, value.lChannelId)
        oos.write(tarscore.int64, 3, value.lSubChannelId)
        oos.write(tarscore.int64, 4, value.lPresenterUid)
        oos.write(tarscore.string, 5, value.sStreamName)
        oos.write(tarscore.string, 6, value.sFlvUrl)
        oos.write(tarscore.string, 7, value.sFlvUrlSuffix)
        oos.write(tarscore.string, 8, value.sFlvAntiCode)
        oos.write(tarscore.string, 9, value.sHlsUrl)
        oos.write(tarscore.string, 10, value.sHlsUrlSuffix)
        oos.write(tarscore.string, 11, value.sHlsAntiCode)
        oos.write(tarscore.int32, 12, value.iLineIndex)
        oos.write(tarscore.int32, 13, value.iIsMultiStream)
        oos.write(tarscore.int32, 14, value.iPCPriorityRate)
        oos.write(tarscore.int32, 15, value.iWebPriorityRate)
        oos.write(tarscore.int32, 16, value.iMobilePriorityRate)
        oos.write(HuyaStreamInfo.vctcls_string, 17, value.vFlvIPList)
        oos.write(tarscore.int32, 18, value.iIsP2PSupport)
        oos.write(tarscore.string, 19, value.sP2pUrl)
        oos.write(tarscore.string, 20, value.sP2pUrlSuffix)
        oos.write(tarscore.string, 21, value.sP2pAntiCode)
        oos.write(tarscore.int64, 22, value.lFreeFlag)
        oos.write(tarscore.int32, 23, value.iIsHEVCSupport)
        oos.write(HuyaStreamInfo.vctcls_string, 24, value.vP2pIPList)
        oos.write(HuyaStreamInfo.mapcls_string_string, 25, value.mpExtArgs)
        oos.write(tarscore.int64, 26, value.lTimespan)
        oos.write(tarscore.int64, 27, value.lUpdateTime)

    @staticmethod
    def readFrom(ios: tarscore.TarsInputStream):
        value = HuyaStreamInfo()
        value.sCdnType = ios.read(tarscore.string, 0, False)
        value.iIsMaster = ios.read(tarscore.int32, 1, False)
        value.lChannelId = ios.read(tarscore.int64, 2, False)
        value.lSubChannelId = ios.read(tarscore.int64, 3, False)
        value.lPresenterUid = ios.read(tarscore.int64, 4, False)
        value.sStreamName = ios.read(tarscore.string, 5, False)
        value.sFlvUrl = ios.read(tarscore.string, 6, False)
        value.sFlvUrlSuffix = ios.read(tarscore.string, 7, False)
        value.sFlvAntiCode = ios.read(tarscore.string, 8, False)
        value.sHlsUrl = ios.read(tarscore.string, 9, False)
        value.sHlsUrlSuffix = ios.read(tarscore.string, 10, False)
        value.sHlsAntiCode = ios.read(tarscore.string, 11, False)
        value.iLineIndex = ios.read(tarscore.int32, 12, False)
        value.iIsMultiStream = ios.read(tarscore.int32, 13, False)
        value.iPCPriorityRate = ios.read(tarscore.int32, 14, False)
        value.iWebPriorityRate = ios.read(tarscore.int32, 15, False)
        value.iMobilePriorityRate = ios.read(tarscore.int32, 16, False)
        value.vFlvIPList = ios.read(HuyaStreamInfo.vctcls_string, 17, False)
        value.iIsP2PSupport = ios.read(tarscore.int32, 18, False)
        value.sP2pUrl = ios.read(tarscore.string, 19, False)
        value.sP2pUrlSuffix = ios.read(tarscore.string, 20, False)
        value.sP2pAntiCode = ios.read(tarscore.string, 21, False)
        value.lFreeFlag = ios.read(tarscore.int64, 22, False)
        value.iIsHEVCSupport = ios.read(tarscore.int32, 23, False)
        value.vP2pIPList = ios.read(HuyaStreamInfo.vctcls_string, 24, False)
        value.mpExtArgs = ios.read(HuyaStreamInfo.mapcls_string_string, 25, False)
        value.lTimespan = ios.read(tarscore.int64, 26, False)
        value.lUpdateTime = ios.read(tarscore.int64, 27, False)
        return value




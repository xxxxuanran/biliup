from biliup.common.tars import tarscore
from .StreamInfo import HuyaStreamInfo
from .MultiStreamInfo import HuyaMultiStreamInfo
from ..packet.__util import auto_decode_fields


@auto_decode_fields
class HuyaBeginLiveNotice(tarscore.struct):

    __tars_class__ = "HUYA.BeginLiveNotice"

    # 定义类级别的复合类型
    vctcls_streaminfo = tarscore.vctclass(HuyaStreamInfo)
    vctcls_string = tarscore.vctclass(tarscore.string)
    vctcls_multistreaminfo = tarscore.vctclass(HuyaMultiStreamInfo)
    mapcls_string_string = tarscore.mapclass(tarscore.string, tarscore.string)

    def __init__(self):
        self.lPresenterUid: tarscore.int64 = 0
        self.iGameId: tarscore.int32 = 0
        self.sGameName: tarscore.string = ""
        self.iRandomRange: tarscore.int32 = 0
        self.iStreamType: tarscore.int32 = 0
        self.vStreamInfo = HuyaBeginLiveNotice.vctcls_streaminfo()
        self.vCdnList = HuyaBeginLiveNotice.vctcls_string()
        self.lLiveId: tarscore.int64 = 0
        self.iPCDefaultBitRate: tarscore.int32 = 0
        self.iWebDefaultBitRate: tarscore.int32 = 0
        self.iMobileDefaultBitRate: tarscore.int32 = 0
        self.lMultiStreamFlag: tarscore.int64 = 0
        self.sNick: tarscore.string = ""
        self.lYYId: tarscore.int64 = 0
        self.lAttendeeCount: tarscore.int64 = 0
        self.iCodecType: tarscore.int32 = 0
        self.iScreenType: tarscore.int32 = 0
        self.vMultiStreamInfo = HuyaBeginLiveNotice.vctcls_multistreaminfo()
        self.sLiveDesc: tarscore.string = ""
        self.lLiveCompatibleFlag: tarscore.int64 = 0
        self.sAvatarUrl: tarscore.string = ""
        self.iSourceType: tarscore.int32 = 0
        self.sSubchannelName: tarscore.string = ""
        self.sVideoCaptureUrl: tarscore.string = ""
        self.iStartTime: tarscore.int32 = 0
        self.lChannelId: tarscore.int64 = 0
        self.lSubChannelId: tarscore.int64 = 0
        self.sLocation: tarscore.string = ""
        self.iCdnPolicyLevel: tarscore.int32 = 0
        self.iGameType: tarscore.int32 = 0
        self.mMiscInfo = HuyaBeginLiveNotice.mapcls_string_string()
        self.iShortChannel: tarscore.int32 = 0
        self.iRoomId: tarscore.int32 = 0
        self.bIsRoomSecret: tarscore.int32 = 0
        self.iHashPolicy: tarscore.int32 = 0
        self.lSignChannel: tarscore.int64 = 0
        self.iMobileWifiDefaultBitRate: tarscore.int32 = 0
        self.iEnableAutoBitRate: tarscore.int32 = 0
        self.iTemplate: tarscore.int32 = 0
        self.iReplay: tarscore.int32 = 0

    @staticmethod
    def writeTo(oos: tarscore.TarsOutputStream, value):
        oos.write(tarscore.int64, 0, value.lPresenterUid)
        oos.write(tarscore.int32, 1, value.iGameId)
        oos.write(tarscore.string, 2, value.sGameName)
        oos.write(tarscore.int32, 3, value.iRandomRange)
        oos.write(tarscore.int32, 4, value.iStreamType)
        oos.write(HuyaBeginLiveNotice.vctcls_streaminfo, 5, value.vStreamInfo)
        oos.write(HuyaBeginLiveNotice.vctcls_string, 6, value.vCdnList)
        oos.write(tarscore.int64, 7, value.lLiveId)
        oos.write(tarscore.int32, 8, value.iPCDefaultBitRate)
        oos.write(tarscore.int32, 9, value.iWebDefaultBitRate)
        oos.write(tarscore.int32, 10, value.iMobileDefaultBitRate)
        oos.write(tarscore.int64, 11, value.lMultiStreamFlag)
        oos.write(tarscore.string, 12, value.sNick)
        oos.write(tarscore.int64, 13, value.lYYId)
        oos.write(tarscore.int64, 14, value.lAttendeeCount)
        oos.write(tarscore.int32, 15, value.iCodecType)
        oos.write(tarscore.int32, 16, value.iScreenType)
        oos.write(HuyaBeginLiveNotice.vctcls_multistreaminfo, 17, value.vMultiStreamInfo)
        oos.write(tarscore.string, 18, value.sLiveDesc)
        oos.write(tarscore.int64, 19, value.lLiveCompatibleFlag)
        oos.write(tarscore.string, 20, value.sAvatarUrl)
        oos.write(tarscore.int32, 21, value.iSourceType)
        oos.write(tarscore.string, 22, value.sSubchannelName)
        oos.write(tarscore.string, 23, value.sVideoCaptureUrl)
        oos.write(tarscore.int32, 24, value.iStartTime)
        oos.write(tarscore.int64, 25, value.lChannelId)
        oos.write(tarscore.int64, 26, value.lSubChannelId)
        oos.write(tarscore.string, 27, value.sLocation)
        oos.write(tarscore.int32, 28, value.iCdnPolicyLevel)
        oos.write(tarscore.int32, 29, value.iGameType)
        oos.write(HuyaBeginLiveNotice.mapcls_string_string, 30, value.mMiscInfo)
        oos.write(tarscore.int32, 31, value.iShortChannel)
        oos.write(tarscore.int32, 32, value.iRoomId)
        oos.write(tarscore.int32, 33, value.bIsRoomSecret)
        oos.write(tarscore.int32, 34, value.iHashPolicy)
        oos.write(tarscore.int64, 35, value.lSignChannel)
        oos.write(tarscore.int32, 36, value.iMobileWifiDefaultBitRate)
        oos.write(tarscore.int32, 37, value.iEnableAutoBitRate)
        oos.write(tarscore.int32, 38, value.iTemplate)
        oos.write(tarscore.int32, 39, value.iReplay)

    @staticmethod
    def readFrom(ios: tarscore.TarsInputStream):
        value = HuyaBeginLiveNotice()
        value.lPresenterUid = ios.read(tarscore.int64, 0, False)
        value.iGameId = ios.read(tarscore.int32, 1, False)
        value.sGameName = ios.read(tarscore.string, 2, False)
        value.iRandomRange = ios.read(tarscore.int32, 3, False)
        value.iStreamType = ios.read(tarscore.int32, 4, False)
        value.vStreamInfo = ios.read(HuyaBeginLiveNotice.vctcls_streaminfo, 5, False)
        value.vCdnList = ios.read(HuyaBeginLiveNotice.vctcls_string, 6, False)
        value.lLiveId = ios.read(tarscore.int64, 7, False)
        value.iPCDefaultBitRate = ios.read(tarscore.int32, 8, False)
        value.iWebDefaultBitRate = ios.read(tarscore.int32, 9, False)
        value.iMobileDefaultBitRate = ios.read(tarscore.int32, 10, False)
        value.lMultiStreamFlag = ios.read(tarscore.int64, 11, False)
        value.sNick = ios.read(tarscore.string, 12, False)
        value.lYYId = ios.read(tarscore.int64, 13, False)
        value.lAttendeeCount = ios.read(tarscore.int64, 14, False)
        value.iCodecType = ios.read(tarscore.int32, 15, False)
        value.iScreenType = ios.read(tarscore.int32, 16, False)
        value.vMultiStreamInfo = ios.read(HuyaBeginLiveNotice.vctcls_multistreaminfo, 17, False)
        value.sLiveDesc = ios.read(tarscore.string, 18, False)
        value.lLiveCompatibleFlag = ios.read(tarscore.int64, 19, False)
        value.sAvatarUrl = ios.read(tarscore.string, 20, False)
        value.iSourceType = ios.read(tarscore.int32, 21, False)
        value.sSubchannelName = ios.read(tarscore.string, 22, False)
        value.sVideoCaptureUrl = ios.read(tarscore.string, 23, False)
        value.iStartTime = ios.read(tarscore.int32, 24, False)
        value.lChannelId = ios.read(tarscore.int64, 25, False)
        value.lSubChannelId = ios.read(tarscore.int64, 26, False)
        value.sLocation = ios.read(tarscore.string, 27, False)
        value.iCdnPolicyLevel = ios.read(tarscore.int32, 28, False)
        value.iGameType = ios.read(tarscore.int32, 29, False)
        value.mMiscInfo = ios.read(HuyaBeginLiveNotice.mapcls_string_string, 30, False)
        value.iShortChannel = ios.read(tarscore.int32, 31, False)
        value.iRoomId = ios.read(tarscore.int32, 32, False)
        value.bIsRoomSecret = ios.read(tarscore.int32, 33, False)
        value.iHashPolicy = ios.read(tarscore.int32, 34, False)
        value.lSignChannel = ios.read(tarscore.int64, 35, False)
        value.iMobileWifiDefaultBitRate = ios.read(tarscore.int32, 36, False)
        value.iEnableAutoBitRate = ios.read(tarscore.int32, 37, False)
        value.iTemplate = ios.read(tarscore.int32, 38, False)
        value.iReplay = ios.read(tarscore.int32, 39, False)
        return value

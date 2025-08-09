from biliup.common.tars import tarscore
from .__util import auto_decode_fields
from ..wup_struct.UserId import HuyaUserId
from ..wup_struct.BeginLiveNotice import HuyaBeginLiveNotice
from ..wup_struct.StreamSettingNotice import HuyaStreamSettingNotice

@auto_decode_fields
class HuyaGetLivingInfoReq(tarscore.struct):

    __tars_class__ = "HUYA.GetLivingInfoReq"

    def __init__(self):
        self.tId: HuyaUserId = HuyaUserId()
        self.lTopSid: tarscore.int64 = 0
        self.lSubSid: tarscore.int64 = 0
        self.lPresenterUid: tarscore.int64 = 0
        self.sTraceSource: tarscore.string = ""
        self.sPassword: tarscore.string = ""
        self.iRoomId: tarscore.int64 = 0
        self.iFreeFlowFlag: tarscore.int32 = 0
        self.iIpStack: tarscore.int32 = 0

    @staticmethod
    def writeTo(oos: tarscore.TarsOutputStream, value):
        oos.write(HuyaUserId, 0, value.tId)
        oos.write(tarscore.int64, 1, value.lTopSid)
        oos.write(tarscore.int64, 2, value.lSubSid)
        oos.write(tarscore.int64, 3, value.lPresenterUid)
        oos.write(tarscore.string, 4, value.sTraceSource)
        oos.write(tarscore.string, 5, value.sPassword)
        oos.write(tarscore.int64, 6, value.iRoomId)
        oos.write(tarscore.int32, 7, value.iFreeFlowFlag)
        oos.write(tarscore.int32, 8, value.iIpStack)

    @staticmethod
    def readFrom(ios: tarscore.TarsInputStream):
        value = HuyaGetLivingInfoReq()
        value.tId = ios.read(HuyaUserId, 0, False)
        value.lTopSid = ios.read(tarscore.int64, 1, False)
        value.lSubSid = ios.read(tarscore.int64, 2, False)
        value.lPresenterUid = ios.read(tarscore.int64, 3, False)
        value.sTraceSource = ios.read(tarscore.string, 4, False)
        value.sPassword = ios.read(tarscore.string, 5, False)
        value.iRoomId = ios.read(tarscore.int64, 6, False)
        value.iFreeFlowFlag = ios.read(tarscore.int32, 7, False)
        value.iIpStack = ios.read(tarscore.int32, 8, False)
        return value


@auto_decode_fields
class HuyaGetLivingInfoRsp(tarscore.struct):

    __tars_class__ = "HUYA.GetLivingInfoRsp"

    def __init__(self):
        self.bIsLiving: tarscore.int32 = 0
        self.tNotice: HuyaBeginLiveNotice = HuyaBeginLiveNotice()
        self.tStreamSettingNotice: HuyaStreamSettingNotice = HuyaStreamSettingNotice()
        self.bIsSelfLiving: tarscore.int32 = 0
        self.sMessage: tarscore.string = ""
        self.iShowTitleForImmersion: tarscore.int32 = 0

    @staticmethod
    def writeTo(oos: tarscore.TarsOutputStream, value):
        oos.write(tarscore.int32, 0, value.bIsLiving)
        oos.write(HuyaBeginLiveNotice, 1, value.tNotice)
        oos.write(HuyaStreamSettingNotice, 2, value.tStreamSettingNotice)
        oos.write(tarscore.int32, 3, value.bIsSelfLiving)
        oos.write(tarscore.string, 4, value.sMessage)
        oos.write(tarscore.int32, 5, value.iShowTitleForImmersion)

    @staticmethod
    def readFrom(ios: tarscore.TarsInputStream):
        value = HuyaGetLivingInfoRsp()
        value.bIsLiving = ios.read(tarscore.int32, 0, False)
        value.tNotice = ios.read(HuyaBeginLiveNotice, 1, False)
        value.tStreamSettingNotice = ios.read(HuyaStreamSettingNotice, 2, False)
        value.bIsSelfLiving = ios.read(tarscore.int32, 3, False)
        value.sMessage = ios.read(tarscore.string, 4, False)
        value.iShowTitleForImmersion = ios.read(tarscore.int32, 5, False)
        return value

    def as_dict(self):
        def _convert_to_dict(obj):
            if isinstance(obj, list):
                # 处理 vector 类型 - 必须在 hasattr(__dict__) 之前检查
                return [_convert_to_dict(item) for item in obj]
            elif isinstance(obj, dict):
                # 处理 map 类型 - 必须在 hasattr(__dict__) 之前检查
                return {str(k): _convert_to_dict(v) for k, v in obj.items()}
            elif hasattr(obj, '__dict__'):
                # 处理结构体对象
                result = {}
                for attr_name, attr_value in vars(obj).items():
                    result[attr_name] = _convert_to_dict(attr_value)
                return result
            else:
                # 基本类型直接返回
                return obj

        return _convert_to_dict(self)

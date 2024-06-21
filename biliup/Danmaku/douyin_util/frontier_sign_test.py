import execjs  # 导入 execjs 库
import hashlib

from xbogus import _0x26d461

class ByteDance:
    @staticmethod
    def md5(string) -> str:
        return hashlib.md5(bytearray(string)).hexdigest()

    @staticmethod
    def decode(hex_str) -> list:
        return list(bytes.fromhex(hex_str))

# https://juejin.cn/post/7256769427600949305
# https://blog.csdn.net/weixin_46084750/article/details/136541654
# https://blog.csdn.net/wangenjie1992/article/details/136631034

# https://blog.csdn.net/m0_75268677/article/details/137596255

def main():
    # e = "2f5d497b88accae9df4c90bcba019ffa"
    # list = ByteDance.decode(ByteDance.md5(ByteDance.decode(e)))
    # print(list)
    # if [105, 79, 195, 101, 93, 204, 30, 3, 92, 154, 42, 65, 123, 151, 206, 6] == list:
    #     print("true")
    val = _0x26d461()
    print(val)
    if val == "14":
        print("true")

if __name__ == "__main__":
    main()
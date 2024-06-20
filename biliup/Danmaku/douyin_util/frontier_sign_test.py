import execjs  # 导入 execjs 库

# 载入 JavaScript 文件
def load_js(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def main():
    js_code = load_js("e:/Projects/biliup/biliup/Danmaku/douyin_util/webmssdk.es5.js")  # 指定 JavaScript 文件名
    context = execjs.compile(js_code)  # 编译 JS 代码

    # 创建一个 JS 对象，并设置其键和值
    js_object = {"X-MS-STUB": "4da9bc16093d71bc00627f22f4552c0a"}

    # 调用 JavaScript 中的 _0x5c2014 函数，并传入 js_object
    result = context.call("_0x5c2014", js_object)
    print("Result from JS function:", result)

if __name__ == "__main__":
    main()
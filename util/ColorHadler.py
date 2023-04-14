# RGB格式颜色转换为16进制颜色格式
def RGB_to_Hex(rgb):
    RGB = rgb.split(',')  # 将RGB格式划分开来
    color = '#'
    for i in RGB:
        num = int(i)
        # 将R、G、B分别转化为16进制拼接转换并大写  hex() 函数用于将10进制整数转换成16进制，以字符串形式表示
        color += str(hex(num))[-2:].replace('x', '0').upper()
    # print(color)
    return color


def RGB_tuple_to_Hex(rgb_tuple):
    color = '#'
    for i in rgb_tuple:
        num = int(i)
        # 将R、G、B分别转化为16进制拼接转换并大写  hex() 函数用于将10进制整数转换成16进制，以字符串形式表示
        color += str(hex(num))[-2:].replace('x', '0').upper()
    # print(color)
    return color


# 16进制颜色格式颜色转换为RGB格式
def Hex_to_RGB(hex):
    r = int(hex[1:3], 16)
    g = int(hex[3:5], 16)
    b = int(hex[5:7], 16)
    rgb = str(r) + ',' + str(g) + ',' + str(b)
    # print(rgb)
    return rgb

# 16进制颜色格式颜色转换为RGB格式
def Hex_to_RGB_tuple(hex):
    r = int(hex[1:3], 16)
    g = int(hex[3:5], 16)
    b = int(hex[5:7], 16)
    # rgb = str(r) + ',' + str(g) + ',' + str(b)
    rgb = (r,g,b)
    # print(rgb)
    return rgb


def Hex_to_RGB_float_tuple(hex):
    r = round(int(hex[1:3], 16)/255,2)
    g = round(int(hex[3:5], 16)/255,2)
    b = round(int(hex[5:7], 16)/255,2)
    # rgb = str(r) + ',' + str(g) + ',' + str(b)
    rgb = (r,g,b)
    # print(rgb)
    return rgb

def RGB_tuple_RGB_float_tuple(rgb):
    r = round(rgb[0]/255,2)
    g = round(rgb[1]/255,2)
    b = round(rgb[2]/255,2)
    return (r,g,b)


# 获取所有的RGB颜色
def get_allRGB():
    rgb = []
    for i in range(0, 256):
        for j in range(0, 256):
            for c in range(0, 256):
                rgb.append(str(i) + ',' + str(j) + ',' + str(c))
    return (rgb)
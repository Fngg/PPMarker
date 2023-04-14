
# 输入参数 str 需要判断的字符串
# 返回值   True：该字符串为浮点数；False：该字符串不是浮点数。
def IsFloatNum(str):
    s=str.split('.')
    if len(s)>2 or len(s)==0:
        return False
    else:
        for si in s:
            if not si.isdigit():
                return False
        return True
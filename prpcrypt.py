class prpcrypt():
    def __init__(self):
        self.k = 'djq%5cu#-jeq15abg$z9_i#_w=$o88m!*alpbedlbat8cr74sd0123456789' \
                 'djq%5cu#-jeq15abg$z9_i#_w=$o88m!*alpbedlbat8cr74sd0123456789' \
                 '*alpbedlbat8cr74sd0123456789djq%5cu#-jeq15abg$z9_i#_w=$o88m!' \
                 'djq%5cu#-jeq15abg$z9_i#_w=$o88m!*alpbedlbat8cr74sd0123456789' \
                 'djq%5cu#-jeq15abg$z9_i#_w=$o88m!*alpbedlbat8cr74sd0123456789' \
                 '*alpbedlbat8cr74sd0123456789djq%5cu#-jeq15abg$z9_i#_w=$o88m!' \
                 'djq%5cu#-jeq15abg$z9_i#_w=$o88m!*alpbedlbat8cr74sd0123456789'
    def enctry(self, s):
        encry_str = ""
        for i, j in zip(s, self.k):
            # i为字符，j为秘钥字符
            temp = str(ord(i)+ord(j))+'_' # 加密字符 = 字符的Unicode码 + 秘钥的Unicode码
            encry_str = encry_str + temp
        return encry_str

    def dectry(self, p):
        dec_str = ""
        for i, j in zip(p.split("_")[:-1], self.k):
            # i 为加密字符，j为秘钥字符
            temp = chr(int(i) - ord(j))  # 解密字符 = (加密Unicode码字符 - 秘钥字符的Unicode码)的单字节字符
            dec_str = dec_str + temp
        return dec_str

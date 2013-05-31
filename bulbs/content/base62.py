AB = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def base10to62(num):
        if num == 0:
                return AB[0]

        arr = []

        while num:
                rem = num % 62
                num = num - rem
                num = num / 62
                arr.append(AB[rem])

        arr.reverse()
        return ''.join(arr)


def base62to10(numString):
        numString = numString[::-1]
        # print numString
        b10 = 0
        i = 0

        for char in numString:
                place = 62 ** i
                # print place
                value = AB.index(char)
                b10 = b10 + (value * place)
                i = i + 1

        return b10

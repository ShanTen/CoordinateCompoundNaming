from lexer import passTokens
import huepy as hp

while 1:
    text = input("NM => ")
    res, err = passTokens(text)

    if err:
        print(hp.red(err.stringify()))
    else:
        print(hp.orange(text))
        print(hp.green(res))
        print("-----")
    
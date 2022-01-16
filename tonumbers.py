
def transfer(number: str):
    return number.replace('K', '0'*3).replace('M', '0'*6)
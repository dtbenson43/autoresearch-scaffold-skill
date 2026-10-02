def solve(n):
    if type(n) is not int or not 0 <= n <= 1000:
        raise ValueError('domain')
    total = 0
    for k in range(n + 1):
        total += k * k
    return total

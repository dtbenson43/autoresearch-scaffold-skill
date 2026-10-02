def solve(n):
    if type(n) is not int or not 0 <= n <= 1000:
        raise ValueError('domain')
    return n * (n + 1) * (2 * n + 1) // 6

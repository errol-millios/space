def signum(x): return 1 if x > 0 else -1 if x < 0 else 0

def trunc(s):
    n = 40
    if len(s) > n:
        s = s[:n] + ' ...'
    return s

import numpy as np

# population must be sorted
def multivariateHypergeometricSample(population, size, scale=10000, minSamples=2):
    sample = np.random.choice(scale, int(min(scale, max(minSamples, size * scale))), False)
    sample.sort()
    intervals = np.cumsum([proportion * scale for key, proportion in population])
    N = len(intervals)

    intervalCounts = [0] * N
    upper = intervals[0]
    currentInterval = 0
    it = iter(sample)
    k = it.next()
    while True:
        if k < upper:
            intervalCounts[currentInterval] += 1
            k = it.next()
        else:
            currentInterval += 1
            if currentInterval >= N:
                break
            upper = intervals[currentInterval]

    index = (i for i in xrange(N))
    return [(key, float(intervalCounts[index.next()]) / scale) for key, _ in population]

if __name__ == '__main__':
    print(multivariateHypergeometricSample([('a', 0.1), ('b', 0.2)], 0.01))

"""Generate statistics on measurement error.

Error for Poisson process sampling in the case of a 1-D object travelling at
constant speed with steady .
"""

import random
import math
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import emcee


def lnprob(theta, errors):
    sigma, = theta
    if sigma < 0:
        return -np.inf
    return np.sum(np.log(sigma) - sigma*errors)
    # return np.sum(np.log(1/(math.sqrt(2)*math.pi*sigma)) -
    #               0.5 * errors**2 / sigma**2)

speed = 50.0 / 3.6  # km/h to m/s
cache_rate = 30
sample_rate = - math.log(0.205) / 30.0
last_sampled_time = 0
next_sample_interval = 0
errors = []
actual_pos = 0
measured_pos = 0

for cache in range(cache_rate, 1000000, cache_rate):
    prev_sampled_time = last_sampled_time
    while last_sampled_time + next_sample_interval < cache:
        last_sampled_time += next_sample_interval
        next_sample_interval = -math.log(1.0 - random.random()) / sample_rate

    actual_pos += cache_rate * speed
    measured_pos = (last_sampled_time) * speed
    errors.append(actual_pos - measured_pos)

# n, bins, patches = plt.hist(np.asarray(errors), 50, normed=1,
#                            facecolor='green', alpha=0.75)
# l = plt.plot(bins)
n, bins, patches = plt.hist(np.asarray(errors), 50, normed=1, cumulative=False)

ndim, nwalkers = 1, 100
pos = [100 + 1e-4*np.random.randn(ndim) for i in range(nwalkers)]

sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob,
                                args=(np.asarray(errors),))

sampler.run_mcmc(pos, 1000)

samples = sampler.chain[:, 500:, :].reshape((-1, ndim))

# samples[:, 2] = np.exp(samples[:, 2])
l_mcmc, = map(lambda v: (v[1], v[2]-v[1], v[1]-v[0]),
              zip(*np.percentile(samples, [16, 50, 84],
                                 axis=0)))
print l_mcmc
# y = mlab.normpdf(bins, 0, l_mcmc[0]).cumsum()
sigma = l_mcmc[0]
y = sigma * np.exp(- sigma * bins)
plt.plot(bins, y, 'r--')

plt.show()

# speed = uniform dist, time = exp dist
# distance = speed * time
# p(distance) = integral 0 to max-speed of (A)*(l * exp(-l*distance/speed)) dspeed
# = A*

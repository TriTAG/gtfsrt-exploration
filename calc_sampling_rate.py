"""x."""
# Assume Poisson distribution for GRT data updates
# Expected no. of data updates in 30 seconds (approx) is lambda
# In 30 second interval
#     * P(no update) = exp(-lambda)
#     * P(at least one update) = 1 - P(no update)
# These are all independent, so can be chained together multiplicatively
# when trying to find maximum likelihood
# P(samples|lambda) = P(no)**(no. w/o update)*P(1+)**(no. with update)
# P(lambda) = { zero if <= 0 }

# next_time = -math.log(1.0 - random.random()) / rateParameter

import numpy as np
import math
import emcee


def lnlike(theta, n_missed, n_sampled):
    """Log likelihood function."""
    l, = theta
    P_miss = math.exp(-l)
    P_sample = 1 - P_miss
    return n_sampled * math.log(P_sample) + n_missed * math.log(P_miss)


def lnprior(theta):
    """Log prior function."""
    l, = theta
    if l > 0:
        return 0.0
    return -np.inf


def lnprob(theta, n_missed, n_sampled):
    """Log probability function."""
    lp = lnprior(theta)
    if not np.isfinite(lp):
        return -np.inf
    return lp + lnlike(theta, n_missed, n_sampled)

ndim, nwalkers = 1, 100
pos = [1 + 1e-4*np.random.randn(ndim) for i in range(nwalkers)]

sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob, args=(52502, 230201))

sampler.run_mcmc(pos, 5000)

samples = sampler.chain[:, 2500:, :].reshape((-1, ndim))

# samples[:, 2] = np.exp(samples[:, 2])
l_mcmc, = map(lambda v: (v[1], v[2]-v[1], v[1]-v[0]),
              zip(*np.percentile(samples, [16, 50, 84],
                                 axis=0)))
print l_mcmc

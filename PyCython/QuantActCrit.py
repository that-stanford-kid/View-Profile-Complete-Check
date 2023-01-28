# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 12:57:47 2022
@author: p0ne
"""
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import sympy as smp
plt.style.use(['seaborn-ticks', 'dark_background'])

x = np.linspace(0,3,1000)
f = 2*np.exp(-2*x)
F = 1-np.exp(-2*x)

plt.figure(figsize=(8,3))
plt.plot(x, f, label=r'$f(x)$')
plt.plot(x,F, label=r'$F(x)$')
plt.legend()
plt.xlabel('$x$', fontsize=20)
plt.legend()
plt.show()

Us = np.random.rand(10000)
plt.hist(Us)
plt.show()

Us = np.random.rand(10000)
F_inv_Us = -np.log(1-Us)/2

plt.figure(figsize=(8,3))
plt.plot(x, f, label=r'$f(x)$')
plt.hist(F_inv_Us, histtype='step', color='orange', density='norm', bins=100,  linewidth=1.3, label='F^{-1}(u)$')
plt.legend()
plt.xlabel('$x$', fontsize=20)
plt.legend()
plt.show()

x, y, F1, F2, E1, E2 = smp.symbols('x y F_1 F_2 E_1 E_2', real=True, positive=True)
fs = F1*smp.exp(-smp.sqrt(x/E1)) + F2*smp.exp(-smp.sqrt(x/E2))
fs

Fs = smp.integrate(fs, (x,0,y)).doit()
Fs

Fn = smp.lambdify((y, E1, E2, F1, F2), Fs)
fn = smp.lambdify((x, E1, E2, F1, F2), fs)

E1 = E2 = 0,2
F1 = 1.3
F2 = 1.4
x = np.linspace(0,5,1000)
f = fn(x, E1, E2, F1, F2)
F = Fn(x, E1, E2, F1, F2)

plt.figure(figsize=(8,3))
plt.plot(x, f, label=r'$f(x)$')
plt.plot(x,F, label=r'$F(x)$')
plt.legend()
plt.xlabel('$x$', fontsize=20)
plt.legend()
plt.show()

F_inv_Us = x[np.searchsorted(F[:-1], Us)]

plt.figure(figsize=(11,4))
plt.plot(x, f, label=r'$f(x)$')
plt.hist(F_inv_Us, histtype='step', color='red', density='norm', bins=100)
plt.legend()
plt.xlabel('$x$', fontsize=20)
plt.legend()
plt.xlim(0,2)
plt.show()

r = np.random.rayleigh(size=1000)
plt.hist(r, bins=100)
plt.show()

N = 100000 #poisson variables in 10s window slide, counting variables.unique
# p1
X = np.random.poisson(lam=4, size=N) # lambda = 4
# p2
x = np.linspace(0,5,1000)
F = Fn(x, E1, E2, F1, F2)
Us = np.random.rand(X.sum())
E = x[np.searchsorted(F[:-1], Us)]

# get net sum of signlads detected after n experiments, ie total
idx = np.insert(x.cumsum(), 0, 0)[:-1]
idx[0:10]
E[0:10]
E_10s = np.add.reduceat(E, idx)
plt.figure() # differential of f(x) | F(x)

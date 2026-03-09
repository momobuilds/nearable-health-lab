import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

def plot_pz(b, a):
    """ Plot zeros and poles of a filter given its coefficients """
    zeros, poles, _ = signal.tf2zpk(b, a)
    
    plt.figure(figsize=(6, 6))
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.grid(True, linestyle='--', linewidth=0.5)
    
    plt.scatter(np.real(zeros), np.imag(zeros), marker='o', color='blue', label='Zeros')
    plt.scatter(np.real(poles), np.imag(poles), marker='x', color='red', label='Poles')
    
    unit_circle = plt.Circle((0, 0), 1, color='gray', fill=False, linestyle='dashed')
    plt.gca().add_patch(unit_circle)
    
    plt.xlabel('Real')
    plt.ylabel('Imaginary')
    plt.title('Pole-Zero Plot')
    plt.legend()
    plt.axis('equal')
    plt.show()

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D


def plot_different_values(plot_values):

    alphas = np.array([p[0] for p in plot_values])
    weights = np.array([p[1] for p in plot_values])
    scores = np.array([p[2] for p in plot_values])

    # Recover the grid
    unique_alphas = np.unique(alphas)
    unique_weights = np.unique(weights)

    A, W = np.meshgrid(unique_alphas, unique_weights, indexing="ij")

    Z = np.zeros_like(A, dtype=float)

    alpha_index = {a: i for i, a in enumerate(unique_alphas)}
    weight_index = {w: j for j, w in enumerate(unique_weights)}

    for a, w, s in plot_values:
        Z[alpha_index[a], weight_index[w]] = s

    fig = plt.figure(figsize=(9,7))
    ax = fig.add_subplot(111, projection="3d")

    ax.plot_surface(A, W, Z)

    ax.set_xlabel(r"$\alpha$")
    ax.set_ylabel(r"$w$")
    ax.set_zlabel("Bell score")

    plt.show()






import scipy
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from gpsearch.examples import Michalewicz, Bukin
from gpsearch import custom_KDE, Likelihood, GaussianInputs, BlackBox
import GPy


def main():

    ndim = 2
    
   #domain = [ [-4,4], [-4,4] ]
   #mean = np.zeros(ndim)
   #cov = np.array([1,1])
   #inputs = GaussianInputs(domain, mean, cov)
   #my_map = BlackBox(lambda x: 5 + x[0] + x[1] + 2*np.cos(x[0]) + 2*np.sin(x[1]))

    function = Michalewicz(rescale_X=True)
    my_map, inputs = function.my_map, function.inputs
    domain = inputs.domain
   #mean = np.zeros(inputs.input_dim) + np.pi/2
   #cov = np.ones(inputs.input_dim)*0.1

    mean = np.zeros(inputs.input_dim) + 0.5
    cov = np.ones(inputs.input_dim)*0.01

    inputs = GaussianInputs(domain, mean, cov)
    
    ngrid = 100
    pts = inputs.draw_samples(n_samples=ngrid, sample_method="grd")
    ndim = pts.shape[-1]
    grd = pts.reshape( (ngrid,)*ndim + (ndim,) ).T
    X, Y = grd[0], grd[1]

    # Compute map
    yy = my_map.evaluate(pts)
    ZZ = yy.reshape( (ngrid,)*ndim ).T

    # Compute input pdf
    pdfx = inputs.pdf(pts)
    PX = pdfx.reshape( (ngrid,)*ndim ).T
        
    # Compute likelihood ratio
    x, y = custom_KDE(yy, weights=inputs.pdf(pts)).evaluate()
    fnTn = scipy.interpolate.interp1d(x, y)
    fx = inputs.pdf(pts).flatten()
    fy = fnTn(yy).flatten()
    yyg = fx/fy
    ZL = yyg.reshape( (ngrid,)*ndim ).T

    # Compute GMM fit
    kwargs_GMM = dict(n_components=2, covariance_type="full")
    model = GPy.models.GPRegression(np.random.rand(2,ndim), np.random.rand(2,1))
    likelihood = Likelihood(model, inputs)
    gmm = likelihood._fit_gmm(pts, yyg, kwargs_GMM)
    zg = np.exp(gmm.score_samples(pts))
    ZG = zg.reshape( (ngrid,)*ndim ).T

    fig = plt.figure(figsize=(6.0,1.65), constrained_layout=True)
    fs=10

  # fig = plt.figure(figsize=(2.7,0.75), constrained_layout=True)
  # fs=9

    fig.set_constrained_layout_pads(w_pad=0.02, h_pad=0.01)
    n_contours = 14
    n_contours = 7

    ax1 = plt.subplot(1, 4, 1)
    plt.contourf(X, Y, ZZ, n_contours, cmap='terrain')
    plt.contour(X, Y, ZZ, n_contours, colors='k', linewidths=0.75, linestyles="solid")
    plt.title(r"$f(\mathbf{x})$", fontsize=fs)

    ax2 = plt.subplot(1, 4, 2)
    cnt2 = plt.contourf(X, Y, PX, 50, cmap='Reds')
    plt.title(r"$p_\mathbf{x}(\mathbf{x})$", fontsize=fs)

    ax3 = plt.subplot(1, 4, 3)
    cnt3 = plt.contourf(X, Y, ZL, 50, cmap='Reds')
    plt.title(r"$w(\mathbf{x})$", fontsize=fs)

    ax4 = plt.subplot(1, 4, 4)
    cnt4 = plt.contourf(X, Y, ZG, 50, cmap='Reds')
    plt.title(r"$w_\mathit{GMM}(\mathbf{x})$", fontsize=fs)

    for cnt in (cnt2, cnt3, cnt4):
        for c in cnt.collections:
            c.set_edgecolor("face")

    for ax in (ax2, ax3, ax4):
        ax.contour(X, Y, ZZ, n_contours, colors='0.5', linewidths=0.2, linestyles="solid")

    for ax in (ax1, ax2, ax3, ax4):
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.tick_params(length=0)

    plt.savefig("new_likelihood.pdf")
    plt.close()


if __name__ == "__main__":

    main()

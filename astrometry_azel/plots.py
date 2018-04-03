from pathlib import Path
import logging
import xarray
from matplotlib.pyplot import figure

def plotazel(scale:xarray.Dataset):

    plottype = 'contour'

    fg = figure(figsize=(12,5))
    ax = fg.subplots(1,2,sharey=True)

    fg.suptitle(f'{scale.filename.name} {scale.lat} {scale.lon} {scale.time}')
# %%
    axa=ax[0]

    if plottype=='image':
        hia = axa.imshow(scale['az'],origin='lower')
        hc = fg.colorbar(hia)
        hc.set_label('Azimuth [deg]')
    elif plottype == 'contour':
        cs = axa.contour(scale['x'], scale['y'], scale['az'])
        axa.clabel(cs, inline=1,fmt='%0.1f')

    axa.set_xlabel('x-pixel')
    axa.set_ylabel('y-pixel')
    axa.set_title('azimuth')
# %%
    axe = ax[1]
    if plottype=='image':
        hie = axe.imshow(scale['el'], origin='lower')
        hc = fg.colorbar(hie)
        hc.set_label('Elevation [deg]')
    elif plottype == 'contour':
        cs = axe.contour(scale['x'], scale['y'], scale['el'])
        axe.clabel(cs, inline=1,fmt='%0.1f')

    axe.set_xlabel('x-pixel')
    axe.set_ylabel('y-pixel')
    axe.set_title('elevation')


def plotradec(scale:xarray.Dataset):

    plottype = 'contour'

    fg = figure(figsize=(12,5))
    axs = fg.subplots(1,2, sharey=True)

    ax = axs[0]

    if plottype=='image':
        hri = ax.imshow(scale['ra'],origin='lower')
        hc = fg.colorbar(hri)
        hc.set_label('RA [deg]')
    elif plottype == 'contour':
        cs= ax.contour(scale['x'], scale['y'], scale['ra'])
        ax.clabel(cs, inline=1,fmt='%0.1f')

    ax.set_xlabel('x-pixel')
    ax.set_ylabel('y-pixel')
    ax.set_title('Right Ascension ')
#%%
    ax = axs[1]
    if plottype=='image':
        hdi = ax.imshow(scale['dec'], origin='lower')
        hc = fg.colorbar(hdi)
        hc.set_label('Dec [deg]')
    elif plottype == 'contour':
        cs= ax.contour(scale['x'], scale['y'], scale['dec'])
        ax.clabel(cs, inline=1,fmt='%0.1f')
    ax.set_xlabel('x-pixel')
    ax.set_ylabel('y-pixel')
    ax.set_title('Declination')


def plotimagestack(img,fn,makeplot,clim=None):
    fn = Path(fn).expanduser()
    #%% plotting
    if img.ndim==3 and img.shape[0] == 3: #it seems to be an RGB image
        cmap = None
        imnorm = None
        img = img.transpose([1,2,0]) #imshow() needs colors to be last axis
    else:
        cmap = 'gray'
        imnorm=None
        #imnorm = LogNorm()

    fg = figure()
    ax = fg.gca()
    if clim is None:
        hi = ax.imshow(img,origin='lower',interpolation='none',cmap=cmap,norm=imnorm)
    else:
        hi = ax.imshow(img,origin='lower',interpolation='none',cmap=cmap,vmin=clim[0],vmax=clim[1],norm=imnorm)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(str(fn))
    if cmap is not None:
        try:
            hc = fg.colorbar(hi)
            hc.set_label(f'Data numbers {img.dtype}')
        except Exception as e:
            logging.warning(f'trouble making picture colorbar  {e}')
#%%
    if 'png' in makeplot:
        plotFN = fn.parent/(fn.stem+'_picture.png')
        print('writing', plotFN)
        fg.savefig(plotFN, bbox_inches='tight', dpi=150)

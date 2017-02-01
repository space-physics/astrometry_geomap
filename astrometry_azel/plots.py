#!/usr/bin/env python
from pathlib import Path
import logging
from matplotlib.pyplot import figure

def plotazel(az,el,x=None,y=None, fn='',camLatLon='',timeFrame='',makeplot='',ttxt=''):
    fn = Path(fn)

    if 'show' in makeplot or 'png' in makeplot:
        plottype = 'contour'

        fg = figure(figsize=(12,5))
        axa = fg.add_subplot(1,2,1)
        if plottype=='image':
            hia = axa.imshow(az,origin='lower')
            hc = fg.colorbar(hia)
            hc.set_label('Azimuth [deg]')
        elif plottype == 'contour':
            if x is not None and y is not None:
                cs = axa.contour(x,y,az)
            else:
                cs = axa.contour(az)
            axa.clabel(cs, inline=1,fmt='%0.1f')

        axa.set_xlabel('x-pixel')
        axa.set_ylabel('y-pixel')

        ttxt += 'az.: {} {} {}'.format(fn.name, camLatLon, timeFrame)
        axa.set_title(ttxt)

        axe = fg.add_subplot(1,2,2)
        if plottype=='image':
            hie = axe.imshow(el,origin='lower')
            hc = fg.colorbar(hie)
            hc.set_label('Elevation [deg]')
        elif plottype == 'contour':
            if x is not None and y is not None:
                cs = axe.contour(x,y,el)
            else:
                cs = axe.contour(el)
            axe.clabel(cs, inline=1,fmt='%0.1f')
        axe.set_xlabel('x-pixel')
        axe.set_ylabel('y-pixel')
        axe.set_title('el.: {} {} {}'.format(fn.name, camLatLon, timeFrame))
#%%
        if 'png' in makeplot:
            plotFN = fn.parent/(fn.stem+'_azel.png')
            print('writing  {}'.format(plotFN))
            fg.savefig(str(plotFN),bbox_inches='tight',dpi=150)

        return fg,axa,axe

def plotradec(ra,dec,x,y,camLatLon,fn,makeplot):
    fn = Path(fn).expanduser()

    if 'show' in makeplot or 'png' in makeplot:
        plottype = 'contour'

        fg = figure(figsize=(12,5))
        ax = fg.add_subplot(1,2,1)
        if plottype=='image':
            hri = ax.imshow(ra,origin='lower')
            hc = fg.colorbar(hri)
            hc.set_label('RA [deg]')
        elif plottype == 'contour':
            cs= ax.contour(x,y,ra)
            ax.clabel(cs, inline=1,fmt='%0.1f')

        ax.set_xlabel('x-pixel')
        ax.set_ylabel('y-pixel')
        ax.set_title('RA: {} {}'.format(fn.name, camLatLon))

        axd = fg.add_subplot(1,2,2)
        if plottype=='image':
            hdi = axd.imshow(dec,origin='lower')
            hc = fg.colorbar(hdi)
            hc.set_label('Dec [deg]')
        elif plottype == 'contour':
            cs= axd.contour(x,y,dec)
            axd.clabel(cs, inline=1,fmt='%0.1f')
        axd.set_xlabel('x-pixel')
        axd.set_ylabel('y-pixel')
        ax.set_title('RA: {} {}'.format(fn.name, camLatLon))
#%%
        if 'png' in makeplot:
            plotFN = fn.parent/(fn.stem+'_radec.png')
            print('writing  {}'.format(plotFN))
            fg.savefig(str(plotFN),bbox_inches='tight',dpi=150)

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
            hc.set_label('Data numbers '+ str(img.dtype))
        except Exception as e:
            logging.warning('trouble making picture colorbar  {}'.format(e))
#%%
    if 'png' in makeplot:
        plotFN = fn.parent/(fn.stem+'_picture.png')
        print('writing  {}'.format(plotFN))
        fg.savefig(str(plotFN),bbox_inches='tight',dpi=150)

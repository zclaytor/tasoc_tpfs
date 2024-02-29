import matplotlib.pyplot as plt
from matplotlib import patches

from astropy.wcs import WCS
from astropy.io import fits
import lightkurve as lk


class MyTPF(object):
    """
    Basic TPF class to give interactions similar to Lightkurve TargetPixelFiles

    Attributes
        filename (str): path to source file
        flux (ndarray): 2D array of summed flux
        pipeline_mask (ndarray): 2D boolean array indicated aperture pixels
        wcs (astropy.wcs.WCS): world coordinate system from source file
    """
    def __init__(self, filename):
        """
        Read basic TPF information from a FITS file

        Parameters:
            filename (str): full path to FITS file
        """
        with fits.open(filename) as hdul:
            self.filename = filename
            self.flux = hdul[2].data
            self.pipeline_mask = (hdul[3].data & 2).astype(bool)
            self.wcs = WCS(hdul[2])

    @property
    def shape(self):
        """Returns the (height, width) of the TPF.
        """
        return self.flux.shape
    
    def get_central_coordinate(self):
        """Returns an astropy.coordinates.SkyCoord object with the TPF central coordinates
        """
        h, w = self.shape
        return self.wcs.pixel_to_world(w//2, h//2)
    
    def plot(self, ax=None, aperture_mask="pipeline", mask_color="w", **kw):
        """
        Plot the TPF a la lightkurve.TargetPixelFile.plot

        Parameters
            ax (matplotlib axes object): axes to plot the TPF
            aperture_mask (str or ndarray): boolean array for aperture
            mask_color (str): color string for the aperture mask
            kw: other keyword arguments for lightkurve.utils.plot_image

        Returns
            ax (matplotlib axes): the plot axes
        """
        ax = lk.utils.plot_image(self.flux, ax=ax, **kw)

        if aperture_mask is not None:
            if aperture_mask == "pipeline":
                aperture_mask = self.pipeline_mask
            ax = self._plot_aperture(ax, aperture_mask, mask_color)

        return ax

    def _plot_aperture(self, ax, aperture_mask, mask_color="w"):
        """Add the aperture mask to the existing TPF plot
        """
        for i in range(aperture_mask.shape[0]):
            for j in range(aperture_mask.shape[1]):
                if aperture_mask[i, j]:
                    xy = (j - 0.5, i - 0.5)
                    rect = patches.Rectangle(
                        xy=xy,
                        width=1,
                        height=1,
                        color=mask_color,
                        fill=False,
                        hatch="//",
                    )
                    ax.add_patch(rect)
        return ax


def get_tasoc_tpf(tic, sector=None):
    """
    The full pipeline, from TIC ID to TESSCut TPF

    Parameters
        tic (int or str): TIC ID for target

    Returns
        tpf (TessTargetPixelFile): TESSCut-created TPF of target centered on
            TASOC TPF central coordinate.
    """
    sr = lk.search_lightcurve(f"TIC {tic}", author="tasoc", sector=sector)
    lc = sr.download()
    tpf0 = MyTPF(lc.filename)

    coord = tpf0.get_central_coordinate()
    sr = lk.search_tesscut(coord, sector=sector)
    tpf = sr.download(cutout_size=tpf0.shape)
    tpf.pipeline_mask = tpf0.pipeline_mask
    return tpf


if __name__ == "__main__":
    # demonstrate a basic example of the pipeline
    tic = 142086812
    sector = 6

    sr = lk.search_lightcurve(f"TIC {tic}", author="tasoc", sector=sector)
    lc = sr.download()
    tpf0 = MyTPF(lc.filename)
    tpf0.plot(aperture_mask="pipeline", scale="log")    

    coord = tpf0.get_central_coordinate()
    sr = lk.search_tesscut(coord, sector=sector)
    tpf = sr.download(cutout_size=tpf0.shape)
    tpf.plot(aperture_mask=tpf0.pipeline_mask, scale="log") 

    plt.show()
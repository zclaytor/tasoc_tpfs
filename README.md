# tasoc_tpfs

Recreate (approximately) TASOC target pixel files.

The TASOC light curves are available on MAST, but not the target pixel files (TPFs). This is a quick and rough way to approximately recreate the TPFs from the pixel data stored in the light curve file.

Note that it has two calls to lightkurve.search and SearchResult.download. Using this many times in rapid succession could fail.

Also note that this doesn't perfectly reproduce the TASOC TPFs. I'm not sure the TASOC files store the full distortion data, so the results may be one or two pixels off in either direction. Since the TASOC apertures are usually pretty big, this should be fine for the most part. For single targets, you can always use numpy.roll to move the aperture to the position it should be.

from utilsLib import *
import re

def version(HeadURL = r"$HeadURL: svn+ssh://svn.lsstcorp.org/DMS/utils/trunk/python/lsst/utils.i $",
            ProductName=None):
    """
    Return a product name and version string, given a HeadURL string.
    If a different version is setup in eups, include it in the return string.
    """

    version_svn = guessSvnVersion(HeadURL)

    if not ProductName:
        # Guess the package name from HeadURL by extracting directory components
        # between DMS and trunk/branches/tickets/tags
        try:
            m = re.match(r".*/DMS/(.*)/(?:branches|tags|tickets|trunk)/.*", HeadURL)
            ProductName = m.group(1).replace('/','_')
        except:
            return "unknown product " + version_svn
    try:
        import eups
    except ImportError:
        pass
    else:
        try:
            version_eups = eups.Eups().findSetupVersion(ProductName)[0]
        except:
            version_eups = None
        if (version_eups and version_eups != version_svn): 
            return "%s %s (setup: %s)" % (ProductName, version_svn, version_eups)
    return "%s %s" % (ProductName, version_svn)

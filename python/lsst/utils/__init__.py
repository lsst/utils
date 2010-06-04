from utilsLib import *

def version(HeadURL, productName=None):
    """Return productName's version given a HeadURL string. If a different version is setup, return that too

N.b. you need to tell svn to expand that HeadURL in the first place!
"""

    version_eups = "(unknown)"
    version_svn = guessSvnVersion(HeadURL)

    if productName:
        try:
            import eups
        except ImportError:
            pass
        else:
            try:
                version_eups = eups.getSetupVersion(productName)
            except AttributeError:
                pass

    if version_eups == version_svn:
        return version_svn
    else:
        return "%s (setup: %s)" % (version_svn, version_eups)

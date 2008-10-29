# -*- python -*-
#
# Setup our environment
#
import glob, os.path, re, os
import lsst.SConsUtils as scons

env = scons.makeEnv("utils",
                    r"$HeadURL$",
                    [["boost", "boost/regex.hpp", "boost_regex:C++"],
                     ["python", "Python.h"], # needed for Swig
                    ])

env.libs["utils"] += env.getlibs("boost")
#
# Build/install things
#
for d in Split("lib python/lsst/utils doc"):
    SConscript(os.path.join(d, "SConscript"))

env['IgnoreFiles'] = r"(~$|\.pyc$|^\.svn$|\.o$)"

if False:
    Alias("install", [env.Install(env['prefix'], "python"),
                      env.Install(env['prefix'], "include"),
                      env.Install(env['prefix'], "lib"),
                      env.InstallAs(os.path.join(env['prefix'], "doc", "doxygen"),
                                    os.path.join("doc", "htmlDir")),
                      env.InstallEups(env['prefix'] + "/ups", glob.glob("ups/*.table"))])
    Clean("install", env['prefix'])
else:
    env.InstallLSST(env['prefix'], ["python", "include", "lib", "doc", "ups"])

scons.CleanTree(r"*~ core *.so *.os *.o")

#
# Build TAGS files
#
files = scons.filesToTag()
if files:
    env.Command("TAGS", files, "etags -o $TARGET $SOURCES")

env.Declare()
env.Help("""
LSST general-purpose utilities package
""")


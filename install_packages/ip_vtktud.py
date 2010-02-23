# Copyright (c) Charl P. Botha, TU Delft.
# All rights reserved.
# See COPYRIGHT for details.

# added -fpermissive to CMAKE_CXX_FLAGS to workaround g++ 4.3 compile
# problem on the included CPT code.  We were getting "changes meaning
# of" errors as documented in 
# http://stupefydeveloper.blogspot.com/2008/11/c-name-lookup-changes-in-g-43.html

import config
from install_package import InstallPackage
import os
import shutil
import utils

BASENAME = "vtktud"
SVN_REPO = "https://graphics.tudelft.nl/svn/tudvis/trunk/vtktud"
SVN_REL = 2876

dependencies = ['vtk']

class VTKTUD(InstallPackage):
    
    def __init__(self):
        self.source_dir = os.path.join(config.archive_dir, BASENAME)
        self.build_dir = os.path.join(config.build_dir, '%s-build' %
                                      (BASENAME,))
        self.inst_dir = os.path.join(config.inst_dir, BASENAME)

    def get(self):
        if os.path.exists(self.source_dir):
            utils.output("vtktud already checked out, skipping step.")

        else:
            os.chdir(config.archive_dir)
            # checkout trunk into directory vtktud
            ret = os.system("%s co %s %s -r%s" % (config.SVN,
                SVN_REPO, BASENAME, SVN_REL))
            if ret != 0:
                utils.error("Could not SVN checkout.  Fix and try again.")

    def unpack(self):
        # no unpack step
        pass

    def configure(self):
        if os.path.exists(
            os.path.join(self.build_dir, 'CMakeFiles/cmake.check_cache')):
            utils.output("vtktud build already configured.")
            return
        
        if not os.path.exists(self.build_dir):
            os.mkdir(self.build_dir)

        cmake_params = "-DBUILD_SHARED_LIBS=ON " \
                       "-DBUILD_CONTRIB=OFF " \
                       "-DBUILD_TESTING=OFF " \
                       "-DCMAKE_BACKWARDS_COMPATIBILITY=2.6 " \
                       "-DCMAKE_BUILD_TYPE=RelWithDebInfo " \
                       "-DCMAKE_INSTALL_PREFIX=%s " \
                       "-DVTK_DIR=%s" % (self.inst_dir, config.VTK_DIR)

        # we only add this under posix as a work-around to compile the
        # STLib code under g++
        if os.name == 'posix':
            cmake_params = cmake_params + " -DCMAKE_CXX_FLAGS=-fpermissive "

        ret = utils.cmake_command(self.build_dir, self.source_dir,
                cmake_params)

        if ret != 0:
            utils.error("Could not configure vtktud.  Fix and try again.")
        

    def build(self):
        posix_file = os.path.join(self.build_dir, 
                'bin/libvtktudGraphicsPython.so')
        nt_file = os.path.join(self.build_dir, 'bin',
                config.BUILD_TARGET, 'vtktudGraphicsPythonD.dll')

        if utils.file_exists(posix_file, nt_file):    
            utils.output("vtktud already built.  Skipping build step.")

        else:
            os.chdir(self.build_dir)
            ret = utils.make_command('VTKTUDOSS.sln')

            if ret != 0:
                utils.error("Could not build vtktud.  Fix and try again.")
        

    def install(self):
        config.VTKTUDOSS_PYTHON = os.path.join(
            self.inst_dir, 'lib')

        config.VTKTUDOSS_LIB = os.path.join(self.inst_dir, 'lib')

        test_file = os.path.join(config.VTKTUDOSS_LIB, 'vtktud.py')
        if os.path.exists(test_file):
            utils.output("vtktud already installed, skipping step.")
        else:
            os.chdir(self.build_dir)
            ret = utils.make_command('VTKTUDOSS.sln', install=True)

            if ret != 0:
                utils.error(
                "Could not install vtktud.  Fix and try again.")
 
    def clean_build(self):
        # nuke the build dir, the source dir is pristine and there is
        # no installation
        utils.output("Removing build dir.")
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)

    def get_installed_version(self):
        import vtktud
        return vtktud.version


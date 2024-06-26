# -*- coding: utf-8 -*-

import glob
import os
import shutil

from invoke import Context

from .base import BuilderBase
from .binarybuilders import PyInstallerBuilderLinuxSimple

from buildtools.defines import (APPIMAGE_BUILD_DIR,
                                NEED_FOR_BUILD_DIR,
                                PLUGINS_DIR)


class BuilderAppImage(BuilderBase):
    '''
    Class to create AppImage package for Linux.
    '''
    def __init__(self, c: Context, is_stable: bool = False):
        super().__init__(c, APPIMAGE_BUILD_DIR, is_stable)
        self._appdir_name = 'Outwiker.AppDir'
        self._appimage_result_name = 'Outwiker-x86_64.AppImage'

        self._temp_dir = os.path.join(self.facts.temp_dir, 'AppImage')
        self._app_dir = os.path.join(self._temp_dir, self._appdir_name)
        self._opt_dir = os.path.join(self._app_dir, 'opt')
        self._binary_dir = os.path.join(self._opt_dir, 'outwiker')
        self._plugins_dir = os.path.join(self._binary_dir, PLUGINS_DIR)
        self._result_full_path = os.path.join(self.build_dir,
                                              self._appimage_result_name)

    def clear(self):
        self._remove(self._result_full_path)

    def _build(self):
        self._create_plugins_dir()
        self._copy_appimage_files()
        self._createdir_tree()
        self._create_binaries()
        self._copy_plugins(self._plugins_dir)
        self._download_appimagetool()
        self._build_appimage()
        self._copy_result()

    def _copy_appimage_files(self):
        src = os.path.join(NEED_FOR_BUILD_DIR, u'AppImage', u'Outwiker.AppDir')
        dest = self._app_dir
        shutil.copytree(src, dest)

    def _createdir_tree(self):
        os.makedirs(self._opt_dir)

    def _create_binaries(self):
        dest_dir = self._binary_dir
        src_dir = self.temp_sources_dir
        temp_dir = self.facts.temp_dir

        linuxBuilder = PyInstallerBuilderLinuxSimple(src_dir, dest_dir, temp_dir)
        linuxBuilder.build()

    def _download_appimagetool(self):
        with self.context.cd(self._temp_dir):
            self.context.run(u'wget "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"')
            self.context.run(u'chmod a+x appimagetool-x86_64.AppImage')

    def _build_appimage(self):
        with self.context.cd(self._temp_dir):
            self.context.run('./appimagetool-*.AppImage --appimage-extract')
            self.context.run(u'ARCH=x86_64 squashfs-root/AppRun {}'.format(self._appdir_name))

    def _copy_result(self):
        src = os.path.join(self._temp_dir, self._appimage_result_name)
        dest = self.build_dir
        shutil.copy(src, dest)

    def get_appimage_files(self):
        result_files = []

        for fname in glob.glob(os.path.join(self.facts.build_dir_linux,
                                            '*.AppImage')):
            result_files.append(fname)

        return result_files

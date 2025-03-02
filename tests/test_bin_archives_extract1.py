# -*- coding: utf-8 -*-

""" Test for dji-firmware-tools, known archives extraction check.

    This test verifies functions of the script by extracting some
    packages, then unsigning some modules from the inside,
    re-signing them and checking if the resulting files
    are identical.
"""

# Copyright (C) 2023 Mefistotelis <mefistotelis@gmail.com>
# Copyright (C) 2023 Original Gangsters <https://dji-rev.slack.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import filecmp
import glob
import itertools
import logging
import os
import re
import sys
import tarfile
import pathlib
import zipfile
import pytest
from unittest.mock import patch

# Import the functions to be tested
sys.path.insert(0, './')
import filediff
from dji_imah_fwsig import main as dji_imah_fwsig_main


LOGGER = logging.getLogger(__name__)

def case_bin_archive_extract(modl_inp_fn):
    """ Test case for extraction check, and prepare data for tests which use the extracted files.
    """
    LOGGER.info("Testcase file: {:s}".format(modl_inp_fn))
    ignore_unknown_format = False

    inp_path, inp_filename = os.path.split(modl_inp_fn)
    inp_path = pathlib.Path(inp_path)
    inp_basename, modl_fileext = os.path.splitext(inp_filename)

    # For some files, we may want to ignore unrecognized format because the files can be incorrectly decrypted (due to no key)
    if (re.match(r'^(wm100)[a]?_(0801|0905).*$', inp_basename, re.IGNORECASE)):
        ignore_unknown_format = True # PUEK not published
    if (re.match(r'^(wm620)_(0801|0802|0905).*$', inp_basename, re.IGNORECASE)):
        ignore_unknown_format = True # PUEK not published

    if len(inp_path.parts) > 1:
        out_path = os.sep.join(["out"] + list(inp_path.parts[1:]))
    else:
        out_path = "out"
    modules_path1 = os.sep.join([out_path, "{:s}-extr1".format(inp_basename)])
    if not os.path.exists(modules_path1):
        os.makedirs(modules_path1)

    if tarfile.is_tarfile(modl_inp_fn):
        with tarfile.open(modl_inp_fn) as tarfh:
            if type(tarfh.fileobj).__name__ == "GzipFile":
                command = ["tar", "-zxf", modl_inp_fn, "--directory={}".format(modules_path1)]
            else:
                command = ["tar", "-xf", modl_inp_fn, "--directory={}".format(modules_path1)]
            LOGGER.info(' '.join(command))
            # extracting file
            tarfh.extractall(modules_path1)
    elif zipfile.is_zipfile(modl_inp_fn):
        with zipfile.ZipFile(modl_inp_fn) as zipfh:
            command = ["unzip", "-q", "-o", "-d", modules_path1,  modl_inp_fn]
            LOGGER.info(' '.join(command))
            # extracting file
            zipfh.extractall(modules_path1)
    else:
        if not ignore_unknown_format:
            assert False, "Unrecognized archive format of the module file: {:s}".format(modl_inp_fn)
        LOGGER.warning("Unrecognized archive format of the module file: {:s}".format(modl_inp_fn))
    pass


@pytest.mark.order(2) # must be run after test_dji_imah_fwsig_rebin
@pytest.mark.parametrize("modl_inp_dir,test_nth", [
    ('out/wm100-spark',1,),
    ('out/wm220-mavic',1,),
    ('out/wm330-phantom_4_std',1,),
    ('out/wm331-phantom_4_pro',1,),
    ('out/wm335-phantom_4_pro_v2',1,),
    ('out/wm620-inspire_2',1,),
  ] )
def test_bin_archives_imah1_extract(capsys, modl_inp_dir, test_nth):
    """ Test if known archives are extracting correctly, and prepare data for tests which use the extracted files.
    """
    if test_nth < 1:
        pytest.skip("limited scope")

    modl_inp_filenames = [fn for fn in itertools.chain.from_iterable([ glob.glob(e, recursive=True) for e in (
        # Some Android OTA/TGZ/TAR modules contain boot images with another stage of IMaH encryption
        "{}/*/*_0801.bin".format(modl_inp_dir),
        "{}/*/*_0802.bin".format(modl_inp_dir),
        "{}/*/*_0805.bin".format(modl_inp_dir),
        "{}/*/*_0905.bin".format(modl_inp_dir),
        "{}/*/*_0907.bin".format(modl_inp_dir),
        "{}/*/*_1301.bin".format(modl_inp_dir),
        "{}/*/*_1407.bin".format(modl_inp_dir),
        "{}/*/*_2801.bin".format(modl_inp_dir),
      ) ]) if os.path.isfile(fn)]

    if len(modl_inp_filenames) < 1:
        pytest.skip("no package files to test in this directory")

    for modl_inp_fn in modl_inp_filenames:
        case_bin_archive_extract(modl_inp_fn)
        capstdout, _ = capsys.readouterr()
    pass

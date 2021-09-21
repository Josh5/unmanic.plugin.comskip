#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    plugins.tmp.py

    Written by:               Josh.5 <jsunnex@gmail.com>
    Date:                     21 Sep 2021, (7:02 PM)

    Copyright:
        Copyright (C) 2021 Josh Sunnex

        This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
        Public License as published by the Free Software Foundation, version 3.

        This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
        implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
        for more details.

        You should have received a copy of the GNU General Public License along with this program.
        If not, see <https://www.gnu.org/licenses/>.

"""

import logging
import mimetypes
import os

from unmanic.libs.unplugins.settings import PluginSettings

# Configure plugin logger
logger = logging.getLogger("Unmanic.Plugin.comskip")


class Settings(PluginSettings):
    settings = {
        'config': '',
    }
    form_settings = {
        "config": {
            "label":      "Comskip configuration",
            "input_type": "textarea",
        },
    }


def test_valid_mimetype(file_path):
    """
    Test the given file path for its mimetype.
    If the mimetype cannot be detected, it will fail this test.
    If the detected mimetype is not in the configured 'allowed_mimetypes'
        class variable, it will fail this test.

    :param file_path:
    :return:
    """
    # Only run this check against video/audio/image MIME types
    mimetypes.init()
    file_type = mimetypes.guess_type(file_path)[0]

    # If the file has no MIME type then it cannot be tested
    if file_type is None:
        logger.debug("Unable to fetch file MIME type - '{}'".format(file_path))
        return False

    # Make sure the MIME type is either audio, video or image
    file_type_category = file_type.split('/')[0]
    if file_type_category not in ['video']:
        logger.debug("File MIME type not 'video' - '{}'".format(file_path))
        return False

    return True


def on_library_management_file_test(data):
    """
    Runner function - enables additional actions during the library management file tests.

    The 'data' object argument includes:
        path                            - String containing the full path to the file being tested.
        issues                          - List of currently found issues for not processing the file.
        add_file_to_pending_tasks       - Boolean, is the file currently marked to be added to the queue for processing.

    :param data:
    :return:

    """
    # Get the path to the file
    abspath = data.get('path')

    # Ensure this is a video file
    if not test_valid_mimetype(abspath):
        return data

    # Check for txt file with the same name as the video file
    split_file_out = os.path.splitext(abspath)
    comskip_file_out = "{}.txt".format(split_file_out[0])

    if not os.path.exists(os.path.join(comskip_file_out)):
        # Mark this file to be added to the pending tasks
        data['add_file_to_pending_tasks'] = True
        logger.debug("No comskip configuration found for file '{}'. It should be added to task list.".format(abspath))

    return data


def on_worker_process(data):
    """
    Runner function - enables additional configured processing jobs during the worker stages of a task.

    The 'data' object argument includes:
        exec_command            - A command that Unmanic should execute. Can be empty.
        command_progress_parser - A function that Unmanic can use to parse the STDOUT of the command to collect progress stats. Can be empty.
        file_in                 - The source file to be processed by the command.
        file_out                - The destination that the command should output (may be the same as the file_in if necessary).
        original_file_path      - The absolute path to the original file.
        repeat                  - Boolean, should this runner be executed again once completed with the same variables.

    :param data:
    :return:
    
    """
    # Default to no FFMPEG command required. This prevents the FFMPEG command from running if it is not required
    data['exec_command'] = []
    data['repeat'] = False

    # Get the path to the file
    abspath = data.get('file_in')

    # Ensure this is a video file
    if not test_valid_mimetype(abspath):
        return data

    # Check for txt file with the same name as the video file
    file_dirname = os.path.dirname(abspath)
    file_sans_ext = os.path.splitext(os.path.basename(abspath))[0]
    comskip_file_out = "{}.txt".format(file_sans_ext)

    if not os.path.exists(os.path.join(file_dirname, comskip_file_out)):
        # Mark this file to be added to the pending tasks
        data['add_file_to_pending_tasks'] = True

        # Set config file path
        settings = Settings()
        profile_directory = settings.get_profile_directory()

        # Set the output file
        config = settings.get_setting('config')
        if not config:
            logger.error("Plugin not configured.")

        # Write comskip settings file
        config_file = os.path.join(profile_directory, 'comskip.ini')
        with open(config_file, "w") as f:
            f.write(config)
            # Ensure the end of the file has a linebreak
            f.write("\n\n")

            # The file_in needs to be the file_out
        data['file_out'] = abspath

        # Generate comskip command
        data['exec_command'] = [
            'comskip',
            '--ini={}'.format(config_file),
            '--output={}'.format(file_dirname),
            '--output-filename={}'.format(file_sans_ext),
            abspath
        ]

    return data

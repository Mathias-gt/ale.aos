#
# (c) 2017 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = """
author: Mathias Guillemot (@Mathias-gt)
name: aos
short_description: Use aos cliconf to run command on Alcatel-Lucent Enterprise AOS platform
description:
- This aos plugin provides low level abstraction apis for sending and receiving CLI
  commands from Alcatel-Lucent Enterprise AOS network devices.
version_added: 1.0.0
options:
  aos_use_sessions:
    type: boolean
    default: true
    description:
    - Specifies if sessions should be used on remote host or not
    env:
    - name: ANSIBLE_AOS_USE_SESSIONS
    vars:
    - name: ansible_aos_use_sessions
  config_commands:
    description:
    - Specifies a list of commands that can make configuration changes
      to the target device.
    - When `ansible_network_single_user_mode` is enabled, if a command sent
      to the device is present in this list, the existing cache is invalidated.
    version_added: 2.0.0
    type: list
    elements: str
    default: []
    vars:
    - name: ansible_aos_config_commands
"""

import json
import re

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_text
from ansible.module_utils.common._collections_compat import Mapping
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import (
    NetworkConfig,
    dumps,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list
from ansible_collections.ansible.netcommon.plugins.plugin_utils.cliconf_base import (
    CliconfBase,
)

from ansible_collections.ale.aos.plugins.module_utils.network.aos.aos import session_name


class Cliconf(CliconfBase):
    __rpc__ = CliconfBase.__rpc__ + [
        "commit",
        "discard_changes",
        "get_diff",
        "run_commands",
    ]

    def __init__(self, *args, **kwargs):
        super(Cliconf, self).__init__(*args, **kwargs)
        self._device_info = {}
        self._session_support = None

    def get_config(self, source="running", flags=None, format="text"):
        options_values = self.get_option_values()
        if format not in options_values["format"]:
            raise ValueError(
                "'format' value %s is invalid. Valid values are %s"
                % (format, ",".join(options_values["format"])),
            )

        lookup = {"running": "show configuration snapshot", "startup": "cat working/vcsetup.cfg"}
        if source not in lookup:
            raise ValueError(
                "fetching configuration from %s is not supported" % source,
            )

        cmd = "%s " % lookup[source]
        if format and format != "text":
            cmd += "| %s " % format

        cmd += " ".join(to_list(flags))
        cmd = cmd.strip()
        return self.send_command(cmd)

    def edit_config(self, candidate=None, replace=None, comment=None):
        resp = {}
        results = []
        requests = []

        for line in to_list(candidate):
            if not isinstance(line, Mapping):
                line = {"command": line}
            cmd = line["command"]
            try:
                results.append(self.send_command(**line))
            except AnsibleConnectionFailure as exc:
                # Handle connection failure or other exceptions as needed
                raise
            requests.append(cmd)

        resp["request"] = requests
        resp["response"] = results
        return resp

    def get(
        self,
        command,
        prompt=None,
        answer=None,
        sendonly=False,
        newline=True,
        output=None,
        check_all=False,
        version=None,
    ):
        if output:
            command = self._get_command_with_output(command, output, version)
        return self.send_command(
            command=command,
            prompt=prompt,
            answer=answer,
            sendonly=sendonly,
            newline=newline,
            check_all=check_all,
        )

    def commit(self):
        self.send_command("commit")


    def run_commands(self, commands=None, check_rc=True):
        if commands is None:
            raise ValueError("'commands' value is required")
        responses = list()
        for cmd in to_list(commands):
            if not isinstance(cmd, Mapping):
                cmd = {"command": cmd}

            output = cmd.pop("output", None)
            version = cmd.pop("version", None)
            if output:
                cmd["command"] = self._get_command_with_output(
                    cmd["command"],
                    output,
                    version,
                )

            try:
                out = self.send_command(**cmd)
            except AnsibleConnectionFailure as e:
                if check_rc:
                    raise
                out = getattr(e, "err", e)
            out = to_text(out, errors="surrogate_or_strict")

            if out is not None:
                try:
                    out = json.loads(out)
                except ValueError:
                    out = out.strip()

                responses.append(out)
        return responses

    def get_diff(
        self,
        candidate=None,
        running=None,
        diff_match="line",
        diff_ignore_lines=None,
        path=None,
        diff_replace="line",
    ):
        diff = {}
        device_operations = self.get_device_operations()
        option_values = self.get_option_values()

        if candidate is None and device_operations["supports_generate_diff"]:
            raise ValueError(
                "candidate configuration is required to generate diff",
            )

        if diff_match not in option_values["diff_match"]:
            raise ValueError(
                "'match' value %s in invalid, valid values are %s"
                % (diff_match, ", ".join(option_values["diff_match"])),
            )

        if diff_replace not in option_values["diff_replace"]:
            raise ValueError(
                "'replace' value %s in invalid, valid values are %s"
                % (diff_replace, ", ".join(option_values["diff_replace"])),
            )

        # prepare candidate configuration
        candidate_obj = NetworkConfig(indent=3)
        candidate_obj.load(candidate)

        if running and diff_match != "none" and diff_replace != "config":
            # running configuration
            running_obj = NetworkConfig(
                indent=3,
                contents=running,
                ignore_lines=diff_ignore_lines,
            )
            configdiffobjs = candidate_obj.difference(
                running_obj,
                path=path,
                match=diff_match,
                replace=diff_replace,
            )

        else:
            configdiffobjs = candidate_obj.items

        diff["config_diff"] = dumps(configdiffobjs, "commands") if configdiffobjs else ""
        return diff

    def get_device_info(self):
        if not self._device_info:
            device_info = {}

            device_info["network_os"] = "aos"
            reply = self.get("show microcode")
            data = to_text(reply, errors="surrogate_or_strict").strip()

            match = re.search(r"\b\d+\.\d+\.\d+\.\w+\b", data)
            if match:
                device_info["network_os_version"] = match.group(0)

            match = re.search(r"(/[\w/]+)", data)
            if match:
                path = match.group(1)
            match = re.search(r"\b(\w+\.\w+)\b", data)
            if match:
                device_info["network_os_image"] = "{path}/{image}".format(path=path,image=match.group(1))


            reply = self.get("show system")
            data = to_text(reply, errors="surrogate_or_strict").strip()

            match = re.search(r"Description:\s+.*?(\bOS[\w-]+)\b", data)
            if match:
                device_info["network_os_model"] = match.group(1)

            match = re.search(r"Name:\s+(\S+),?", data)
            if match:
                device_info["network_os_hostname"] = match.group(1).rstrip(',')

            self._device_info = device_info

        return self._device_info

    def get_device_operations(self):
        return {
            "supports_diff_replace": False,
            "supports_commit": False,
            "supports_rollback": False,
            "supports_defaults": False,
            "supports_onbox_diff": False,
            "supports_commit_comment": False,
            "supports_multiline_delimiter": False,
            "supports_diff_match": False,
            "supports_diff_ignore_lines": False,
            "supports_generate_diff": False,
            "supports_replace": False,
        }

    def get_option_values(self):
        return {
            "format": ["text", "json"],
            "diff_match": ["line", "strict", "exact", "none"],
            "diff_replace": ["line", "block", "config"],
            "output": ["text", "json"],
        }

    def get_capabilities(self):
        result = super(Cliconf, self).get_capabilities()
        result["device_operations"] = self.get_device_operations()
        result.update(self.get_option_values())

        return json.dumps(result)

    def set_cli_prompt_context(self):
        """
        Make sure we are in the operational cli mode
        :return: None
        """
        if self._connection.connected:
            self._update_cli_prompt_context(config_context="")

    def _get_command_with_output(self, command, output, version):
        options_values = self.get_option_values()
        if output not in options_values["output"]:
            raise ValueError(
                "'output' value %s is invalid. Valid values are %s"
                % (output, ",".join(options_values["output"])),
            )

        if output == "json" and not command.endswith("| json"):
            cmd = "%s | json" % command
        else:
            cmd = command
        if version != "latest" and "| json" in cmd:
            cmd = "%s version %s" % (cmd, version)
        return cmd

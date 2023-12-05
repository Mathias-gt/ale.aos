#
# This code is part of Ansible, but is an independent component.
#
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# (c) 2017 Red Hat, Inc.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import json
import os
import time

from ansible.module_utils._text import to_text
from ansible.module_utils.connection import Connection, ConnectionError
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import (
    NetworkConfig,
    dumps,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    ComplexList,
    to_list,
)


_DEVICE_CONNECTION = None


def get_connection(module):
    global _DEVICE_CONNECTION
    if not _DEVICE_CONNECTION:
        connection_proxy = Connection(module._socket_path)
        #cap = json.loads(connection_proxy.get_capabilities())
        #if cap["network_api"] == "cliconf":
        conn = Cli(module)
        _DEVICE_CONNECTION = conn
    return _DEVICE_CONNECTION


def transform_commands(module):
    transform = ComplexList(
        dict(
            command=dict(key=True),
            output=dict(),
            prompt=dict(type="list"),
            answer=dict(type="list"),
            newline=dict(type="bool", default=True),
            sendonly=dict(type="bool", default=False),
            check_all=dict(type="bool", default=False),
            version=dict(
                type="str",
                default="latest",
                choices=["latest", "1"],
            ),
        ),
        module,
    )

    return transform(module.params["commands"])


def session_name():
    """Generate a unique string to be used as a configuration session name."""
    return "ansible_%d" % (time.time() * 100)


class Cli:
    def __init__(self, module):
        self._module = module
        self._device_configs = {}
        self._session_support = None
        self._connection = None

    def _get_connection(self):
        if self._connection:
            return self._connection
        self._connection = Connection(self._module._socket_path)

        return self._connection

    def get_config(self, flags=None):
        """Retrieves the current config from the device or cache"""
        flags = [] if flags is None else flags

        cmd = "show configuration snapshot "
        cmd += " ".join(flags)
        cmd = cmd.strip()

        try:
            return self._device_configs[cmd]
        except KeyError:
            conn = self._get_connection()
            try:
                out = conn.get_config(flags=flags)
            except ConnectionError as exc:
                self._module.fail_json(
                    msg=to_text(exc, errors="surrogate_then_replace"),
                )

            cfg = to_text(out, errors="surrogate_then_replace").strip()
            self._device_configs[cmd] = cfg
            return cfg

    def run_commands(self, commands, check_rc=True):
        """Run list of commands on remote device and return results"""
        connection = self._get_connection()
        try:
            response = connection.run_commands(
                commands=commands,
                check_rc=check_rc,
            )
        except ConnectionError as exc:
            self._module.fail_json(
                msg=to_text(exc, errors="surrogate_then_replace"),
            )
        return response

    def get_session_config(self, commands, commit=False, replace=False):
        """Loads the config commands onto the remote device"""
        conn = self._get_connection()
        try:
            response = conn.get_session_config(commands, commit, replace)
        except ConnectionError as exc:
            message = getattr(exc, "err", to_text(exc))
            if "check mode is not supported without configuration session" in message:
                self._module.warn(
                    "AOS can not check config without config session",
                )
                response = {"changed": True}
            else:
                self._module.fail_json(
                    msg="%s" % message,
                    data=to_text(message, errors="surrogate_then_replace"),
                )

        return response

    def load_config(self, commands, commit=False, replace=False):
        """Loads the config commands onto the remote device"""
        conn = self._get_connection()
        try:
            response = conn.edit_config(commands, commit, replace)
        except ConnectionError as exc:
            message = getattr(exc, "err", to_text(exc))
            if "check mode is not supported without configuration session" in message:
                self._module.warn(
                    "AOS can not check config without config session",
                )
                response = {"changed": True}
            else:
                self._module.fail_json(
                    msg="%s" % message,
                    data=to_text(message, errors="surrogate_then_replace"),
                )

        return response

    def get_diff(
        self,
        candidate=None,
        running=None,
        diff_match="line",
        diff_ignore_lines=None,
        path=None,
        diff_replace="line",
    ):
        conn = self._get_connection()
        try:
            diff = conn.get_diff(
                candidate=candidate,
                running=running,
                diff_match=diff_match,
                diff_ignore_lines=diff_ignore_lines,
                path=path,
                diff_replace=diff_replace,
            )
        except ConnectionError as exc:
            self._module.fail_json(
                msg=to_text(exc, errors="surrogate_then_replace"),
            )
        return diff

    def get_capabilities(self):
        """Returns platform info of the remove device"""
        if hasattr(self._module, "_capabilities"):
            return self._module._capabilities

        connection = self._get_connection()
        try:
            capabilities = connection.get_capabilities()
        except ConnectionError as exc:
            self._module.fail_json(
                msg=to_text(exc, errors="surrogate_then_replace"),
            )
        self._module._capabilities = json.loads(capabilities)
        return self._module._capabilities

def is_json(cmd):
    return to_text(cmd, errors="surrogate_then_replace").endswith("| json")


def to_command(module, commands):
    transform = ComplexList(
        dict(
            command=dict(key=True),
            output=dict(type="str", default="text"),
            prompt=dict(type="list"),
            answer=dict(type="list"),
            newline=dict(type="bool", default=True),
            sendonly=dict(type="bool", default=False),
            check_all=dict(type="bool", default=False),
            version=dict(type="str", default="latest"),
        ),
        module,
    )

    return transform(to_list(commands))


def get_config(module, flags=None):
    flags = None if flags is None else flags

    conn = get_connection(module)
    return conn.get_config(flags)


def run_commands(module, commands, check_rc=True):
    conn = get_connection(module)
    return conn.run_commands(to_command(module, commands), check_rc=check_rc)


def load_config(module, config, commit=False, replace=False):
    conn = get_connection(module)
    return conn.load_config(config, commit, replace)


def get_session_config(module, config, commit=False, replace=False):
    conn = get_connection(module)
    return conn.get_session_config(config, commit, replace)


def get_diff(
    self,
    candidate=None,
    running=None,
    diff_match="line",
    diff_ignore_lines=None,
    path=None,
    diff_replace="line",
):
    conn = self.get_connection()
    return conn.get_diff(
        candidate=candidate,
        running=running,
        diff_match=diff_match,
        diff_ignore_lines=diff_ignore_lines,
        path=path,
        diff_replace=diff_replace,
    )


def get_capabilities(module):
    conn = get_connection(module)
    return conn.get_capabilities()

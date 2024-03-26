#!/usr/bin/python
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
module: aos_command
author: Mathias Guillemot (@mathias-gt)
short_description: Module to run commands on remote devices.
description:
  - Sends arbitrary commands to an aos node and returns the results read from the device.
    This module includes an argument that will cause the module to wait for a specific
    condition before returning or timing out if the condition is not met.
  - This module does not support running commands in configuration mode. Please use
    L(aos_config,https://docs.ansible.com/ansible/latest/collections/ale/aos/aos_config_module.html#ansible-collections-ale-aos-aos-config-module)
    to configure AOS devices.
version_added: 1.0.0
extends_documentation_fragment:
  - ale.aos.aos
notes:
  - Tested against Alcatel-Lucent Enterprise AOS Version 8.9.R3 on OS6900.
  - This module works with connection C(network_cli).
    See U(https://docs.ansible.com/ansible/latest/network/user_guide/platform_aos.html)
options:
  commands:
    description:
      - List of commands to send to the remote aos device over the configured provider.
        The resulting output from the command is returned. If the I(wait_for) argument
        is provided, the module is not returned until the condition is satisfied or
        the number of retries has expired. If a command sent to the device requires
        answering a prompt, it is possible to pass a dict containing I(command), I(answer)
        and I(prompt). Common answers are 'y' or "\\r" (carriage return, must be double
        quotes). See examples.
    required: true
    type: list
    elements: raw
  wait_for:
    description:
      - List of conditions to evaluate against the output of the command. The task will
        wait for each condition to be true before moving forward. If the conditional
        is not true within the configured number of retries, the task fails. See examples.
    aliases:
      - waitfor
    type: list
    elements: str
  match:
    description:
      - The I(match) argument is used in conjunction with the I(wait_for) argument to
        specify the match policy.  Valid values are C(all) or C(any).  If the value
        is set to C(all) then all conditionals in the wait_for must be satisfied.  If
        the value is set to C(any) then only one of the values must be satisfied.
    default: all
    type: str
    choices:
      - any
      - all
  retries:
    description:
      - Specifies the number of retries a command should by tried before it is considered
        failed. The command is run on the target device every retry and evaluated against
        the I(wait_for) conditions.
    default: 9
    type: int
  interval:
    description:
      - Configures the interval in seconds to wait between retries of the command. If
        the command does not pass the specified conditions, the interval indicates how
        long to wait before trying the command again.
    default: 1
    type: int
"""

EXAMPLES = r"""
- name: Run show version on remote devices
  ale.aos.aos_command:
    commands: show microcode

# output-

# ok: [aosxeappliance] => {
#     "changed": false,
#     "invocation": {
#         "module_args": {
#             "commands": [
#                 "show microcode"
#             ],
#             "interval": 1,
#             "match": "all",
#             "retries": 10,
#             "wait_for": null
#         }
#     },
#     "stdout": [
#         "   /flash/working\n   Package           Release                 Size     Description\n-----------------+-------------------------+---------+-----------------------------------\nYos.img           8.9.221.R03               125523399 Alcatel-Lucent OS\n"
#     ],
#     "stdout_lines": [
#         [
#             "   /flash/working",
#             "   Package           Release                 Size     Description",
#             "-----------------+-------------------------+---------+-----------------------------------"
#             "Yos.img           8.9.221.R03               125523399 Alcatel-Lucent OS"
#             ""
#         ]
#     ]
# }

- name: Run show version and check to see if output contains AOS
  ale.aos.aos_command:
    commands: show microcode
    wait_for: result[0] contains Alcatel-Lucent

# output-

# ok: [aosxeappliance] => {
#     "changed": false,
#     "invocation": {
#         "module_args": {
#             "commands": [
#                 "show microcode"
#             ],
#             "interval": 1,
#             "match": "all",
#             "retries": 10,
#             "wait_for": [
#                 "result[0] contains Alcatel-Lucent"
#             ]
#         }
#     },
#     "stdout": [
#         "   /flash/working\n   Package           Release                 Size     Description\n-----------------+-------------------------+---------+-----------------------------------\nYos.img           8.9.221.R03               125523399 Alcatel-Lucent OS\n"
#     ],
#     "stdout_lines": [
#         [
#             "   /flash/working",
#             "   Package           Release                 Size     Description",
#             "-----------------+-------------------------+---------+-----------------------------------"
#             "Yos.img           8.9.221.R03               125523399 Alcatel-Lucent OS"
#             ""
#         ]
#     ]
# }

- name: Run multiple commands on remote nodes
  ale.aos.aos_command:
    commands:
      - show microcode
      - show interfaces

# output-

# ok: [aosxeappliance] => {
#     "changed": false,
#     "invocation": {
#         "module_args": {
#             "commands": [
#                 "show microcode",
#                 "show interfaces"
#             ],
#             "interval": 1,
#             "match": "all",
#             "retries": 10,
#             "wait_for": null
#         }
#     },
#     "stdout": [
#         "   /flash/working\n   Package           Release                 Size     Description\n-----------------+-------------------------+---------+-----------------------------------\nYos.img           8.9.221.R03               125523399 Alcatel-Lucent OS\n"
#         "Chassis/Slot/Port          : 1/1/1   "
#     ],
#     "stdout_lines": [
#         [
#             "   /flash/working",
#             "   Package           Release                 Size     Description",
#             "-----------------+-------------------------+---------+-----------------------------------"
#             "Yos.img           8.9.221.R03               125523399 Alcatel-Lucent OS"
#             ""
#         ],
#         [
#             "Chassis/Slot/Port          : 1/1/1   ",
#             " Operational Status        : up,",
#             " Port-Down/Violation Reason: None,",
#             " Last Time Link Changed    : Wed Jan 15 09:28:37 2020,",
#             " Number of Status Change   : 3,",
#             " Type                      : Ethernet,",
#             " SFP/XFP                   : 10 / 100 / 1000 BaseX,",
#             " Interface Type            : Fiber,",
#             " EPP                       : Disabled,",
#             " Link-Quality              : N/A,",
#             " MAC address               : 78:24:59:64:69:98,",
#             " BandWidth (Megabits)      :     1000,  		Duplex           : Full,",
#             " Autonegotiation           :   1  [ 1000-F                       ],",
#             " Long Frame Size(Bytes)    : 9216,",
#             " Inter Frame Gap(Bytes)    : 12,",
#             " loopback mode             : N/A,",
#             " Rx              :",
#             " Bytes Received  :             31751868, Unicast Frames :               175950,",
#             " Broadcast Frames:                  253, M-cast Frames  :               232391,",
#             " UnderSize Frames:                    0, OverSize Frames:                    0,",
#             " Lost Frames     :                    0, Error Frames   :                    0,",
#             " CRC Error Frames:                    0, Alignments Err :                    0,",
#             " Tx              :",
#             " Bytes Xmitted   :              4340966, Unicast Frames :                15886,",
#             " Broadcast Frames:                 3264, M-cast Frames  :                45368,",
#             " UnderSize Frames:                    0, OverSize Frames:                    0,",
#             " Lost Frames     :                    0, Collided Frames:                    0,",
#             " Error Frames    :                    0, Collisions     :                    0,",
#             " Late collisions :                    0, Exc-Collisions :                    0"
#         ]
#     ]
# }

- name: Run multiple commands and evaluate the output
  ale.aos.aos_command:
    commands:
      - show microcode
      - show interfaces
    wait_for:
      - result[0] contains Alcatel-Lucent
      - result[1] contains 1/1/1

# output-
# failed play as result[1] contains 1/1/1 is false

# fatal: [aosxeappliance]: FAILED! => {
#     "changed": false,
#     "failed_conditions": [
#         "result[1] contains 1/1/1"
#     ],
#     "invocation": {
#         "module_args": {
#             "commands": [
#                 "show microcode",
#                 "show interfaces"
#             ],
#             "interval": 1,
#             "match": "all",
#             "retries": 10,
#             "wait_for": [
#                 "result[0] contains Alcatel-Lucent",
#                 "result[1] contains 1/1/1"
#             ]
#         }
#     },
#     "msg": "One or more conditional statements have not been satisfied"
# }

- name: Run commands that require answering a prompt
  ale.aos.aos_command:
    commands:
      - command: "clear counters GigabitEthernet2"
        prompt: 'Clear "show interface" counters on this interface \[confirm\]'
        answer: "y"
      - command: "clear counters GigabitEthernet3"
        prompt: "[confirm]"
        answer: "\r"

# output-

# ok: [aosxeappliance] => {
#     "changed": false,
#     "invocation": {
#         "module_args": {
#             "commands": [
#                 {
#                     "answer": "y",
#                     "check_all": false,
#                     "command": "clear counters GigabitEthernet2",
#                     "newline": true,
#                     "output": null,
#                     "prompt": "Clear \"show interface\" counters on this interface \\[confirm\\]",
#                     "sendonly": false
#                 },
#                 {
#                     "answer": "\r",
#                     "check_all": false,
#                     "command": "clear counters GigabitEthernet3",
#                     "newline": true,
#                     "output": null,
#                     "prompt": "[confirm]",
#                     "sendonly": false
#                 }
#             ],
#             "interval": 1,
#             "match": "all",
#             "retries": 10,
#             "wait_for": null
#         }
#     },
#     "stdout": [
#         "Clear \"show interface\" counters on this interface [confirm]y",
#         "Clear \"show interface\" counters on this interface [confirm]"
#     ],
#     "stdout_lines": [
#         [
#             "Clear \"show interface\" counters on this interface [confirm]y"
#         ],
#         [
#             "Clear \"show interface\" counters on this interface [confirm]"
#         ]
#     ]
# }

- name: Run commands with complex values like special characters in variables
  ale.aos.aos_command:
    commands:
      ["{{ 'test aaa group TEST ' ~ user ~ ' ' ~ password ~ ' new-code' }}"]
  vars:
    user: "dummy"
    password: "!dummy"

# ok: [aosxeappliance] => {
#     "changed": false,
#     "invocation": {
#         "module_args": {
#             "commands": [
#                 "test aaa group group test !dummy new-code"
#             ],
#             "interval": 1,
#             "match": "all",
#             "retries": 10,
#             "wait_for": null
#         }
#     },
#     "stdout": [
#         "User was successfully authenticated."
#     ],
#     "stdout_lines": [
#         [
#             "User was successfully authenticated."
#         ]
#     ]
# }
"""

RETURN = """
stdout:
  description: The set of responses from the commands
  returned: always apart from low level errors (such as action plugin)
  type: list
  sample: ['...', '...']
stdout_lines:
  description: The value of stdout split into a list
  returned: always apart from low level errors (such as action plugin)
  type: list
  sample: [['...', '...'], ['...'], ['...']]
failed_conditions:
  description: The list of conditionals that have failed
  returned: failed
  type: list
  sample: ['...', '...']
"""
import time

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.parsing import (
    Conditional,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_lines,
    transform_commands,
)

from ansible_collections.ale.aos.plugins.module_utils.network.aos.aos import run_commands


def parse_commands(module, warnings):
    commands = transform_commands(module)
    if module.check_mode:
        for item in list(commands):
            if not item["command"].startswith("show"):
                warnings.append(
                    "Only show commands are supported when using check mode, not executing %s"
                    % item["command"],
                )
                commands.remove(item)
    return commands


def main():
    """main entry point for module execution"""
    argument_spec = dict(
        commands=dict(type="list", elements="raw", required=True),
        wait_for=dict(type="list", elements="str", aliases=["waitfor"]),
        match=dict(default="all", choices=["all", "any"]),
        retries=dict(default=9, type="int"),
        interval=dict(default=1, type="int"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    warnings = list()
    result = {"changed": False, "warnings": warnings}
    commands = parse_commands(module, warnings)
    wait_for = module.params["wait_for"] or list()
    conditionals = []
    try:
        conditionals = [Conditional(c) for c in wait_for]
    except AttributeError as exc:
        module.fail_json(msg=to_text(exc))
    retries = module.params["retries"]
    interval = module.params["interval"]
    match = module.params["match"]
    while retries >= 0:
        responses = run_commands(module, commands)
        for item in list(conditionals):
            if item(responses):
                if match == "any":
                    conditionals = list()
                    break
                conditionals.remove(item)
        if not conditionals:
            break
        time.sleep(interval)
        retries -= 1
    if conditionals:
        failed_conditions = [item.raw for item in conditionals]
        msg = "One or more conditional statements have not been satisfied"
        module.fail_json(msg=msg, failed_conditions=failed_conditions)
    result.update({"stdout": responses, "stdout_lines": list(to_lines(responses))})
    module.exit_json(**result)


if __name__ == "__main__":
    main()

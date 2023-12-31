# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# utils

from __future__ import absolute_import, division, print_function


__metaclass__ = type


def get_interface_number(name):
    digits = ""
    for char in name:
        if char.isdigit() or char in "/.":
            digits += char
    return digits

def vlan_range_to_list(vlans):
    result = []
    if vlans:
        if isinstance(vlans, str):
            vlans = vlans.split(",")
        for part in vlans:
            if part == "none":
                break
            if "-" in part:
                a, b = part.split("-")
                a, b = int(a), int(b)
                result.extend(range(a, b + 1))
            else:
                a = int(part)
                result.append(a)
        return numerical_sort(result)
    return result


def numerical_sort(string_int_list):
    """Sorts list of integers that are digits in numerical order."""
    as_int_list = []

    for vlan in string_int_list:
        as_int_list.append(int(vlan))
    as_int_list.sort()
    return list(set(as_int_list))

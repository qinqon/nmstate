#
# Copyright (c) 2019 Red Hat, Inc.
#
# This file is part of nmstate
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#

from contextlib import contextmanager
import copy

import libnmstate
from libnmstate.schema import Interface
from libnmstate.schema import InterfaceState
from libnmstate.schema import InterfaceType
from libnmstate.schema import OVSBridge
from libnmstate.schema import OVSBridgePortType


class Bridge:
    def __init__(self, name):
        self._name = name
        self._ifaces = [
            {
                Interface.NAME: name,
                Interface.TYPE: InterfaceType.OVS_BRIDGE,
                OVSBridge.CONFIG_SUBTREE: {},
            }
        ]
        self._bridge_iface = self._ifaces[0]

    def set_options(self, options):
        self._bridge_iface[OVSBridge.CONFIG_SUBTREE][
            OVSBridge.OPTIONS_SUBTREE
        ] = options

    def add_system_port(self, name):
        self._add_port(name, OVSBridgePortType.SYSTEM)

    def add_internal_port(self, name, ipv4_state):
        self._add_port(name, OVSBridgePortType.INTERNAL)
        self._ifaces.append(
            {
                Interface.NAME: name,
                Interface.TYPE: InterfaceType.OVS_INTERFACE,
                Interface.IPV4: ipv4_state,
            }
        )

    def _add_port(self, name, _type):
        self._bridge_iface[OVSBridge.CONFIG_SUBTREE].setdefault(
            OVSBridge.PORT_SUBTREE, []
        ).append({OVSBridge.PORT_NAME: name, OVSBridge.PORT_TYPE: _type})

    @contextmanager
    def create(self):
        desired_state = {
            Interface.KEY: _set_ifaces_state(self._ifaces, InterfaceState.UP)
        }
        libnmstate.apply(desired_state)
        try:
            yield desired_state
        finally:
            desired_state = {
                Interface.KEY: _set_ifaces_state(
                    self._ifaces, InterfaceState.ABSENT
                )
            }
            libnmstate.apply(desired_state, verify_change=False)


def _set_ifaces_state(ifaces, state):
    ifaces = copy.deepcopy(ifaces)
    for iface in ifaces:
        iface[Interface.STATE] = state
    return ifaces
#
# Copyright (c) 2018-2019 Red Hat, Inc.
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
import copy

import libnmstate
from libnmstate.schema import DNS
from libnmstate.schema import Route
from libnmstate.schema import Interface

from . import statelib
from .statelib import INTERFACES


def assert_state(desired_state_data):
    """Given a state, assert it against the current state."""

    current_state_data = libnmstate.show()
    # Ignore route and dns for assert check as the check are done in the test
    # case code.
    current_state_data.pop(Route.KEY, None)
    current_state_data.pop(DNS.KEY, None)
    desired_state_data = copy.deepcopy(desired_state_data)
    desired_state_data.pop(Route.KEY, None)
    desired_state_data.pop(DNS.KEY, None)

    current_state = statelib.State(current_state_data)
    current_state.filter(desired_state_data)
    current_state.normalize()

    full_desired_state = statelib.State(current_state.state)
    full_desired_state.update(desired_state_data)
    full_desired_state.remove_absent_entries()
    full_desired_state.normalize()

    assert full_desired_state.state == current_state.state


def assert_absent(*ifnames):
    """ Assert that a interface is not present in the current state """

    current_state = statelib.show_only(ifnames)
    assert not current_state[INTERFACES]


def assert_mac_address(state, expected_mac=None):
    """ Asserts that all MAC addresses of ifaces in a state are the same """
    macs = _iface_macs(state)
    if not expected_mac:
        expected_mac = next(macs)
    for mac in macs:
        assert expected_mac.upper() == mac


def _iface_macs(state):
    for ifstate in state[Interface.KEY]:
        yield ifstate[Interface.MAC]

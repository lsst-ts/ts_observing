# This file is part of ts_observing.
#
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
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

from __future__ import annotations

"""
Classes supporting observing blocks.
"""

__all__ = ["ObservingBlock", "ObservingScript", "SchedulingConstraints"]

import uuid
from typing import Any

from pydantic import BaseModel, Field, validator


class SchedulingConstraints(BaseModel):
    """Scheduling constraints to apply to an ObservingBlock."""

    # A key question here is whether different types of constraints are
    # handled as their own Constraint classes or if we enumerate
    # constraints here as an explicit list. For now use a list.

    airmass_min: float | None = None
    """Minimum airmass for this observation."""

    @validator("airmass_min")
    def check_airmass(cls, v):  # noqa: N805
        if v < 1.0:
            raise ValueError(f"Airmass must b >= 1.0 not {v!r}")
        return v


class ObservingScript(BaseModel):
    """A representation of a single observing script with parameters"""

    name: str
    """Name of observing script to run."""

    standard: bool
    """Flag to indicate whether or not this is referring to a standard
    script."""

    parameters: dict[str, Any]
    """Parameters to pass to the observing script."""


class ObservingBlock(BaseModel):
    """A collection of observation scripts and associated scheduling
    constraints.
    """

    name: str
    """Name of this observing block."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    """Unique identifier of this block."""

    constraints: SchedulingConstraints | None = None
    """Constraints to apply when scheduling this block."""

    scripts: list[ObservingScript]
    """Ordered list of observing scripts to execute."""

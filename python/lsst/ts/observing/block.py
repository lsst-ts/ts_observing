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

__all__ = ["ObservingBlock", "ObservingScript", "AirmassConstraint", "SeeingConstraint"]

import uuid
from typing import Any, Literal, Union

from pydantic import BaseModel, Field, validator
from typing_extensions import Annotated


class SchedulingConstraint(BaseModel):
    class Config:
        extra = "allow"
        allow_mutation = False


class AirmassConstraint(SchedulingConstraint):
    """A constraint on the airmass of the target."""

    name: Literal["airmass"] = "airmass"
    """Constraint name."""

    min: float
    """Minimum airmass for this observation."""

    @validator("min")
    def check_min(cls, v):  # noqa: N805
        if v < 1.0:
            raise ValueError(f"Airmass must b >= 1.0 not {v!r}")
        return v


class SeeingConstraint(SchedulingConstraint):
    """A constraint on the DIMM seeing value."""

    name: Literal["seeing"] = "seeing"
    """Constraint name."""

    max: float
    """Maximum DIMM seeing for this observation in arcsec."""

    @validator("max")
    def check_max(cls, v):  # noqa: N805
        if v < 0.0:
            raise ValueError("Maximum seeing must be positive.")
        return v


# Explicitly declare all the constraint classes allowed and tell pydantic
# that the name field should be used to work out which class to instantiate
# when reconstructing from JSON.
SchedulingConstraints = Annotated[Union[AirmassConstraint, SeeingConstraint], Field(discriminator="name")]


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

    # Ideally constraints would be a set with only one allowed per type.
    constraints: list[SchedulingConstraints] = Field(default_factory=list)
    """Constraints to apply when scheduling this block."""

    scripts: list[ObservingScript]
    """Ordered list of observing scripts to execute."""

    def add_constraint(self, constraint: SchedulingConstraints) -> None:
        """Add a new constraint to the observing block.

        Parameters
        ----------
        constraint : `SchedulingConstraint`
            The new constraint.
        """
        if not isinstance(constraint, SchedulingConstraint):
            raise ValueError("Constraint has the wrong type.")

        # Do not check yet if we are replacing a previous constraint.
        self.constraints.append(constraint)
        return

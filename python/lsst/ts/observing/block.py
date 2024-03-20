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

"""Classes supporting observing blocks."""

from __future__ import annotations

__all__ = [
    "ObservingBlock",
    "ObservingScript",
    "AirmassConstraint",
    "SkyBrightnessConstraint",
    "MoonBrightnessConstraint",
    "MoonDistanceConstraint",
    "CloudExtinctionConstraint",
    "SeeingConstraint",
]

import uuid
from typing import Annotated, Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SchedulingConstraint(BaseModel):
    """Base class for all scheduling constraints."""

    model_config = ConfigDict(extra="allow", frozen=True)


class AirmassConstraint(SchedulingConstraint):
    """A constraint on the airmass of the target."""

    name: Literal["airmass"] = "airmass"
    """Constraint name."""

    max: float
    """Maximum airmass for this observation."""

    @field_validator("max")
    @classmethod
    def check_max(cls, v: float) -> float:
        if v < 1.0:
            raise ValueError(f"Airmass must b >= 1.0 not {v!r}")
        return v


class MoonBrightnessConstraint(SchedulingConstraint):
    """A constraint on the moon brightness."""

    name: Literal["moon_brightness"] = "moon_brightness"
    """Constraint name."""

    max: float
    """Relative Moon brightness (0.0 to 1.0)."""

    @field_validator("max")
    @classmethod
    def check_max(cls, v: float) -> float:
        b_min = 0.0
        b_max = 1.0
        if v < b_min or v > b_max:
            raise ValueError(f"Moon brightness constraint must be between {b_min} and {b_max}, not {v!r}.")
        return v


class MoonDistanceConstraint(SchedulingConstraint):
    """A constraint on the moon distance."""

    name: Literal["moon_distance"] = "moon_distance"
    """Constraint name."""

    max: float
    """Minimum distance of target from Moon (0.0 to 180.0 deg)."""

    @field_validator("max")
    @classmethod
    def check_max(cls, v: float) -> float:
        d_min = 0.0
        d_max = 180.0
        if v < d_min or v > d_max:
            raise ValueError(f"Moon distance constraint must be between {d_min} and {d_max}, not {v!r}.")
        return v


class SkyBrightnessConstraint(SchedulingConstraint):
    """Maximum sky brightness allowed for this observation."""

    name: Literal["sky_brightness"] = "sky_brightness"
    """Constraint name."""

    max: float
    """Maximum allowed sky brightness (mag)."""

    # Including the band in the class has some advantages over having
    # class per-band, although a class per-band allows you to more easily
    # ensure that you aren't duplicating constraints by checking that
    # you don't have two constraints of the same class.
    band: str
    """Observing band for which this sky brightness is relevant (ugrizy)."""

    @field_validator("band")
    @classmethod
    def check_band(cls, v: str) -> str:
        if v not in (bands := "ugrizy"):
            raise ValueError(f"Band constraint must be one of {bands} not {v!r}.")
        return v

    @field_validator("max")
    @classmethod
    def check_max(cls, v: float) -> float:
        if v < 0.0:
            raise ValueError(f"Sky brightness constraint must be positive, not {v!r}.")
        return v


class CloudExtinctionConstraint(SchedulingConstraint):
    """Maximum cloud extinction allowed for this observation."""

    name: Literal["cloud_extinction"] = "cloud_extinction"
    """Constraint name."""

    max: float
    """Maximum allowed cloud extinction."""

    @field_validator("max")
    @classmethod
    def check_max(cls, v: float) -> float:
        if v < 0.0:
            raise ValueError(f"Cloud extinction must be positive, not {v!r}.")
        return v


class SeeingConstraint(SchedulingConstraint):
    """A constraint on the DIMM seeing value."""

    name: Literal["seeing"] = "seeing"
    """Constraint name."""

    max: float
    """Maximum DIMM seeing for this observation in arcsec."""

    @field_validator("max")
    @classmethod
    def check_max(cls, v: float) -> float:
        if v < 0.0:
            raise ValueError(f"Maximum seeing must be positive, not {v!r}.")
        return v


# Explicitly declare all the constraint classes allowed and tell pydantic
# that the name field should be used to work out which class to instantiate
# when reconstructing from JSON.
SchedulingConstraints = Annotated[
    AirmassConstraint
    | MoonBrightnessConstraint
    | MoonDistanceConstraint
    | CloudExtinctionConstraint
    | SkyBrightnessConstraint
    | SeeingConstraint,
    Field(discriminator="name"),
]


class ObservingScript(BaseModel):
    """A representation of a single observing script with parameters."""

    name: str
    """Name of observing script to run."""

    standard: bool
    """Flag to indicate whether or not this is referring to a standard
    script."""

    parameters: dict[str, Any]
    """Parameters to pass to the observing script."""

    def get_script_configuration(self) -> str:
        """Get script configuration as a yaml string.

        Returns
        -------
        config : `str`
            Script configuration.
        """

        def represent_string_with_colon(dumper, data):
            if ":" in data:
                return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="'")
            return dumper.represent_scalar("tag:yaml.org,2002:str", data)

        yaml.representer.SafeRepresenter.add_representer(str, represent_string_with_colon)
        return (
            yaml.safe_dump(self.parameters, default_flow_style=False, sort_keys=False)
            if self.parameters
            else ""
        )


class ObservingBlock(BaseModel):
    """A collection of observation scripts and associated scheduling
    constraints.
    """

    name: str
    """Name of this observing block."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    """Unique identifier of this block."""

    program: str
    """Observing program of which this block is a part."""

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

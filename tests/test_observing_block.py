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

import json
import unittest
import uuid

import pydantic
from lsst.ts.observing import (
    AirmassConstraint,
    CloudExtinctionConstraint,
    MoonBrightnessConstraint,
    MoonDistanceConstraint,
    ObservingBlock,
    ObservingScript,
    SeeingConstraint,
    SkyBrightnessConstraint,
)


class TestConstraints(unittest.TestCase):
    def test_airmass(self):
        c = AirmassConstraint(max=1.4)
        self.assertEqual(c.max, 1.4)

        with self.assertRaises(pydantic.ValidationError):
            AirmassConstraint(max=0.5)

    def test_sky_brightness(self):
        c = SkyBrightnessConstraint(max=2.0, band="u")
        self.assertEqual(c.band, "u")

        with self.assertRaises(pydantic.ValidationError):
            SkyBrightnessConstraint(max=1.0, band="x")

        with self.assertRaises(pydantic.ValidationError):
            SkyBrightnessConstraint(max=-1.0, band="u")

    def test_moon_brightness(self):
        b = MoonBrightnessConstraint(max=0.8)
        self.assertEqual(b.max, 0.8)

        with self.assertRaises(pydantic.ValidationError):
            MoonBrightnessConstraint(max=1.5)

        with self.assertRaises(pydantic.ValidationError):
            MoonBrightnessConstraint(max=-2.0)

        with self.assertRaises(pydantic.ValidationError):
            MoonBrightnessConstraint(max="half")

    def test_moon_distance(self):
        b = MoonDistanceConstraint(max=90.0)
        self.assertEqual(b.max, 90.0)

        with self.assertRaises(pydantic.ValidationError):
            MoonDistanceConstraint(max=190.0)

        with self.assertRaises(pydantic.ValidationError):
            MoonDistanceConstraint(max=-2.0)

    def test_cloud_extinction(self):
        e = CloudExtinctionConstraint(max=8.0)
        self.assertEqual(e.max, 8.0)

        with self.assertRaises(pydantic.ValidationError):
            CloudExtinctionConstraint(max=-10.0)

        with self.assertRaises(pydantic.ValidationError):
            CloudExtinctionConstraint(max="cirrus")

    def test_seeing(self):
        s = SeeingConstraint(max=0.4)
        self.assertEqual(s.max, 0.4)

        with self.assertRaises(pydantic.ValidationError):
            SeeingConstraint(max=-0.1)


class TestObservingBlock(unittest.TestCase):
    def test_basic(self):
        # No validation of script names or script parameters.

        script1 = ObservingScript(name="slew", standard=True, parameters={"target": "W48"})
        script2 = ObservingScript(name="standard_visit", standard=False, parameters={"exptime": 30.0})

        block = ObservingBlock(
            name="OBS-123",
            program="SITCOM-456",
            scripts=[script1, script2],
            constraints=[AirmassConstraint(max=1.5)],
        )

        self.assertEqual(block.name, "OBS-123")
        self.assertEqual(block.program, "SITCOM-456")
        self.assertEqual(len(block.scripts), 2)
        self.assertEqual(len(block.constraints), 1)

        block.add_constraint(SeeingConstraint(max=0.5))
        self.assertEqual(len(block.constraints), 2)
        block.add_constraint(SkyBrightnessConstraint(max=10.0, band="u"))

        with self.assertRaises(ValueError):
            block.add_constraint({"moon_brightness": 0.8})

        # Round trip via json.
        new = ObservingBlock.parse_obj(json.loads(block.json()))
        self.assertEqual(new, block)

        # Ensure that an external UUID can override.
        our_id = uuid.uuid4()
        block = ObservingBlock(name="Testing", program="Something", scripts=[script1, script2], id=our_id)
        self.assertEqual(block.id, our_id)


if __name__ == "__main__":
    unittest.main()

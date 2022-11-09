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
from lsst.ts.observing import ObservingBlock, ObservingScript, SchedulingConstraints


class TestConstraints(unittest.TestCase):
    def test_airmass(self):
        c = SchedulingConstraints(airmass_min=1.4)
        self.assertEqual(c.airmass_min, 1.4)

        with self.assertRaises(pydantic.ValidationError):
            SchedulingConstraints(airmass_min=0.5)


class TestObservingBlock(unittest.TestCase):
    def test_basic(self):
        # No validation of script names or script parameters.

        script1 = ObservingScript(name="slew", parameters={"target": "W48"})
        script2 = ObservingScript(name="standard_visit", parameters={"exptime": 30.0})

        block = ObservingBlock(name="Testing", scripts=[script1, script2])

        self.assertEqual(block.name, "Testing")
        self.assertEqual(len(block.scripts), 2)

        # Round trip via json.
        new = ObservingBlock.parse_obj(json.loads(block.json()))
        self.assertEqual(new, block)

        # Ensure that an external UUID can override.
        our_id = uuid.uuid4()
        block = ObservingBlock(name="Testing", scripts=[script1, script2], id=our_id)
        self.assertEqual(block.id, our_id)


if __name__ == "__main__":
    unittest.main()

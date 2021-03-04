# -*- coding: utf-8 -*-
"""Verse


LaTeX Songs to HTML
Copyright (C) 2021  Davide Peressoni

based on:
LaTeX Songs 2 Web
Copyright (C) 2019  Carlos Galindo

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from line import Line

from typing import List, Dict

class Verse:
  """Represents a verse.

  Parameters
  ----------
  isChorus: bool
    If true the verse is indeed a chorus, default False

  isNumbered: bool
    If true the verse is numbered, default True

  indent: bool
    If true the verse is indented, default True

  Attributes
  ----------
  isChorus: bool
    If true the verse is indeed a chorus

  numbered: bool
    If true the verse is numbered

  indent: bool
    If true the verse is indented

  lines: List[line]
    The lines of the verse
  """

  def __init__(self, isChorus: bool = False, isNumbered: bool = True, indent: bool = True):
    self.isChorus = isChorus
    self.numbered = not isChorus and isNumbered
    self.lines: List[Line] = []
    self.indent: bool = not isChorus and indent

  def addLine(self, l: Line):
    """Adds a new line

    Parameters
    ----------

    l: line
      The lines of the verse
    """

    self.lines.append(l)

  def transpose(self, amount: int):
    """Transpose the verse chords

    Parameters
    ----------

    amount: int
      Semitones to transpose
    """
    for l in self.lines:
      l.transpose(amount)

  def hasChords(self) -> bool:
    """Check if the verse has chords

    Returns
    ----------

    bool
      True if the verse has chords, False elsewhere
    """
    for l in self.lines:
      if l.hasChords():
        return True
    return False

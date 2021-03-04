# -*- coding: utf-8 -*-
"""Chord
Represents a Chord

LaTeX Songs to HTML
Copyright (C) 2021  Davide Peressoni

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

from collections import defaultdict
from enum import IntEnum
from itertools import count

from typing import Union, List, DefaultDict, Optional


class Chord:
  """Represents a chord.

  Parameters
  ----------
  chord: str
    A string describing the chord.

    You can use:

    - letter notes (A, B, C, D, E, F, G, H)
    - `#` for sharp and `&` for flat
    - other symbols (`-`, `4`, `7`, ...)

  Note
  ----
    European notation is used, so B=H and B&=H&=A#.

  Example
  -------
    >>> print(Chord('C&-7'))
    Si-7

  """

  CHORDS: DefaultDict[str, Optional[int]] = defaultdict(lambda:None)
  """Dictionary to convert english chords into semitones."""
  CHORDS.update({
    # notes:
    'A' : 9,
    'B' : 11,
    'C' : 0,
    'D' : 2,
    'E' : 4,
    'F' : 5,
    'G' : 7,
    'H' : 11,
    # accidentals:
    '#' : 1,
    '♯' : 1,
    '&' : -1,
    '♭' : -1
  })

  Note = IntEnum('Note', zip(['Do', 'Do♯', 'Re', 'Mi♭', 'Mi', 'Fa', 'Fa♯', 'Sol', 'Sol♯', 'La', 'Si♭', 'Si'], count()))
  """Represents a note in italian notation."""
  Note.__str__ = lambda self: self.name # print the note instead of debug info
  Note.__add__ = lambda self, n: Chord.Note((int(self)+n)%12) # Sum notes modulo 12

  def __init__(self, chord: str, tran: int = 0):
    """Build a chord."""

    self._chord: List[Union[str, Chord.Note]] = []
    """List of tokens composing the chord."""

    for c in chord:
      if (n := self.CHORDS[c]) is not None and (
        len(self._chord) == 0 or
        type(self._chord[-1]) is not str or
        not self._chord[-1][-1].isalnum()
      ):
        # if is a note name or an accidental
        if c in ['#','&', '♯', '♭']:
          # if is a sharp or flat
          if self._chord[-1] == '\\':
            self._chord.pop()
          if not isinstance(last := self._chord[-1], Chord.Note):
            raise TypeError(f"Cannot read chord {chord}: {last} is not a valid note")
          self._chord[-1] += n
        else:
          self._chord.append(self.Note(n))
      else:
        # other symbols
        self._chord.append(c)
    self.transpose(tran)

  def transposed(self, n = 0) -> str:
    """Get transposed chord as string.

    Parameters
    ----------
    n: int
      Semitones of transposition.

    Returns
    -------
    str
      Transposed chord.
    """
    if n is None: n = 0

    text = ""

    for e in self._chord:
      if isinstance(e, self.Note):
        # transpose only notes
        text += str(e + n)
      else:
        text += e

    return text

  def transpose(self, n = 0):
    """Transpose the chord.

    Parameters
    ----------
    n: int
      Semitones of transposition.

    """
    if n is None: n = 0

    self.text = self.transposed(n)
    """String representing the chord."""

  def __str__(self):
    return self.text

  def __iadd__(self, txt: str):
    """Append text to the chord."""
    self._chord.append(txt)
    self.text += txt
    return self

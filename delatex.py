# -*- coding: utf-8 -*-
"""delatex
Escape LaTeX

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

import re
from enum import Enum

from line import SPAN_BEGIN, SPAN_END

from dominate.util import raw

class format(Enum):
  """Represents an output text format.

  Enumeration
  -----------
    * PLAIN
    * HTML
  """
  PLAIN = 'plain'
  HTML = 'HTML'

def delatex(src: str, out: format = format.PLAIN, remove_other: bool = True) -> str:
  """Escape LaTeX string.

    Parameters
    ----------
    src: str
      String to escape.

    out: format
      Output format, default format.PLAIN

    remove_other: bool
      If true removes all not known macros, default True

    Returns
    -------
    str
      Escaped string.
    """
  src = str(src)

  if out == format.HTML:
    src = src.\
      replace(r'\\', '<br>').\
      replace(r'\newline', '<br>').\
      replace(r'\star', '&starf;').\
      replace('~','&nbsp;').\
      replace(r'\dimshed', '&deg;').\
      replace(r'\meterCutC', '&#x1D135;').\
      replace(r'\lrep', '&#x1D106;').\
      replace(r'\rrep', '&#x1D107;')

    for env in SPAN_BEGIN:
      src = re.sub(r"(\\"+env+r"[ \t]*?)\{[ \t]*\}", '', src)
      src = re.sub(r"(\\"+env+r"[ \t]*?\{)(([^\{\}]*|\{.*?\})*?)(\}|$)", f"{SPAN_BEGIN[env]}\\2{SPAN_END[env]}", src)

  src = src.\
    replace(r'\\', '\n').\
    replace(r'\newline', '\n').\
    replace(r'\star', '⋆').\
    replace('~',' ').\
    replace(r'\dimshed', '°').\
    replace(r'\meterCutC', '𝄵').\
    replace(r'\lrep', '𝄆').\
    replace(r'\rrep', '𝄇')

  src = src.\
    replace('---', '—­').\
    replace('--', '–').\
    replace(r'\dots', '…').\
    replace('$', '').\
    replace(r'\ast', '*').\
    replace(r'\ ', ' ').\
    replace(r'\%', '%').\
    replace(r'\#', '#').\
    replace(r'\textbackslash', '\\')

  if remove_other:
    src = re.sub(r"\\(\d?[\d\w]+)[ \t]*?(\{.*?\}|\[.*?\])*", '', src)

  src = src.\
    replace('{', '').\
    replace('}', '')

  return raw(src.replace('\n','')) if out == format.HTML else src

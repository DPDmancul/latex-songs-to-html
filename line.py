# -*- coding: utf-8 -*-
"""Line


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

import re

from typing import List, Dict, Any
Obj = Dict[str, Any]


def _span_begin(cls: str):
  return f'<em class="{cls}">'
SPAN_BEGIN = {
  'echo': _span_begin('echo'),
  'poetry': _span_begin('poetry'),
  'emph': '<em>',
  'textit': '<i>',
  'textbf': '<b>',
  'underline': '<u>',
  'alert': '<mark>',
  'textsuperscript': '<sup>',
  'textsubscript': '<sub>',
  'textnormal': '<span class="normal">',
  'textsmall': '<small class="small">',
  'texttiny': '<small class="tiny">',
}
SPAN_END = {
  'echo': '</em>',
  'poetry': '</em>',
  'emph': '</em>',
  'textbf': '</b>',
  'textit': '</i>',
  'underline': '</u>',
  'alert': '</mark>',
  'textsuperscript': '</sup>',
  'textsubscript': '</sub>',
  'textnormal': '</span>',
  'textsmall': '</small>',
  'texttiny': '</small>',
}

class Line:
  """Represents a verse line.

  Parameters
  ----------
  text: str
    The text of the line

  extras: List[Obj]
    The extras (chrods, envs, ...) related to a specific char of the line

  Attributes
  ----------
  l: Optional[List[str]]
    lyrics tokens

  c: List[Obj]
    chord tokens

  """

  def __init__(self, text: str, extras: List[Obj]):
    self.text = text
    self.extras = extras

    self.l: Optional[List[str]] = [''] # lyrics
    self.c: List[Obj] = [{'chord': '', 'rowspan': 1}] # chords

    if text.strip() == '':
      # if no lyrics then put extras in the line of chords
      nolyrics = True
      self.l = None
      def add_lyrics(txt: str):
        self.c[-1]['chord'] += txt
      def new_lyric(txt: str = ''):
        self.c.append({'chord': txt, 'rowspan': 1})
      def get_lyric():
        self.c[-1]['chord']
    else:
      nolyrics = False
      def add_lyrics(txt: str):
        self.l[-1] += txt
      def new_lyric(txt: str= ''):
        self.l.append(txt)
      def get_lyric():
        return self.l[-1]

    mid = True
    inside: List[str] = []

    for i in range(len(self.text)):
      if self.extras[i]:
        for e in self.extras[i]:
          if e['type'] == 'chord':
            # Check for floating chord
            # 3 options ^[chord] word ; word [chord] word ; word [chord]$
            floating = (self.text[i] == ' ' and (i == 0 or self.text[i - 1] == ' '))
            self.c.append({'chord': e['data'], 'rowspan': 1, 'env': (SPAN_BEGIN[inside[-1]], SPAN_END[inside[-1]]) if nolyrics and inside else None})
            if inside:
              add_lyrics(SPAN_END[inside[-1]])
            if floating:
              new_lyric()
              self.c.append({})
            new_lyric(SPAN_BEGIN[inside[-1]] if inside else '')
            mid = True
          elif e['type'] == 'dir-rep':
            self.c.append({'class': e['data'], 'rowspan': 2})
            self.c.append({})
            if mid and inside:
              add_lyrics(SPAN_END[inside[-1]] if inside else '')
            mid = False
          elif e['type'] == 'rep':
            new_lyric(f'<span class="rep">(×{e["data"]})</span>')
            self.c.append({})
            mid = False
          elif (env := e['type']) in SPAN_BEGIN:
            if not mid:
              new_lyric('')
              mid = True
            inside.append(env)
            start = SPAN_BEGIN[env] + ('(' if env == 'echo' else '')
            add_lyrics(start)
          elif (env := e['type']) == 'close':
            if not mid:
              new_lyric(SPAN_BEGIN[inside[-1]])
              mid = True
            end = (')' if inside[-1] == 'echo' else '') + SPAN_END[inside.pop()]
            add_lyrics(end)
          elif e['type'] == 'skip':
            add_lyrics(f'</td><td class="{e["data"]}">&nbsp;</td><td>')
          elif e['type'] == 'text':
            if self.c and 'chord' in self.c[-1]:
              self.c[-1]['chord'] += e['data']
            else:
              self.c.append({'chord': e['data'], 'rowspan': 1})
          else:
            raise Exception(f"Unrecognized type {e['type']}")

      if not mid:
        new_lyric(SPAN_BEGIN[inside[-1]] if inside else '')
      mid = True
      add_lyrics(self.text[i])


    if self.l is not None:
      self.l = [re.sub(r"(^ +| +$)", '&nbsp;' , e) for i,e in enumerate(self.l)]


  def transpose(self, amount: int):
    """Transpose the line chords

    Parameters
    ----------

    amount: int
      Semitones to transpose
    """
    for e in self.c:
      if 'chord' in e:
        e['chord'].transpose(amount)

  def hasChords(self) -> bool:
    """Check if the line has chords

    Returns
    ----------

    bool
      True if the line has chords, False elsewhere
    """
    for crd in self.c:
      if 'chord' in crd and str(crd['chord']).strip() != '':
        return True
    return False

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LaTeX Songs to HTML
Convert a LaTeX Songs book to an HTML page.

Setup
-----

    pip3 install -r requirements.txt

Usage
-----

    python3 songs.py source.tex output.html [language [toc_title]]

Where
  * `language` is the HTML language code (default "en").
  * `toc_title` is the title of the toc (default "Table of contents").

License
-------

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

from song import load_songs
from delatex import delatex, format

import sys
from pathlib import Path

from typing import Union, Optional

import dominate
from dominate.tags import *


def songs_to_html(source: Union[Path, str], out: Union[Path, str], lang: str = 'en', toc: str = 'Table of contents'):
  """Convert a LaTeX Songs book to an HTML page.

  Arguments
  ---------

    source: Union[Path, str]
      Input `tex` file

    out: Union[Path, str]
      Output `html` file

    lang: str
      the HTML language code, default "en"

    toc: str
      the title of the toc, default "Table of contents"

  """

  source: Path = Path(source)
  out: Path = Path(out)

  songs = load_songs(source)

  title = songs[0][0]
  songs[0] = (None, songs[0][1])

  doc = dominate.document(title=delatex(title))
  doc['lang'] = 'it'

  n_sec = len(songs)-1

  with doc.head:
    meta(charset="utf-8")
    style("""
      .hidden{
        display: none;
      }

      /* Fonts */
      em, i{
        font-style: italic;
      }
      strong, b{
        font-weight: bold;
      }
      u{
        text-decoration: underline;
      }
      small, .small{
        font-size: smaller /* small */;
      }
      .tiny{
        font-size: smaller /* x-small */;
      }
      .poetry{
        font-style: normal;
        font-family: 'TeX Gyre Chorus', 'Monotype Corsiva', 'URW Chancery L', 'Apple Chancery', 'Felipa', 'Sand', 'Script MT', 'Textile', 'Zapf Chancery', chancery, cursive;
      }
      .normal{
        font-style: normal;
        font-weight: normal;
        text-decoration: none;
        font-size: medium;
      }

      /* Song table */
      td{
        padding: 0;
        line-height: 1.1em;
      }

      /* Song header */
      .song-header{
        display: flex;
        margin-top: 5px;
        margin-bottom: 5px;
      }
      .song-number{
        font-size: 1.5em;
        background: lightgray;
        padding: 5px;
        margin-right: 5px;
        min-width: 40px;
        text-align: center;
      }
      .song-title{
        text-transform: uppercase;
      }
      .song-title, .song-author{
        margin: 0;
      }
      .song-info{
        display: flex;
        flex-direction: column;
      }

      /* Verses and choruses */
      .verse{
        padding: 5px;
      }
      .verse-num-col{
        width: 30px;
        padding-right: 5px;
        text-align: right;
      }
      .chorus {
        border-left: 1px black solid;
      }
      .chorus strong{
        font-weight: normal;
      }

      /* Skip */
      .bigskip{
        line-height: 1.3em;
      }
      .medskip{
        line-height: .8em;
      }
      .smallskip{
        line-height: .3em;
      }

      /* Notes */
      .note{
        background: lightgray;
        padding: 5px;
      }

      /* Meter */
      .meter-fraction{
        display: inline-block;
        line-height: 0.85em;
        font-size: 80%;
        text-align: center;
        vertical-align: middle;
      }
      .meter-fraction sup, .meter-fraction sub{
        display: block;
        vertical-align: baseline;
        font-size: inherit;
      }

      /* Sections */
      @media only screen{
        body{
          margin-left: 30px;
        }
        .section-label{
          position: sticky;
          top: 200px;
          display: inline-grid;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: medium;
          font-weight: normal;
          margin-left: -30px;
          width: 20px;
          height: calc(100vh / """ + str(n_sec) + """);
          min-height: 30px;
          background: lightgray;
        }
      }
    """)

    with doc:
      h1(delatex(title, format.HTML))
      p(a(toc, href="#toc"))

      for i, (section_name, song_list) in enumerate(songs):
        if not song_list: continue
        with section(id=f"sec-{delatex(section_name)}" if section_name else ""):
          if section_name:
            h2(delatex(section_name, format.HTML), cls="section-label", style=f"top: {(i-1)*100/n_sec}vh")
          for song in song_list:
            with article(cls="song"):
              with header(cls="song-header"):
                strong(song.number, cls="song-number")
                with div(cls="song-info"):
                  h3(span(song.number, ". ", cls="hidden"), delatex(song.name, format.HTML), id=f"song-{song.number}", cls="song-title")
                  p(delatex(song.author, format.HTML), cls="song-author")
              verse_num = 1
              for verse in song.verses:
                with div(cls=f'verse {"chorus" if verse.isChorus else ""}'):
                  first_col = None
                  if verse.indent:
                    first_col = ''
                    if verse.numbered:
                      first_col = f'{verse_num}.'
                      verse_num += 1

                  for line in verse.lines:
                    with table():
                      if line.hasChords():
                        with tr(__pretty=False):
                          if first_col is not None:
                            td('' if line.l else first_col, cls="verse-num-col")
                          for chord in line.c:
                            td(delatex(
                              "{0}{2}{1}".format(
                                *(
                                  chord['env']
                                  if 'env' in chord and chord['env'] is not None
                                  else ('', '')
                                ),
                                chord['chord']
                              ),
                              format.HTML
                            ) if 'chord' in chord else '')
                      if line.l:
                        with tr(__pretty=False):
                          if first_col is not None:
                            td(first_col, cls="verse-num-col")
                          for token in line.l:
                            content = delatex(token, format.HTML)
                            if verse.isChorus:
                              td(strong(content))
                            else:
                              td(content)
                      if (line.hasChords() or line.l) and first_col is not None:
                        first_col = ''

      with nav(id="toc"):
        h2(toc)
        with ul():
          for section_name, song_list in songs:
            if not song_list: continue
            with li(a(delatex(section_name, format.HTML),href=f"#sec-{delatex(section_name)}")).add(ol()) if section_name else ol():
              for song in song_list:
                li(a(delatex(song.name.replace("<br>"," "), format.HTML), href=f"#song-{song.number}"), br(), em(delatex(song.author)), value=song.number)

  with out.open('w') as file:
    file.write(doc.render(pretty=True))


if __name__ == "__main__":
  if '-h' in sys.argv or '--help' in sys.argv:
    print(f"""LaTeX Songs to HTML
Usage: {sys.argv[0]} source.tex output.html [language [toc_name]]
Where
  - `language` is the HTML language code (default "en").
  - `toc_title` is the title of the toc (default "Table of contents").""")
    exit(0)
  if len(sys.argv) <= 1:
    sys.argv.append(input("Insert input LaTeX main file: "))
  if len(sys.argv) <= 2:
    sys.argv.append(input("Insert output html file: "))
  songs_to_html(*sys.argv[1:])

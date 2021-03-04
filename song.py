# -*- coding: utf-8 -*-
"""Song

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

from verse import Verse
from line import Line, SPAN_BEGIN
from chord import Chord

from delatex import delatex

from pathlib import Path
import re
import copy

from typing import List, Optional, TextIO, Union, Tuple, Dict


class Song:
  """Represents a song.

  Parameters
  ----------
  file: TextIO
    The song source file.

  index: int
    The song number

  Attributes
  ----------
  name: str
    The song title

  number: int
    The song number

  author: Optional[str]
    The song author

  capo: Optional[int]
    The capo of the song

  verses:List[verse]
    The verses of the song

  """

  def hasChords(self) -> bool:
    """Check if the song has chords

    Returns
    ----------

    bool
      True if the song has chords, False elsewhere
    """
    for v in self.verses:
      if v.hasChords():
        return True
    return False

  def __init__(self, file: TextIO, index: int):
    self.name: str = ''
    self.number: int = 0
    self.author: Optional[str] = None
    self.capo: Optional[int] = None
    self.verses: List[Verse] = []

    def read_author(text: str) -> Optional[str]:
      author = re.search(r"by=\{(.*?)\}",text)
      return author.group(1) if author else None

    memorizeRe = re.compile(r"^\\memorize")
    chordRe = re.compile(r"^\\\[(.+?)\]")
    repeatRe = re.compile(r"^\^")
    repRe = re.compile(r"^\\rep(\{)?((?(1).+?(?=\})|\d))\}?")
    dirRepRe = re.compile(r"^\\([lr]rep)")
    macroRe = re.compile(r"^\\(\d?[\d\w]+)[ \t]*?(\{.*?\}|\[.*?\])*")
    elseRe = re.compile(r"^\\else")
    fiRe = re.compile(r"^\\fi")
    tranposeRe = re.compile(r"^\\transpose *?\{(-?\+?\d+?)\}")
    songBeginRe = re.compile(r"\\beginsong *?\{((?:[^\{\}]|\{.*?\})*?)\}(\[.*?\])?")
    songEndRe = re.compile(r"^\\endsong")
    verseCmdRe = re.compile(r"^\\(begin|end)(verse|chorus)(\*?)")
    capoRe = re.compile(r"^\\capo\{(\d+?)\}")
    replayRe = re.compile(r"^\\replay")
    chordswapRe = re.compile(r"^\\chords(on|off)")
    skipRe = re.compile(r"^\\((small|med|big)skip)")
    noteRe = re.compile(r"^\\(?:music|text)note[ \t]*?\{(([^\{]|\{.*?\})*?)\}")
    nolyricsRe = re.compile(r"^\\nolyrics")
    stackRe = re.compile(r"^(\{|\})")
    # Helpers
    ignore: bool = False
    verse: Optional[Verse] = None
    global_chord: bool = True
    local_chord: bool = True
    meter: Optional[Tuple[str, str]] = ('4','4')
    verse_indent: bool = True
    class scope:
      def __init__(self, dict: Optional[Dict] = None):
        if dict is not None:
          self.__dict__ = dict
          return
        self.nolyrics: bool = False
        self.transpose: int = 0
      def __copy__(self):
        return type(self)(copy.copy(self.__dict__))
      def __deepcopy__(self, memo):
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(copy.deepcopy(self.__dict__))
            memo[id_self] = _copy
        return _copy
    class scope_list(list):
      def add(self):
        self.append(copy.deepcopy(self[-1]) if self else scope())
    stack: List[scope_list] = scope_list([scope()])
    # Memory and replay variables
    memory: List[Chord] = []
    memorizing: bool = False
    replayIndex: int = 0

    line_addendum = ''
    for line in file:
      try:
        line = line_addendum + line
        line_addendum = ''
        line_skip: Optional[str] = None
        # remove comments
        text = re.sub(r"%.*$", '', line)
        text = re.sub(r"\\brk(\{\})?", '', text) # rm \brk commands

        def text_modifier(modifier: str, terminator: str = r"(?=\}|\]|$|\\end(?:verse|chorus))"): return r"\\(" + modifier + r")(?P<spc>([\\ \t]*)(?(spc)(?:[^\{\}\[\]]|\{.*?\}|\\\[.*?\])*|))" + terminator
        for modifier, sub in [("small|tiny", r'\\text\1{\2}'), ("itshape", r'\\textit{\2}'), ("normalfont", r'\\textnormal{\2}')]:
          if (res := re.search(text_modifier(modifier, terminator='$'), text)) and ((arg := res.group(2)) is None or arg.strip() not in [r'\endverse',r'\endchorus']):
            line_addendum += f"\\{res.group(1)} "
          text = re.sub(text_modifier(modifier), sub, text)

        extras: List[List] = [[]]

        while (i := len(extras) - 1) < len(text):
          beginning, remain = text[:i], text[i:]

          def text_without(s: str, add: str = '' ):
            return beginning + add + text[i + len(s): ]

          if ignore:
            if fiRe.match(remain):
              ignore = False
              text = text_without('\\fi')
          elif res := re.match(r"([^\|]*?)\\meter(\{|\d)", remain):
            if res := re.match(re.escape(before := res.group(1))+r'\\meter(\{)?((?(1).+?(?=\})|(?:\d|\\[^ ]+)))(?(1)\})(?:(\{)?((?(3)\d+(?=\})|\d))(?(3)\}))?', remain):
              text = beginning + re.sub('^'+re.escape(res.group(0)), before.replace("\\", r"\\"), remain, 1)
              meter = res.group(2, 4)
          elif meter is not None and '|' in remain:
            class_frac = '"meter-fraction"'
            text = beginning + re.sub('\|',f'<span class="meter">{"<span class="+class_frac+"><sup>%s</sup><sub>%s</sub></span>"%meter if len(meter) == 2 and meter[1] is not None else meter[0]}</span>'.replace('\\', r'\\'), remain, 1)
            meter = None
          # Command lookup
          elif the_transpose := tranposeRe.search(remain):
            text = text_without(the_transpose.group(0))
            stack[-1].transpose = int(the_transpose.group(1))
          elif theSongBegin := songBeginRe.search(remain):
            text = text_without(theSongBegin.group(0))
            self.name = theSongBegin.group(1)
            if res := re.match(r"(.*)\\\\((?:[^\{\}]|\{.*\})*)", self.name):
              self.name = f"{res.group(1)}<br>({res.group(2)})"
            self.number = index
            self.author = read_author(theSongBegin.group(2))
          elif songEndRe.match(remain):
            text = beginning
            return
          elif theVerseCmd := verseCmdRe.search(remain):
            text = text_without(theVerseCmd.group(0))
            if theVerseCmd.group(1) == 'begin':
              if theVerseCmd.group(2) == 'verse' and len(memory) == 0:
                memorizing = True
              replayIndex = 0
              verse = Verse(theVerseCmd.group(2) == 'chorus', theVerseCmd.group(3)!='*', indent=verse_indent)
              verse_indent = True
              stack.add()
            else: #verse end
              if verse.isChorus != (theVerseCmd.group(2) == 'chorus'):
                raise Exception(f'Song #{index}: ended chorus-verse with wrong command.')
              memorizing = False;
              self.verses.append(verse)
              verse = None
              local_chord = global_chord
              stack.pop()
          elif theCapo := capoRe.search(remain):
            text = text_without(theCapo.group(0))
            self.capo = int(theCapo.group(1))
          elif elseRe.match(remain):
            ignore = True
            text = text_without('\\else')
          elif theChord := chordRe.search(remain):
            text = text_without(theChord.group(0))
            c = Chord(theChord.group(1), stack[-1].transpose)
            if local_chord:
              extras[i].append({ 'type': 'chord', 'data': c })
            if memorizing:
              memory.append(c)
          elif repeatRe.match(remain):
            text = text_without('^')
            if replayIndex < len(memory):
              if local_chord:
                extras[i].append({ 'type': 'chord', 'data': memory[replayIndex].transposed(stack[-1].transpose) })
              replayIndex+=1
          # elif theDirRep := dirRepRe.search(remain):
          #   text = text_without(theDirRep.group(0))
          #   extras[i].append({ 'type': 'dir-rep', 'data': theDirRep.group(1) })
          elif theRep := repRe.search(remain):
            text = text_without(theRep.group(0))
            extras[i].append({ 'type': 'rep', 'data': theRep.group(2) })
          elif memorizeRe.search(remain):
            text = text_without('\\memorize')
            memory = []
            memorizing = True
          elif replayRe.match(remain):
            text = text_without('\\replay')
            replayIndex = 0
          elif res := chordswapRe.match(remain):
            text = text_without(res.group(0))
            local_chord = res.group(1) == 'on'
            if verse is None:
              global_chord = local_chord
          elif res := skipRe.match(remain):
            text = text_without(res.group(0))
            line_skip = res.group(1)
          elif res := noteRe.match(remain):
            text = text_without(res.group(0), add=f'<p class="note">{res.group(1)}</p>')
          elif res := nolyricsRe.match(remain):
            text = text_without(res.group(0))
            stack[-1].nolyrics = True
          elif res := stackRe.match(remain):
            text = text_without(res.group(0))
            if res.group(1) == '{':
              stack.add()
            else:
              if len(stack) >= 2:
                stack.pop()
              else:
                print(f"Song #{index} ({self.name}): Unmatched braces `{line}`")
          elif res := re.match(r"\\noindent", remain):
            text = text_without(res.group(0))
            verse_indent = False
          else:
            class ContinueOuter(Exception): pass
            try:
              for env in SPAN_BEGIN:
                if res := re.match(r"^(\\"+env+r"[ \t\n]*?)\{[ \t\n]*\}", remain):
                  text = text_without(res.group(0))
                elif theEnv := re.match(r"^(\\"+env+r"[ \t]*?\{)(([^\{\}]*|\{.*?\})*?)(\}|$)", remain):
                  text = text_without(theEnv.group(0), add= f'{theEnv.group(2)}\\{env}end ')
                  extras[i].append({ 'type': env })
                  if theEnv.group(4) == '':
                    line_addendum += theEnv.group(1)
                  raise ContinueOuter()
                elif re.match(r"^\\"+env+"end", remain):
                  text = text_without(f'\\{env}end')
                  extras[i].append({ 'type': 'close' })
                else:
                  continue
                raise ContinueOuter()
            except ContinueOuter:
              continue

            # Command lookup end, removing any unrecognized command
            theMacro = macroRe.match(remain)
            if theMacro and delatex(tex := theMacro.group(0)) == '':
              print(f"Song #{index} ({self.name}): unrecognized command `{tex}`")

            if stack[-1].nolyrics:
              if len(extras[i]) != 0 and extras[i][-1]['type'] == 'text':
                extras[i][-1]['data'] += remain[0]
              else:
                extras[i].append({'type':'text', 'data':remain[0]})
              text = beginning + remain[1:]
              continue

            extras.append([])

        if not verse and text.strip() != '':
          #print(f"l outside v: {text}")
          v = Verse(isNumbered=False, indent=verse_indent)
          verse_indent = True
          v.addLine(Line(text,[[] for c in text]))
          self.verses.append(v)
          continue
        if ignore or text.strip() == '' and len(extras[0]) == 0:
          continue

        if verse is not None:
          verse.addLine(Line(' ' * len(extras) if text.strip() == '' else text, extras))

        if line_skip:
          (verse if verse is not None else self.verses[-1]).addLine(Line('', [[{'type': 'skip', 'data': line_skip}]]))
      except:
        print(f"On line: `{line}`")
        raise


Section = Tuple[Optional[str],List[Song]]

def load_songs(source: Union[Path, str]) -> List[Section]:
  """Load songs from source file

  Parameters
  ----------
  source: Union[Path, str]
    source file

  Returns
  -------
  List[Section]
    List containing the sections. Each section is a tuple with the title of the section and a list of its songs.
  """
  source: Path = Path(source)

  songs: List[Section] = []
  with source.open('r') as file:
    into_songs = False
    index = 0
    for line in file:
      # Remove comments
      line = re.sub(r"%.*$", '', line)
      # Traverse into \input commands for songs
      if res := re.search(r"\\(?:songsection\*?|.?section\*?)\{([^\}]+)\}", line):
        songs.append((res.group(1),[]))
        continue
      if not into_songs:
        if re.match(r"\\begin\{songs\}", line):
          into_songs = True # songs environment started
        continue
      if re.match(r"\\end\{songs\}", line):
        break # songs environment ended
      inputRe = re.search(r"\\input\{([^\}]+)\}", line)
      if inputRe:
        song = inputRe.group(1)
        if re.search(r"\.tex$", song) is None:
          song += '.tex'
        index += 1
        with (source.parent/song).open('r') as song_file:
          # TODO: allow more than one song per file
          try:
            print(f"Reading song {song_file.name}")
            songs[-1][1].append(Song(song_file, index))
          except:
            print(f"In song {song_file.name}")
            raise
    return songs

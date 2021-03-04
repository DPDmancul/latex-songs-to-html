# $`\LaTeX`$ Songs to HTML
Convert a $`\LaTeX`$ [Songs](https://www.ctan.org/tex-archive/macros/latex/contrib/songs) book to an HTML page.

Version 0.1.0

## Setup
```py
pip3 install -r requirements.txt
```

## Usage
```py
python3 songs.py source.tex output.html [language [toc_title]]
```
Where
  * `language` is the HTML language code (default "en").
  * `toc_title` is the title of the toc (default "Table of contents").

## Limitations
Only a subset of macros are converted, and there are some extra limitations (e.g. one song per `tex` file).

The converter was tested with this songbook: https://gitlab.com/DPDmancul/nomadi  
Preview: https://dpdmancul.gitlab.io/nomadi/

## License

The code was inspired by  [$`\LaTeX`$ Songs 2 Web](https://gitlab.com/kauron/latexsongs2web/) and so it's licensed under _GNU AGPLv3_

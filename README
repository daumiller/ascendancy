# ascendancy #

Utilities to extract and convert Ascendancy game resources (in Python 3).

## commands ##

- **cob.py** file.cob output_directory
- **font.py** file.fnt file.pal
- **shape.py** file.shp file.pal
- **voice.py** (file.voc | file.raw)

## resouce guide ##

    mkdir cob0 cob1 cob2
    ./cob.py ASCEND00.COB cob0
    ./cob.py ASCEND01.COB cob1
    ./cob.py ASCEND02.COB cob2

    cob0/*.txt - plain text files
     *.dip - plain text diplomacy files

    cob1/data/*.dll - crap
              *.fnt - font files => font.py cob1/data/bifont.fnt cob1/data/game.pal
              *.gif - standard GIFs
              *.haz - shading files (no tool for these guys)
              *.pal - palettes (used by font.py and shape.py for png rendering)
              *.raw - raw PCM sound files => voice.py cob1/data/intro00.raw
              *.shp - shape/image files => shape.py cob1/data/0opening.shp cob1/data/game.pal
              *.tmp - crap? look like SHP files, but don't process correctly...
              *.voc - voice file (or raw PCM data) => voice.py cob1/data/bang01.voc

    cob2/*.tsv - 1/2 TSV/BIN screen-recorded tutorials
         *.bin - 2/2 TSV/BIN screen-recorded tutorials
         data/*.flc - standard AutoDesk FLC animation (convertable with QuickTime)
              *.fnt - another font file => font.py cob2/data/intro.fnt cob1/data/logo.pal
              *.gif - standard GIFs
              *.shp - shape/image files => shape.py cob1/data/0opening.shp cob1/data/game.pal
              *.tmp - crap? look like SHP files, but don't process correctly...

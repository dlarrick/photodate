# photodate
Simple script to manage approximate dates in Exif and some structured tags within UserComment

```
Usage: photodate [options] filename

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -r, --read            
  -C, --copy            copy date and UserComment from src to dest
  -Y YEARRANGE, --yearrange=YEARRANGE
  -y YEAR, --year=YEAR  
  -m MONTH, --month=MONTH
  -d DAY, --day=DAY     
  -p PEOPLE, --people=PEOPLE
  -l LOCATION, --location=LOCATION
  -c COMMENT, --comment=COMMENT
```

I wrote this script because I am digitizing old family photos and have only approximate date information, but want to
record with as much accuracy as I have. It calculates the DateTimeOriginal EXIF field as the midpoint of the date given,
and writes what was provided to an ApproximateDate sub-tag of UserComment. The people, location, and comment are also written
to sub-tags of UserComment if given.

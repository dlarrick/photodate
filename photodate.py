#!/usr/bin/python
""" Utility to set original date & approximate date in EXIF
"""
import optparse
import re
import math
import datetime
import pyexiv2

def validate_options(parser, options):
    """ Validate command-line options
    """
    if options.read:
        return True
    havedate = options.year or options.yearrange
    havecomment = options.comment or options.people or options.location
    if not havedate and not havecomment:
        parser.error("Need year/yearrange or people/location/comment")
    if options.year and options.yearrange:
        parser.error("Specify only year or yearrange, not both")
    if options.yearrange:
        if not validate_yearrange(options.yearrange):
            parser.error("Yearrange should be XXXX-YYYY")
        if options.month or options.day:
            parser.error("Yearrange should be by itself")
    if options.year:
        if not validate_year(options.year):
            parser.error("Year should be XXXX")
    if options.month:
        if not validate_month(options.month):
            parser.error("Invalid month (should be numeric)")
        if not options.year:
            parser.error("Month specified without year")
    if options.day:
        if not options.month:
            parser.error("Day specified without month")
        if not options.year:
            parser.error("Day specified without year")
        if not validate_day(options.year, options.month, options.day):
            parser.error("Invalid day")

    return True

def validate_yearrange(yearrange):
    """ Validate yearrange option, must be XXXX-YYYY with X < Y
    """
    if not re.match('^[0-9]{4}-[0-9]{4}$', yearrange):
        return False
    try:
        year1, year2 = yearrange.split('-')
        if year1 >= year2:
            return False
        return True
    except ValueError:
        return False

def validate_year(year):
    """ Validate year option, must be YYYY
    """
    return re.match('^[0-9]{4}$', year)

def validate_month(month):
    """ Validate month option, must be numeric 0-12
    """
    try:
        monthnum = int(month)
        return monthnum < 13 and monthnum > 0
    except ValueError:
        return False

def validate_day(year, month, day):
    """ Validate day option, must be a day in that month/year
    """
    try:
        datetime.date(int(year), int(month), int(day))
        return True
    except ValueError:
        return False

def make_exif_date(yearrange, year, month, day):
    """ Construct datetime.date object from yearrange or year/month/day
    """
    synyear = 0
    synmonth = 0
    synday = 0
    if yearrange:
        year1, year2 = yearrange.split('-')
        if (int(year2) - int(year1)) % 2 == 1:
            # Odd number of years, use J 1
            synyear = int(math.ceil((float(year2) + float(year1)) / 2))
            synmonth = 1
            synday = 1
        else:
            # Even number of years, use June 1
            synyear = int(math.floor((float(year2) + float(year1)) / 2))
            synmonth = 6
            synday = 1
        trydate = datetime.date(synyear, synmonth, synday)
        return trydate
    if day:
        trydate = datetime.date(int(year), int(month), int(day))
        return trydate
    if month:
        synday = 15
        trydate = datetime.date(int(year), int(month), synday)
        return trydate
    synmonth = 6
    synday = 1
    trydate = datetime.date(int(year), synmonth, synday)
    return trydate

def make_exif_datetime(yearrange, year, month, day):
    """ Construct datetime.datetime object from yearrange or year/month/day
    """
    exif_date = make_exif_date(yearrange, year, month, day)
    return datetime.datetime(exif_date.year, exif_date.month, exif_date.day, 0, 0, 0)

def make_approximate_date(yearrange, year, month, day):
    """ Construct human approximate date string
    """
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    if yearrange:
        return yearrange
    if day:
        return '%s %s, %s' % (months[int(month)], day, year)
    if month:
        return '%s %s' % (months[int(month)], year)
    return year

def do_read(args):
    """ Read and print fields of interest:
    Exif.Photo.DateTimeOriginal
    Exif.Photo.UserComment
    """
    for photo in args:
        metadata = pyexiv2.ImageMetadata(photo)
        metadata.read()
        print photo
        if 'Exif.Photo.DateTimeOriginal' in metadata.exif_keys:
            tag = metadata['Exif.Photo.DateTimeOriginal']
            print 'DateTimeOriginal: %s' % str(tag.value)
        if 'Exif.Photo.UserComment' in metadata.exif_keys:
            tag = metadata['Exif.Photo.UserComment']
            print 'UserComment: %s' % str(tag.value)
        print ''

def assemble_comment(approximate_date, people, location, comment):
    """ Assemble Exif comment from named fields and freeform comment
    """
    result = ''
    first = True
    if comment:
        result += comment
        first = False
    if people:
        if not first:
            result += '\n'
        result += 'People: '
        result += people
        first = False
    if location:
        if not first:
            result += '\n'
        result += 'Location: '
        result += location
        first = False
    if approximate_date:
        if not first:
            result += '\n'
        result += 'ApproximateDate: '
        result += approximate_date
    return result

def main():
    """ Entry point
    """
    parser = optparse.OptionParser(usage="usage: %prog [options] filename")
    parser.add_option('-r', '--read', action='store_true', dest='read')
    parser.add_option('-Y', '--yearrange', action='store', type='string', dest='yearrange')
    parser.add_option('-y', '--year', action='store', type='string', dest='year')
    parser.add_option('-m', '--month', action='store', type='string', dest='month')
    parser.add_option('-d', '--day', action='store', type='string', dest='day')
    parser.add_option('-p', '--people', action='store', type='string', dest='people')
    parser.add_option('-l', '--location', action='store', type='string', dest='location')
    parser.add_option('-c', '--comment', action='store', type='string', dest='comment')
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error("Please supply a photo filename")
    validate_options(parser, options)

    if options.read:
        do_read(args)
        exit(0)

    havedate = options.year or options.yearrange
    approximate_date = ''
    if havedate:
        exif_datetime = make_exif_datetime(
            options.yearrange, options.year, options.month, options.day)
        approximate_date = make_approximate_date(
            options.yearrange, options.year, options.month, options.day)

    final_comment = assemble_comment(
        approximate_date, options.people, options.location, options.comment)
    for photo in args:
        metadata = pyexiv2.ImageMetadata(photo)
        metadata.read()
        metadata['Exif.Photo.UserComment'] = final_comment
        if havedate:
            metadata['Exif.Photo.DateTimeOriginal'] = exif_datetime
        metadata.write()

    do_read(args)

if __name__ == '__main__':
    main()

#!/usr/bin/python

import optparse
import re
import pyexiv2

def validate_options(parser, options):
    if not options.year and not options.yearrange:
        parser.error("Need at least year or yearrange")
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
            parser.error("Month should be numeric")
        if not options.year:
            parser.error("Month specified without year")
    if options.day:
        if not options.month:
            parser.error("Day specified without month")
        if not options.year:
            parser.error("Day specified without year")
        if not validate_day(options.year, options.month, options.day):
            parser.error("Invalid day")

def validate_yearrange(range):
    return re.match('^[0-9]{4}-[0-9]{4}$', range)

def validate_year(year):
    return re.match('^[0-9]{4}$', year)

def validate_month(month):
    try:
        monthnum = int(month)
        return monthnum < 13 and monthnum > 0
    except ValueError:
        return False

def validate_day(year, month, day):
    # FIXME, look at month / leapyear
    try:
        daynum = int(day)
        return daynum < 32 and daynum > 0
    except ValueError:
        return False

def make_exif_date(yearrange, year, month, day):
    return "NYI"

def make_approximate_date(yearrange, year, month, day):
    return "NYI"

def main():
    parser = optparse.OptionParser(usage="usage: %prog [options] filename")
    parser.add_option('-Y', '--yearrange', action='store', type='string', dest='yearrange')
    parser.add_option('-y', '--year', action='store', type='string', dest='year')
    parser.add_option('-m', '--month', action='store', type='string', dest='month')
    parser.add_option('-d', '--day', action='store', type='string', dest='day')
    (options, args) = parser.parse_args()

    print options
    print args

    if len(args) != 1:
        parser.error("Please supply a photo filename")
    validate_options(parser, options)

    exif_date = make_exif_date(options.yearrange, options.year, options.month, options.day)
    approximate_date = make_approximate_date(
        options.yearrange, options.year, options.month, options.day)

    print "exif_date is %s" % str(exif_date)
    print "approximate_date is %s" % approximate_date

if __name__ == '__main__':
    main()

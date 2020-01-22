#!/usr/bin/env bash

set -eu

usage() {
    cat << EOT >&2
$(basename $0): Get/set version ("vYYYYMMDD" string) for CMORised data by
listing version directories (get) or moving files (set) to the appropriate
directory.
  If needed, a new version directory is created. Empty version directories are
removed. When moving files would overwrite existing files, the user is
prompted.
  Note that the script has a safety switch (-m)! If the switch is *not* used on
the command line, it runs in dry-run mode (i.e. no files are moved).

Usage: $(basename $0) -l | -v <version> [-m] DIR

       -l            List versions present in DIR
       -v <version>  Set version to be used for all files
                     <version> must match: v20[0-9][0-9][01][0-9][0-9][0-9]
       -m            Safety switch: actually move files (dry-run if not set)

EOT
}

error() {
    echo "ERROR: $1" >&2
    [ -z ${2+x} ] && exit 99
    exit $2
}

warning() {
    echo "WARNING: $1" >&2
}

while getopts ":lmv:" opt
do
    case "$opt" in
    l)  list=1
        ;;
    m)  move=1
        ;;
    v)  version=$OPTARG
        ;;
    \?) usage
        error "Invalid option: -$OPTARG" 1
        ;;
    :)  error "Option -$OPTARG requires an argument." 2
        ;;
    esac
done
shift $((OPTIND-1))

if [ -z ${version+x} ] && [ -z ${list+x} ]
then
    usage
    error "Either -l or -v must be used" 3
fi

if [ -z ${1+x} ] || [ ! -d $1 ]
then
    usage
    set +u
    error "Missing or invalid directory: '$1'" 4
else
    directory=$1
fi

if [ ! -z ${list+x} ]
then
    for d in $(find $directory -type d -name "v20[0-9][0-9][01][0-9][0-9][0-9]")
    do
        basename $d
    done | sort -u
    exit 0
fi

if [ ! -z ${version+x} ]
then
    [ -z ${move+x} ] && warning "Not moving any files (dry-run mode)"

    [[ $version =~ v20[0-9][0-9][01][0-9]{3}$ ]] || error "Invalid version string '$version'" 5

    for d in $(find $directory -type d -name "v20[0-9][0-9][01][0-9][0-9][0-9]")
    do
        this_version=$(basename $d)
        if [[ ! $this_version =~ $version ]]
        then
            echo "Processing directory '$d'"
            new_version_dir="$(dirname $d)/$version/"
            for f in $d/*.nc
            do
                if [ -z ${move+x} ]
                then
                    echo "Moving: $f --> $new_version_dir"
                else
                    [ -d $new_version_dir ] || mkdir --verbose $new_version_dir
                    mv --interactive --verbose $f $new_version_dir
                fi
            done
            if [ -z ${move+x} ]
            then
                echo "Removing directory: $d"
            else
                rmdir --verbose $d || warning "Directory not empty: '$d'"
            fi
        fi
    done
fi

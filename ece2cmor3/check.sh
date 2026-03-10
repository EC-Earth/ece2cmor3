#!/usr/bin/env bash

set -ue

# defaults
delete_copies=false
submit_new=false
show_usage=false

while getopts 'dsh' opt; do
	case $opt in
		d ) delete_copies=true ;;
		s ) submit_new=true ;;
		h ) show_usage=true ;;
		* ) echo "-$opt undefined"; show_usage=true ;;
	esac
done

shift "$(($OPTIND -1))"

e=$1

if $show_usage; then
	echo 'use with caution'
	exit -1
fi

case $e in
	CD63 ) y1=1951; y2=$((y1+299)) ;;
	CD73 ) y1=2001; y2=$((y1+299)) ;;
	CD74 ) y1=1926; y2=$((y1+299)) ;;
	CD75 ) y1=2051; y2=$((y1+145)) ;;
	CD76 ) y1=2101; y2=$((y1+299)) ;;
        CD78 ) y1=2001; y2=$((y1+99)) ;;
	CD79 ) y1=2101; y2=$((y1+199)) ;;
	CD80 ) y1=2201; y2=$((y1+299)) ;;
	* ) echo "$e years ?"; exit -1 ;;
esac
# for testing
###y2=$((y1+19))

d=/nobackup/rossby27/proj/optimesm/cmorized/$e


# find and delete copies and temporary files
# use ONLY after all years have been processed
echo "copies and temporary files in $d"
for f in $(find $d -type f -regextype posix-extended -not -regex '.*_g.\.nc' -not -regex '.*_[0-9]{4,8}-[0-9]{4,8}\.nc'); do
	echo $f
	$delete_copies && rm -f $f
done


# find years with missing data
ll=''
for y in $(seq $y1 $y2); do
	n=$(find $d -type f -name "*_${y}*nc" | wc -l)
	# there could be more than 391 files on two or more days
	# (to be fixed later with versions.sh)
	if [ $n -lt 391 ]; then
		echo $e $y $n
		# delete old files (CAUTION)
		if $submit_new; then
			find $d -type f -name "*_${y}*nc" -delete
		fi
		ll+=",$((y-y1))"
	fi
done	

if [ -x $ll ]; then
	echo "$e: all years $y1-$y2 look fine, exiting"
	exit 0
fi 

if $submit_new; then
	set -x
	./submit.sh "${ll:1}" $e
	set +x
else
	echo "$e: problem with legs ${ll:1}"
	echo "no new job submitted (run with -s)"
fi

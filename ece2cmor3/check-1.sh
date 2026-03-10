#!/usr/bin/env bash

set -ue

e=$1

# run this first to see if any components haven't been processed (from logfiles)
# run thereafter check.sh for a more thorough check

ifslist=''
nemolist=''
lpjglist=''
co2boxlist=''

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

for y in $(seq $y1 $y2); do
	n=$((y-y1))
	grep 'All files' logfiles/e2c_${e}_ifs_${n}.out 1> /dev/null || ifslist+=",$n"
	grep 'Please review' logfiles/e2c_${e}_co2box_${n}.out 1> /dev/null || co2boxlist+=",$n"
	grep 'Please review' logfiles/e2c_${e}_nemo_${n}.out 1> /dev/null || nemolist+=",$n"
	grep 'Please review' logfiles/e2c_${e}_lpjg_${n}.out 1> /dev/null || lpjglist+=",$n"
done

[ -z $ifslist ] && echo "$e ifs OK" || echo ${ifslist:1}
[ -z $lpjglist ] && echo "$e lpjg OK" || echo ${lpjglist:1}
[ -z $nemolist ] && echo "$e nemo OK" || echo ${nemolist:1}
[ -z $co2boxlist ] && echo "$e co2box OK" || echo ${co2boxlist:1}

if (( 0 == 1 )); then
	set -x
	[ ! -z $ifslist ] && sbatch -a ${ifslist:1}%10 -n 12 -t 6:0:0 -J ${e}-ifs -o logfiles/e2c_${e}_ifs_%a.out launch_cmip6plus.sh $e ifs
	[ ! -z $lpjglist ] && sbatch -a ${lpjglist:1}%10 -n 2 -t 6:00:0 -J ${e}-lpjg -o logfiles/e2c_${e}_lpjg_%a.out launch_cmip6plus.sh $e lpjg
	[ ! -z $nemolist ] && sbatch -a ${nemolist:1}%10 -n 1 -t 6:0:0 -J ${e}-nemo -o logfiles/e2c_${e}_nemo_%a.out launch_cmip6plus.sh $e nemo
	[ ! -z $co2boxlist ] && sbatch -a ${co2boxlist:1}%1 -n 1 -t 15:0 -J ${e}-co2box -o logfiles/e2c_${e}_co2box_%a.out launch_cmip6plus.sh $e co2box
	set +x
fi

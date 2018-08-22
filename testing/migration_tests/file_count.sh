#file: file_count.sh
#usage: $ file_count.sh

#Define the path to logs
path="/Users/aell/terminal/done"


echo "SN/LK - Testing Iteration Step 1 - Transform logs to remove IP addresses"
echo "---"
echo "Case #1 - SDC Log file counts"
echo "---"
echo -n "Jan 16: ";find $path -type f -print | grep '2016-01' | wc -l
echo -n "Feb 16: ";find $path -type f -print | grep '2016-02' | wc -l
echo -n "Mar 16: ";find $path -type f -print | grep '2016-03' | wc -l
echo -n "Apr 16: ";find $path -type f -print | grep '2016-04' | wc -l
echo -n "May 16: ";find $path -type f -print | grep '2016-05' | wc -l
echo -n "Jun 16: ";find $path -type f -print | grep '2016-06' | wc -l
echo -n "Jul 16: ";find $path -type f -print | grep '2016-07' | wc -l
echo -n "Aug 16: ";find $path -type f -print | grep '2016-08' | wc -l
echo -n "Sep 16: ";find $path -type f -print | grep '2016-09' | wc -l
echo -n "Oct 16: ";find $path -type f -print | grep '2016-10' | wc -l
echo -n "Nov 16: ";find $path -type f -print | grep '2016-11' | wc -l
echo -n "Dec 16: ";find $path -type f -print | grep '2016-12' | wc -l
echo -n "Jan 17: ";find $path -type f -print | grep '2017-01' | wc -l
echo -n "Feb 17: ";find $path -type f -print | grep '2017-02' | wc -l
echo -n "Mar 17: ";find $path -type f -print | grep '2017-03' | wc -l
echo -n "Apr 17: ";find $path -type f -print | grep '2017-04' | wc -l
echo -n "May 17: ";find $path -type f -print | grep '2017-05' | wc -l
echo -n "Jun 17: ";find $path -type f -print | grep '2017-06' | wc -l
echo -n "Jul 17: ";find $path -type f -print | grep '2017-07' | wc -l
echo -n "Aug 17: ";find $path -type f -print | grep '2017-08' | wc -l
echo -n "Sep 17: ";find $path -type f -print | grep '2017-09' | wc -l
echo -n "Oct 17: ";find $path -type f -print | grep '2017-10' | wc -l
echo -n "Nov 17: ";find $path -type f -print | grep '2017-11' | wc -l
echo -n "Dec 17: ";find $path -type f -print | grep '2017-12' | wc -l
echo "==============="
echo -n "Total: ";find $path -type f -print | grep '.log' | wc -l

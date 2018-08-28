# File:   c2_s2_unique_ips.sh
# Usage:  $ perl ./c2_s2_unique_ips.pl *.log
#         - run in the folder containing logs.

# prints every unique IP address per line over all input SDC log files

my %ips;
 
while (<>) {
    next unless /(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/;
    $ips{$1} = 1;
}
 
for (keys(%ips)) {
    print "$_\n";
}

#!/usr/bin/perl

opendir CURRDIR, "." or die "Could not open specified directory:$!";
my @files = grep /.+\.xaif$/, readdir CURRDIR;
close CURRDIR;

foreach $file (@files) {
 if (-e "complete/$file") {
   system("bk edit complete/$file");
   unlink "complete/$file";
 } 
 $command = "SAX2Print -f -p $file > complete/$file";
 print "$command\n";
 system($command);
}



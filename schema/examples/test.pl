#!/usr/bin/perl

opendir CURDIR, '.' or die "Could not open specified directory: $!";
@allfiles = grep /^\w+\.xaif/,readdir CURDIR;
close CURDIR;

foreach $file (@allfiles) {
  print "\n\n==================================================================================";
  print "\nTesting $file";
  print "\n==================================================================================\n";
  system("SAX2Print $file");
  print "\n";
}

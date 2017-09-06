#!/usr/local/bin/python


#
# Script for handling .mobileprovision files for iOS
# 
#

import os
from os.path import expanduser
import subprocess
import plistlib
import click
from operator import itemgetter

path = os.path.expanduser("~") + "/Library/MobileDevice/Provisioning Profiles/"
if os.getenv("MP_HOME"):
    path = os.getenv("MP_HOME")

@click.group()
@click.option('-b','--bundleID',required=False,help="Search by BundleID")
def cli(bundleid):
    """A tool for working with mobile provisioning profiles"""


@click.option('-b','--bundleID',required=False,help="Search by BundleID")
@click.option('-v','--verbose',required=False,help="Verbose - will output filename, Name, AppIDName, and Bundle ID")
@click.option('-d','--distribution-only',required=False,is_flag=True,default=False,help="Show Distribution Profiles Only")
@click.command()
def list(bundleid,verbose,distribution_only):
    """List all mobile provisioning profiles"""
    profiles = []
    profile_list = getAllProfiles()
    for profile in profile_list:
        
        profile_type = "Distribution" if isDistribution(profile) else "Development"
        profile["type"] = profile_type
        if not bundleid is None:
            if bundleid in profile["Entitlements"]["application-identifier"]:
                profiles.append(profile)
        else:
            profiles.append(profile)

    if len(profiles) == 0:
        print(click.style("Could not find specified bundle ID",fg='red'))
    else:
        for profile in profiles:
            print(click.style(profile["Name"],fg="green") + "\t" + click.style(profile["Entitlements"]["application-identifier"],fg='blue') + "\t" + click.style(profile["type"],fg='magenta'))



@click.command()
@click.option('-n','--name',required=True,help="Search by Name")
@click.option('-b','--bundleid',required=False,help="Search by BundleID")
@click.option('-e','--entitlements-only',required=False,is_flag=True,default=False,help="Show Entitlements Only")
def view(name,bundleid,entitlements_only):
    """View a specific mobile provisioning profile by name or bundleID"""

    if (name is None and bundleid is None):
        print(click.style("Please specify -b bundleID or -n name",fg='red'))

    profile_list = getAllProfiles()
    for profile in profile_list:
        if bundleid is not None:
            if profile["Entitlements"]["application-identifier"] == bundleid:
                foundProfile = True
                if entitlements_only == True:
                    print(profile["Entitlements"])
                else:
                    runCmd(['security', 'cms', '-D', '-i', path + profile["filename"]])
                break
            
        elif (name is not None):
            if profile["Name"] == name:
                foundProfile = True
                if entitlements_only == True:
                    print(profile["Entitlements"])
                else:
                    runCmd(['security', 'cms', '-D', '-i', path + profile["filename"]])
                break

    if not foundProfile:
        print(click.style("Profile Name must be an exact match, run the list command to see a list of profile names",fg='red'))


@click.command()
@click.argument("name",required=True)
def profile_path(name):
    """Returns a full file path based on the name. Userful for chaining with other commands"""
    
    profile_list = getAllProfiles()
    for profile in profile_list:
        if name == profile["Name"]:
            print path + profile["filename"]
            return

@click.command()
@click.option('--all',help="Delete all provisioning profiles")
def delete(all):
    '''Delete a provisioning profile'''



'''
Helpler Methods
'''

def isDistribution(profile):
    isDistribution = False
    try:
        if( profile["ProvisionsAllDevices"] == True):
            isDistribution = True

    except :
        isDistribution = False
    return isDistribution
        

def getAllFiles():
    global path
    filelist = os.listdir(path)
    if len(filelist) > 0:
        filelist.remove('.DS_Store')
    
    if(len(filelist) ==0):
        print(click.style("Cannot find any mobile provisioning profiles",fg='red'))
        return None
    else:
        return filelist

def getAllProfiles():
    global path
    filelist = getAllFiles()
    profiles = []
    for file in filelist:
        mobileprovision_path = path  + file   
        profile = read_mobileprovision(mobileprovision_path)
        profile["filename"] = file
        profiles.append(profile)

    profiles.sort(key=itemgetter('Name'))
    return profiles


def runCmd(cmdArray):
    p = subprocess.Popen(cmdArray,stdout=subprocess.PIPE)
    output = p.communicate()[0]
    print(output)

def read_mobileprovision(mobileprovision_path):
    # From http://stackoverflow.com/questions/6398364/parsing-mobileprovision-files-in-bash/10490095#10490095
    return plistlib.readPlist(subprocess.Popen(['security', 'cms', '-D', '-i', mobileprovision_path], stdout=subprocess.PIPE).stdout)

'''
Add Commands to CLI
'''
cli.add_command(list)
cli.add_command(view)
cli.add_command(profile_path)
cli.add_command(delete)

if __name__ == '__main__':
    cli()
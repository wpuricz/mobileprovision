#!/usr/bin/env python


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
    """A tool for working with iOS provisioning profiles"""

'''
List Command
'''
@click.argument("name",required=False)
@click.option('-b','--bundleID',required=False,help="Search by BundleID")
@click.option('-d','--distribution-only',required=False,is_flag=True,default=False,help="Show Distribution Profiles Only")
@click.command()
def list(name,bundleid,distribution_only):
    """List all mobile provisioning profiles"""
    mode = SearchMode.Name
    if name is not None:
        mode = SearchMode.Name
    elif bundleid is not None:
        mode = SearchMode.BundleID
    else:
        mode = SearchMode.All
    
    if distribution_only == True:
        print(click.style("-d not implemented yet",fg='red'))
        return
    profiles = []
    profile_list = getAllProfiles()
    for profile in profile_list:
        
        profile_type = "Distribution" if isDistribution(profile) else "Development"
        profile["type"] = profile_type

        if mode == SearchMode.Name:
            if name in profile["Name"]:
                profiles.append(profile)

        elif mode == SearchMode.BundleID:
            if bundleid in profile["Entitlements"]["application-identifier"]:
                profiles.append(profile)

        elif mode == SearchMode.All:
            profiles.append(profile)
        else:
            print(click.style("Could not determine search mode",fg='red'))
            return

    if len(profiles) == 0:
        print(click.style("No profiles found",fg='red'))
    else:
        for profile in profiles:
            print(click.style(profile["Name"],fg="green") + "\t" + click.style(profile["Entitlements"]["application-identifier"],fg='blue') + "\t" + click.style(profile["type"],fg='magenta') + " " + profile["filename"])


'''
View Command
'''
@click.command()
@click.argument("name",required=False)
@click.option('-b','--bundleid',required=False,help="Search by BundleID")
@click.option('-e','--entitlements-only',required=False,is_flag=True,default=False,help="Show Entitlements Only")
def view(name,bundleid,entitlements_only):
    """View a specific iOS provisioning profile by name or bundleID"""
    mode = None
    if name is not None:
        mode = SearchMode.Name
    elif bundleid is not None:
        mode = SearchMode.BundleID
    else:
        print(click.style("Please specify -b bundleID or -n name",fg='red'))
        return

    foundProfile = False
    profile_list = getAllProfiles()
    for profile in profile_list:
        if mode == SearchMode.BundleID:
            if profile["Entitlements"]["application-identifier"] == bundleid:
                foundProfile = True
                if entitlements_only == True:
                    print(profile["Entitlements"])
                else:
                    runCmd(['security', 'cms', '-D', '-i', path + profile["filename"]])
                break
            
        elif mode == SearchMode.Name:
            if profile["Name"] == name:
                foundProfile = True
                if entitlements_only == True:
                    print(profile["Entitlements"])
                else:
                    runCmd(['security', 'cms', '-D', '-i', path + profile["filename"]])
                break

    if not foundProfile:
        print(click.style("Profile Name must be an exact match, run the list command to see a list of profile names",fg='red'))


'''
Profile Path Command
'''
@click.command()
@click.argument("name",required=True)
def profile_path(name):
    """Returns a full file path based on the name. Userful for chaining with other commands"""
    
    profile_list = getAllProfiles()
    for profile in profile_list:
        if name == profile["Name"]:
            print path + profile["filename"]
            return

'''
Delete Command
'''
@click.command()
@click.option('--all',help="Delete all provisioning profiles")
def delete(all):
    """Delete a provisioning profile"""



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
        print(click.style("Cannot find any provisioning profiles",fg='red'))
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
        print(profile["filename"])
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

class SearchMode:
    Name, BundleID, All = range(3)

'''
Add Commands to CLI
'''
cli.add_command(list)
cli.add_command(view)
cli.add_command(profile_path)
cli.add_command(delete)

if __name__ == '__main__':
    cli()
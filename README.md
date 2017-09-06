### Tool for working with iOS .mobileprovision Files
This is a tool for working with .mobileprovision files in iOS

Status: Work in Progress, not all methods are implemented

Dependencies:

    pip install click

By default it will search the directory ${HOME}/Library/MobileDevice/Provisioning Profiles/ where XCode currently stores the profiles

if you need to change the directory set an environment variable called MP_HOME to your path

    export $MP_HOME=/path/to/your/directory

#### Listing 

    mp list                         # Lists all mobile provision profiles
    mp list "My app name"           # Lists by app name
    mp list -b "com.mycompany.app"  # List by bundle ID 

#### Viewing
View the entire raw mobile provision by app name, bundle ID, or filename. BundleID or name will need to be an exact match. App name can be found by using the list command.

    mp view -n "My app" 
    mp view -b "com.company.app"    

#### Delete 
Todo


### Credit
Credit to the answer in this stack overflow blog post for parsing files
http://stackoverflow.com/questions/6398364/parsing-mobileprovision-files-in-bash/10490095#10490095
# /usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import datetime
import email.mime.multipart
import email.mime.text
import ftplib
import getpass
import optparse
import os
import smtplib
import sys

# ipa相关参数
ipaRootDir = "/Users/" + getpass.getuser() + "/Desktop/"
ipaTargetName = None
ipaFileDir = datetime.datetime.today().strftime(
    "%Y-%m-%d-%H-%M-%S")

# email参数
emailFromUser = None
emailToUser = None
emailPassword = None
emailHost = None


def gitPull():
    print('*========================*')
    print('Git Pull Start')
    os.system('git pull origin dev')


def mkdir():
    if not os.path.exists(ipaRootDir + ipaFileDir):
        os.system('cd %s;mkdir %s' % (ipaRootDir, ipaFileDir))


def getConfig():
    if not os.path.exists('Setting.ini'):
        print('*========================*')
        print('Please Input Your Setting')
        setConfig('Setting.ini')
    else:
        try:
            global emailFromUser
            global emailToUser
            global emailPassword
            global emailHost

            config = configparser.ConfigParser()
            config.read('Setting.ini')
            emailFromUser = config.get('Settings', 'emailFromUser')
            emailToUser = config.get('Settings', 'emailToUser')
            emailPassword = config.get('Settings', 'emailPassword')
            emailHost = config.get('Settings', 'emailHost')

        except Exception as e:
            raise e
        finally:
            print('*========================*')
            print('Your Setting:')
            print('emailFromUser:' + emailFromUser)
            print('emailToUser:' + emailToUser)
            print('emailPassword:' + emailPassword)
            print('emailHost:' + emailHost)
    global ipaFileDir
    ipaFileDir += ('-' + ipaTargetName + '/')


def setConfig(path):
    global emailFromUser
    global emailToUser
    global emailPassword
    global emailHost

    emailFromUser = input('Input EmailFromUser:')
    emailToUser = input('Input EmailToUser:')
    emailPassword = input('Input EmailPassword:')
    emailHost = input('Input EmailHost:')

    if emailFromUser == '' or emailToUser == '' or emailPassword == '' or emailHost == '':
        raise ValueError('Please Enter Valid Setting')
        sys.exit(0)

    config = configparser.ConfigParser()
    config.add_section('Settings')
    config.set('Settings', 'emailFromUser', emailFromUser)
    config.set('Settings', 'emailToUser', emailToUser)
    config.set('Settings', 'emailPassword', emailPassword)
    config.set('Settings', 'emailHost', emailHost)

    try:
        os.system('touch Setting.ini')
        with open(path, 'w') as fileHandler:
            config.write(fileHandler)
    except Exception as e:
        raise e


def getTargetName():
    files = os.listdir(os.getcwd())
    for file in files:
        if '.xcodeproj' in file:
            name, extend = file.split('.')
            global ipaTargetName
            ipaTargetName = name
    print('*========================*')
    print('TargetName:%s' % (ipaTargetName))


def cleanProject():
    print('*========================*')
    print('Clean Project Start')
    os.system('xcodebuild -workspace %(x)s.xcworkspace -scheme %(x)s clean' %
              {'x': ipaTargetName})
    input('Press Any Key To Continue')


def buildProject():
    print('*========================*')
    print('Build Project Start')
    os.system('xcodebuild -workspace %(x)s.xcworkspace -scheme %(x)s build' %
              {'x': ipaTargetName})
    input('Press Any Key To Continue')


def archiveProject():
    print('*========================*')
    print('Archive Project Start')
    os.system('xcodebuild -workspace %(x)s.xcworkspace -scheme %(x)s archive -configuration Release -archivePath %(y)s.xcarchive' %
              {'x': ipaTargetName, 'y': ipaRootDir + ipaFileDir + ipaTargetName})
    input('Press Any Key To Continue')
    os.system('xcodebuild -exportArchive -archivePath %(x)s.xcarchive -exportPath %(x)s.ipa -exportFormat IPA' %
              {'x': ipaRootDir + ipaFileDir + ipaTargetName})
    input('Press Any Key To Continue')


def main():
    print('*========================*')
    print('Create Ipa Start')
    getTargetName()
    getConfig()
    mkdir()
    # gitPull()
    cleanProject()
    buildProject()
    archiveProject()

if __name__ == '__main__':
    main()

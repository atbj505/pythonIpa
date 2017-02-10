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

# ipa参数
ipaRootDir = "/Users/" + getpass.getuser() + "/Desktop/"
ipaFileDir = datetime.datetime.today().strftime(
    "%Y-%m-%d-%H-%M-%S")

# email参数
emailFromUser = None
emailToUser = None
emailPassword = None
emailHost = None
emailBodyText = None

# 项目参数
projectTargetName = None


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
    ipaFileDir += ('-' + projectTargetName + '/')


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


def removeConfig():
    os.system('rm Setting.ini')


def setOptParse():
    p = optparse.OptionParser()

    p.add_option("-m", "--message", action="store_true",
                 default=None, help="enter email body text")
    p.add_option("-r", "--remove", action="store_true",
                 default=None, help="remove config file")

    options, arguments = p.parse_args()

    if options.message and len(arguments):
        global emailBodyText
        emailBodyText = ''.join(arguments)
    else:
        raise ValueError('Please Enter The Email Body Text')

    if options.remove:
        removeConfig()


def getTargetName():
    dirs = os.listdir(os.getcwd())
    global projectTargetName

    for file in dirs:
        if '.xcodeproj' in file:
            name, extend = file.split('.')
            projectTargetName = name

    if not projectTargetName:
        raise Exception('Can Not Find .xcodeproj file')
    print('*========================*')
    print('TargetName:%s' % (projectTargetName))


def cleanProject():
    print('*========================*')
    print('Clean Project Start')
    os.system('xcodebuild -workspace %(x)s.xcworkspace -scheme %(x)s clean' %
              {'x': projectTargetName})
    input('Press Any Key To Continue')


def buildProject():
    print('*========================*')
    print('Build Project Start')
    os.system('xcodebuild -workspace %(x)s.xcworkspace -scheme %(x)s build' %
              {'x': projectTargetName})
    input('Press Any Key To Continue')


def archiveProject():
    print('*========================*')
    print('Archive Project Start')
    os.system('xcodebuild -workspace %(x)s.xcworkspace -scheme %(x)s archive -configuration Release -archivePath %(y)s.xcarchive' %
              {'x': projectTargetName, 'y': ipaRootDir + ipaFileDir + projectTargetName})
    input('Press Any Key To Continue')
    os.system('xcodebuild -exportArchive -archivePath %(x)s.xcarchive -exportPath %(x)s.ipa -exportFormat IPA' %
              {'x': ipaRootDir + ipaFileDir + projectTargetName})
    input('Press Any Key To Continue')


def sendMail(to_addr, from_addr, subject,  body_text):
    print('*========================*')
    print('Send Mail Start')
    msg = email.mime.multipart.MIMEMultipart()
    msg['from'] = from_addr
    msg['to'] = ', '.join(to_addr)
    msg['subject'] = subject

    print(msg['to'])

    txt = email.mime.text.MIMEText(body_text)
    msg.attach(txt)

    server = smtplib.SMTP('mail.idengyun.com')
    server.login(from_addr, emailPassword)
    server.sendmail(from_addr, to_addr, str(msg))
    server.quit()

    input('Press Any Key To Continue')


def main():
    print('*========================*')
    print('Create Ipa Start')
    setOptParse()
    getTargetName()
    getConfig()
    mkdir()
    # gitPull()
    cleanProject()
    buildProject()
    archiveProject()
    sendMail(emailToUser, emailFromUser, ipaFileDir, emailBodyText)

if __name__ == '__main__':
    main()

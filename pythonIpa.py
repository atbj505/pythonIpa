# /usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import datetime
import email.mime.image
import email.mime.multipart
import email.mime.text
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
projectChangeLog = None
isWorkSpace = False


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
    p.add_option("-c", "--changelog", action="store_true",
                 default=None, help="enter changelog")

    options, arguments = p.parse_args()

    if options.message and len(arguments):
        global emailBodyText
        emailBodyText = ''.join(arguments)
    # else:
    #     raise ValueError('Please Enter The Email Body Text')

    if options.remove:
        removeConfig()

    if options.changelog and len(arguments):
        global projectChangeLog
        projectChangeLog = ''.join(arguments)
    else:
        raise ValueError('Please Enter The ChangeLog')


def getTargetName():
    dirs = os.listdir(os.getcwd())
    global projectTargetName

    for file in dirs:
        if '.xcodeproj' in file:
            name, extend = file.split('.')
            projectTargetName = name

        if '.xcworkspace' in file:
            global isWorkSpace
            isWorkSpace = True

    if not projectTargetName:
        raise Exception('Can Not Find .xcodeproj file')
    print('*========================*')
    print('TargetName:%s' % (projectTargetName))


def cleanProject():
    print('*========================*')
    print('Clean Project Start')
    if isWorkSpace:
        os.system('xcodebuild -workspace %(x)s.xcworkspace -scheme %(x)s clean' %
                  {'x': projectTargetName})
    else:
        os.system('xcodebuild clean')
    input('Press Any Key To Continue')


def buildProject():
    print('*========================*')
    print('Build Project Start')
    if isWorkSpace:
        os.system('xcodebuild -workspace %(x)s.xcworkspace -scheme %(x)s build' %
                  {'x': projectTargetName})
    else:
        os.system('xcodebuild build')
    input('Press Any Key To Continue')


def archiveProject():
    print('*========================*')
    print('Archive Project Start')
    if isWorkSpace:
        os.system('fir build_ipa %(x)s.xcworkspace -o %(y)s -w -S %(x)s' %
                  {'x': projectTargetName, 'y': ipaFileDir})
    else:
        os.system('fir build_ipa %(x)s.xcworkspace -o %(y)s' %
                  {'x': projectTargetName, 'y': ipaFileDir})
    input('Press Any Key To Continue')


def uploadToFir():
    print('*========================*')
    print('Archive Project Start')
    dirs = os.listdir(ipaFileDir)
    ipaPath = None
    for file in dirs:
        if '.ipa' in file:
            ipaPath = ipaFileDir + '/' + file
    os.system('fir publish %(x)s -c "%(y)s" -Q' %
              {'x': ipaPath, 'y': projectChangeLog})

    input('Press Any Key To Continue')


def sendMail(to_addr, from_addr, subject, body_text):
    print('*========================*')
    print('Send Mail Start')
    msg = email.mime.multipart.MIMEMultipart()
    msg['from'] = from_addr
    msg['to'] = to_addr
    msg['subject'] = subject

    print(msg['to'])

    txt = email.mime.text.MIMEText(body_text + '\n' + projectChangeLog)
    msg.attach(txt)

    with open('fir-' + projectTargetName + '.png', 'r') as target:
        image = email.mine.image.MIMEImage(fp.read())
        msg.attach(image)

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
    gitPull()
    cleanProject()
    buildProject()
    archiveProject()
    uploadToFir()
    sendMail(emailToUser, emailFromUser, ipaFileDir, emailBodyText)

if __name__ == '__main__':
    main()

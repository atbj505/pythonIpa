# -*- coding: utf-8 -*-

import configparser
import datetime
import email.encoders
import email.mime.base
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
    input('Press Any Key To Continue')


def mkdir():
    if not os.path.exists(ipaRootDir + ipaFileDir):
        os.system('cd %s;mkdir %s' % (ipaRootDir, ipaFileDir))
    os.system("chmod -R 777 %s" % ipaRootDir + ipaFileDir)


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
        emailBodyText = arguments[0]
    # else:
    #     raise ValueError('Please Enter The Email Body Text')

    if options.remove:
        removeConfig()

    if options.changelog and len(arguments):
        global projectChangeLog
        projectChangeLog = arguments[1]
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
                  {'x': projectTargetName, 'y': ipaRootDir + ipaFileDir})
    else:
        os.system('fir build_ipa %(x)s.xcworkspace -o %(y)s' %
                  {'x': projectTargetName, 'y': ipaRootDir + ipaFileDir})
    input('Press Any Key To Continue')


def uploadToFir():
    print('*========================*')
    print('UploadToFir Project Start')
    dirs = os.listdir(ipaRootDir + ipaFileDir)
    ipaPath = None
    for file in dirs:
        if '.ipa' in file:
            ipaPath = ipaRootDir + ipaFileDir + file
            os.system('fir publish %(x)s -c "%(y)s" -Q' %
                      {'x': ipaPath, 'y': projectChangeLog})
            break

    input('Press Any Key To Continue')


def sendMail(to_addr, from_addr, subject, body_text):
    print('*========================*')
    print('Send Mail Start')
    msg = email.mime.multipart.MIMEMultipart()
    msg['from'] = from_addr
    msg['to'] = to_addr
    msg['subject'] = subject

    print('To:', msg['to'])

    txt = email.mime.text.MIMEText(body_text + '\n' + projectChangeLog)
    msg.attach(txt)

    dirs = os.listdir(ipaRootDir + ipaFileDir)

    for file in dirs:
        if '.png' in file:
            with open(ipaRootDir + ipaFileDir + file, 'rb') as fileHandler:
                # image = email.mime.image.MIMEImage(fileHandler.read())
                # image.add_header('Content-ID', 'image1')
                # msg.attach(image)
                image = email.mime.base.MIMEBase('image', 'png', filename=file)
                image.add_header('Content-Disposition',
                                 'attachment', filename=file)
                image.add_header('Content-ID', '<0>')
                image.add_header('X-Attachment-Id', '0')
                image.set_payload(fileHandler.read())
                email.encoders.encode_base64(image)
                msg.attach(image)
            break

    server = smtplib.SMTP(emailHost)
    server.login(from_addr, emailPassword)
    server.sendmail(from_addr, to_addr.split(','), str(msg))
    server.quit()

    print('Create Ipa Finish')
    print('*========================*')


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

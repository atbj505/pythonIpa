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

keychainPassword = None
isExcuteStepByStep = False


def gitPull():
    print('*========================*')
    print('Git Pull Start')
    os.system('git pull origin dev')
    if isExcuteStepByStep:
        input('Press Any Key To Continue')


def mkdir():
    if not os.path.exists(ipaRootDir + ipaFileDir):
        os.system('cd %s;mkdir %s' % (ipaRootDir, ipaFileDir))
    os.system("chmod -R 777 %s" % ipaRootDir + ipaFileDir)


def keychainUnlock():
    os.system("security unlock-keychain -p '%s' %s" %
              (keychainPassword, "~/Library/Keychains/login.keychain"))


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
            global keychainPassword

            config = configparser.ConfigParser()
            config.read('Setting.ini')
            emailFromUser = config.get('Settings', 'emailFromUser')
            emailToUser = config.get('Settings', 'emailToUser')
            emailPassword = config.get('Settings', 'emailPassword')
            emailHost = config.get('Settings', 'emailHost')
            keychainPassword = config.get('Settings', 'keychainPassword')

        except Exception as e:
            raise e
        finally:
            print('*========================*')
            print('Your Setting:')
            print('emailFromUser:' + emailFromUser)
            print('emailToUser:' + emailToUser)
            print('emailHost:' + emailHost)
    global ipaFileDir
    ipaFileDir += ('-' + projectTargetName + '/')


def setConfig(path):
    global emailFromUser
    global emailToUser
    global emailPassword
    global emailHost
    global keychainPassword

    emailFromUser = input('Input EmailFromUser:')
    emailToUser = input('Input EmailToUser:')
    emailPassword = input('Input EmailPassword:')
    emailHost = input('Input EmailHost:')
    keychainPassword = input('Input KeychainPassword:')

    if emailFromUser == '' or emailToUser == '' or emailPassword == '' or emailHost == '':
        raise ValueError('Please Enter Valid Setting')

    config = configparser.ConfigParser()
    config.add_section('Settings')
    config.set('Settings', 'emailFromUser', emailFromUser)
    config.set('Settings', 'emailToUser', emailToUser)
    config.set('Settings', 'emailPassword', emailPassword)
    config.set('Settings', 'emailHost', emailHost)
    config.set('Settings', 'keychainPassword', keychainPassword)

    try:
        os.system('touch Setting.ini')
        with open(path, 'w') as fileHandler:
            config.write(fileHandler)
    except Exception as e:
        raise e


def removeConfig():
    if 'Setting.ini' in os.listdir():
        os.system('rm Setting.ini')


def setOptParse():
    p = optparse.OptionParser()

    p.add_option("-m", "--message", action="store",
                 default=None, help="enter email body text")
    p.add_option("-r", "--remove", action="store_true",
                 default=None, help="remove config file")
    p.add_option("-c", "--changelog", action="store",
                 default=None, help="enter changelog")
    p.add_option("-s", "--step", action="store_true",
                 default=None, help="excute step by step")

    options, arguments = p.parse_args()

    if options.message:
        global emailBodyText
        emailBodyText = options.message

    if options.remove:
        removeConfig()

    if options.changelog:
        global projectChangeLog
        projectChangeLog = options.changelog
    else:
        raise ValueError('Please Enter The ChangeLog')

    if options.step:
        global isExcuteStepByStep
        isExcuteStepByStep = True


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
    if isExcuteStepByStep:
        input('Press Any Key To Continue')


def buildProject():
    print('*========================*')
    print('Build Project Start')
    if isWorkSpace:
        os.system('xcodebuild -workspace %(x)s.xcworkspace -scheme %(x)s build' %
                  {'x': projectTargetName})
    else:
        os.system('xcodebuild build')

    if isExcuteStepByStep:
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

    if isExcuteStepByStep:
        input('Press Any Key To Continue')


def uploadToFir():
    print('*========================*')
    print('UploadToFir Project Start')
    dirs = os.listdir(ipaRootDir + ipaFileDir)
    downloadUrl = None
    for file in dirs:
        if '.ipa' in file:
            ipaPath = ipaRootDir + ipaFileDir + file
            ret = os.popen('fir publish %(x)s -c "%(y)s" -Q' %
                           {'x': ipaPath, 'y': projectChangeLog})
            for info in ret.readlines():
                if "Published succeed" in info:
                    downloadUrl = info[info.find('http'):]
                    break
            break
    return downloadUrl


def sendMail(to_addr, from_addr, subject, body_text, downloadUrl):
    print('*========================*')
    print('Send Mail Start')
    msg = email.mime.multipart.MIMEMultipart()
    msg['from'] = from_addr
    msg['to'] = to_addr
    msg['subject'] = subject

    print('To:', msg['to'])

    txt = email.mime.text.MIMEText(
        body_text + '\n' + projectChangeLog + '\n' + downloadUrl)
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
    # 获取参数
    setOptParse()
    # 获取项目名称
    getTargetName()
    # 获取配置文件
    getConfig()
    # 生成打包文件所在文件夹
    mkdir()
    # 解锁钥匙串
    keychainUnlock()
    # 获取最新代码
    gitPull()
    # 清理工程
    cleanProject()
    # 编译
    buildProject()
    # 打包
    archiveProject()
    # 上传到fir
    downloadUrl = uploadToFir()
    # 发送邮件
    sendMail(emailToUser, emailFromUser,
             ipaFileDir, emailBodyText, downloadUrl)

if __name__ == '__main__':
    main()

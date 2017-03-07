#!/usr/bin/env python3
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


class Package():
    def __init__(self):
        # email参数
        self.emailFromUser = None
        self.emailToUser = None
        self.emailPassword = None
        self.emailHost = None
        self.emailBodyText = None
        # 项目参数
        self.projectTargetName = None
        self.projectChangeLog = None
        self.isWorkSpace = False

        self.keychainPassword = None
        self.isExcuteStepByStep = False

    def gitPull(self):
        print('*========================*')
        print('Git Pull Start')
        os.system('git pull origin dev')
        if self.isExcuteStepByStep:
            input('Press Any Key To Continue')

    def mkdir(self):
        if not os.path.exists(ipaRootDir + ipaFileDir):
            os.system('cd %s;mkdir %s' % (ipaRootDir, ipaFileDir))
        os.system("chmod -R 777 %s" % ipaRootDir + ipaFileDir)

    def keychainUnlock(self):
        os.system("security unlock-keychain -p '%s' %s" %
                  (self.keychainPassword, "~/Library/Keychains/login.keychain"))

    def getConfig(self):
        if not os.path.exists('Setting.ini'):
            print('*========================*')
            print('Please Input Your Setting')
            self.setConfig('Setting.ini')
        else:
            try:
                config = configparser.ConfigParser()
                config.read('Setting.ini')
                self.emailFromUser = config.get('Settings', 'emailFromUser')
                self.emailToUser = config.get('Settings', 'emailToUser')
                self.emailPassword = config.get('Settings', 'emailPassword')
                self.emailHost = config.get('Settings', 'emailHost')
                self.keychainPassword = config.get(
                    'Settings', 'keychainPassword')

            except Exception as e:
                raise e
            finally:
                print('*========================*')
                print('Your Setting:')
                print('emailFromUser:' + self.emailFromUser)
                print('emailToUser:' + self.emailToUser)
                print('emailHost:' + self.emailHost)
        global ipaFileDir
        ipaFileDir += ('-' + self.projectTargetName + '/')

    def setConfig(self, path):
        self.emailFromUser = input('Input EmailFromUser:')
        self.emailToUser = input('Input EmailToUser:')
        self.emailPassword = input('Input EmailPassword:')
        self.emailHost = input('Input EmailHost:')
        self.keychainPassword = input('Input KeychainPassword:')

        if self.emailFromUser == '' or self.emailToUser == '' or self.emailPassword == '' or self.emailHost == '':
            raise ValueError('Please Enter Valid Setting')

        config = configparser.ConfigParser()
        config.add_section('Settings')
        config.set('Settings', 'emailFromUser', self.emailFromUser)
        config.set('Settings', 'emailToUser', self.emailToUser)
        config.set('Settings', 'emailPassword', self.emailPassword)
        config.set('Settings', 'emailHost', self.emailHost)
        config.set('Settings', 'keychainPassword', self.keychainPassword)

        try:
            os.system('touch Setting.ini')
            with open(path, 'w') as fileHandler:
                config.write(fileHandler)
        except Exception as e:
            raise e

    def removeConfig(self):
        if 'Setting.ini' in os.listdir():
            os.system('rm Setting.ini')

    def setOptParse(self):
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
            self.emailBodyText = options.message

        if options.remove:
            removeConfig()

        if options.changelog:
            self.projectChangeLog = options.changelog
        else:
            raise ValueError('Please Enter The ChangeLog')

        if options.step:
            self.isExcuteStepByStep = True

    def getTargetName(self):
        dirs = os.listdir(os.getcwd())

        for file in dirs:
            if '.xcodeproj' in file:
                name, extend = file.split('.')
                self.projectTargetName = name

            if '.xcworkspace' in file:
                self.isWorkSpace = True

        if not self.projectTargetName:
            raise Exception('Can Not Find .xcodeproj file')
        print('*========================*')
        print('TargetName:%s' % (self.projectTargetName))

    def getTargetVersion(self):
        def plistBuddy(plistFilePath):
            plistFilePath = plistFilePath.replace(' ', '\\ ')
            ret = os.popen('/usr/libexec/PlistBuddy -c "Print CFBundleShortVersionString" %s' %
                           plistFilePath)
            projectVersion = ret.readline().replace('\n', '')

            ret = os.popen('/usr/libexec/PlistBuddy -c "Print CFBundleDisplayName" %s' %
                           plistFilePath)
            projectDisplayName = ret.readline().replace('\n', '')

            ret = os.popen('/usr/libexec/PlistBuddy -c "Print CFBundleVersion" %s' %
                           plistFilePath)
            projectBuildVersion = ret.readline().replace('\n', '')

            return (projectDisplayName, projectVersion, projectBuildVersion)

        rootDirs = os.listdir('./%s' % self.projectTargetName)
        plistFilePath = None
        for subDir in rootDirs:
            if "Info.plist" in subDir:
                plistFilePath = ('./%s/Info.plist' % self.projectTargetName)
                return plistBuddy(plistFilePath)
            elif os.path.isdir('./%s/%s' % (self.projectTargetName, subDir)):
                childDirs = os.listdir('./%s/%s' %
                                       (self.projectTargetName, subDir))
                for subChildDirs in childDirs:
                    if "Info.plist" in subChildDirs:
                        plistFilePath = ('./%s/%s/Info.plist' %
                                         (self.projectTargetName, subDir))
                        return plistBuddy(plistFilePath)

    def cleanProject(self):
        print('*========================*')
        print('Clean Project Start')
        if self.isWorkSpace:
            os.system('xcodebuild -workspace %(x)s.xcworkspace -scheme %(x)s clean' %
                      {'x': self.projectTargetName})
        else:
            os.system('xcodebuild clean')
        if self.isExcuteStepByStep:
            input('Press Any Key To Continue')

    def buildProject(self):
        print('*========================*')
        print('Build Project Start')
        if self.isWorkSpace:
            os.system('xcodebuild -workspace %(x)s.xcworkspace -scheme %(x)s build' %
                      {'x': self.projectTargetName})
        else:
            os.system('xcodebuild build')

        if self.isExcuteStepByStep:
            input('Press Any Key To Continue')

    def archiveProject(self):
        print('*========================*')
        print('Archive Project Start')

        if self.isWorkSpace:
            os.system('fir build_ipa %(x)s.xcworkspace -o %(y)s -w -S %(x)s' %
                      {'x': self.projectTargetName, 'y': ipaRootDir + ipaFileDir})
        else:
            os.system('fir build_ipa %(x)s.xcodeproj -o %(y)s' %
                      {'x': self.projectTargetName, 'y': ipaRootDir + ipaFileDir})

        if self.isExcuteStepByStep:
            input('Press Any Key To Continue')

    def uploadToFir(self):
        print('*========================*')
        print('UploadToFir Project Start')
        dirs = os.listdir(ipaRootDir + ipaFileDir)
        downloadUrl = None
        for file in dirs:
            if '.ipa' in file:
                ipaPath = ipaRootDir + ipaFileDir + file
                ret = os.popen('fir publish %(x)s -c "%(y)s" -Q' %
                               {'x': ipaPath, 'y': self.projectChangeLog})
                for info in ret.readlines():
                    if "Published succeed" in info:
                        downloadUrl = info[info.find('http'):]
                        return downloadUrl

    def sendMail(self, to_addr, from_addr, subject, body_text, downloadUrl):
        print('*========================*')
        print('Send Mail Start')
        msg = email.mime.multipart.MIMEMultipart()
        msg['from'] = from_addr
        msg['to'] = to_addr
        msg['subject'] = '_'.join(subject)

        print('To:', msg['to'])

        if body_text:
            emailContent = (subject[0] + ':' + '\n' + '\t' +
                            self.projectChangeLog + '\n' + '\t' + body_text + '\n' + '\t' + downloadUrl + '\n')
        else:
            emailContent = (subject[0] + ':' + '\n' + '\t' +
                            self.projectChangeLog + '\n' + '\t' + downloadUrl + '\n')
        txt = email.mime.text.MIMEText(emailContent)
        msg.attach(txt)

        dirs = os.listdir(ipaRootDir + ipaFileDir)

        for file in dirs:
            if '.png' in file:
                with open(ipaRootDir + ipaFileDir + file, 'rb') as fileHandler:
                    image = email.mime.base.MIMEBase(
                        'image', 'png', filename=file)
                    image.add_header('Content-Disposition',
                                     'attachment', filename=file)
                    image.add_header('Content-ID', '<0>')
                    image.add_header('X-Attachment-Id', '0')
                    image.set_payload(fileHandler.read())
                    email.encoders.encode_base64(image)
                    msg.attach(image)
                break

        server = smtplib.SMTP(self.emailHost)
        server.login(from_addr, self.emailPassword)
        server.sendmail(from_addr, to_addr.split(','), str(msg))
        server.quit()

        print('Create Ipa Finish')
        print('*========================*')

    def start(self):
        print('*========================*')
        print('Create Ipa Start')
        # 获取参数
        self.setOptParse()
        # 获取项目名称
        self.getTargetName()
        # 获取版本信息
        projectInfo = self.getTargetVersion()
        # 获取配置文件
        self.getConfig()
        # 生成打包文件所在文件夹
        self.mkdir()
        # 解锁钥匙串
        self.keychainUnlock()
        # 获取最新代码
        self.gitPull()
        # 清理工程
        self.cleanProject()
        # 编译
        self.buildProject()
        # 打包
        self.archiveProject()
        # 上传到fir
        downloadUrl = self.uploadToFir()
        # 发送邮件
        self.sendMail(self.emailToUser, self.emailFromUser,
                      projectInfo, self.emailBodyText, downloadUrl)


if __name__ == '__main__':
    package = Package()
    package.start()

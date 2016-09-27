# -*- coding: utf-8 -*-
# coding:utf-8
import os
import os.path
import shutil
import sys
reload(sys)
sys.setdefaultencoding('utf8')

__author__ = 'lancelrq'



class LocalStorage(object):
    
    def __init__(self, root_dir, folder_name):
        """
        初始化
        :param root_dir: 根目录
        :param folder_name: 子目录
        :return:
        """
        self.folder_dir = (u'%s/%s' % (root_dir, folder_name)).encode('utf-8')  # 绝对目录路径
        if os.path.exists(self.folder_dir.encode('utf-8')) is False:            # 如果目录不存在则新建
            os.mkdir(self.folder_dir.encode('utf-8'))

    def get_file_path(self, file_name):
        """返回文件绝对路径"""
        return u"%s/%s" % (self.folder_dir.encode('utf-8'), file_name.encode('utf-8'))

    def is_file(self, file_name):
        """判断是否为文件，如果不存在则返回False"""
        if self.exists(file_name):
            return os.path.isfile(self.get_file_path(file_name))
        return False

    def is_folder(self, folder_name):
        """判断是否为文件夹，如果不存在则返回False"""
        if self.exists(folder_name):
            return os.path.isdir(self.get_file_path(folder_name))
        return False

    def exists(self, file_name):
        """判断路径是否存在"""
        if os.path.exists(self.get_file_path(file_name)):             # 判断文件是否存在
            return True
        else:
            return False

    def get_child_dir_storage(self, child_folder_name):
        """返回子目录的存储访问类"""
        if self.is_folder(child_folder_name):
            return LocalStorage(self.folder_dir, child_folder_name)

    def get_current_path(self):
        """返回当前目录位置"""
        return self.folder_dir.encode('utf-8')

    def new_file(self, file_name, file_body, file_mode='text'):
        """
        新建/覆盖写入文件
        :param file_name: 文件名
        :param file_body: 写入内容
        :param file_mode: 写入模式(text|bin)
        :return:
        """
        file_path = self.get_file_path(file_name)
        try:
            if file_mode == 'text':
                fp = open(file_path.encode('utf-8'), 'w')
                fp.write(file_body)
                fp.close()
            else:
                fp = open(file_path.encode('utf-8'), 'wb')
                fp.write(file_body)
                fp.close()
            return True
        except BaseException, ex:
            return False

    def clone_file(self, file_name, source_full_path):
        """
        将文件克隆进来
        :param file_name: 目标文件名
        :param source_full_path: 源文件完整地址
        :return:
        """
        if os.path.exists(source_full_path):
            shutil.copy(source_full_path, self.get_file_path(file_name))
            return True
        else:
            return False

    def rename(self, file_name, new_name):
        """
        重命名
        :param file_name: 源文件
        :param new_name: 新文件名
        :return:
        """
        if self.exists(file_name):
            shutil.copy2(self.get_file_path(file_name), self.get_file_path(new_name))
            return True
        else:
            return False

    def delete(self, file_name):
        """
        删除文件/目录
        :param file_name: 文件名
        :return:
        """
        if not self.exists(file_name):
            return False
        file_path = self.get_file_path(file_name)
        try:
            if self.is_folder(file_name):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path.encode('utf-8'))
            return True
        except BaseException, e:
            print str(e)
            return False

    def new_folder(self, folder_name):
        """
        新建文件夹（不推荐使用）
        :param folder_name: 文件夹名称
        :return:
        """
        if self.is_folder(folder_name):
            return False
        try:
            os.mkdir(self.get_file_path(folder_name).encode('utf-8'))
            return True
        except BaseException, e:
            return False

    def read_file(self, file_name, file_mode='text'):
        """
        读取文件内容
        :param file_name: 文件名
        :param file_mode: 打开模式(text|bin)
        :return:
        """
        if not self.is_file(file_name):
            return None
        file_path = self.get_file_path(file_name)
        try:
            dat = None
            if file_mode == 'text':
                fp = open(file_path, 'r')
                dat = fp.read()
                fp.close()
            else:
                fp = open(file_path, 'rb')
                dat = fp.read()
                fp.close()
            return dat
        except BaseException, e:
            return None

    def open_file(self, file_name, method='r'):
        """
        打开文件指针
        :param file_name:
        :param method: 打开模式(r|w|w+|rb|wb|wb+)
        :return:
        """
        try:
            file_path = self.get_file_path(file_name)
            fp = open(file_path, method)
            return fp
        except BaseException, e:
            return None

    def get_files_list(self, path='', with_info=False, full_path=False):
        """
        读取文件列表
        :param path: 扫描子路径，不写则为当前文件夹
        :param with_info: 返回文件详细信息
        :param full_path: 返回完整路径
        :return:
        """
        if not self.is_folder(path):
            return []
        tpath = self.get_file_path(path)
        lists = os.listdir(tpath)
        flist = []
        for item in lists:
            if os.path.isfile(os.path.join(tpath.encode('utf-8'), item.encode('utf-8'))):
                if full_path:
                    fp = os.path.join(tpath.encode('utf-8'), item.encode('utf-8'))
                else:
                    fp = item
                if with_info:
                    flist.append({
                        'file_name': fp,
                        'modify_time': os.path.getatime(os.path.join(tpath.encode('utf-8'), item.encode('utf-8'))),
                        'create_time': os.path.getctime(os.path.join(tpath.encode('utf-8'), item.encode('utf-8'))),
                        'size':  os.path.getsize(os.path.join(tpath.encode('utf-8'), item.encode('utf-8')))
                    })
                else:
                    flist.append(fp)
        return flist

    def get_dirs_list(self, path='', full_path=False):
        """
        返回目录
        :param path: 扫描子路径，不写则为当前文件夹
        :param full_path: 返回完整路径
        :return:
        """
        if not self.is_folder(path):
            return []
        tpath = self.get_file_path(path)
        lists = os.listdir(tpath)
        flist = []
        for item in lists:
            if os.path.isdir(os.path.join(tpath.encode('utf-8'), item.encode('utf-8'))):
                if full_path:
                    flist.append(os.path.join(tpath.encode('utf-8'), item.encode('utf-8')))
                else:
                    flist.append(item)
        return flist

    def get_file_attribute(self, file_name):
        """
        获取文件属性
        :param file_name: 文件名
        :return:
        """
        if self.exists(file_name):
            fn_path = self.get_file_path(file_name)
            return {
                'modify_time': os.path.getatime(fn_path),
                'create_time': os.path.getctime(fn_path),
                'size':  os.path.getsize(fn_path)
            }
        else:
            return {}

    def get_file_size(self, file_name):
        """
        获取文件大小
        :param file_name:
        :return:
        """
        if self.exists(file_name):
            fn_path = self.get_file_path(file_name)
            return os.path.getsize(fn_path)
        else:
            return -1
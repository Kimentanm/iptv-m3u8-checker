#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/10/23 15:27
# @Author  : Alex Kwan
# @Email   : gjy-alex@hotmail.com
# @File    : main.py
import m3u8
import utils.tools
import time
import os
import threading
from urllib import request


class Iptv(object):
    playlist_file = 'playlists/'
    m3u8_file_path = 'output/'
    delay_threshold = 5000

    resultData = {}

    def __init__(self):
        self.T = utils.tools.Tools()
        self.now = int(time.time() * 1000)

    # 从网络url中获取源文件
    def getPlaylistFromNetwork(self, url):
        playList = []
        if url[-4:] == '.txt':
            response = request.urlopen(url)
            txt = response.read().decode('utf-8')
            lines = txt.split('\r\n')
            total = len(lines)
            for i in range(0, total):
                line = lines[i].strip('\n')
                item = line.split(',', 1)
                if len(item) == 2:
                    data = {
                        'title': item[0],
                        'url': item[1],
                    }
                    playList.append(data)
        elif url[-4:] == '.m3u':
            try:
                m3u8_obj = m3u8.load(url)
                total = len(m3u8_obj.segments)
                for i in range(0, total):
                    tmp_title = m3u8_obj.segments[i].title
                    tmp_url = m3u8_obj.segments[i].uri
                    data = {
                        'title': tmp_title,
                        'url': tmp_url,
                    }
                    playList.append(data)
            except Exception as e:
                print(e)
        return playList

    # 从本地获取直播源文件
    def getPlaylist(self):

        '''
        :return playList:
        #从playlist文件夹读取文件，反馈urlList。
        #目前支持两类格式:
        #1、m3u文件格式
        #2、.txt格式，但内容必须是如下格式：
        战旗柯南1,http://dlhls.cdn.zhanqi.tv/zqlive/69410_SgVxl.m3u8
        战旗柯南2,http://alhls.cdn.zhanqi.tv/zqlive/219628_O3y9l.m3u8
        '''
        playList = []
        # 读取文件
        path = os.listdir(self.playlist_file)
        for p in path:
            if os.path.isfile(self.playlist_file + p):
                if p[-4:] == '.txt':
                    with open(self.playlist_file + p, 'r') as f:
                        lines = f.readlines()
                        total = len(lines)
                        for i in range(0, total):
                            line = lines[i].strip('\n')
                            item = line.split(',', 1)
                            if len(item) == 2:
                                data = {
                                    'title': item[0],
                                    'url': item[1],
                                }
                                playList.append(data)
                elif p[-4:] == '.m3u':

                    try:
                        m3u8_obj = m3u8.load(self.playlist_file + p)
                        total = len(m3u8_obj.segments)
                        for i in range(0, total):
                            tmp_title = m3u8_obj.segments[i].title
                            tmp_url = m3u8_obj.segments[i].uri
                            data = {
                                'title': tmp_title,
                                'url': tmp_url,
                            }
                            playList.append(data)
                    except Exception as e:
                        print(e)
        return playList

    def checkPlayList(self, playList):
        '''
        :return: True or False
        验证每一个直播源；对于有效直播源才插入数据库；同时，如果数据库中存在title相同的记录，则比较DELAY时间，保存DELAY小的。
        '''
        total = len(playList)
        if (total <= 0): return False
        threadList = []
        for i in range(0, total):
            print('Checking[ %s / %s ]:%s' % (i, total, playList[i]['title']))
            thread_check = threading.Thread(target=self.checkPlay, args=(playList[i],))
            thread_check.start()
            threadList.append(thread_check)
        for threadItem in threadList:
            threadItem.join()

    def checkPlay(self, playItem):
        tmp_title = playItem['title']
        tmp_url = playItem['url']

        netstat = self.T.chkPlayable(tmp_url)
        # print(netstat)
        if netstat > 0 and netstat < self.delay_threshold:
            data = {
                'title': tmp_title,
                'url': tmp_url,
                'delay': netstat,
                'updatetime': self.now,
            }
            self.addData(data)

        else:
            pass

    def addData(self, data):
        title = data['title']
        try:
            if title not in self.resultData:
                self.resultData[title] = data
            else:
                old_delay = self.resultData[data['title']]['delay']
                if int(data['delay']) < int(old_delay):
                    self.resultData[title] = data
        except Exception as e:
            print(e)

    def writeM3U8File(self):
        try:
            # 创建output文件夹
            if not os.path.exists(self.m3u8_file_path):
                os.makedirs(self.m3u8_file_path)

            result = self.resultData.values()
            # 排序
            sorted(result, key=lambda value: value['title'])

            if len(result) > 0:
                output_file = self.m3u8_file_path + str(time.time() * 1000) + '.m3u'
                with open(output_file, 'w') as f:
                    f.write("#EXTM3U\n")
                    for item in result:
                        f.write("#EXTINF:-1, %s\n" % (item['title']))
                        f.write("%s\n" % (item['url']))
                print('共获得 %s 个有效直播源！' % (len(result)))
            else:
                print('无有效直播源！')
                pass
        except Exception as e:
            print(e)


if __name__ == '__main__':
    iptv = Iptv()
    print('开始......')
    playlist = iptv.getPlaylistFromNetwork('https://gitee.com/happiness-2022/mytv/raw/master/mytv2.txt')
    # playlist = iptv.getPlaylist()
    iptv.checkPlayList(playlist)
    iptv.writeM3U8File()
    print('结束.....')

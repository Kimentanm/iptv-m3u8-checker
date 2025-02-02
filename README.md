# IPTV 直播源批量检测程序

## Fork
Fork From [AlexKwan1981/iptv-m3u8-checker](https://github.com/AlexKwan1981/iptv-m3u8-checker)

### 新增内容
- 去除sqlite数据库改用内存临时存储
- 增加多线程，速度比原先快了大概95%
- 新增从网络URL中获取直播源源文件（使用getPlaylistFromNetwork方法）

## 简介

### 主要功能
对直播源进行批量检测，将优质有效的直播源生成M3U文件
- 将待检测的直播源文件放置到playlists文件夹下：  
  - 支持多个文件  
  - 目前支持m3u格式的文件和txt格式，详见playlists文件下的示例
- 直播源检测原理  
  - 对每个连接进行测试, 同时记录当前网络对该连接的延迟.（参考了https://github.com/EvilCult/iptv-m3u-maker,致谢！）  
  - 对于同一个频道（titile同名），仅保留延迟最低的一个直播源
- 针对有效的优质直播源，将其输出为 **m3u** 文件，文件名称是当前时间。

## 项目使用方法

本项目基于 **python3.7** 进行开发 
- 主要参数  
playlist_file = 'playlists/'  
直播源源文件存放路径
m3u8_file_path = 'output/'  
检测后的M3U文件存放路径
delay_threshold = 5000  
响应延迟阈值，单位毫秒。超过这个阈值则认为直播源质量较差
- 在ouput文件下放置待检测的直播源清单  
- python main.py

## 待优化内容
- sqllite入库部分代码尚未优化
- 对于部分m3u格式的属性标签上不支持，存在读入m3u文件异常的情况
- 目前生成m3u文件尚不支持分组标签 
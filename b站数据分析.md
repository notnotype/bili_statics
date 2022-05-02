1. pandas
2. numpy
3. requests
4. matplotlib
5. sklearn

## 数据搜集方案

### up信息

1. 关注数
2. 粉丝数
3. 获赞数
4. 播放数
5. 阅读数

### 视频信息

视频信息是一个时间相关的数据。需要增量式爬虫不断收集信息。每一个时间节点的数据包含：

- cover
- 视频名字
- 视频播放量
- 总弹幕量
- 当前日期
- 发布日期
- 视频简介
- 点赞数
- 投币数
- 收藏数
- 转发数
- 当前时间节点评论信息*
- 视频地址

```text
aid: 340093159
author: "原神"
bvid: "BV1T94y1f7UE"
comment: 24017
copyright: "1"
created: 1648094443
description: "社奉行的"
hide_click: false
is_live_playback: 0
is_pay: 0
is_steins_gate: 0
is_union_video: 0
length: "07:47"
mid: 401742377
pic: "http://i0.hdslb.com/bfs"
play: 4004012
review: 0
subtitle: ""
title: "《原神》神里绫人角色PV——「灯火照夜」"
typeid: 172
video_review: 35492
```

### 评论信息

每一个时间节点包含的评论信息。包含：

- 评论用户信息*
- 评论内容
- 当前时间
- 评论发表日期
- 点赞数
- 回复评论信息*
- 回复哪一条评论
# 接口规范

基于 JSON 的 API，包含以下接口:

1. 握手
1. 注册
1. 登录
1. 广播消息
1. 获取在线用户

## 握手

##### 请求体

参数名 | 类型 | 描述
---|---|---
action | string | 动作
agent | string | 客户端类型

#### 请求示例

{"action": "handshake", "agent": "MINET"}

#### 响应示例

{"server": "MIRO"}

#### 异常示例

{"code": "UNKNOWN_AGENT", "message": "Your agent is rejected."}


## 注册


##### 请求体

参数名 | 类型 | 描述
---|---|---
action | string | 动作
username | string | 用户名
password | string | 密码
nickname | string | 昵称


#### 请求示例

{"action": "register", "username": "%s", "password": "%s", "nickname": "%s"}

#### 响应示例

{"code":"REGISTER_SUCCESS","message":"success"}

#### 异常示例

{"code":"REGISTER_FAIL","message":"xxx"}

## 登录

##### 请求体

参数名 | 类型 | 描述
---|---|---
action | string | 动作
username | string | 用户名
password | string | 密码


#### 请求示例

{"action": "login", "username": "%s", "password": "%s"}

#### 响应示例

{"code":"LOGIN_SUCCESS","message":"success"}

向其他客户端广播一条{"action": "login", "username": "1", "password": "1"}

#### 异常示例

{"code":"LOGIN_FAIL","message":"xxx"}


## 登出

##### 请求体

参数名 | 类型 | 描述
---|---|---
action | string | 动作

#### 请求示例

{"action": "logout"}

#### 响应示例

{"code":"LOGOUT_SUCCESS","message":"success"}

向其他客户端广播一条{"action": "logout", "username": "1", "password": "1"}


## 广播消息

##### 请求体

参数名 | 类型 | 描述
---|---|---
action | string | 动作
content | string | 消息内容

#### 请求示例

{"action": "broadcast", "content": "hehe"}

#### 响应示例

{"code": "BROADCAST_SUCCESS","message":""}

#### 异常示例

{"code":"BROADCAST_FAIL","message":"content length must > 0"}

## 获取在线用户

##### 请求体

参数名 | 类型 | 描述
---|---|---
action | string | 动作

#### 请求示例

{"action": "get_online_user"}

#### 响应示例

{u'user': [u'userxxx']}

#### 异常示例

None

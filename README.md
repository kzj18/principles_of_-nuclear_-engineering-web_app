# 针对燃耗问题的网页APP开发

## 一、项目简介

本项目针对燃耗计算问题分别基于`python-streamlit`框架开发了网页APP。本项目的宗旨是本项目是为不同平台、不同使用需求的用户带来便捷的、个性化的反应堆燃耗计算服务。

---

## 二、项目成果

本项目完成了网页APP在服务器、Heroku的部署，部署方法及实例平台详见后文。

---

## 三、实例介绍

* 实例1

  实例1是一个定通量燃耗的实例，其各参数如下。

  | 参数 | 值 |
  | --- | --- |
  | 中子通量 | ${10}^{14}{cm}^{-2}\cdot{s}^{-1}$ |
  | 燃耗步长 | 10天 |
  | ${}^{238}U$含量 | 980千克每吨 |
  | ${}^{235}U$含量 | 19千克每吨 |
  | ${}^{234}U$含量 | 1千克每吨 |

  计算结果如下图所示。

![](./.pic/example1.png)

* 实例2

  实例2是一个定功率燃耗的实例，其各参数如下。

  | 参数 | 值 |
  | --- | --- |
  | 比功率 | 300兆瓦每吨 |
  | 燃耗步长 | 1天 |
  | ${}^{238}U$含量 | 980千克每吨 |
  | ${}^{235}U$含量 | 19千克每吨 |
  | ${}^{234}U$含量 | 1千克每吨 |

  计算结果如下图所示。

![](./.pic/example2.png)

## 四、网页APP

### 4.1.服务器部署方法

1. 安装`Docker`，可以参考[菜鸟教程](https://www.runoob.com/docker/docker-tutorial.html)。
2. 通过`wget`命令下载本项目的[Docker镜像](https://cloud.tsinghua.edu.cn/f/9d47b47f1e804521bec7/)，在终端中输入

```
wget https://cloud.tsinghua.edu.cn/seafhttp/files/a773a06b-f63b-4d86-a091-35814ab0648d/principles_of_nuclear_engineering_web_app_v0.1.tar
```

3. 导入Docker镜像，在终端中输入

```
sudo docker load < principles_of_nuclear_engineering_web_app_v0.1.tar
```

4. 由Docker镜像创建Docker容器并运行，完成部署，在终端中输入

```
sudo docker run -d -p 8501:8501 principles_of_nuclear_engineering_web_app:v0.1
```

其中，`-d`使Docker容器在后台运行，`-p 8501:8501`将容器的`8501`端口暴露在外网。

5. 查看Docker容器，在终端中输入

```
sudo docker ps -a
```

6. 若要停止网页APP，停止Docker容器，在终端中输入

```
sudo docker stop <CONTAINER ID>
```

7. 若要重启网页APP，重启Docker容器，在终端中输入

```
sudo docker restart <CONTAINER ID>
```

* 利用本方法部署的网页APP可以[点击链接访问](http://http://180.76.237.109:8501/)。

---

### 4.2.利用Heroku进行部署

部署过程参考博客[《还在嫌弃作业不够秀？快来试试streamlit+heroku 搭建自己的炫酷app叭》](https://blog.csdn.net/weixin_44984664/article/details/105776080)。

* 利用本方法部署的的网页APP可以[点击链接访问](https://burnup-calculator.herokuapp.com/)，访问需要科学上网。

---

### 4.3.界面及操作说明

#### 4.3.1.默认模式

默认模式下的界面如下图所示。

![](./.pic/interface_default.png)

* 标题及燃耗链信息区

  用户可以在这里看到实时使用的燃耗链参数，以确认所使用的计算参数复合预期。

* 主配置区

  用户可以在此处调整燃耗步长大小以及内燃耗步长的精度，选择需要展示的核素。
  用户可以在此处配置燃料的初始成分，本项目的默认模式只开放了${}^{234}U$、${}^{235}U$和${}^{238}U$三种核素的成分配置，其他核素在默认模式下的初始成分为0。

* 副配置区

  用户可以在此处选择开启或关闭专家模式、调整计算模式、输入相应计算模式需要用户提供的中子通量大小或比功率大小。
  由于调整展示参数的功能区不常用且占地较大，因此将其放入副配置区。

* 结果展示区

  用户可以在此选择计算方法并查看计算结果，在图片处右键点击并选择“另存为”即可保存图片，右键点击图片下方的超链接并另存为csv文件即可保存计算结果（数值解）。

#### 4.3.2.专家模式

专家模式下的界面如下图所示。

![](./.pic/interface_expert.png)

* 标题及燃耗链信息区

  相比默认模式，专家模式在本区域为用户提供了下载默认模式燃耗链配置文件的超链接，用户可以参考该配置文件创建、修改并上传自己的燃耗链文件，从而实现自定义燃耗链计算。更多可供参考的配置文件可访问[这里](https://gitee.com/kzj18/principles_of_-nuclear_-engineering/tree/master/Examples)。

* 主配置区

  相比默认模式，专家模式在本区域开放了所有核素的初始成分配置。
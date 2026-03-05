# ecshop_UI
电商UI自动化测试项目（实习用）

一、项目简介

本项目是基于开源电商系统ECShop的UI自动化测试，采用Selenium + Python + pytest + Allure技术栈，实现了对电商核心流程的自动化测试，以UIPO项目demo展示对PO模式的理解与运用。

二、说明

1、ECShop环境：

本地部署：通过PHPStudy和本地源码文件搭建，访问地址为localhost；

在线替代：可直接使用在线开源电商平台，仅需修改测试脚本中的URL即可；

2、allure_report查看报告：

由于浏览器的同源策略会对file://协议（本地文件协议）施加严格的访问限制（即当HTML文件以file://方式打开时，其发起的本地文件请求会被判定为“跨源请求”，浏览器会拦截这类请求），所以其中的index.html无法直接打开查看。

请在终端执行以下命令启动本地服务器：

python -m http.server 8888 #端口号可自行选择

后续访问 http://localhost:8888 （同上）即可查看完整的allure报告；

3、PO模式说明：

UIPO文件夹是基于已完成项目引入的PO模式（page object）示例，该模块仅用于展示PO模式的设计思想，尚未集成到完整的测试流程中；

4、CI/CD说明：

本项目为本地部署，PHPstudy环境下的数据库无法被外部访问修改，且无法使用fixture来隔离测试数据；

因此，CI/CD流程将在第二个项目api接口自动化测试中来体现。

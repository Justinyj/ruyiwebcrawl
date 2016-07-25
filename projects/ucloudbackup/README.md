# mongo数据恢复说明
从ucloud备份下来的数据为tgz格式，需要在预先建立好的dump目录下解压，解压后会有/dump/tmp/backup/udb-sbjftb
在udb-sbjftb目录下会出现若干个文件夹： ‘db_wechat’,’db_cache’  等。文件夹中有bson和json文件。
### I.查看数据流程
    1.安装mongo （视环境不同有一系列问题要解决）
    2.运行mongod指令（数据库默认运行在http://127.0.0.1:27017/）
    3.新开终端，输入mongo进入shell，输入show dbs查看数据库，默认新建的为test。
    4.终端输入mongorestore -d [your_db_name] [your_dump_dir] ,在此例子中则是
    mongorestore -d test  /dump/tmp/backup/udb-sbjftb/[directory]  ,选择db_wechat  db_cache等文件夹进行恢复。
    恢复后在mongo shell中输入show dbs会看到相应的db占用空间增大。
    5.show collections 查看所有collection，输入db.[collection_name].find()可以遍历整个collection

### II.检验备份是否有效
    1.确认collections的集合于标准集合相等
    2.输入db.systemPropertyModel.find()查看NumberLong字段检验有效性
    3.每天统计各个collections的信息条数，发送统计消息



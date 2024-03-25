# SearchXlsGui 搜索excel中的内容 

## 介绍 

源于游戏项目中多使用excel进行数值配置,  开发此工具在多个excel中进行搜索相关文本 

## 使用

**搜索**
1. 选中要搜索的文件夹
2. 排除/只在某些文件中进行搜索
3. 填写文本内容

**查看**
1. 提供查看`文件夹`, `sheet`,`cell位置`, `cell内容`, `整行数据内容`
2. 在选中行`右击`, 可打开文件/文件夹


> ![image](https://github.com/elroy93/searchXlsGui/assets/43977905/795638a3-67e7-41d9-a72a-3f90869bbe87)




## 技术栈
- pyside6 : qt界面
- openxls : 读取excel的内容
- zerorpc : qt多页面的通信

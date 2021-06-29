# trans
一个翻译小工具，每次翻译需要去开网页 麻烦 自己写了一个 



## 依赖安装



```shell
pip3 install pyperclip
pip3 install demjson
pip3 install js2py
pip3 install requests
```



## Linux

```shell
pyinstaller -F trans.py 
cd dist
cp trans /usr/lcoal/bin/
```

## windows



```shell
pyinstaller -F trans.py 
```

就exe懂的都懂



## 运行方式

~~~

trans xx  //会自动拷贝到粘贴板
trans //读取粘贴板内容 翻译 拷贝到粘贴板

~~~

## 更多功能

多语言选择 目前不想做了

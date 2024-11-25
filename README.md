[English](#eng)/[日本語](#jp)
# slibjupyter
<a name="eng"></a>
## About this plugin
This plugin is

## Installation
This plugin is available via pip. It can be installed directly from github.
```sh
pip install git+https://github.com/YujiSue/slibjupyter.git
```

## Usage

###  Example of a script like code
```py
%%slibscript
auto name = "Hoge;
// C
printf("Hello! %s!", name);
// C++
std::cout<< "Hello! " << name << "!" << std::endl;
// C++ with slib
auto name = "Hoge";
SPrint("Hello! ", name, "!"); 
```
---

<a name="jp"></a>
## このプラグインについて
このプラグインは、Jupyter上でC/C++(要[slib]()併用)を簡単に実行するためのプラグインです。  

##  インストール方法
下記のように、そのままGithubからインストールできます。
```sh
pip install git+https://github.com/YujiSue/slibjupyter.git
```

## 使用方法
マジックコマンドをつけることで、バックグラウンドで実行ファイルを生成します。  

###  スクリプト型表記の例
```py
%%slibscript
auto name = "Hoge;
// C
printf("Hello! %s!", name);
// C++
std::cout<< "Hello! " << name << "!" << std::endl;
// C++ with slib
auto name = "Hoge";
SPrint("Hello! ", name, "!"); 
```

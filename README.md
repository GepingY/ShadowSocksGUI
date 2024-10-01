# ShadowSocksGUI
## Introduction
This is a graphical version of ShadowSocks.  
This app is designed to replace `Shadowsocks-Qt5` at `https://github.com/shadowsocks/shadowsocks-qt5`, since it's outdated, no longer maintained, and has a lot of trouble running on newer versions of Ubuntu.  
In the current version, this app is only an interface that controls a ShadowSocks core, meaning that it does not have the ShadowSocks core integrated inside the app, so you will have to download the core as a dependencies, Read below. Later versions might integrate the ShadowSocks core into the interface to form a full app.

## How to use
1. Go to `https://github.com/GepingY/ShadowSocksGUI/releases/tag/v1.0` and download the latest version of the executable file `ssGUI`.  
2. Download `shadowsocks-libev` by running `sudo apt update && sudo apt install shadowsocks-libev`. Verify if it's installed by running `ss-local -h`.  
3. Go to the directory where you downloaded the app. For CLI, run `./ssGUI`; for GUI, simply execute it (you might need to set the permissions or make it executable).

## Requirements
This program is tested on `Ubuntu 24.04 Noble` with `shadowsocks-libev 3.3.5` as the ShadowSocks core.  
This program requires `shadowsocks-libev` for the ShadowSocks core. The recommended version is `3.3.5` or above since it's tested on `3.3.5`.

## Bug
If you are having any issues requesting/using the app, please contact me through `Issues` or at `ygp3737@gmail.com`. I will make sure it gets fixed.

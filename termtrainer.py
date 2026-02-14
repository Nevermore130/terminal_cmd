#!/usr/bin/env python3
"""
TermTrainer - macOS Terminal Command Practice Tool
帮助用户快速熟悉终端操作命令，成为高效的终端程序员
"""

import json
import os
import random
import sys
import subprocess
import readline
from datetime import datetime
from pathlib import Path
from typing import Optional

# ANSI颜色代码
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

def colored(text: str, color: str) -> str:
    return f"{color}{text}{Colors.RESET}"

# 命令数据库
COMMANDS_DB = {
    "file_operations": {
        "name": "文件操作",
        "icon": "📁",
        "commands": [
            {
                "command": "ls",
                "description": "列出目录内容",
                "examples": ["ls", "ls -la", "ls -lh", "ls -R"],
                "exercises": [
                    {"question": "列出当前目录的所有文件（包括隐藏文件）", "answers": ["ls -a", "ls -A", "ls --all"]},
                    {"question": "以详细格式列出文件，并显示人类可读的文件大小", "answers": ["ls -lh", "ls -hl"]},
                    {"question": "递归列出所有子目录的内容", "answers": ["ls -R", "ls --recursive"]},
                ]
            },
            {
                "command": "cat",
                "description": "显示文件内容",
                "examples": ["cat file.txt", "cat -n file.txt", "cat file1 file2"],
                "exercises": [
                    {"question": "显示文件 config.txt 的内容并带行号", "answers": ["cat -n config.txt", "cat --number config.txt"]},
                    {"question": "合并 a.txt 和 b.txt 的内容并显示", "answers": ["cat a.txt b.txt"]},
                ]
            },
            {
                "command": "cp",
                "description": "复制文件或目录",
                "examples": ["cp file1 file2", "cp -r dir1 dir2", "cp -i file dest"],
                "exercises": [
                    {"question": "递归复制整个 src 目录到 backup", "answers": ["cp -r src backup", "cp -R src backup", "cp --recursive src backup"]},
                    {"question": "复制文件时保留原有属性（权限、时间戳等）", "answers": ["cp -p file dest", "cp --preserve file dest", "cp -a file dest"]},
                ]
            },
            {
                "command": "mv",
                "description": "移动或重命名文件",
                "examples": ["mv old new", "mv file dir/", "mv -i file dest"],
                "exercises": [
                    {"question": "将 old_name.txt 重命名为 new_name.txt", "answers": ["mv old_name.txt new_name.txt"]},
                    {"question": "移动文件时如果目标存在则提示确认", "answers": ["mv -i file dest", "mv --interactive file dest"]},
                ]
            },
            {
                "command": "rm",
                "description": "删除文件或目录",
                "examples": ["rm file", "rm -r dir", "rm -f file"],
                "exercises": [
                    {"question": "递归删除整个 temp 目录及其内容", "answers": ["rm -r temp", "rm -R temp", "rm --recursive temp", "rm -rf temp"]},
                    {"question": "删除文件前提示确认", "answers": ["rm -i file", "rm --interactive file"]},
                ]
            },
            {
                "command": "touch",
                "description": "创建空文件或更新时间戳",
                "examples": ["touch file.txt", "touch -t 202401010000 file"],
                "exercises": [
                    {"question": "创建一个名为 newfile.txt 的空文件", "answers": ["touch newfile.txt"]},
                    {"question": "同时创建 a.txt, b.txt, c.txt 三个文件", "answers": ["touch a.txt b.txt c.txt"]},
                ]
            },
            {
                "command": "head",
                "description": "显示文件开头部分",
                "examples": ["head file", "head -n 20 file", "head -c 100 file"],
                "exercises": [
                    {"question": "显示 log.txt 文件的前15行", "answers": ["head -n 15 log.txt", "head -15 log.txt", "head --lines=15 log.txt"]},
                ]
            },
            {
                "command": "tail",
                "description": "显示文件结尾部分",
                "examples": ["tail file", "tail -n 20 file", "tail -f log"],
                "exercises": [
                    {"question": "实时监控 app.log 文件的新增内容", "answers": ["tail -f app.log", "tail --follow app.log"]},
                    {"question": "显示 data.txt 的最后25行", "answers": ["tail -n 25 data.txt", "tail -25 data.txt"]},
                ]
            },
        ]
    },
    "directory_operations": {
        "name": "目录操作",
        "icon": "📂",
        "commands": [
            {
                "command": "cd",
                "description": "切换目录",
                "examples": ["cd /path", "cd ~", "cd ..", "cd -"],
                "exercises": [
                    {"question": "返回上一级目录", "answers": ["cd .."]},
                    {"question": "切换到用户主目录", "answers": ["cd ~", "cd", "cd $HOME"]},
                    {"question": "返回上一次所在的目录", "answers": ["cd -"]},
                ]
            },
            {
                "command": "pwd",
                "description": "显示当前工作目录",
                "examples": ["pwd", "pwd -P"],
                "exercises": [
                    {"question": "显示当前所在目录的完整路径", "answers": ["pwd"]},
                ]
            },
            {
                "command": "mkdir",
                "description": "创建目录",
                "examples": ["mkdir dir", "mkdir -p a/b/c", "mkdir -m 755 dir"],
                "exercises": [
                    {"question": "创建多层嵌套目录 project/src/main", "answers": ["mkdir -p project/src/main", "mkdir --parents project/src/main"]},
                    {"question": "创建目录并设置权限为755", "answers": ["mkdir -m 755 mydir", "mkdir --mode=755 mydir"]},
                ]
            },
            {
                "command": "rmdir",
                "description": "删除空目录",
                "examples": ["rmdir dir", "rmdir -p a/b/c"],
                "exercises": [
                    {"question": "删除空目录 empty_folder", "answers": ["rmdir empty_folder"]},
                ]
            },
            {
                "command": "tree",
                "description": "以树形结构显示目录",
                "examples": ["tree", "tree -L 2", "tree -d"],
                "exercises": [
                    {"question": "显示目录树，但只显示2层深度", "answers": ["tree -L 2"]},
                    {"question": "只显示目录，不显示文件", "answers": ["tree -d"]},
                ]
            },
        ]
    },
    "text_processing": {
        "name": "文本处理",
        "icon": "📝",
        "commands": [
            {
                "command": "grep",
                "description": "文本搜索",
                "examples": ["grep pattern file", "grep -r pattern dir", "grep -i pattern file"],
                "exercises": [
                    {"question": "在 code.py 中搜索包含 'error' 的行（忽略大小写）", "answers": ["grep -i error code.py", "grep --ignore-case error code.py"]},
                    {"question": "递归搜索目录中所有包含 'TODO' 的文件", "answers": ["grep -r TODO .", "grep -R TODO .", "grep --recursive TODO ."]},
                    {"question": "显示匹配行及其前后各2行的上下文", "answers": ["grep -C 2 pattern file", "grep --context=2 pattern file"]},
                ]
            },
            {
                "command": "sed",
                "description": "流编辑器",
                "examples": ["sed 's/old/new/g' file", "sed -i '' 's/a/b/g' file"],
                "exercises": [
                    {"question": "将文件中所有 'foo' 替换为 'bar'", "answers": ["sed 's/foo/bar/g' file", "sed 's/foo/bar/g' file"]},
                    {"question": "删除文件中的空行", "answers": ["sed '/^$/d' file"]},
                ]
            },
            {
                "command": "awk",
                "description": "文本分析工具",
                "examples": ["awk '{print $1}' file", "awk -F: '{print $1}' file"],
                "exercises": [
                    {"question": "打印文件每行的第一列（默认空格分隔）", "answers": ["awk '{print $1}' file"]},
                    {"question": "使用冒号作为分隔符，打印第一和第三列", "answers": ["awk -F: '{print $1,$3}' file", "awk -F':' '{print $1,$3}' file"]},
                ]
            },
            {
                "command": "sort",
                "description": "排序文本",
                "examples": ["sort file", "sort -n file", "sort -r file"],
                "exercises": [
                    {"question": "按数字大小排序文件内容", "answers": ["sort -n file", "sort --numeric-sort file"]},
                    {"question": "逆序排序文件内容", "answers": ["sort -r file", "sort --reverse file"]},
                ]
            },
            {
                "command": "uniq",
                "description": "去重或统计重复行",
                "examples": ["uniq file", "uniq -c file", "uniq -d file"],
                "exercises": [
                    {"question": "统计每行出现的次数", "answers": ["uniq -c file", "uniq --count file"]},
                    {"question": "只显示重复的行", "answers": ["uniq -d file", "uniq --repeated file"]},
                ]
            },
            {
                "command": "wc",
                "description": "统计字数、行数等",
                "examples": ["wc file", "wc -l file", "wc -w file"],
                "exercises": [
                    {"question": "统计文件的行数", "answers": ["wc -l file", "wc --lines file"]},
                    {"question": "统计文件的单词数", "answers": ["wc -w file", "wc --words file"]},
                ]
            },
            {
                "command": "cut",
                "description": "切割文本",
                "examples": ["cut -d: -f1 file", "cut -c1-10 file"],
                "exercises": [
                    {"question": "提取以冒号分隔的第一个字段", "answers": ["cut -d: -f1 file", "cut -d ':' -f1 file"]},
                    {"question": "提取每行的前10个字符", "answers": ["cut -c1-10 file", "cut -c 1-10 file"]},
                ]
            },
        ]
    },
    "process_management": {
        "name": "进程管理",
        "icon": "⚙️",
        "commands": [
            {
                "command": "ps",
                "description": "显示进程状态",
                "examples": ["ps", "ps aux", "ps -ef"],
                "exercises": [
                    {"question": "显示所有用户的所有进程详细信息", "answers": ["ps aux", "ps -ef"]},
                    {"question": "显示当前用户的进程", "answers": ["ps", "ps -u $USER"]},
                ]
            },
            {
                "command": "top",
                "description": "实时显示进程状态",
                "examples": ["top", "top -o cpu", "top -o mem"],
                "exercises": [
                    {"question": "按CPU使用率排序显示进程", "answers": ["top -o cpu", "top -o %CPU"]},
                ]
            },
            {
                "command": "kill",
                "description": "终止进程",
                "examples": ["kill PID", "kill -9 PID", "kill -15 PID"],
                "exercises": [
                    {"question": "强制终止进程ID为1234的进程", "answers": ["kill -9 1234", "kill -KILL 1234", "kill -SIGKILL 1234"]},
                    {"question": "优雅终止进程ID为5678的进程", "answers": ["kill 5678", "kill -15 5678", "kill -TERM 5678"]},
                ]
            },
            {
                "command": "killall",
                "description": "按名称终止进程",
                "examples": ["killall process_name", "killall -9 process_name"],
                "exercises": [
                    {"question": "终止所有名为 python 的进程", "answers": ["killall python", "killall -9 python"]},
                ]
            },
            {
                "command": "bg",
                "description": "将任务放到后台运行",
                "examples": ["bg", "bg %1"],
                "exercises": [
                    {"question": "将当前暂停的任务放到后台继续运行", "answers": ["bg", "bg %1"]},
                ]
            },
            {
                "command": "fg",
                "description": "将后台任务调到前台",
                "examples": ["fg", "fg %1"],
                "exercises": [
                    {"question": "将后台任务调回前台运行", "answers": ["fg", "fg %1"]},
                ]
            },
            {
                "command": "jobs",
                "description": "显示后台任务列表",
                "examples": ["jobs", "jobs -l"],
                "exercises": [
                    {"question": "显示当前shell的所有后台任务", "answers": ["jobs", "jobs -l"]},
                ]
            },
            {
                "command": "nohup",
                "description": "忽略挂起信号运行命令",
                "examples": ["nohup command &", "nohup ./script.sh &"],
                "exercises": [
                    {"question": "在后台运行 script.sh，即使退出终端也继续运行", "answers": ["nohup ./script.sh &", "nohup sh script.sh &"]},
                ]
            },
        ]
    },
    "network": {
        "name": "网络工具",
        "icon": "🌐",
        "commands": [
            {
                "command": "curl",
                "description": "传输数据的命令行工具",
                "examples": ["curl url", "curl -O url", "curl -X POST url"],
                "exercises": [
                    {"question": "下载文件并保存为原始文件名", "answers": ["curl -O url", "curl --remote-name url"]},
                    {"question": "发送POST请求到指定URL", "answers": ["curl -X POST url", "curl --request POST url"]},
                    {"question": "显示HTTP响应头信息", "answers": ["curl -I url", "curl --head url"]},
                ]
            },
            {
                "command": "wget",
                "description": "网络文件下载",
                "examples": ["wget url", "wget -c url", "wget -r url"],
                "exercises": [
                    {"question": "断点续传下载文件", "answers": ["wget -c url", "wget --continue url"]},
                    {"question": "递归下载整个网站", "answers": ["wget -r url", "wget --recursive url"]},
                ]
            },
            {
                "command": "ping",
                "description": "测试网络连通性",
                "examples": ["ping host", "ping -c 4 host"],
                "exercises": [
                    {"question": "ping google.com 4次后停止", "answers": ["ping -c 4 google.com"]},
                ]
            },
            {
                "command": "ssh",
                "description": "安全远程登录",
                "examples": ["ssh user@host", "ssh -p 2222 user@host", "ssh -i key user@host"],
                "exercises": [
                    {"question": "使用指定端口2222连接远程服务器", "answers": ["ssh -p 2222 user@host"]},
                    {"question": "使用私钥文件连接远程服务器", "answers": ["ssh -i keyfile user@host", "ssh -i ~/.ssh/keyfile user@host"]},
                ]
            },
            {
                "command": "scp",
                "description": "安全复制文件到远程",
                "examples": ["scp file user@host:path", "scp -r dir user@host:path"],
                "exercises": [
                    {"question": "将本地 data.txt 复制到远程服务器的 /tmp 目录", "answers": ["scp data.txt user@host:/tmp", "scp data.txt user@host:/tmp/"]},
                    {"question": "递归复制整个目录到远程服务器", "answers": ["scp -r dir user@host:path", "scp -r dir user@host:/path"]},
                ]
            },
            {
                "command": "netstat",
                "description": "显示网络连接状态",
                "examples": ["netstat -an", "netstat -tlnp"],
                "exercises": [
                    {"question": "显示所有监听中的TCP端口", "answers": ["netstat -tln", "netstat -an | grep LISTEN"]},
                ]
            },
            {
                "command": "lsof",
                "description": "列出打开的文件",
                "examples": ["lsof", "lsof -i :8080", "lsof -p PID"],
                "exercises": [
                    {"question": "查看哪个进程占用了8080端口", "answers": ["lsof -i :8080"]},
                ]
            },
        ]
    },
    "permission_ownership": {
        "name": "权限与所有权",
        "icon": "🔐",
        "commands": [
            {
                "command": "chmod",
                "description": "修改文件权限",
                "examples": ["chmod 755 file", "chmod +x file", "chmod -R 644 dir"],
                "exercises": [
                    {"question": "给脚本文件添加可执行权限", "answers": ["chmod +x script.sh", "chmod u+x script.sh"]},
                    {"question": "设置文件权限为所有者可读写执行，其他人只读", "answers": ["chmod 744 file", "chmod u=rwx,go=r file"]},
                    {"question": "递归修改目录及其所有内容的权限为755", "answers": ["chmod -R 755 dir", "chmod --recursive 755 dir"]},
                ]
            },
            {
                "command": "chown",
                "description": "修改文件所有者",
                "examples": ["chown user file", "chown user:group file", "chown -R user dir"],
                "exercises": [
                    {"question": "修改文件所有者为 admin", "answers": ["chown admin file", "sudo chown admin file"]},
                    {"question": "同时修改文件的所有者和所属组", "answers": ["chown user:group file"]},
                ]
            },
            {
                "command": "chgrp",
                "description": "修改文件所属组",
                "examples": ["chgrp group file", "chgrp -R group dir"],
                "exercises": [
                    {"question": "修改文件的所属组为 developers", "answers": ["chgrp developers file"]},
                ]
            },
            {
                "command": "sudo",
                "description": "以管理员权限执行命令",
                "examples": ["sudo command", "sudo -u user command", "sudo -i"],
                "exercises": [
                    {"question": "以root权限编辑系统配置文件", "answers": ["sudo vim /etc/hosts", "sudo nano /etc/hosts", "sudo vi /etc/hosts"]},
                    {"question": "切换到root用户的shell", "answers": ["sudo -i", "sudo su -", "sudo -s"]},
                ]
            },
        ]
    },
    "compression": {
        "name": "压缩与解压",
        "icon": "📦",
        "commands": [
            {
                "command": "tar",
                "description": "打包和解包文件",
                "examples": ["tar -cvf archive.tar files", "tar -xvf archive.tar", "tar -czvf archive.tar.gz files"],
                "exercises": [
                    {"question": "创建一个gzip压缩的tar包", "answers": ["tar -czvf archive.tar.gz files", "tar -czf archive.tar.gz files"]},
                    {"question": "解压tar.gz文件到当前目录", "answers": ["tar -xzvf archive.tar.gz", "tar -xzf archive.tar.gz"]},
                    {"question": "查看tar包中的文件列表（不解压）", "answers": ["tar -tvf archive.tar", "tar -tf archive.tar"]},
                ]
            },
            {
                "command": "gzip",
                "description": "压缩文件",
                "examples": ["gzip file", "gzip -d file.gz", "gzip -k file"],
                "exercises": [
                    {"question": "压缩文件并保留原文件", "answers": ["gzip -k file", "gzip --keep file"]},
                    {"question": "解压gzip文件", "answers": ["gzip -d file.gz", "gunzip file.gz"]},
                ]
            },
            {
                "command": "zip",
                "description": "创建zip压缩包",
                "examples": ["zip archive.zip files", "zip -r archive.zip dir"],
                "exercises": [
                    {"question": "递归压缩整个目录为zip文件", "answers": ["zip -r archive.zip dir"]},
                ]
            },
            {
                "command": "unzip",
                "description": "解压zip文件",
                "examples": ["unzip archive.zip", "unzip -d dir archive.zip"],
                "exercises": [
                    {"question": "解压zip文件到指定目录", "answers": ["unzip archive.zip -d dir", "unzip -d dir archive.zip"]},
                    {"question": "查看zip包内容（不解压）", "answers": ["unzip -l archive.zip"]},
                ]
            },
        ]
    },
    "system_info": {
        "name": "系统信息",
        "icon": "💻",
        "commands": [
            {
                "command": "uname",
                "description": "显示系统信息",
                "examples": ["uname", "uname -a", "uname -r"],
                "exercises": [
                    {"question": "显示完整的系统信息", "answers": ["uname -a", "uname --all"]},
                    {"question": "只显示内核版本", "answers": ["uname -r", "uname --kernel-release"]},
                ]
            },
            {
                "command": "df",
                "description": "显示磁盘空间使用情况",
                "examples": ["df", "df -h", "df -T"],
                "exercises": [
                    {"question": "以人类可读格式显示磁盘使用情况", "answers": ["df -h", "df --human-readable"]},
                ]
            },
            {
                "command": "du",
                "description": "显示目录空间使用情况",
                "examples": ["du", "du -sh dir", "du -h --max-depth=1"],
                "exercises": [
                    {"question": "显示当前目录的总大小（人类可读格式）", "answers": ["du -sh .", "du -sh"]},
                    {"question": "显示当前目录下各子目录的大小", "answers": ["du -h --max-depth=1", "du -h -d 1"]},
                ]
            },
            {
                "command": "free",
                "description": "显示内存使用情况",
                "examples": ["free", "free -h", "free -m"],
                "exercises": [
                    {"question": "以人类可读格式显示内存使用情况", "answers": ["free -h", "free --human"]},
                ]
            },
            {
                "command": "uptime",
                "description": "显示系统运行时间",
                "examples": ["uptime"],
                "exercises": [
                    {"question": "查看系统运行了多长时间", "answers": ["uptime"]},
                ]
            },
            {
                "command": "whoami",
                "description": "显示当前用户名",
                "examples": ["whoami"],
                "exercises": [
                    {"question": "显示当前登录的用户名", "answers": ["whoami"]},
                ]
            },
            {
                "command": "which",
                "description": "显示命令的路径",
                "examples": ["which python", "which -a python"],
                "exercises": [
                    {"question": "查找python命令的完整路径", "answers": ["which python", "which python3"]},
                ]
            },
            {
                "command": "env",
                "description": "显示环境变量",
                "examples": ["env", "env | grep PATH"],
                "exercises": [
                    {"question": "显示所有环境变量", "answers": ["env", "printenv"]},
                ]
            },
            {
                "command": "echo",
                "description": "输出文本或变量",
                "examples": ["echo hello", "echo $PATH", "echo -n text"],
                "exercises": [
                    {"question": "显示PATH环境变量的值", "answers": ["echo $PATH"]},
                    {"question": "输出文本但不换行", "answers": ["echo -n text", "echo -n 'text'"]},
                ]
            },
        ]
    },
    "search_find": {
        "name": "搜索与查找",
        "icon": "🔍",
        "commands": [
            {
                "command": "find",
                "description": "查找文件",
                "examples": ["find . -name '*.txt'", "find / -type f -size +100M", "find . -mtime -7"],
                "exercises": [
                    {"question": "在当前目录递归查找所有 .py 文件", "answers": ["find . -name '*.py'", "find . -name \"*.py\""]},
                    {"question": "查找大于100MB的文件", "answers": ["find . -size +100M", "find . -type f -size +100M"]},
                    {"question": "查找7天内修改过的文件", "answers": ["find . -mtime -7", "find . -type f -mtime -7"]},
                    {"question": "查找所有空目录", "answers": ["find . -type d -empty"]},
                ]
            },
            {
                "command": "locate",
                "description": "快速查找文件（基于数据库）",
                "examples": ["locate filename", "locate -i filename"],
                "exercises": [
                    {"question": "忽略大小写搜索文件名包含config的文件", "answers": ["locate -i config"]},
                ]
            },
            {
                "command": "whereis",
                "description": "查找命令的二进制文件、源文件和手册",
                "examples": ["whereis ls", "whereis python"],
                "exercises": [
                    {"question": "查找 bash 命令的所有相关文件", "answers": ["whereis bash"]},
                ]
            },
        ]
    },
    "advanced": {
        "name": "高级技巧",
        "icon": "🚀",
        "commands": [
            {
                "command": "|",
                "description": "管道 - 将一个命令的输出作为另一个的输入",
                "examples": ["ls | grep txt", "cat file | sort | uniq", "ps aux | grep python"],
                "exercises": [
                    {"question": "列出所有文件并只显示包含 .log 的行", "answers": ["ls | grep .log", "ls | grep '\\.log'"]},
                    {"question": "统计当前目录下的文件数量", "answers": ["ls | wc -l", "ls -1 | wc -l"]},
                ]
            },
            {
                "command": ">",
                "description": "输出重定向 - 将输出写入文件（覆盖）",
                "examples": ["echo hello > file.txt", "ls > files.txt"],
                "exercises": [
                    {"question": "将 ls 命令的输出保存到 files.txt", "answers": ["ls > files.txt"]},
                ]
            },
            {
                "command": ">>",
                "description": "追加重定向 - 将输出追加到文件",
                "examples": ["echo line >> file.txt"],
                "exercises": [
                    {"question": "将文本追加到日志文件末尾", "answers": ["echo 'log entry' >> log.txt", "echo \"log entry\" >> log.txt"]},
                ]
            },
            {
                "command": "&&",
                "description": "逻辑与 - 前一命令成功才执行后一命令",
                "examples": ["mkdir dir && cd dir", "make && make install"],
                "exercises": [
                    {"question": "创建目录 project 后立即进入该目录", "answers": ["mkdir project && cd project"]},
                ]
            },
            {
                "command": "||",
                "description": "逻辑或 - 前一命令失败才执行后一命令",
                "examples": ["test -f file || touch file"],
                "exercises": [
                    {"question": "如果文件不存在则创建它", "answers": ["test -f file || touch file", "[ -f file ] || touch file"]},
                ]
            },
            {
                "command": "xargs",
                "description": "构建并执行命令行",
                "examples": ["find . -name '*.txt' | xargs rm", "cat urls.txt | xargs wget"],
                "exercises": [
                    {"question": "删除所有查找到的 .tmp 文件", "answers": ["find . -name '*.tmp' | xargs rm", "find . -name '*.tmp' -exec rm {} \\;"]},
                ]
            },
            {
                "command": "alias",
                "description": "创建命令别名",
                "examples": ["alias ll='ls -la'", "alias ..='cd ..'"],
                "exercises": [
                    {"question": "创建别名 ll 代表 ls -la", "answers": ["alias ll='ls -la'", "alias ll=\"ls -la\""]},
                ]
            },
            {
                "command": "history",
                "description": "显示命令历史",
                "examples": ["history", "history 20", "!123"],
                "exercises": [
                    {"question": "显示最近执行的20条命令", "answers": ["history 20", "history | tail -20"]},
                ]
            },
            {
                "command": "!!",
                "description": "执行上一条命令",
                "examples": ["!!", "sudo !!"],
                "exercises": [
                    {"question": "以管理员权限重新执行上一条命令", "answers": ["sudo !!"]},
                ]
            },
        ]
    },
}

class ProgressTracker:
    """进度追踪器"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.progress_file = self.data_dir / "progress.json"
        self.data = self._load_progress()

    def _load_progress(self) -> dict:
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "total_exercises": 0,
            "correct_answers": 0,
            "streak": 0,
            "best_streak": 0,
            "categories_completed": {},
            "commands_practiced": {},
            "last_practice": None,
            "achievements": [],
            "wrong_answers": {},
        }

    def save(self):
        with open(self.progress_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def _ensure_wrong_answers(self):
        """确保数据中包含 wrong_answers 字段（兼容旧数据）"""
        if "wrong_answers" not in self.data:
            self.data["wrong_answers"] = {}

    def record_wrong_answer(self, category: str, command: str, question: str,
                            answers: list, user_answer: str):
        """记录错题到错题本"""
        self._ensure_wrong_answers()
        key = f"{category}::{command}::{question}"
        if key in self.data["wrong_answers"]:
            entry = self.data["wrong_answers"][key]
            entry["wrong_count"] += 1
            entry["last_wrong"] = datetime.now().isoformat()
            entry["last_user_answer"] = user_answer
        else:
            self.data["wrong_answers"][key] = {
                "category": category,
                "command": command,
                "question": question,
                "answers": answers,
                "wrong_count": 1,
                "last_wrong": datetime.now().isoformat(),
                "last_user_answer": user_answer,
            }

    def remove_wrong_answer(self, key: str):
        """从错题本中移除已掌握的题目"""
        self._ensure_wrong_answers()
        if key in self.data["wrong_answers"]:
            del self.data["wrong_answers"][key]

    def get_wrong_exercises(self) -> list:
        """获取错题列表，按错误次数降序排列"""
        self._ensure_wrong_answers()
        wrong = self.data["wrong_answers"]
        exercises = []
        for key, entry in wrong.items():
            exercises.append({"key": key, **entry})
        exercises.sort(key=lambda x: x["wrong_count"], reverse=True)
        return exercises

    def record_attempt(self, category: str, command: str, correct: bool):
        self.data["total_exercises"] += 1
        if correct:
            self.data["correct_answers"] += 1
            self.data["streak"] += 1
            self.data["best_streak"] = max(self.data["best_streak"], self.data["streak"])
        else:
            self.data["streak"] = 0

        if category not in self.data["categories_completed"]:
            self.data["categories_completed"][category] = {"total": 0, "correct": 0}
        self.data["categories_completed"][category]["total"] += 1
        if correct:
            self.data["categories_completed"][category]["correct"] += 1

        if command not in self.data["commands_practiced"]:
            self.data["commands_practiced"][command] = {"total": 0, "correct": 0}
        self.data["commands_practiced"][command]["total"] += 1
        if correct:
            self.data["commands_practiced"][command]["correct"] += 1

        self.data["last_practice"] = datetime.now().isoformat()
        self._check_achievements()
        self.save()

    def _check_achievements(self):
        achievements = []
        if self.data["total_exercises"] >= 10 and "初学者" not in self.data["achievements"]:
            achievements.append("初学者")
        if self.data["total_exercises"] >= 50 and "练习达人" not in self.data["achievements"]:
            achievements.append("练习达人")
        if self.data["total_exercises"] >= 100 and "终端大师" not in self.data["achievements"]:
            achievements.append("终端大师")
        if self.data["streak"] >= 5 and "连胜新秀" not in self.data["achievements"]:
            achievements.append("连胜新秀")
        if self.data["streak"] >= 10 and "连胜达人" not in self.data["achievements"]:
            achievements.append("连胜达人")
        if self.data["best_streak"] >= 20 and "连胜大师" not in self.data["achievements"]:
            achievements.append("连胜大师")

        for ach in achievements:
            if ach not in self.data["achievements"]:
                self.data["achievements"].append(ach)
                print(colored(f"\n🏆 解锁成就: {ach}!", Colors.YELLOW + Colors.BOLD))

    def get_accuracy(self) -> float:
        if self.data["total_exercises"] == 0:
            return 0.0
        return (self.data["correct_answers"] / self.data["total_exercises"]) * 100

    def get_stats(self) -> dict:
        return {
            "total": self.data["total_exercises"],
            "correct": self.data["correct_answers"],
            "accuracy": self.get_accuracy(),
            "streak": self.data["streak"],
            "best_streak": self.data["best_streak"],
            "achievements": self.data["achievements"],
        }


class TermTrainer:
    """终端命令练习器主类"""

    def __init__(self):
        self.data_dir = Path.home() / ".termtrainer"
        self.progress = ProgressTracker(self.data_dir)
        self.current_category = None

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_header(self):
        header = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ████████╗███████╗██████╗ ███╗   ███╗                       ║
║   ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║                       ║
║      ██║   █████╗  ██████╔╝██╔████╔██║                       ║
║      ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║                       ║
║      ██║   ███████╗██║  ██║██║ ╚═╝ ██║                       ║
║      ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝                       ║
║                                                               ║
║   ████████╗██████╗  █████╗ ██╗███╗   ██╗███████╗██████╗      ║
║   ╚══██╔══╝██╔══██╗██╔══██╗██║████╗  ██║██╔════╝██╔══██╗     ║
║      ██║   ██████╔╝███████║██║██╔██╗ ██║█████╗  ██████╔╝     ║
║      ██║   ██╔══██╗██╔══██║██║██║╚██╗██║██╔══╝  ██╔══██╗     ║
║      ██║   ██║  ██║██║  ██║██║██║ ╚████║███████╗██║  ██║     ║
║      ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝     ║
║                                                               ║
║          🖥️  macOS 终端命令练习器  🖥️                         ║
║              成为高效的终端程序员                              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
        print(colored(header, Colors.CYAN))

    def print_menu(self):
        stats = self.progress.get_stats()
        print(f"\n{colored('📊 你的进度:', Colors.YELLOW)} "
              f"练习 {stats['total']} 题 | "
              f"正确率 {stats['accuracy']:.1f}% | "
              f"当前连胜 {stats['streak']} | "
              f"最佳连胜 {stats['best_streak']}")

        if stats['achievements']:
            print(f"{colored('🏆 成就:', Colors.YELLOW)} {', '.join(stats['achievements'])}")

        print(colored("\n═══════════════════════════════════════════════════════════════", Colors.DIM))
        print(colored("\n📚 选择学习模块:\n", Colors.BOLD))

        for i, (key, cat) in enumerate(COMMANDS_DB.items(), 1):
            cmd_count = len(cat["commands"])
            print(f"  {colored(f'[{i}]', Colors.CYAN)} {cat['icon']} {cat['name']:<12} "
                  f"{colored(f'({cmd_count} 个命令)', Colors.DIM)}")

        print(colored("\n═══════════════════════════════════════════════════════════════", Colors.DIM))
        wrong_count = len(self.progress.get_wrong_exercises())
        wrong_label = f" ({wrong_count}题)" if wrong_count > 0 else ""
        print(f"\n  {colored('[a]', Colors.GREEN)} 📖 查看所有命令")
        print(f"  {colored('[r]', Colors.GREEN)} 🎲 随机练习")
        print(f"  {colored('[w]', Colors.GREEN)} 📕 错题本{colored(wrong_label, Colors.RED) if wrong_count else ''}")
        print(f"  {colored('[s]', Colors.GREEN)} 📈 查看详细统计")
        print(f"  {colored('[h]', Colors.GREEN)} ❓ 帮助")
        print(f"  {colored('[q]', Colors.GREEN)} 🚪 退出")
        print()

    def show_all_commands(self):
        self.clear_screen()
        print(colored("\n📖 命令参考手册\n", Colors.BOLD + Colors.CYAN))

        for key, cat in COMMANDS_DB.items():
            print(colored(f"\n{cat['icon']} {cat['name']}", Colors.YELLOW + Colors.BOLD))
            print(colored("─" * 50, Colors.DIM))
            for cmd in cat["commands"]:
                cmd_name = cmd['command'].ljust(12)
                print(f"  {colored(cmd_name, Colors.GREEN)} {cmd['description']}")

        print(colored("\n按 Enter 返回主菜单...", Colors.DIM))
        input()

    def show_help(self):
        self.clear_screen()
        help_text = """
╔═══════════════════════════════════════════════════════════════╗
║                        ❓ 使用帮助                            ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  🎯 目标                                                       ║
║  ────────                                                     ║
║  通过练习熟悉常用的macOS终端命令，提高命令行操作效率          ║
║                                                               ║
║  📝 如何练习                                                   ║
║  ────────                                                     ║
║  1. 选择一个命令类别进行练习                                  ║
║  2. 阅读问题描述，输入你认为正确的命令                        ║
║  3. 系统会告诉你答案是否正确，并显示正确答案                  ║
║  4. 支持多个正确答案（不同的实现方式）                        ║
║                                                               ║
║  📕 错题本                                                     ║
║  ────────                                                     ║
║  • 答错的题目会自动记录到错题本                               ║
║  • 在主菜单按 [w] 打开错题本                                  ║
║  • 错题练习中答对的题目会自动移除                             ║
║  • 错题按错误次数排序，帮你针对弱点练习                      ║
║                                                               ║
║  💡 提示                                                       ║
║  ────────                                                     ║
║  • 输入 'hint' 获取提示                                       ║
║  • 输入 'skip' 跳过当前题目                                   ║
║  • 输入 'quit' 返回上级菜单                                   ║
║  • 答案不区分多余空格，但命令和参数顺序需正确                 ║
║                                                               ║
║  🏆 成就系统                                                   ║
║  ────────                                                     ║
║  • 初学者: 完成10道练习题                                     ║
║  • 练习达人: 完成50道练习题                                   ║
║  • 终端大师: 完成100道练习题                                  ║
║  • 连胜新秀: 连续答对5题                                      ║
║  • 连胜达人: 连续答对10题                                     ║
║  • 连胜大师: 连续答对20题                                     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
        print(colored(help_text, Colors.CYAN))
        print(colored("\n按 Enter 返回主菜单...", Colors.DIM))
        input()

    def show_stats(self):
        self.clear_screen()
        stats = self.progress.get_stats()

        print(colored("\n📈 详细统计\n", Colors.BOLD + Colors.CYAN))
        print(colored("═" * 50, Colors.DIM))

        print(f"\n{colored('总体统计', Colors.YELLOW + Colors.BOLD)}")
        print(f"  总练习数: {stats['total']}")
        print(f"  正确数: {stats['correct']}")
        print(f"  正确率: {stats['accuracy']:.1f}%")
        print(f"  当前连胜: {stats['streak']}")
        print(f"  最佳连胜: {stats['best_streak']}")

        if stats['achievements']:
            print(f"\n{colored('🏆 已获成就', Colors.YELLOW + Colors.BOLD)}")
            for ach in stats['achievements']:
                print(f"  • {ach}")

        cat_stats = self.progress.data.get("categories_completed", {})
        if cat_stats:
            print(f"\n{colored('分类统计', Colors.YELLOW + Colors.BOLD)}")
            for cat, data in cat_stats.items():
                if cat in COMMANDS_DB:
                    cat_name = COMMANDS_DB[cat]["name"]
                    acc = (data["correct"] / data["total"] * 100) if data["total"] > 0 else 0
                    bar_len = int(acc / 5)
                    bar = "█" * bar_len + "░" * (20 - bar_len)
                    print(f"  {cat_name:<10} [{bar}] {acc:.0f}% ({data['correct']}/{data['total']})")

        print(colored("\n按 Enter 返回主菜单...", Colors.DIM))
        input()

    def normalize_answer(self, answer: str) -> str:
        """规范化答案用于比较"""
        return ' '.join(answer.strip().split())

    def check_answer(self, user_answer: str, correct_answers: list) -> bool:
        """检查答案是否正确"""
        normalized_user = self.normalize_answer(user_answer)
        for ans in correct_answers:
            if self.normalize_answer(ans) == normalized_user:
                return True
        return False

    def practice_category(self, category_key: str):
        """练习特定类别"""
        category = COMMANDS_DB[category_key]
        exercises = []

        for cmd in category["commands"]:
            for ex in cmd.get("exercises", []):
                exercises.append({
                    "command": cmd["command"],
                    "description": cmd["description"],
                    "examples": cmd["examples"],
                    **ex
                })

        if not exercises:
            print(colored("该类别暂无练习题", Colors.YELLOW))
            return

        random.shuffle(exercises)

        self.clear_screen()
        print(colored(f"\n{category['icon']} {category['name']} - 练习模式\n", Colors.BOLD + Colors.CYAN))
        print(colored("输入 'hint' 获取提示, 'skip' 跳过, 'quit' 退出\n", Colors.DIM))
        print(colored("═" * 60, Colors.DIM))

        question_num = 0
        session_total = 0
        session_correct = 0
        for ex in exercises:
            question_num += 1
            print(f"\n{colored(f'题目 {question_num}/{len(exercises)}', Colors.YELLOW)}")
            print(f"{colored('命令:', Colors.DIM)} {ex['command']} - {ex['description']}")
            print(f"\n{colored('❓ 问题:', Colors.CYAN)} {ex['question']}")

            while True:
                try:
                    user_input = input(colored("\n💻 你的答案: ", Colors.GREEN)).strip()
                except EOFError:
                    return

                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'skip':
                    print(colored(f"\n⏭️  跳过。正确答案: {ex['answers'][0]}", Colors.YELLOW))
                    self.progress.record_attempt(category_key, ex['command'], False)
                    self.progress.record_wrong_answer(
                        category_key, ex['command'], ex['question'],
                        ex['answers'], '(跳过)')
                    session_total += 1
                    break
                elif user_input.lower() == 'hint':
                    print(colored(f"\n💡 提示: 命令以 '{ex['command']}' 开头", Colors.YELLOW))
                    print(colored(f"   示例: {', '.join(ex['examples'][:2])}", Colors.DIM))
                    continue
                elif not user_input:
                    continue

                session_total += 1
                if self.check_answer(user_input, ex['answers']):
                    print(colored("\n✅ 正确！", Colors.GREEN + Colors.BOLD))
                    self.progress.record_attempt(category_key, ex['command'], True)
                    session_correct += 1
                else:
                    print(colored("\n❌ 错误", Colors.RED))
                    print(colored(f"   正确答案: {ex['answers'][0]}", Colors.YELLOW))
                    if len(ex['answers']) > 1:
                        print(colored(f"   其他写法: {', '.join(ex['answers'][1:])}", Colors.DIM))
                    self.progress.record_attempt(category_key, ex['command'], False)
                    self.progress.record_wrong_answer(
                        category_key, ex['command'], ex['question'],
                        ex['answers'], user_input)
                break

            if user_input.lower() == 'quit':
                break

            print(colored("─" * 60, Colors.DIM))

        print(colored("\n🎉 该类别练习完成！", Colors.GREEN + Colors.BOLD))
        session_accuracy = (session_correct / session_total * 100) if session_total > 0 else 0
        stats = self.progress.get_stats()
        print(f"本轮正确率: {session_accuracy:.1f}% ({session_correct}/{session_total}) | 连胜: {stats['streak']}")
        print(colored("\n按 Enter 返回主菜单...", Colors.DIM))
        input()

    def random_practice(self, count: int = 10):
        """随机练习"""
        all_exercises = []
        for cat_key, category in COMMANDS_DB.items():
            for cmd in category["commands"]:
                for ex in cmd.get("exercises", []):
                    all_exercises.append({
                        "category_key": cat_key,
                        "category_name": category["name"],
                        "command": cmd["command"],
                        "description": cmd["description"],
                        "examples": cmd["examples"],
                        **ex
                    })

        random.shuffle(all_exercises)
        exercises = all_exercises[:count]

        self.clear_screen()
        print(colored(f"\n🎲 随机练习 ({count}题)\n", Colors.BOLD + Colors.CYAN))
        print(colored("输入 'hint' 获取提示, 'skip' 跳过, 'quit' 退出\n", Colors.DIM))
        print(colored("═" * 60, Colors.DIM))

        question_num = 0
        session_total = 0
        session_correct = 0
        for ex in exercises:
            question_num += 1
            cat_name = ex['category_name']
            print(f"\n{colored(f'题目 {question_num}/{len(exercises)}', Colors.YELLOW)} "
                  f"{colored(f'[{cat_name}]', Colors.DIM)}")
            print(f"{colored('命令:', Colors.DIM)} {ex['command']} - {ex['description']}")
            print(f"\n{colored('❓ 问题:', Colors.CYAN)} {ex['question']}")

            while True:
                try:
                    user_input = input(colored("\n💻 你的答案: ", Colors.GREEN)).strip()
                except EOFError:
                    return

                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'skip':
                    print(colored(f"\n⏭️  跳过。正确答案: {ex['answers'][0]}", Colors.YELLOW))
                    self.progress.record_attempt(ex['category_key'], ex['command'], False)
                    self.progress.record_wrong_answer(
                        ex['category_key'], ex['command'], ex['question'],
                        ex['answers'], '(跳过)')
                    session_total += 1
                    break
                elif user_input.lower() == 'hint':
                    print(colored(f"\n💡 提示: 命令以 '{ex['command']}' 开头", Colors.YELLOW))
                    print(colored(f"   示例: {', '.join(ex['examples'][:2])}", Colors.DIM))
                    continue
                elif not user_input:
                    continue

                session_total += 1
                if self.check_answer(user_input, ex['answers']):
                    print(colored("\n✅ 正确！", Colors.GREEN + Colors.BOLD))
                    self.progress.record_attempt(ex['category_key'], ex['command'], True)
                    session_correct += 1
                else:
                    print(colored("\n❌ 错误", Colors.RED))
                    print(colored(f"   正确答案: {ex['answers'][0]}", Colors.YELLOW))
                    if len(ex['answers']) > 1:
                        print(colored(f"   其他写法: {', '.join(ex['answers'][1:])}", Colors.DIM))
                    self.progress.record_attempt(ex['category_key'], ex['command'], False)
                    self.progress.record_wrong_answer(
                        ex['category_key'], ex['command'], ex['question'],
                        ex['answers'], user_input)
                break

            if user_input.lower() == 'quit':
                break

            print(colored("─" * 60, Colors.DIM))

        print(colored("\n🎉 随机练习完成！", Colors.GREEN + Colors.BOLD))
        session_accuracy = (session_correct / session_total * 100) if session_total > 0 else 0
        stats = self.progress.get_stats()
        print(f"本轮正确率: {session_accuracy:.1f}% ({session_correct}/{session_total}) | 连胜: {stats['streak']}")
        print(colored("\n按 Enter 返回主菜单...", Colors.DIM))
        input()

    def show_wrong_notebook(self):
        """查看错题本"""
        self.clear_screen()
        wrong_exercises = self.progress.get_wrong_exercises()

        print(colored("\n📕 错题本\n", Colors.BOLD + Colors.CYAN))
        print(colored("═" * 60, Colors.DIM))

        if not wrong_exercises:
            print(colored("\n🎉 错题本是空的，你太棒了！", Colors.GREEN + Colors.BOLD))
            print(colored("\n按 Enter 返回主菜单...", Colors.DIM))
            input()
            return

        print(f"\n共有 {colored(str(len(wrong_exercises)), Colors.YELLOW + Colors.BOLD)} 道错题\n")

        for i, ex in enumerate(wrong_exercises, 1):
            cat_name = COMMANDS_DB.get(ex['category'], {}).get('name', ex['category'])
            print(f"  {colored(f'{i}.', Colors.CYAN)} [{cat_name}] "
                  f"{colored(ex['command'], Colors.GREEN)} - {ex['question']}")
            wrong_count_val = ex['wrong_count']
            print(f"     {colored(f'错误次数: {wrong_count_val}', Colors.RED)} | "
                  f"正确答案: {colored(ex['answers'][0], Colors.YELLOW)}")
            if ex.get('last_user_answer'):
                print(f"     上次回答: {colored(ex['last_user_answer'], Colors.DIM)}")
            print()

        print(colored("─" * 60, Colors.DIM))
        print(f"\n  {colored('[p]', Colors.GREEN)} 开始练习错题")
        print(f"  {colored('[c]', Colors.GREEN)} 清空错题本")
        print(f"  {colored('[Enter]', Colors.GREEN)} 返回主菜单")

        choice = input(colored("\n请选择 > ", Colors.GREEN)).strip().lower()
        if choice == 'p':
            self.practice_wrong_answers()
        elif choice == 'c':
            confirm = input(colored("确认清空错题本？(y/n) > ", Colors.YELLOW)).strip().lower()
            if confirm == 'y':
                self.progress._ensure_wrong_answers()
                self.progress.data["wrong_answers"] = {}
                self.progress.save()
                print(colored("\n✅ 错题本已清空", Colors.GREEN))
                input(colored("按 Enter 返回主菜单...", Colors.DIM))

    def practice_wrong_answers(self):
        """错题练习模式"""
        wrong_exercises = self.progress.get_wrong_exercises()

        if not wrong_exercises:
            print(colored("\n🎉 错题本是空的，没有需要复习的题目！", Colors.GREEN))
            input(colored("按 Enter 返回主菜单...", Colors.DIM))
            return

        self.clear_screen()
        print(colored(f"\n📕 错题练习 ({len(wrong_exercises)}题)\n", Colors.BOLD + Colors.CYAN))
        print(colored("答对的题目将从错题本中移除", Colors.DIM))
        print(colored("输入 'hint' 获取提示, 'skip' 跳过, 'quit' 退出\n", Colors.DIM))
        print(colored("═" * 60, Colors.DIM))

        removed_count = 0
        question_num = 0

        for ex in wrong_exercises:
            question_num += 1
            cat_name = COMMANDS_DB.get(ex['category'], {}).get('name', ex['category'])

            # 查找对应命令的 examples
            examples = []
            cat_data = COMMANDS_DB.get(ex['category'], {})
            for cmd in cat_data.get('commands', []):
                if cmd['command'] == ex['command']:
                    examples = cmd.get('examples', [])
                    break

            wrong_count_val = ex['wrong_count']
            print(f"\n{colored(f'题目 {question_num}/{len(wrong_exercises)}', Colors.YELLOW)} "
                  f"{colored(f'[{cat_name}]', Colors.DIM)} "
                  f"{colored(f'(错{wrong_count_val}次)', Colors.RED)}")
            print(f"{colored('命令:', Colors.DIM)} {ex['command']}")
            print(f"\n{colored('❓ 问题:', Colors.CYAN)} {ex['question']}")

            while True:
                try:
                    user_input = input(colored("\n💻 你的答案: ", Colors.GREEN)).strip()
                except EOFError:
                    return

                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'skip':
                    print(colored(f"\n⏭️  跳过。正确答案: {ex['answers'][0]}", Colors.YELLOW))
                    break
                elif user_input.lower() == 'hint':
                    print(colored(f"\n💡 提示: 命令以 '{ex['command']}' 开头", Colors.YELLOW))
                    if examples:
                        print(colored(f"   示例: {', '.join(examples[:2])}", Colors.DIM))
                    continue
                elif not user_input:
                    continue

                if self.check_answer(user_input, ex['answers']):
                    print(colored("\n✅ 正确！已从错题本移除", Colors.GREEN + Colors.BOLD))
                    self.progress.remove_wrong_answer(ex['key'])
                    self.progress.record_attempt(ex['category'], ex['command'], True)
                    removed_count += 1
                else:
                    print(colored("\n❌ 还是错了，继续加油！", Colors.RED))
                    print(colored(f"   正确答案: {ex['answers'][0]}", Colors.YELLOW))
                    if len(ex['answers']) > 1:
                        print(colored(f"   其他写法: {', '.join(ex['answers'][1:])}", Colors.DIM))
                    self.progress.record_attempt(ex['category'], ex['command'], False)
                    self.progress.record_wrong_answer(
                        ex['category'], ex['command'], ex['question'],
                        ex['answers'], user_input)
                break

            if user_input.lower() == 'quit':
                break

            print(colored("─" * 60, Colors.DIM))

        remaining = len(wrong_exercises) - removed_count
        print(colored("\n📕 错题练习完成！", Colors.GREEN + Colors.BOLD))
        print(f"本次答对 {colored(str(removed_count), Colors.GREEN)} 题，"
              f"还剩 {colored(str(remaining), Colors.YELLOW)} 道错题")
        session_accuracy = (removed_count / question_num * 100) if question_num > 0 else 0
        stats = self.progress.get_stats()
        print(f"本轮正确率: {session_accuracy:.1f}% ({removed_count}/{question_num}) | 连胜: {stats['streak']}")
        print(colored("\n按 Enter 返回主菜单...", Colors.DIM))
        input()

    def run(self):
        """主运行循环"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_menu()

            try:
                choice = input(colored("请选择 > ", Colors.GREEN)).strip().lower()
            except (EOFError, KeyboardInterrupt):
                print(colored("\n\n👋 再见！继续加油练习终端命令！", Colors.CYAN))
                break

            if choice == 'q':
                print(colored("\n👋 再见！继续加油练习终端命令！", Colors.CYAN))
                break
            elif choice == 'a':
                self.show_all_commands()
            elif choice == 'r':
                self.random_practice()
            elif choice == 'w':
                self.show_wrong_notebook()
            elif choice == 's':
                self.show_stats()
            elif choice == 'h':
                self.show_help()
            elif choice.isdigit():
                idx = int(choice) - 1
                categories = list(COMMANDS_DB.keys())
                if 0 <= idx < len(categories):
                    self.practice_category(categories[idx])
                else:
                    print(colored("无效选择，请重试", Colors.RED))
                    input()


def main():
    trainer = TermTrainer()
    trainer.run()


if __name__ == "__main__":
    main()

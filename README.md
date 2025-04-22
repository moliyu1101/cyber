# 网络攻击测试工具

这是一个带有Web界面的网络攻击测试工具，支持TCP SYN洪水攻击和ARP欺骗攻击。本工具**仅供网络安全测试和教育目的使用**。

## 功能特点

- 现代化、用户友好的Web界面
- TCP SYN洪水攻击功能
- ARP欺骗攻击功能
- 支持自动检测网关和网络接口
- 多线程攻击能力

## 安装要求

- Python 3.6+
- Flask
- Scapy

## 安装步骤

1. 克隆此仓库：

```bash
git clone https://github.com/yourusername/network-attack-tool.git
cd network-attack-tool
```

2. 安装所需依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

1. 启动Web应用：

```bash
cd app
sudo python app.py
```

> 注意：需要使用`sudo`权限运行，因为网络攻击工具需要访问底层网络接口。

2. 在Web浏览器中访问：`http://127.0.0.1:5000`

3. 在Web界面中，选择所需的攻击类型并填写必要的信息：

### TCP SYN洪水攻击
- 目标IP地址（必填）
- 目标端口（必填）
- 攻击持续时间（默认：60秒）
- 线程数（默认：10）

### ARP欺骗攻击
- 目标IP地址（必填）
- 网关IP地址（可选，留空自动检测）
- 网络接口（可选，留空自动检测）

## 免责声明

本工具仅供网络安全测试和教育目的使用。未经授权对计算机系统和网络进行攻击属于违法行为。使用者需承担所有法律责任。作者对工具的使用所造成的任何后果不承担责任。

## 可能的常见问题

1. **运行时出现权限错误**

   确保使用`sudo`权限运行：
   ```bash
   sudo python app.py
   ```

2. **无法导入Scapy模块**

   确保正确安装了Scapy：
   ```bash
   pip install scapy
   ```

3. **ARP攻击无法自动检测网关或接口**

   手动指定网关IP和网络接口：
   ```
   网关IP：可通过命令 `route -n get default | grep gateway` (MacOS) 或 `ip route | grep default` (Linux) 获取
   网络接口：可通过命令 `ifconfig` 查看可用网络接口
   ```

## 注意事项

- 本工具在Windows系统上可能会有兼容性问题，建议在Linux或MacOS系统上运行。
- 某些网络环境或防火墙设置可能会阻止或限制攻击效果。
- 根据不同的操作系统和网络环境，可能需要修改代码中的某些参数以获得最佳效果。 

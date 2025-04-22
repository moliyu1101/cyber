#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from flask import Flask, render_template, request, jsonify
from attack_utils import AttackTools

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/syn_flood', methods=['POST'])
def syn_flood():
    """执行TCP SYN洪水攻击"""
    data = request.json
    target_ip = data.get('target_ip', '')
    target_port = data.get('target_port', '')
    attack_time = int(data.get('attack_time', 60))
    threads = int(data.get('threads', 10))
    
    # 执行攻击
    result = AttackTools.syn_flood(target_ip, target_port, attack_time, threads)
    return jsonify(result)

@app.route('/syn_flood/status', methods=['GET'])
def syn_flood_status():
    """获取TCP SYN洪水攻击的状态"""
    attack_id = request.args.get('attack_id')
    result = AttackTools.get_syn_flood_status(attack_id)
    return jsonify(result)

@app.route('/syn_flood/stop', methods=['POST'])
def stop_syn_flood():
    """停止TCP SYN洪水攻击"""
    data = request.json
    attack_id = data.get('attack_id')
    result = AttackTools.stop_syn_flood(attack_id)
    return jsonify(result)

@app.route('/arp_spoof', methods=['POST'])
def arp_spoof():
    """执行ARP欺骗攻击"""
    data = request.json
    target_ip = data.get('target_ip', '')
    gateway_ip = data.get('gateway_ip', '')
    interface = data.get('interface', '')
    
    # 执行攻击
    result = AttackTools.arp_spoof(target_ip, gateway_ip, interface)
    return jsonify(result)

@app.route('/arp_spoof/status', methods=['GET'])
def arp_spoof_status():
    """获取ARP欺骗攻击的状态"""
    attack_id = request.args.get('attack_id')
    result = AttackTools.get_arp_spoof_status(attack_id)
    return jsonify(result)

@app.route('/arp_spoof/stop', methods=['POST'])
def stop_arp_spoof():
    """停止ARP欺骗攻击"""
    data = request.json
    attack_id = data.get('attack_id')
    result = AttackTools.stop_arp_spoof(attack_id)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True) 
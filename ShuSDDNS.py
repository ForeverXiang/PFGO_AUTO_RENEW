import sys
import requests
import hashlib
import json
import configparser
from pathlib import Path
from datetime import datetime

def get_config_path():
    """
    获取配置文件的路径。这将根据应用是直接运行还是通过PyInstaller打包后运行来确定。
    """
    if getattr(sys, 'frozen', False):
        # 如果程序是通过PyInstaller打包的，则使用可执行文件所在的目录
        dir_path = Path(sys.executable).parent
    else:
        # 如果程序是直接运行的，则使用脚本所在的目录
        dir_path = Path(__file__).parent
    return dir_path / 'ShuSDDNS.config'

def read_config(config_path):
    config = configparser.ConfigParser()
    with open(config_path, 'r', encoding='utf-8') as configfile:
        config.read_file(configfile)
    return config['DEFAULT']

def get_rules_with_node_info(api_url, api_id, api_token):
    def call_api(action, data=None):
        token_md5 = hashlib.md5(api_token.encode()).hexdigest()
        headers = {"Content-Type": "application/json"}
        params = {"id": api_id, "token": token_md5, "action": action}
        json_data = json.dumps(data) if data else None
        response = requests.post(api_url, headers=headers, params=params, data=json_data)
        return response.json()['data'] if response.ok and response.json().get('success') else None

    rules_data = call_api("list_rules")
    if not rules_data:
        return []

    rules_info = []
    for _, rule_details in rules_data.items():
        node_info = call_api("get_node_info", {"node_id": rule_details['node']})
        rules_info.append({
            "id": rule_details['id'],
            "remoteip": rule_details['remoteip'],
            "remoteport": rule_details['remoteport'],
            "node": rule_details['node'],
            "msg": rule_details['msg'],
            "node_name": node_info.get('name', 'Unknown') if node_info else 'Unknown',
            "node_addr": node_info.get('addr', 'Unknown') if node_info else 'Unknown',
        })

    return rules_info

def update_dns_record(cf_api_token, zone_id, domain, subdomain, ip):
    headers = {
        "Authorization": f"Bearer {cf_api_token}",
        "Content-Type": "application/json"
    }
    dns_record_name = f"{subdomain}.{domain}"
    get_records_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?name={dns_record_name}"
    records_response = requests.get(get_records_url, headers=headers)
    records = records_response.json()["result"]

    if records:
        record = records[0]
        if record["content"] == ip:
            # If the IP address has not changed, skip update
            return {"status": "skipped", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        record_id = record["id"]
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
        data = {"type": "A", "name": dns_record_name, "content": ip, "ttl": 1}
        update_response = requests.put(url, headers=headers, json=data)
    else:
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
        data = {"type": "A", "name": dns_record_name, "content": ip, "ttl": 1}
        update_response = requests.post(url, headers=headers, json=data)

    status = "success" if update_response.ok else "failed"
    return {"status": status, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

def main():
    config_path = get_config_path()
    config = read_config(config_path)
    api_url = config['API_URL']
    api_id = config['API_ID']
    api_token = config['API_TOKEN']
    cf_api_token = config['CLOUDFLARE_API_TOKEN']
    zone_id = config['ZONE_ID']
    domain = config['DOMAIN']

    rules_info = get_rules_with_node_info(api_url, api_id, api_token)
    dns_updates = []
    for rule in rules_info:
        update_result = update_dns_record(cf_api_token, zone_id, domain, rule["msg"], rule["node_addr"])
        if update_result["status"] != "skipped":
            dns_updates.append({
                "subdomain": rule["msg"],
                "ip": rule["node_addr"],
                "status": update_result["status"],
                "timestamp": update_result["timestamp"]
            })

    # Write to file only if there are updates
    if dns_updates:
        with open("ShuSDDNS_record.json", "w", encoding='utf-8') as file:
            json.dump({"rules_info": rules_info, "dns_updates": dns_updates}, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
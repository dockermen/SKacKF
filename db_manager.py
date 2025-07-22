import argparse
import sqlite3
from datetime import datetime, timedelta, timezone
import time
from datebase import *
import uuid
import json
import requests


def list_all_users():
    """List all users from user_info table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT user_name, expire_time, account_num, remain_num, is_activated FROM user_info')
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No users found.")
        return
        
    print("\nUser List:")
    print("-" * 80)
    print(f"{'Username':<20} {'Expire Time':<20} {'Account Num':<12} {'Remain':<8} {'Active'}")
    print("-" * 80)
    for row in rows:
        print(f"{row[0]:<20} {row[1]:<20} {row[2]:<12} {row[3]:<8} {'Yes' if row[4] else 'No'}")

def list_all_devices():
    """List all devices from user_device table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, status, expire_time, augmentSession FROM user_device')
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No devices found.")
        return
        
    print("\nDevice List:")
    print("-" * 70)
    print(f"{'ID':<5} {'Email':<30} {'Status':<8} {'Expire Time'}")
    print("-" * 70)
    for row in rows:
        augsession = json.loads(row[4])
        print(f"{row[0]:<5} {row[1]:<30} {'Active' if row[2] else 'Inactive':<8} {row[3]} Token: {augsession.get('accessToken')} Url: {augsession.get('tenantURL')}")


def check_device_endtime():
    """Update all devices Session Endtime from user_device table"""
    s = requests.session()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_device where status = 1')
    rows = cursor.fetchall()
    
    def _is_expire_time_more_than_one_day(expire_time_str):
        from datetime import datetime, timedelta, timezone
        import re
        """
        判断expire_time（UTC）和当前上海时间（UTC+8）相差是否满1天（24小时）。
        :param expire_time_str: 过期时间字符串，格式如 '2025-07-20T05:08:44Z' 或 '2025-08-01T06:21:57.857044098Z'
        :return: 满1天返回True，否则False
        """
        # 只取到秒，去掉小数点后内容
        match = re.match(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", expire_time_str)
        if match:
            expire_time_str = match.group(1) + "Z"

        # 解析为UTC时间
        try:
            expire_time = datetime.strptime(expire_time_str, "%Y-%m-%dT%H:%M:%SZ")
            expire_time = expire_time.replace(tzinfo=timezone.utc)
        except Exception as e:
            print(f"时间格式错误: {expire_time_str}")
            return False

        # 获取当前上海时间
        shanghai_tz = timezone(timedelta(hours=8))
        now_shanghai = datetime.now(shanghai_tz)

        # 计算 expire_time（UTC）和 now_shanghai（UTC+8）之间的时间差
        # 先把 now_shanghai 转为 UTC
        now_utc = now_shanghai.astimezone(timezone.utc)
        delta = expire_time - now_utc

        # 判断是否大于等于1天
        return delta >= timedelta(days=1)

    def _check_user_status1(url,accessToken):
        now = datetime.now().replace(microsecond=500000) - timedelta(hours=8)


        url = url+"record-session-events"
        header = {
                "Content-Type": "application/json",
                "User-Agent": "Augment.vscode-augment/0.482.1 (win32; x64; 10.0.19045) vscode/1.95.3",
                "x-request-id": str(uuid.uuid4()),
                "x-request-session-id": str(uuid.uuid4()),
                "x-api-version": "2",
                "Authorization":f"Bearer {accessToken}"
            }
        body = {
                "client_name": "vscode-extension",
                "events": [
                    {
                        "time": now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z",
                        "event": {
                            "onboarding_session_event": {
                                "event_time_sec": int(time.time()),
                                "event_time_nsec": 500000000,
                                "event_name": "used-chat",
                                "user_agent": "Augment.vscode-augment/0.487.1 (win32; x64; 10.0.19045) vscode/1.95.3"
                            }
                        }
                    }
                ]
            }
        res = s.post(url,headers=header,json=body,timeout=10)
        if "suspended" in res.text:
            return False,f"id: {id} 邮箱: {email} 账号已暂停 {res.text}"
        return True,True

    for row in rows:
        try:
            id,email, augmentSession,status,expire_time,other = row
            # if id != 29:
            #     continue
            #print(id,email, augmentSession,status,expire_time,other)
            accessToken = json.loads(augmentSession).get("accessToken")
            path_url = json.loads(augmentSession).get("tenantURL")
            url = path_url+"subscription-info"
            status,msg = _check_user_status1(path_url,accessToken)
            if not status:
                print(msg)
                update_user_device(email, 0,expire_time=expire_time,other=other)
                continue

            header = {
                "Content-Type": "application/json",
                "User-Agent": "Augment.vscode-augment/0.482.1 (win32; x64; 10.0.19045) vscode/1.95.3",
                "x-request-id": str(uuid.uuid4()),
                "x-request-session-id": str(uuid.uuid4()),
                "x-api-version": "2",
                "Authorization":f"Bearer {accessToken}"
            }
            res = s.post(url,headers=header,json={},timeout=10)
            if "InactiveSubscription" in res.text or "Invalid token" in res.text:
                print(f"id: {id} 邮箱: {email} 账号已失效")
                update_user_device(email, 0,expire_time=expire_time,other=other)
                continue
            res = res.json()
            activesubscription = res.get("subscription").get("ActiveSubscription","")
            usage_balance_depleted = activesubscription.get("usage_balance_depleted",False)
            end_date = activesubscription.get("end_date","")
            if end_date and not _is_expire_time_more_than_one_day(end_date):
                print(f"id: {id} 邮箱: {email} 到期时间: {end_date} 不足一天，执行禁用")
                update_user_device(email, 0,expire_time=expire_time,other=other)
                continue
            if usage_balance_depleted:
                print(f"id: {id} 邮箱: {email} 余额不足")
                update_user_device(email, 0,expire_time=expire_time,other=other)
            else:
                print(f"id: {id} 邮箱: {email} 到期时间: {end_date} 状态：{not usage_balance_depleted}")
                cursor.execute('''
                    UPDATE user_device
                    SET expire_time = ?
                        WHERE email = ?
                    ''', (end_date,email))
                conn.commit()
        except Exception as e:
            print(f"Error Update all devices Session Endtime from device: {str(e)}")

    
    conn.close()


def add_user(args):
    """Add a new user"""
    try:
        user_id = insert_user_info(
            args.username,
            args.expire_time or datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            args.account_num,
            args.remain_num,
            args.validity_days
        )
        if user_id:
            print(f"Successfully added user: {args.username}")
        else:
            print("Failed to add user. Username might already exist.")
    except Exception as e:
        print(f"Error adding user: {str(e)}")

def update_user_remain(args):
    """disable user remain num"""
    try:
        update_user_remain_num(args.username, args.remain_num)
        print(f"Successfully disable user : {args.username}")
    except Exception as e:
        print(f"Error disable user : {str(e)}")

def add_device(args):
    """Add a new device"""
    try:
        insert_user_device(args.email, args.session, args.expire_time, args.other)
        print(f"Successfully added device with email: {args.email}")
    except sqlite3.IntegrityError:
        print("Error: Email already exists")
    except Exception as e:
        print(f"Error adding device: {str(e)}")

def update_device(args):
    """Update device information"""
    try:
        update_user_device(args.email, args.status,args.session, args.expire_time, args.other)
        print(f"Successfully updated device: {args.email}")
    except Exception as e:
        print(f"Error updating device: {str(e)}")

def delete_device(args):
    """Delete a device"""
    try:
        delete_user_device(args.id)
        print(f"Successfully deleted device with ID: {args.id}")
    except Exception as e:
        print(f"Error deleting device: {str(e)}")

def get_device_statistics():
    """Get statistics about devices including active count, expired count, etc."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取总设备数
    cursor.execute('SELECT COUNT(*) FROM user_device')
    total_count = cursor.fetchone()[0]
    
    # 获取活跃设备数
    cursor.execute('SELECT COUNT(*) FROM user_device WHERE status = 1')
    active_count = cursor.fetchone()[0]
    
    # 获取过期设备数
    cursor.execute('SELECT COUNT(*) FROM user_device WHERE status = 0')
    expired_count = cursor.fetchone()[0]
    
    conn.close()
    
    print("\nDevice Statistics:")
    print("-" * 40)
    print(f"设备总数: {total_count}")
    print(f"活跃设备数: {active_count}")
    print(f"过期设备数: {expired_count}")
    print("-" * 40)


def main():
    parser = argparse.ArgumentParser(description='Database Management CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List commands
    list_parser = subparsers.add_parser('list', help='List records')
    list_parser.add_argument('type', choices=['users', 'devices'], help='Type of records to list')

    check_device_parser = subparsers.add_parser('check', help='Check device')
    check_device_parser.add_argument("device", help='Type of records to list')

    # 添加新的 stats 命令
    stats_parser = subparsers.add_parser('stats', help='Show device statistics')

    # Add user command
    add_user_parser = subparsers.add_parser('add-user', help='Add a new user')
    add_user_parser.add_argument('username', help='Username')
    add_user_parser.add_argument('--account-num', type=int, required=True, help='Number of accounts')
    add_user_parser.add_argument('--remain-num', type=int, required=True, help='Remaining number')
    add_user_parser.add_argument('--expire-time', help='Expiration time (YYYY-MM-DD HH:MM:SS)')
    add_user_parser.add_argument('--validity-days', type=int, default=30, help='Validity period in days')

    # Add device command
    add_device_parser = subparsers.add_parser('add-device', help='Add a new device')
    add_device_parser.add_argument('email', help='Email address')
    add_device_parser.add_argument('session', help='Augment session data')
    add_device_parser.add_argument('--expire-time', help='Expiration time')
    add_device_parser.add_argument('--other', help='Additional information')

    update_user_parser = subparsers.add_parser('update-user', help='Update user')
    update_user_parser.add_argument('username', help='Username')
    update_user_parser.add_argument('--remain-num', type=int, default=0, help='Remaining number')
    # Update device command
    update_device_parser = subparsers.add_parser('update-device', help='Update device information')
    update_device_parser.add_argument('email', help='Email address')
    update_device_parser.add_argument('status', help='status')
    update_device_parser.add_argument('--session', help='New augment session data')
    update_device_parser.add_argument('--expire-time', help='New expiration time')
    update_device_parser.add_argument('--other', help='New additional information')

    # Delete device command
    delete_device_parser = subparsers.add_parser('delete-device', help='Delete a device')
    delete_device_parser.add_argument('id', type=int, help='Device ID to delete')

    args = parser.parse_args()

    if args.command == 'list':
        if args.type == 'users':
            list_all_users()
        else:
            list_all_devices()
    elif args.command == 'stats':  # 添加新的命令处理
        get_device_statistics()
    elif args.command == 'check':
        check_device_endtime()
    elif args.command == 'update-user':
        update_user_remain(args)
    elif args.command == 'add-user':
        add_user(args)
    elif args.command == 'add-device':
        add_device(args)
    elif args.command == 'update-device':
        update_device(args)
    elif args.command == 'delete-device':
        delete_device(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
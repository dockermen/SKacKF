# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = "user_devices.db"

# 创建数据库和数据表（user_device, user_info, user_email）
# 参数：db_path 数据库文件路径
# 返回值：无


def create_db(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_device (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            augmentSession TEXT,
            status INTEGER DEFAULT 1,
            expire_time TEXT,
            other TEXT
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL UNIQUE,
            expire_time TEXT NOT NULL,
            account_num INTEGER NOT NULL,
            remain_num INTEGER NOT NULL,
            is_activated INTEGER DEFAULT 0,
            activated_time TEXT,
            validity_days INTEGER DEFAULT 30
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_email (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            email_id INTEGER NOT NULL,
            status INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES user_info(id),
            FOREIGN KEY (email_id) REFERENCES user_device(id)
        )
    """
    )

    conn.commit()
    conn.close()


def insert_user_device(
    email, augmentSession, expire_time="", other="", db_path=DB_PATH
):
    # 向user_device表插入一条设备记录
    # 参数：email邮箱，augmentSession会话信息，expire_time过期时间（可选），other其他信息（可选），db_path数据库路径
    # 返回值：无
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO user_device (email, augmentSession,expire_time,other)
        VALUES (?, ?, ?, ?)
    """,
        (email, augmentSession, expire_time, other),
    )
    conn.commit()
    conn.close()


def query_user_devices(db_path=DB_PATH, id=None):
    # 查询所有或指定id的设备的邮箱和会话信息
    # 参数：db_path数据库路径，id设备ID（可选）
    # 返回值：包含(email, augmentSession)的列表

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if id:
        cursor.execute(
            "SELECT email,augmentSession FROM user_device WHERE id = ?", (id,)
        )
    else:
        cursor.execute("SELECT email,augmentSession FROM user_device")
    rows = cursor.fetchall()
    conn.close()
    return rows


def query_user_device(
    idnum: int = 3,
    db_path=DB_PATH,
):
    # 随机查询指定数量的可用设备ID
    # 参数：idnum返回的设备ID数量，db_path数据库路径
    # 返回值：设备ID列表
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM user_device WHERE status = 1 ORDER BY RANDOM() LIMIT ?", (idnum,)
    )
    rows = cursor.fetchall()
    if rows:
        rows = [row[0] for row in rows]
    conn.close()
    return rows


def update_user_device(
    email, status, augmentSession=None, expire_time="", other="", db_path=DB_PATH
):
    # 根据邮箱更新设备状态和信息
    # 参数：email邮箱，status状态，augmentSession会话信息（可选），expire_time过期时间（可选），other其他信息（可选），db_path数据库路径
    # 返回值：无
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if augmentSession:
        cursor.execute(
            """
            UPDATE user_device
            SET augmentSession = ?, status = ?, expire_time = ?, other = ?
            WHERE email = ?
        """,
            (augmentSession, status, expire_time, other, email),
        )
    else:
        cursor.execute(
            """
            UPDATE user_device
            SET status = ?, expire_time = ?, other = ?
            WHERE email = ?
        """,
            (status, expire_time, other, email),
        )
    conn.commit()
    conn.close()


def delete_user_device(user_id, db_path=DB_PATH):
    # 根据user_id删除设备
    # 参数：user_id设备ID，db_path数据库路径
    # 返回值：无
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM user_device
        WHERE user_id = ?
    """,
        (user_id,),
    )
    conn.commit()
    conn.close()


def insert_user_info(
    user_name, expire_time, account_num, remain_num, validity_days=30, db_path=DB_PATH
):
    # 插入一条用户信息记录
    # 参数：user_name用户名，expire_time过期时间，account_num账号数，remain_num剩余数，validity_days有效天数（默认30），db_path数据库路径
    # 返回值：插入行的ID或失败返回False
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_info (user_name,expire_time,account_num,remain_num,validity_days)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_name, expire_time, account_num, remain_num, validity_days),
        )

        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id
    except Exception as e:
        return False


def insert_user_email(user_id, email_id, db_path=DB_PATH):
    # 插入一条用户与邮箱的关联关系
    # 参数：user_id用户ID，email_id邮箱ID，db_path数据库路径
    # 返回值：无
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO user_email (user_id,email_id)
        VALUES (?, ?)
    """,
        (user_id, email_id),
    )
    conn.commit()
    conn.close()


def query_user_email(user_name, db_path=DB_PATH):
    # 查询指定用户名的用户信息
    # 参数：user_name用户名，db_path数据库路径
    # 返回值：包含用户信息和邮箱ID的字典或None
    conn = sqlite3.connect(db_path)
    data = {}
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id,account_num,remain_num,expire_time,is_activated,activated_time
        FROM user_info
        WHERE user_name = ? and remain_num > 0 and expire_time > datetime('now', '+8 hours') and is_activated = 1;
    """,
        (user_name,),
    )
    q_rows = cursor.fetchone()
    if q_rows:
        id, account_num, remain_num, expire_time, is_activated, activated_time = q_rows
        data.update(
            {
                "account_num": account_num,
                "remain_num": remain_num,
                "expire_time": expire_time,
                "is_activated": is_activated,
                "activated_time": activated_time,
            }
        )

        cursor.execute(
            """
            SELECT email_id
            FROM user_email
            WHERE user_id = ? and status = 1
            ORDER BY RANDOM() LIMIT 1
        """,
            (id,),
        )
        infoid_to_eid = cursor.fetchone()
        if infoid_to_eid:
            data["infoid_to_eid"] = infoid_to_eid[0]
    conn.close()
    return data


def quer_user_info_extime(user_name, db_path=DB_PATH):
    # 查询指定用户名的过期时间
    # 参数：user_name用户名，db_path数据库路径
    # 返回值：过期时间字符串或None
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT expire_time from user_info
        WHERE user_name = ?
    """,
        (user_name,),
    )
    rows = cursor.fetchone()
    if rows:
        rows = rows[0]
    conn.close()
    return rows


def update_user_email_status(id, status=0, db_path=DB_PATH):
    # 更新user_email表中指定id的状态
    # 参数：id记录ID，status新状态（默认0），db_path数据库路径
    # 返回值：无
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE user_email
        SET status = ?
        WHERE id = ?
    """,
        (status, id),
    )
    conn.commit()
    conn.close()


def query_user_id(user_name, db_path=DB_PATH):
    # 查询指定用户名的用户ID
    # 参数：user_name用户名，db_path数据库路径
    # 返回值：id或None
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM user_info WHERE user_name = ?", (user_name,))
    row = cursor.fetchone()
    conn.close()
    return row


def activate_user(user_name, db_path=DB_PATH):
    # 激活指定用户账号（如未激活）
    # 参数：user_name用户名，db_path数据库路径
    # 返回值：激活成功返回True，否则返回False
    from datetime import datetime

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    result = cursor.fetchone()

    if result and result[0] == 0:
        activated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        validity_days = result[1] if result[1] else 30

        cursor.execute(
            """
            UPDATE user_info
            SET is_activated = 1,
                activated_time = ?,
                expire_time = datetime('now', '+8 hours', '+' || ? || ' days')
            WHERE user_name = ?
        """,
            (activated_time, validity_days, user_name),
        )

        conn.commit()
        conn.close()
        return True

    conn.close()
    return False


def check_user_activation_status(user_name, db_path=DB_PATH):
    # 查询用户是否已激活及激活时间
    # 参数：user_name用户名，db_path数据库路径
    # 返回值：(is_activated, activated_time)元组或None
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT is_activated, activated_time FROM user_info WHERE user_name = ?",
        (user_name,),
    )
    result = cursor.fetchone()
    conn.close()
    return result


def get_user_info_with_status(user_name, db_path=DB_PATH):
    # 获取用户信息及随机可用邮箱ID（需已激活且有剩余次数）
    # 参数：user_name用户名，db_path数据库路径
    # 返回值：包含用户信息和邮箱ID的字典或None
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, account_num, remain_num, expire_time, is_activated, activated_time, validity_days
        FROM user_info
        WHERE user_name = ?
    """,
        (user_name,),
    )

    result = cursor.fetchone()
    if result:
        (
            id,
            account_num,
            remain_num,
            expire_time,
            is_activated,
            activated_time,
            validity_days,
        ) = result

        data = {
            "account_num": account_num,
            "remain_num": remain_num,
            "expire_time": expire_time,
            "is_activated": is_activated,
            "activated_time": activated_time,
            "validity_days": validity_days,
        }

        if is_activated and remain_num > 0:
            cursor.execute(
                """
                SELECT email_id
                FROM user_email
                WHERE user_id = ? and status = 1
                ORDER BY RANDOM() LIMIT 1
            """,
                (id,),
            )
            infoid_to_eid = cursor.fetchone()
            if infoid_to_eid:
                data["infoid_to_eid"] = infoid_to_eid[0]

        conn.close()
        return data

    conn.close()
    return None


def update_user_remain_num(user_name, new_remain_num, db_path=DB_PATH):

    # 更新指定用户的剩余次数
    # 参数：user_name用户名，new_remain_num新剩余次数，db_path数据库路径
    # 返回值：更新成功返回True，否则返回False
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE user_info
            SET remain_num = ?
            WHERE user_name = ?
        """,
            (new_remain_num, user_name),
        )

        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()

        return rows_affected > 0
    except Exception as e:
        print(f"更新指定用户的剩余次数失败: {str(e)}")
        return False


if __name__ == "__main__":
    create_db()

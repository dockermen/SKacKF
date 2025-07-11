import sqlite3

DB_PATH = 'user_devices.db'

def create_db(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_device (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            augmentSession TEXT,
            status INTEGER DEFAULT 1,
            expire_time TEXT,
            other TEXT
        )
    ''')

    cursor.execute('''
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
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_email (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            email_id INTEGER NOT NULL,
            status INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES user_info(id),
            FOREIGN KEY (email_id) REFERENCES user_device(id)
        )
    ''')

    conn.commit()
    conn.close()

def insert_user_device(email,augmentSession,expire_time="",other="",db_path=DB_PATH):
    #闁告瑱鎷烽弫銈囨嫻閿曗偓瑜拌法鎮伴敓锟�
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_device (email, augmentSession,expire_time,other)
        VALUES (?, ?, ?, ?)
    ''', (email, augmentSession,expire_time,other))
    conn.commit()
    conn.close()

def query_user_devices(db_path=DB_PATH,id=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if id:
        cursor.execute('SELECT email,augmentSession FROM user_device WHERE id = ?', (id,))
    else:
        cursor.execute('SELECT email,augmentSession FROM user_device')
    rows = cursor.fetchall()
    conn.close()
    return rows

def query_user_device(idnum:str=3,db_path=DB_PATH,):
    #濞寸姴绐搒er_device閻炴稏鍔嬮懙鎴︽⒕韫囨梹绨氶柤鎯у槻瑜板檮dnum濞戞搫鎷锋径鍕�矗閿燂拷
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_device WHERE status = 1 ORDER BY RANDOM() LIMIT ?', (idnum,))
    rows = cursor.fetchall()
    if rows:
        rows = [row[0] for row in rows]
    conn.close()
    return rows


def update_user_device(email,status, augmentSession=None ,expire_time="", other="", db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if augmentSession:
        cursor.execute('''
            UPDATE user_device
            SET augmentSession = ?, status = ?, expire_time = ?, other = ?
            WHERE email = ?
        ''', (augmentSession, status, expire_time, other, email))
    else:
        cursor.execute('''
            UPDATE user_device
            SET status = ?, expire_time = ?, other = ?
            WHERE email = ?
        ''', (status, expire_time, other, email))
    conn.commit()
    conn.close()

def delete_user_device(user_id, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM user_device
        WHERE user_id = ?
    ''', (user_id,))
    conn.commit()
    conn.close()


def insert_user_info(user_name,expire_time,account_num,remain_num,validity_days=30,db_path=DB_PATH):
    #闁烩偓鍔嶉崺娑欑┍閳╁啩绱栭悶娑虫嫹
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_info (user_name,expire_time,account_num,remain_num,validity_days)
            VALUES (?, ?, ?, ?, ?)
            ''', (user_name,expire_time,account_num,remain_num,validity_days))
        #闁圭粯甯掗崣鍡涘触鎼淬倗绠查柛銉р偓鐖廵r_info閻炴稏鍔嬬粭鍗沝

        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id
    except Exception as e:
        return False
    
def insert_user_email(user_id,email_id,db_path=DB_PATH):
    #闁烩偓鍔嶉崺娑㈠箯閵夛附绠掗悹鎰剁畱瑜板潡寮堕崘锟斤拷閻炴冻鎷�
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_email (user_id,email_id)
        VALUES (?, ?)
    ''', (user_id,email_id))
    conn.commit()
    conn.close()

def query_user_email(user_name,db_path=DB_PATH):
    #闁艰鲸鏌ㄩ幃搴ㄥ蓟閵夛拷鎷烽柨娑樼焸閳э拷淇虹换鍍絪er_info閻炴稈鏆爏er_name闁挎稑鑻�獮鎾诲蓟閵夛拷鎷穟ser_email閻炴稈鏆媘ail_id闁挎稑濂旂粭鏉�er_info闁哄牞鎷风换鍐�嫉閻斿墎鐟�€圭ǹ寮剁缓鍝劽洪敓锟�
    conn = sqlite3.connect(db_path)
    data = {}
    cursor = conn.cursor()

    #闁哄被鍎撮敓浠嬪嫉閿熺晫绠栭柡鍫㈠枍缁楁牕锟介崣澶岃礋婵炲弶妲掓径鍕�箣閾氬倻鐟撻悹鎰剁畱瑜版寧鎷呯捄銊︽殢闁癸拷鎳庨崰锟�
    cursor.execute('''
        SELECT id,account_num,remain_num,expire_time,is_activated,activated_time
        FROM user_info
        WHERE user_name = ? and remain_num > 0 and expire_time > datetime('now', '+8 hours') and is_activated = 1;
    ''', (user_name,))
    q_rows = cursor.fetchone()
    if q_rows:
        id,account_num,remain_num,expire_time,is_activated,activated_time = q_rows
        data.update({
            'account_num': account_num,
            'remain_num': remain_num,
            'expire_time': expire_time,
            'is_activated': is_activated,
            'activated_time': activated_time
        })

        cursor.execute('''
            SELECT email_id
            FROM user_email
            WHERE user_id = ? and status = 1
            ORDER BY RANDOM() LIMIT 1
        ''', (id,))
        infoid_to_eid = cursor.fetchone()
        if infoid_to_eid:
            data["infoid_to_eid"] = infoid_to_eid[0]
    conn.close()
    return data

def quer_user_info_extime(user_name,db_path=DB_PATH):
    #闁哄被鍎撮敓浠嬫偨閵婏箑鐓曢柡鍕舵嫹閹�線宕氶悧鍫熷焸
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT expire_time from user_info
        WHERE user_name = ?
    ''', (user_name,))
    rows = cursor.fetchone()
    if rows:
        rows = rows[0]
    conn.close()
    return rows



def update_user_email_status(id,status=0,db_path=DB_PATH):
    #闁哄洤鐡ㄩ弻濡榮er_email閻炴稈鏆瀟atus
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE user_email
        SET status = ?
        WHERE id = ?
    ''', (status,id))
    conn.commit()
    conn.close()

def query_user_id(user_name,db_path=DB_PATH):
    #闁哄被鍎撮敓绲瑂er_info閻炴稏鍔嬮懙鎲塻er_name閻庣數鎳撶花鏌ユ儍閸掔惄 闁哄牆锟界粭鏍�矗閿熻姤绠掑☉鎾�亾濞戞搫鎷风划銊╁几閿燂拷
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM user_info WHERE user_name = ?', (user_name,)) #闁哄牆锟界粭鏍�矗閿熻姤绠掑☉鎾�亾濞戞搫鎷风划銊╁几閿燂拷
    row = cursor.fetchone()
    conn.close()
    return row

def activate_user(user_name, db_path=DB_PATH):
    #婵犵�鍋撴繛鑼跺吹閺併倝骞嬮崙銈囩�閻犱礁澧介悿鍡椻攽閳э拷煤閼姐倕笑闁癸拷绀侀幏鏉库攽閳э拷煤缂佹ɑ锟介梻鍌濇彧缁辨繃绂掓惔銏㈣礋婵炶尙绮��鍌炲礆鐠囪尙纾诲┑锟斤拷閸ｆ悂寮�幏宀嬫嫹缂佺姵锟界换鍐�嫉閻斿憡锟介梻鍌︽嫹
    from datetime import datetime
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 濡�絾鐗曢崢娑樜涢埀锟藉蓟閵壯勬殢闁规挳鏀卞Σ鎼佸触閿曗偓閸戯紕绱掕箛鏃傝礋婵炶弓绱�槐婵嬬嵁閹�澘绠�柛娆愮墬濠€渚€寮�崼鐔稿焸濠㈠灈鏅滈弳锟�
    cursor.execute('SELECT is_activated, validity_days FROM user_info WHERE user_name = ?', (user_name,))
    result = cursor.fetchone()

    if result and result[0] == 0:  # 闁烩偓鍔嶉崺娑氣偓娑櫭�﹢锟界▔閺冣偓濠€锟解攽閳э拷煤閿燂拷
        activated_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        validity_days = result[1] if result[1] else 30  # 濠碘€冲€归悘澶娾柦閳╁啯绠掗悹浣稿⒔閻ゅ棝寮垫径瀣�珡闁哄牏鍣︾槐婵囷拷濡�尅鎷�30濠㈣�鎷�

        # 濞寸姴瀛╃缓鍝劽虹紒妯伙拷闂傚倹娼欑槐鎴炴叏鐎ｏ拷鎷风紒鐘筹拷缁诲啴寮甸悢鍛婏拷闂傚偊鎷�
        cursor.execute('''
            UPDATE user_info
            SET is_activated = 1,
                activated_time = ?,
                expire_time = datetime('now', '+8 hours', '+' || ? || ' days')
            WHERE user_name = ?
        ''', (activated_time, validity_days, user_name))

        conn.commit()
        conn.close()
        return True

    conn.close()
    return False

def check_user_activation_status(user_name, db_path=DB_PATH):
    #婵★拷鍋撻柡灞诲劤閺併倝骞嬮柨瀣�礋婵炶尪宕垫慨鎼佸箑閿燂拷
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT is_activated, activated_time FROM user_info WHERE user_name = ?', (user_name,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_user_info_with_status(user_name, db_path=DB_PATH):
    #闁兼儳鍢茶ぐ鍥�偨閵婏箑鐓曢悗鐟版湰閺嗭絾绌遍埄鍐х礀闁挎稑鑻�€垫﹢骞忛敓鐣岃礋婵炶尪宕垫慨鎼佸箑閿燂拷
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, account_num, remain_num, expire_time, is_activated, activated_time, validity_days
        FROM user_info
        WHERE user_name = ?
    ''', (user_name,))

    result = cursor.fetchone()
    if result:
        id, account_num, remain_num, expire_time, is_activated, activated_time, validity_days = result

        data = {
            'account_num': account_num,
            'remain_num': remain_num,
            'expire_time': expire_time,
            'is_activated': is_activated,
            'activated_time': activated_time,
            'validity_days': validity_days
        }

        # 濠碘€冲€归悘澶愭偨閵婏箑鐓曠€圭ǹ寮剁缓鍝劽虹拋宕囩懍闁哄牆锟芥晶鎸庢媴濞嗘劧鎷烽柡浣稿簻缁辨繈鎳㈠畡鏉跨悼闁告瑱鎷烽弫銈夋儍閸掞拷ail_id
        if is_activated and remain_num > 0:
            cursor.execute('''
                SELECT email_id
                FROM user_email
                WHERE user_id = ? and status = 1
                ORDER BY RANDOM() LIMIT 1
            ''', (id,))
            infoid_to_eid = cursor.fetchone()
            if infoid_to_eid:
                data["infoid_to_eid"] = infoid_to_eid[0]

        conn.close()
        return data

    conn.close()
    return None

def update_user_remain_num(user_name, new_remain_num, db_path=DB_PATH):
    """闁哄洤鐡ㄩ弻濠囨偨閵婏箑鐓曢柛鎾�櫃缂嶆垶鎷呯捄銊︽殢婵炲棌鍓濋弳锟�"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE user_info
            SET remain_num = ?
            WHERE user_name = ?
        ''', (new_remain_num, user_name))
        
        # 婵★拷鍋撻柡灞诲劜濡叉悂宕ラ敂钘夌亣闁告梻鍠愬ú鍧楀棘閿燂拷
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    except Exception as e:
        print(f"闁哄洤鐡ㄩ弻濠囨偨閵婏箑鐓曢柛鎾�櫃缂嶆垵鈻庨埄鍐╂�闂佹寧鐟ㄩ敓锟�: {str(e)}")
        return False


if __name__ == "__main__":
    # 闁告帗绋戠紓鎾舵偘閿燂拷
    create_db()

    #print(query_user_device(2))
   


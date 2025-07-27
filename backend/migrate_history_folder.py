#!/usr/bin/env python3
"""
数据库迁移脚本：为 history 表添加 folder_id 列
使用方式: python migrate_history_folder.py
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.engine import get_engine
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def migrate_history_table():
    engine = get_engine()
    
    try:
        # 获取原始连接
        connection = engine.raw_connection()
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        
        # 检查 folder_id 列是否已存在
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='history' AND column_name='folder_id'
        """)
        
        if cursor.fetchone():
            print("✅ folder_id 列已存在，无需迁移")
            return
        
        print("🔄 开始迁移 history 表...")
        
        # 添加 folder_id 列
        cursor.execute("""
            ALTER TABLE history 
            ADD COLUMN folder_id VARCHAR;
        """)
        
        print("✅ 成功添加 folder_id 列")
        
        # 如果 folders 表存在，添加外键约束
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name='folders'
        """)
        
        if cursor.fetchone():
            try:
                cursor.execute("""
                    ALTER TABLE history 
                    ADD CONSTRAINT fk_history_folder 
                    FOREIGN KEY (folder_id) REFERENCES folders(id)
                """)
                print("✅ 成功添加外键约束")
            except Exception as e:
                print(f"⚠️  添加外键约束失败（可能已存在）: {e}")
        
        cursor.close()
        connection.close()
        
        print("🎉 迁移完成！")
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        raise

if __name__ == "__main__":
    migrate_history_table()
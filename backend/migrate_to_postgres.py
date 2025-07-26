#!/usr/bin/env python3
"""
数据库迁移脚本：从 SQLite 迁移数据到 PostgreSQL

使用方法：
1. 确保 PostgreSQL 数据库已创建并配置在 .env 文件中
2. 运行脚本：python migrate_to_postgres.py
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))

load_dotenv()

class DatabaseMigrator:
    def __init__(self):
        self.sqlite_db_path = "bili_note.db"
        self.postgres_url = os.getenv("DATABASE_URL", "postgresql://bili_user:bili_password@localhost:5432/bili_note")
        
        # 解析 PostgreSQL 连接参数
        self.pg_host = os.getenv("POSTGRES_HOST", "localhost")
        self.pg_port = os.getenv("POSTGRES_PORT", "5432")
        self.pg_db = os.getenv("POSTGRES_DB", "bili_note")
        self.pg_user = os.getenv("POSTGRES_USER", "bili_user")
        self.pg_password = os.getenv("POSTGRES_PASSWORD", "bili_password")
        
    def check_sqlite_exists(self):
        """检查 SQLite 数据库是否存在"""
        if not os.path.exists(self.sqlite_db_path):
            print(f"❌ SQLite 数据库文件不存在: {self.sqlite_db_path}")
            return False
        print(f"✅ 找到 SQLite 数据库: {self.sqlite_db_path}")
        return True
    
    def check_postgres_connection(self):
        """检查 PostgreSQL 连接"""
        try:
            conn = psycopg2.connect(
                host=self.pg_host,
                port=self.pg_port,
                database=self.pg_db,
                user=self.pg_user,
                password=self.pg_password
            )
            conn.close()
            print("✅ PostgreSQL 连接成功")
            return True
        except psycopg2.Error as e:
            print(f"❌ PostgreSQL 连接失败: {e}")
            return False
    
    def create_postgres_tables(self):
        """在 PostgreSQL 中创建表结构"""
        try:
            # 使用 SQLAlchemy 创建表
            from app.db.engine import engine, Base
            from app.db.models.models import Model
            from app.db.models.providers import Provider
            from app.db.models.video_tasks import VideoTask
            from app.db.models.history import History
            
            print("🔄 正在创建 PostgreSQL 表结构...")
            Base.metadata.create_all(bind=engine)
            print("✅ PostgreSQL 表结构创建成功")
            return True
        except Exception as e:
            print(f"❌ 创建 PostgreSQL 表结构失败: {e}")
            return False
    
    def migrate_providers(self):
        """迁移 providers 表数据"""
        print("🔄 正在迁移 providers 表数据...")
        
        # 从 SQLite 读取数据
        sqlite_conn = sqlite3.connect(self.sqlite_db_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        try:
            sqlite_cursor.execute("SELECT * FROM providers")
            providers = sqlite_cursor.fetchall()
            
            if not providers:
                print("ℹ️  providers 表中没有数据")
                return True
            
            # 写入 PostgreSQL
            pg_conn = psycopg2.connect(
                host=self.pg_host,
                port=self.pg_port,
                database=self.pg_db,
                user=self.pg_user,
                password=self.pg_password
            )
            pg_cursor = pg_conn.cursor()
            
            for provider in providers:
                pg_cursor.execute("""
                    INSERT INTO providers (id, name, logo, type, api_key, base_url, enabled, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        logo = EXCLUDED.logo,
                        type = EXCLUDED.type,
                        api_key = EXCLUDED.api_key,
                        base_url = EXCLUDED.base_url,
                        enabled = EXCLUDED.enabled,
                        created_at = EXCLUDED.created_at
                """, (
                    provider['id'],
                    provider['name'],
                    provider['logo'],
                    provider['type'],
                    provider['api_key'],
                    provider['base_url'],
                    provider['enabled'],
                    provider['created_at']
                ))
            
            pg_conn.commit()
            pg_cursor.close()
            pg_conn.close()
            
            print(f"✅ 成功迁移 {len(providers)} 条 providers 数据")
            return True
            
        except Exception as e:
            print(f"❌ 迁移 providers 表失败: {e}")
            return False
        finally:
            sqlite_conn.close()
    
    def migrate_models(self):
        """迁移 models 表数据"""
        print("🔄 正在迁移 models 表数据...")
        
        # 从 SQLite 读取数据
        sqlite_conn = sqlite3.connect(self.sqlite_db_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        try:
            sqlite_cursor.execute("SELECT * FROM models")
            models = sqlite_cursor.fetchall()
            
            if not models:
                print("ℹ️  models 表中没有数据")
                return True
            
            # 写入 PostgreSQL
            pg_conn = psycopg2.connect(
                host=self.pg_host,
                port=self.pg_port,
                database=self.pg_db,
                user=self.pg_user,
                password=self.pg_password
            )
            pg_cursor = pg_conn.cursor()
            
            for model in models:
                pg_cursor.execute("""
                    INSERT INTO models (provider_id, model_name, created_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    model['provider_id'],
                    model['model_name'],
                    model['created_at']
                ))
            
            pg_conn.commit()
            pg_cursor.close()
            pg_conn.close()
            
            print(f"✅ 成功迁移 {len(models)} 条 models 数据")
            return True
            
        except Exception as e:
            print(f"❌ 迁移 models 表失败: {e}")
            return False
        finally:
            sqlite_conn.close()
    
    def migrate_video_tasks(self):
        """迁移 video_tasks 表数据"""
        print("🔄 正在迁移 video_tasks 表数据...")
        
        # 从 SQLite 读取数据
        sqlite_conn = sqlite3.connect(self.sqlite_db_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        try:
            sqlite_cursor.execute("SELECT * FROM video_tasks")
            video_tasks = sqlite_cursor.fetchall()
            
            if not video_tasks:
                print("ℹ️  video_tasks 表中没有数据")
                return True
            
            # 写入 PostgreSQL
            pg_conn = psycopg2.connect(
                host=self.pg_host,
                port=self.pg_port,
                database=self.pg_db,
                user=self.pg_user,
                password=self.pg_password
            )
            pg_cursor = pg_conn.cursor()
            
            for task in video_tasks:
                pg_cursor.execute("""
                    INSERT INTO video_tasks (video_id, platform, task_id, created_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (task_id) DO UPDATE SET
                        video_id = EXCLUDED.video_id,
                        platform = EXCLUDED.platform,
                        created_at = EXCLUDED.created_at
                """, (
                    task['video_id'],
                    task['platform'],
                    task['task_id'],
                    task['created_at']
                ))
            
            pg_conn.commit()
            pg_cursor.close()
            pg_conn.close()
            
            print(f"✅ 成功迁移 {len(video_tasks)} 条 video_tasks 数据")
            return True
            
        except Exception as e:
            print(f"❌ 迁移 video_tasks 表失败: {e}")
            return False
        finally:
            sqlite_conn.close()
    
    def verify_migration(self):
        """验证迁移结果"""
        print("🔄 正在验证迁移结果...")
        
        try:
            # 连接两个数据库
            sqlite_conn = sqlite3.connect(self.sqlite_db_path)
            sqlite_cursor = sqlite_conn.cursor()
            
            pg_conn = psycopg2.connect(
                host=self.pg_host,
                port=self.pg_port,
                database=self.pg_db,
                user=self.pg_user,
                password=self.pg_password
            )
            pg_cursor = pg_conn.cursor()
            
            tables = ['providers', 'models', 'video_tasks', 'history']
            
            for table in tables:
                # 获取 SQLite 记录数
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                sqlite_count = sqlite_cursor.fetchone()[0]
                
                # 获取 PostgreSQL 记录数
                pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                pg_count = pg_cursor.fetchone()[0]
                
                if sqlite_count == pg_count:
                    print(f"✅ {table} 表: SQLite({sqlite_count}) = PostgreSQL({pg_count})")
                else:
                    print(f"⚠️  {table} 表: SQLite({sqlite_count}) ≠ PostgreSQL({pg_count})")
            
            sqlite_conn.close()
            pg_conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ 验证迁移失败: {e}")
            return False
    
    def run_migration(self):
        """执行完整的迁移流程"""
        print("🚀 开始数据库迁移...")
        print("=" * 50)
        
        # 1. 检查 SQLite 数据库
        if not self.check_sqlite_exists():
            return False
        
        # 2. 检查 PostgreSQL 连接
        if not self.check_postgres_connection():
            return False
        
        # 3. 创建 PostgreSQL 表结构
        if not self.create_postgres_tables():
            return False
        
        # 4. 迁移数据
        success = True
        success &= self.migrate_providers()
        success &= self.migrate_models()
        success &= self.migrate_video_tasks()
        
        if not success:
            print("❌ 数据迁移过程中出现错误")
            return False
        
        # 5. 验证迁移结果
        if not self.verify_migration():
            return False
        
        print("=" * 50)
        print("🎉 数据库迁移完成！")
        print(f"✅ SQLite 数据已成功迁移到 PostgreSQL")
        print(f"📝 请更新 .env 文件中的 DATABASE_URL 为: {self.postgres_url}")
        
        return True

def main():
    """主函数"""
    migrator = DatabaseMigrator()
    
    print("BiliNote 数据库迁移工具")
    print("SQLite -> PostgreSQL")
    print("=" * 50)
    
    try:
        success = migrator.run_migration()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ 迁移被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 迁移过程中发生未知错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
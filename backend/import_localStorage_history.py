#!/usr/bin/env python3
"""
从浏览器localStorage导入历史数据到PostgreSQL

使用方法：
1. 在浏览器中打开开发者工具，控制台执行：
   console.log(JSON.stringify(JSON.parse(localStorage.getItem('task-storage'))))
2. 将输出的JSON数据保存到 localStorage_export.json 文件中
3. 运行脚本：python import_localStorage_history.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))

load_dotenv()

# 导入必要的模块
from app.db.history_dao import insert_history
from app.db.engine import get_db

class LocalStorageImporter:
    def __init__(self):
        self.export_file = "localStorage_export.json"
        
    def check_export_file(self):
        """检查导出文件是否存在"""
        if not os.path.exists(self.export_file):
            print(f"❌ 导出文件不存在: {self.export_file}")
            print("请按照以下步骤导出localStorage数据：")
            print("1. 在浏览器中打开BiliNote前端页面")
            print("2. 按F12打开开发者工具")
            print("3. 在控制台执行：")
            print("   console.log(JSON.stringify(JSON.parse(localStorage.getItem('task-storage'))))")
            print("4. 复制输出的JSON数据并保存到 localStorage_export.json 文件中")
            return False
        print(f"✅ 找到导出文件: {self.export_file}")
        return True
    
    def load_localStorage_data(self):
        """加载localStorage数据"""
        try:
            with open(self.export_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # localStorage的数据结构：{"state": {"tasks": [...], "currentTaskId": "..."}, "version": 0}
            if 'state' in data and 'tasks' in data['state']:
                tasks = data['state']['tasks']
                print(f"✅ 成功加载 {len(tasks)} 个任务记录")
                return tasks
            else:
                print("❌ localStorage数据格式不正确")
                return []
        except Exception as e:
            print(f"❌ 加载localStorage数据失败: {e}")
            return []
    
    def convert_task_to_history(self, task):
        """将localStorage任务数据转换为历史记录格式"""
        try:
            # 处理markdown版本数据
            markdown_content = ""
            markdown_versions = []
            
            if task.get('markdown'):
                if isinstance(task['markdown'], str):
                    # 旧格式：字符串
                    markdown_content = task['markdown']
                elif isinstance(task['markdown'], list):
                    # 新格式：版本数组
                    if task['markdown']:
                        markdown_content = task['markdown'][0].get('content', '')
                        markdown_versions = task['markdown']
            
            # 处理转录段落数据
            transcript_segments = []
            if task.get('transcript', {}).get('segments'):
                transcript_segments = [
                    {
                        "start": seg.get('start', 0),
                        "end": seg.get('end', 0),
                        "text": seg.get('text', '')
                    }
                    for seg in task['transcript']['segments']
                ]
            
            return {
                'task_id': task['id'],
                'status': task.get('status', 'UNKNOWN'),
                'platform': task.get('platform', ''),
                'title': task.get('audioMeta', {}).get('title'),
                'cover_url': task.get('audioMeta', {}).get('cover_url'),
                'duration': task.get('audioMeta', {}).get('duration'),
                'file_path': task.get('audioMeta', {}).get('file_path'),
                'video_id': task.get('audioMeta', {}).get('video_id'),
                'raw_info': task.get('audioMeta', {}).get('raw_info'),
                'transcript_full_text': task.get('transcript', {}).get('full_text'),
                'transcript_language': task.get('transcript', {}).get('language'),
                'transcript_raw': task.get('transcript', {}).get('raw'),
                'transcript_segments': transcript_segments,
                'markdown_content': markdown_content,
                'markdown_versions': markdown_versions,
                'form_data': task.get('formData')
            }
        except Exception as e:
            print(f"❌ 转换任务数据失败 (task_id={task.get('id', 'unknown')}): {e}")
            return None
    
    def import_tasks(self, tasks):
        """导入任务到历史记录表"""
        success_count = 0
        error_count = 0
        
        for task in tasks:
            try:
                history_data = self.convert_task_to_history(task)
                if not history_data:
                    error_count += 1
                    continue
                
                # 插入历史记录
                result = insert_history(**history_data)
                if result:
                    success_count += 1
                    print(f"✅ 导入成功: {history_data['task_id']} - {history_data.get('title', 'untitled')}")
                else:
                    error_count += 1
                    print(f"❌ 导入失败: {history_data['task_id']}")
                    
            except Exception as e:
                error_count += 1
                print(f"❌ 处理任务失败: {e}")
        
        print(f"\n🎉 导入完成!")
        print(f"✅ 成功导入: {success_count} 条记录")
        if error_count > 0:
            print(f"❌ 导入失败: {error_count} 条记录")
        
        return success_count, error_count
    
    def run_import(self):
        """执行完整的导入流程"""
        print("🚀 开始从localStorage导入历史数据...")
        print("=" * 50)
        
        # 1. 检查导出文件
        if not self.check_export_file():
            return False
        
        # 2. 加载数据
        tasks = self.load_localStorage_data()
        if not tasks:
            print("❌ 没有找到可导入的任务数据")
            return False
        
        # 3. 导入数据
        success_count, error_count = self.import_tasks(tasks)
        
        print("=" * 50)
        if error_count == 0:
            print("🎉 所有历史数据导入成功！")
            return True
        else:
            print(f"⚠️  导入完成，但有 {error_count} 条记录失败")
            return success_count > 0

def main():
    """主函数"""
    importer = LocalStorageImporter()
    
    print("BiliNote 历史数据导入工具")
    print("localStorage -> PostgreSQL")
    print("=" * 50)
    
    try:
        success = importer.run_import()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ 导入被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 导入过程中发生未知错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
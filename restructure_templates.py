#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Template directory restructuring script
Automated execution of template file consolidation and path correction

Usage:
    python restructure_templates.py [--dry-run] [--backup]

Options:
    --dry-run   : Only show operations to be performed, don't actually modify files
    --backup    : Create backup before execution
"""

import os
import shutil
import argparse
import json
from datetime import datetime
from pathlib import Path

class TemplateRestructurer:
    """模板重构器"""
    
    def __init__(self, project_root, dry_run=False, backup=True):
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.backup = backup
        
        # 关键路径定义
        self.templates_dir = self.project_root / "templates"
        self.project_templates_dir = self.project_root / "myhome_project" / "templates"
        self.apps_dir = self.project_root / "myhome_project" / "apps"
        
        # 目标目录结构
        self.target_structure = {
            "base": ["base.html", "_user_nav.html"],
            "registration": ["login.html", "register.html", "logged_out.html"],
            "family": ["profile.html"],
            "events": [],  # 动态确定
            "housework": [],  # 动态确定
            "calendar": [],  # 动态确定
        }
        
        # 模板文件对比结果
        self.template_analysis = {}
        
    def log(self, message, level="INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "📋",
            "WARN": "⚠️", 
            "ERROR": "❌",
            "SUCCESS": "✅",
            "MOVE": "📁",
            "DELETE": "🗑️"
        }.get(level, "📋")
        print(f"[{timestamp}] {prefix} {message}")
    
    def analyze_current_structure(self):
        """分析当前模板结构"""
        self.log("开始分析当前模板结构...")
        
        # 分析 Events 模板冲突
        self._analyze_events_templates()
        
        # 分析其他应用模板
        self._analyze_family_templates()
        self._analyze_housework_templates()
        self._analyze_calendar_templates()
        
        self.log("模板结构分析完成")
        
    def _analyze_events_templates(self):
        """分析 Events 模板冲突"""
        events_sources = {
            "global_events": self.templates_dir / "myhome" / "events",
            "project_events": self.project_templates_dir / "myhome" / "events", 
            "app_events": self.apps_dir / "events" / "templates" / "myhome" / "events"
        }
        
        conflicts = {}
        
        # 收集所有 events 模板文件
        for source_name, source_path in events_sources.items():
                if source_path.exists():
                    for template_file in source_path.glob("*.html"):
                        file_name = template_file.name
                        if file_name not in conflicts:
                            conflicts[file_name] = {}
                        conflicts[file_name][source_name] = {
                            "path": str(template_file),  # 转换为字符串
                            "size": template_file.stat().st_size,
                            "modified": template_file.stat().st_mtime
                        }
        
        # 分析每个冲突文件，选择最佳版本
        for file_name, versions in conflicts.items():
            if len(versions) > 1:
                # 有冲突，选择最大的文件作为主版本
                best_version = max(versions.items(), key=lambda x: x[1]["size"])
                self.template_analysis[f"events/{file_name}"] = {
                    "conflict": True,
                    "versions": versions,
                    "selected": best_version[0],
                    "selected_path": str(best_version[1]["path"]),  # 转换为字符串
                    "duplicates": [k for k in versions.keys() if k != best_version[0]]
                }
                self.log(f"Events 模板冲突: {file_name}, 选择版本: {best_version[0]}", "WARN")
            else:
                # 无冲突
                source_name = list(versions.keys())[0]
                self.template_analysis[f"events/{file_name}"] = {
                    "conflict": False,
                    "selected": source_name,
                    "selected_path": str(versions[source_name]["path"]),  # 转换为字符串
                    "duplicates": []
                }
    
    def _analyze_family_templates(self):
        """分析 Family 模板"""
        family_sources = [
            self.project_templates_dir / "family" / "profile.html",
            self.apps_dir / "family" / "templates" / "family"
        ]
        
        # 处理 profile.html 的特殊情况
        profile_sources = [p for p in family_sources if p.name == "profile.html" and p.exists()]
        if len(profile_sources) > 1:
            # 需要比较修改时间，选择最新的
            latest_profile = max(profile_sources, key=lambda p: p.stat().st_mtime)
            self.template_analysis["family/profile.html"] = {
                "conflict": True,
                "selected_path": str(latest_profile),  # 转换为字符串
                "type": "single_file_conflict"
            }
            self.log(f"Family profile.html 冲突，选择最新版本", "WARN")
        
        # 收集其他 family 模板
        family_dir = self.apps_dir / "family" / "templates" / "family"
        if family_dir.exists():
            for template_file in family_dir.glob("*.html"):
                if template_file.name != "profile.html":
                    self.template_analysis[f"family/{template_file.name}"] = {
                    "conflict": False,
                    "selected_path": str(template_file),  # 转换为字符串
                    "type": "app_template"
                }
    
    def _analyze_housework_templates(self):
        """分析 Housework 模板"""
        housework_dir = self.apps_dir / "housework" / "templates" / "housework"
        if housework_dir.exists():
            for template_file in housework_dir.glob("*.html"):
                self.template_analysis[f"housework/{template_file.name}"] = {
                    "conflict": False,
                    "selected_path": str(template_file),  # 转换为字符串
                    "type": "app_template"
                }
    
    def _analyze_calendar_templates(self):
        """分析 Calendar 模板"""
        calendar_dir = self.project_templates_dir / "family_calendar"
        if calendar_dir.exists():
            for template_file in calendar_dir.glob("*.html"):
                self.template_analysis[f"calendar/{template_file.name}"] = {
                    "conflict": False,
                    "selected_path": str(template_file),  # 转换为字符串
                    "type": "project_template"
                }
    
    def create_backup(self):
        """创建备份"""
        if not self.backup:
            return
            
        backup_dir = self.project_root / f"backup_templates_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log(f"创建备份到: {backup_dir}")
        
        if not self.dry_run:
            backup_dir.mkdir(exist_ok=True)
            
            # 备份所有模板目录
            if self.templates_dir.exists():
                shutil.copytree(self.templates_dir, backup_dir / "templates", dirs_exist_ok=True)
            if self.project_templates_dir.exists():
                shutil.copytree(self.project_templates_dir, backup_dir / "project_templates", dirs_exist_ok=True)
            
            # 备份应用的模板目录
            for app_name in ["events", "family", "housework"]:
                app_template_dir = self.apps_dir / app_name / "templates"
                if app_template_dir.exists():
                    shutil.copytree(app_template_dir, backup_dir / f"{app_name}_templates", dirs_exist_ok=True)
    
    def create_target_structure(self):
        """创建目标目录结构"""
        self.log("创建目标目录结构...")
        
        target_dirs = [
            self.templates_dir / "family",
            self.templates_dir / "events", 
            self.templates_dir / "housework",
            self.templates_dir / "calendar",
            self.templates_dir / "_includes"
        ]
        
        for target_dir in target_dirs:
            if not self.dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
            self.log(f"创建目录: {target_dir}")
    
    def move_templates(self):
        """移动模板文件到目标位置"""
        self.log("开始移动模板文件...")
        
        moved_count = 0
        for template_key, analysis in self.template_analysis.items():
            source_path = analysis["selected_path"]
            
            # 确定目标路径
            target_dir = self.templates_dir / template_key.split("/")[0]
            target_path = target_dir / Path(template_key).name
            
            if source_path != target_path:
                self.log(f"移动: {source_path} → {target_path}", "MOVE")
                if not self.dry_run:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, target_path)
                moved_count += 1
            else:
                self.log(f"跳过: {source_path} (已在目标位置)")
        
        return moved_count
    
    def update_view_references(self):
        """更新视图文件中的模板路径引用"""
        self.log("更新视图文件中的模板路径...")
        
        # 需要更新的文件和路径映射
        updates = {
            "myhome_project/apps/events/views.py": {
                "myhome/events/": "events/"
            },
            "myhome_project/apps/family_calendar/views.py": {
                "family_calendar/": "calendar/"
            }
        }
        
        updated_files = 0
        
        for file_path, path_mappings in updates.items():
            full_path = self.project_root / file_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')
                original_content = content
                
                for old_path, new_path in path_mappings.items():
                    content = content.replace(f'"{old_path}', f'"{new_path}')
                    content = content.replace(f"'{old_path}", f"'{new_path}")
                
                if content != original_content:
                    self.log(f"更新模板路径: {file_path}")
                    if not self.dry_run:
                        full_path.write_text(content, encoding='utf-8')
                    updated_files += 1
        
        return updated_files
    
    def cleanup_old_directories(self):
        """清理旧的空目录"""
        self.log("清理旧目录...")
        
        directories_to_check = [
            self.templates_dir / "myhome",
            self.project_templates_dir / "myhome", 
            self.project_templates_dir / "family_calendar",
        ]
        
        # 检查应用内的模板目录
        for app_name in ["events", "family", "housework"]:
            app_template_dir = self.apps_dir / app_name / "templates"
            directories_to_check.append(app_template_dir)
        
        cleaned_count = 0
        for directory in directories_to_check:
            if directory.exists():
                # 检查目录是否为空或只包含空子目录
                if self._is_empty_directory(directory):
                    self.log(f"删除空目录: {directory}", "DELETE")
                    if not self.dry_run:
                        shutil.rmtree(directory)
                    cleaned_count += 1
        
        return cleaned_count
    
    def _is_empty_directory(self, path):
        """检查目录是否为空"""
        if not path.exists():
            return True
            
        for item in path.rglob("*"):
            if item.is_file():
                return False
        return True
    
    def _make_json_serializable(self, obj):
        """将对象转换为JSON可序列化的格式"""
        if isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return str(obj)  # 将复杂对象转换为字符串
        else:
            return obj
    
    def generate_report(self):
        """生成重构报告"""
        # 确保所有数据都可以JSON序列化
        serializable_analysis = self._make_json_serializable(self.template_analysis)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "template_analysis": serializable_analysis,
            "statistics": {
                "total_templates": len(self.template_analysis),
                "conflicts": len([t for t in self.template_analysis.values() if t.get("conflict", False)]),
                "moved_files": 0,  # 将在执行后更新
                "updated_views": 0,  # 将在执行后更新
                "cleaned_directories": 0  # 将在执行后更新
            }
        }
        
        report_path = self.project_root / "template_restructure_report.json"
        if not self.dry_run:
            report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        
        self.log(f"生成重构报告: {report_path}")
        return report
    
    def execute(self):
        """执行完整的重构流程"""
        self.log("=" * 60)
        self.log("开始模板目录结构重构")
        self.log("=" * 60)
        
        if self.dry_run:
            self.log("🔍 DRY RUN 模式 - 不会修改任何文件", "WARN")
        
        try:
            # 1. 分析当前结构
            self.analyze_current_structure()
            
            # 2. 创建备份
            if self.backup:
                self.create_backup()
            
            # 3. 创建目标结构
            self.create_target_structure()
            
            # 4. 移动模板文件
            moved_count = self.move_templates()
            
            # 5. 更新视图引用
            updated_views = self.update_view_references()
            
            # 6. 清理旧目录
            cleaned_dirs = self.cleanup_old_directories()
            
            # 7. 生成报告
            report = self.generate_report()
            report["statistics"]["moved_files"] = moved_count
            report["statistics"]["updated_views"] = updated_views  
            report["statistics"]["cleaned_directories"] = cleaned_dirs
            
            # 8. 输出总结
            self.log("=" * 60)
            self.log("重构执行完成", "SUCCESS")
            self.log(f"移动文件: {moved_count}")
            self.log(f"更新视图: {updated_views}")
            self.log(f"清理目录: {cleaned_dirs}")
            self.log("=" * 60)
            
            if self.dry_run:
                self.log("💡 这是 DRY RUN，实际执行请移除 --dry-run 参数", "INFO")
            
            return True
            
        except Exception as e:
            self.log(f"重构过程中出现错误: {e}", "ERROR")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="模板目录结构重构工具")
    parser.add_argument("--dry-run", action="store_true", help="仅显示操作，不执行")
    parser.add_argument("--no-backup", action="store_true", help="跳过备份")
    
    args = parser.parse_args()
    
    # 获取项目根目录
    current_dir = Path(__file__).parent
    project_root = current_dir
    
    # 创建重构器并执行
    restructurer = TemplateRestructurer(
        project_root=project_root,
        dry_run=args.dry_run,
        backup=not args.no_backup
    )
    
    success = restructurer.execute()
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
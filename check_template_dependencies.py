#!/usr/bin/env python
"""
模板依赖关系检查工具
检查模板文件之间的继承和引用关系，确保重构后不会破坏功能

使用方法:
    python check_template_dependencies.py
"""

import os
import re
from pathlib import Path
import json
from datetime import datetime

class TemplateDependencyChecker:
    """模板依赖关系检查器"""
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.templates_dir = self.project_root / "templates"
        self.project_templates_dir = self.project_root / "myhome_project" / "templates"
        self.apps_dir = self.project_root / "myhome_project" / "apps"
        
        self.dependencies = {}
        self.errors = []
        self.warnings = []
        
    def log(self, message, level="INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "📋",
            "WARN": "⚠️", 
            "ERROR": "❌",
            "SUCCESS": "✅",
            "FOUND": "🔍"
        }.get(level, "📋")
        print(f"[{timestamp}] {prefix} {message}")
    
    def find_all_templates(self):
        """查找所有模板文件"""
        templates = []
        
        # 搜索所有可能的模板目录
        search_dirs = [
            self.templates_dir,
            self.project_templates_dir,
            self.apps_dir / "events" / "templates",
            self.apps_dir / "family" / "templates", 
            self.apps_dir / "housework" / "templates",
            self.apps_dir / "family_calendar" / "templates"
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                for template_file in search_dir.rglob("*.html"):
                    rel_path = template_file.relative_to(self.project_root)
                    templates.append(str(rel_path))
        
        return templates
    
    def analyze_template(self, template_path):
        """分析单个模板文件的依赖关系"""
        full_path = self.project_root / template_path
        
        if not full_path.exists():
            return None
        
        try:
            content = full_path.read_text(encoding='utf-8')
        except Exception as e:
            self.errors.append(f"读取文件失败: {template_path} - {e}")
            return None
        
        dependencies = {
            "extends": [],
            "includes": [],
            "custom_tags": [],
            "static_files": [],
            "urls": []
        }
        
        # 查找 extends 语句
        extends_pattern = r'{%\s*extends\s+["\']([^"\']+)["\']\s*%}'
        for match in re.finditer(extends_pattern, content):
            template_name = match.group(1)
            dependencies["extends"].append(template_name)
        
        # 查找 include 语句
        include_pattern = r'{%\s*include\s+["\']([^"\']+)["\']\s*%}'
        for match in re.finditer(include_pattern, content):
            template_name = match.group(1)
            dependencies["includes"].append(template_name)
        
        # 查找 load 语句 (自定义标签)
        load_pattern = r'{%\s*load\s+([^{%]+)\s*%}'
        for match in re.finditer(load_pattern, content):
            tags = [tag.strip() for tag in match.group(1).split()]
            dependencies["custom_tags"].extend(tags)
        
        # 查找 static 文件引用
        static_pattern = r'{%\s*static\s+["\']([^"\']+)["\']\s*%}'
        for match in re.finditer(static_pattern, content):
            static_file = match.group(1)
            dependencies["static_files"].append(static_file)
        
        # 查找 URL 引用
        url_pattern = r'{%\s*url\s+["\']([^"\']+)["\'][^{%]*\s*%}'
        for match in re.finditer(url_pattern, content):
            url_name = match.group(1)
            dependencies["urls"].append(url_name)
        
        return dependencies
    
    def check_all_dependencies(self):
        """检查所有模板的依赖关系"""
        self.log("开始检查模板依赖关系...")
        
        templates = self.find_all_templates()
        self.log(f"找到 {len(templates)} 个模板文件", "FOUND")
        
        # 分析每个模板
        for template in templates:
            dependencies = self.analyze_template(template)
            if dependencies:
                self.dependencies[template] = dependencies
        
        # 检查依赖关系
        self.validate_dependencies()
        
        self.log("依赖关系检查完成", "SUCCESS")
    
    def validate_dependencies(self):
        """验证依赖关系是否正确"""
        self.log("验证依赖关系...")
        
        all_templates = set(self.dependencies.keys())
        
        for template, deps in self.dependencies.items():
            # 检查 extends 的模板是否存在
            for extends_template in deps["extends"]:
                if not self._template_exists(extends_template):
                    self.errors.append(f"模板 {template} extends 的模板不存在: {extends_template}")
            
            # 检查 include 的模板是否存在
            for include_template in deps["includes"]:
                if not self._template_exists(include_template):
                    self.errors.append(f"模板 {template} include 的模板不存在: {include_template}")
            
            # 检查自定义标签
            for tag in deps["custom_tags"]:
                if tag == "dict_extras":
                    # 检查 dict_extras 标签库是否存在
                    dict_extras_path = self.apps_dir / "family_calendar" / "templatetags" / "dict_extras.py"
                    if not dict_extras_path.exists():
                        self.errors.append(f"自定义标签库不存在: dict_extras")
            
            # 检查静态文件
            for static_file in deps["static_files"]:
                if not self._static_file_exists(static_file):
                    self.warnings.append(f"静态文件可能不存在: {template} -> {static_file}")
    
    def _template_exists(self, template_name):
        """检查模板是否存在"""
        # Django 模板查找顺序
        
        # 1. 全局 templates 目录
        global_path = self.templates_dir / template_name
        if global_path.exists():
            return True
        
        # 2. 项目模板目录
        project_path = self.project_templates_dir / template_name
        if project_path.exists():
            return True
        
        # 3. 应用模板目录
        app_template_dirs = [
            self.apps_dir / "events" / "templates",
            self.apps_dir / "family" / "templates",
            self.apps_dir / "housework" / "templates",
            self.apps_dir / "family_calendar" / "templates"
        ]
        
        for app_dir in app_template_dirs:
            app_path = app_dir / template_name
            if app_path.exists():
                return True
        
        # 4. 检查是否是重定向到 myhome 子目录
        if not template_name.startswith("myhome/"):
            myhome_path = self.templates_dir / "myhome" / template_name
            if myhome_path.exists():
                return True
        
        return False
    
    def _static_file_exists(self, static_path):
        """检查静态文件是否存在"""
        # 静态文件查找目录
        static_dirs = [
            self.project_root / "static",
            self.project_root / "myhome_project" / "static"
        ]
        
        for static_dir in static_dirs:
            full_path = static_dir / static_path
            if full_path.exists():
                return True
        
        return False
    
    def check_view_references(self):
        """检查视图文件中的模板引用"""
        self.log("检查视图文件中的模板引用...")
        
        view_files = [
            self.apps_dir / "events" / "views.py",
            self.apps_dir / "family" / "views.py",
            self.apps_dir / "housework" / "views.py",
            self.apps_dir / "family_calendar" / "views.py"
        ]
        
        template_refs = []
        
        for view_file in view_files:
            if view_file.exists():
                content = view_file.read_text(encoding='utf-8')
                
                # 查找 render 函数中的模板路径
                render_pattern = r'render\s*\([^,]*,\s*["\']([^"\']+)["\'][^)]*\)'
                for match in re.finditer(render_pattern, content):
                    template_name = match.group(1)
                    template_refs.append({
                        "file": str(view_file.relative_to(self.project_root)),
                        "template": template_name,
                        "line": content[:match.start()].count('\n') + 1
                    })
        
        # 验证引用的模板是否存在
        for ref in template_refs:
            if not self._template_exists(ref["template"]):
                self.errors.append(
                    f"视图文件 {ref['file']} 行 {ref['line']} 引用的模板不存在: {ref['template']}"
                )
        
        self.log(f"检查了 {len(template_refs)} 个模板引用", "FOUND")
    
    def generate_report(self):
        """生成检查报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_templates": len(self.dependencies),
            "errors": self.errors,
            "warnings": self.warnings,
            "dependencies": self.dependencies
        }
        
        # 输出统计信息
        print("\n" + "="*60)
        print("📊 检查结果统计")
        print("="*60)
        print(f"总模板文件数: {len(self.dependencies)}")
        print(f"错误数量: {len(self.errors)}")
        print(f"警告数量: {len(self.warnings)}")
        
        if self.errors:
            print("\n❌ 发现的错误:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if self.warnings:
            print("\n⚠️  警告信息:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ 未发现依赖问题")
        
        print("="*60)
        
        # 保存详细报告
        report_path = self.project_root / "template_dependencies_report.json"
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"📋 详细报告已保存: {report_path}")
        
        return len(self.errors) == 0
    
    def execute(self):
        """执行完整的依赖检查"""
        self.log("开始模板依赖关系检查...")
        
        try:
            self.check_all_dependencies()
            self.check_view_references()
            return self.generate_report()
            
        except Exception as e:
            self.log(f"检查过程中出现错误: {e}", "ERROR")
            return False


def main():
    """主函数"""
    current_dir = Path(__file__).parent
    project_root = current_dir
    
    checker = TemplateDependencyChecker(project_root)
    success = checker.execute()
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
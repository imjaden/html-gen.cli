#!/usr/bin/env python3
"""构建 html-gen pip 包: 生成 src/html_gen/ (同步实现+模板+CSS+skills) 供 setuptools 打包.

用法:
  python3 scripts/build-package.py   # 生成 src/html_gen/
  python3 -m build                    # 构建 wheel (dist/)
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src' / 'html_gen'

INIT = '''"""html-gen — HTML 模板 CLI 生成器 (pip 安装入口).

实现 = 同目录 html-gen.py (scripts/build-package.py 从项目根同步), runpy 加载导出.
"""
from pathlib import Path
import runpy

_ns = runpy.run_path(str(Path(__file__).parent / 'html-gen.py'))
main = _ns['main']
__version__ = _ns['__version__']
__release_date__ = _ns['__release_date__']
'''


def main():
    shutil.rmtree(SRC, ignore_errors=True)
    SRC.mkdir(parents=True)
    (SRC / '__init__.py').write_text(INIT, encoding='utf-8')
    for f in ('html-gen.py', 'style-guide.css',
              'layout-doc.html', 'layout-table.html',
              'layout-knowledge.html', 'layout-slide.html'):
        shutil.copy2(ROOT / f, SRC / f)
    shutil.copytree(ROOT / 'skills', SRC / 'skills')
    n_skills = len(list((SRC / 'skills').iterdir()))
    print(f'✅ src/html_gen/ 生成: {len(list(SRC.iterdir()))} 项 (skills/ {n_skills} 个)')


if __name__ == '__main__':
    main()

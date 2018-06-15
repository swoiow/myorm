#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
http://alembic.zzzcomputing.com/en/latest/api/index.html
http://alembic.zzzcomputing.com/en/latest/api/commands.html
http://alembic.zzzcomputing.com/en/latest/api/config.html#alembic.config.Config
"""


from __future__ import absolute_import

import os
import os.path as osph
import sys

os.environ["LIB_DOC"] = "0"
sys.path.insert(0, osph.join(osph.abspath(osph.dirname(__file__)), osph.pardir))
sys.path.insert(0, osph.join(osph.abspath(osph.dirname(__file__)), "src"))
sys.path.insert(0, osph.join(osph.abspath(osph.dirname(__file__)), osph.pardir, "WEB"))

_migration_path = osph.join(osph.curdir, ".alembic")
_base_path = osph.abspath(osph.dirname(__file__))

_origin_line = """# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None"""

_new_line = """
from cells.db.dbutils import OrmBase
target_metadata = OrmBase.metadata

import glob
from importlib.machinery import SourceFileLoader
from os.path import (join, realpath)
mods_map = {}
mods = glob.glob(join(realpath("."), "*", "models.py")) + glob.glob(join(realpath("."), "*", "model.py"))

for idx, mod_ph in enumerate(mods):
    mod = SourceFileLoader("dynamic_imp_mod.{}".format(idx), mod_ph).load_module()

    for o in dir(mod):
        _obj = type(getattr(mod, o))
        if issubclass(_obj, OrmBase) and hasattr(_obj, "__tablename__"):
            mods_map[idx] = _obj
"""


class Help(object):
    """ 帮助函数

    """

    @staticmethod
    def init_db():
        if osph.exists(_migration_path):
            return _migration_path + " has existed!"

        else:
            from alembic import command
            from alembic.config import Config

            alembic_cfg = Config(
                file_="alembic.ini",
            )
            command.init(alembic_cfg, _migration_path, template='generic')

            # 修改 env.py 文件
            patch_env()

            print("请修改 alembic.ini 中 sqlalchemy.url 的值")

    @staticmethod
    def makemigrations():
        if osph.exists(_migration_path):
            import time
            from alembic import command
            from alembic.config import Config

            alembic_cfg = Config("alembic.ini")
            output = command.revision(
                alembic_cfg,
                message=str(int(time.time())),
                autogenerate=True,
            )

        else:
            return _migration_path + " not existed!"

    @staticmethod
    def migrate(revision="head"):
        if osph.exists(_migration_path):
            from alembic.config import Config
            from alembic import command

            alembic_cfg = Config("alembic.ini")
            # alembic_cfg.set_main_option("url", "sqlite:///database.db")  # for test

            output = command.upgrade(alembic_cfg, revision=revision)
            return output

        else:
            return _migration_path + " not existed!"

    # def auto_migrate():
    #     Help.makemigrations()
    #     Help.migrate()

    def __repr__(self):
        return "<{} @{}>".format(self.__class__.__name__, hex(id(self.__class__)))


def patch_env():
    from alembic.config import Config
    alembic_cfg = Config("alembic.ini")

    env_path = alembic_cfg.get_main_option("script_location")
    env_path = osph.join(env_path, "env.py")
    with open(env_path, "r") as rf:
        _origin_f = rf.read()

    with open(env_path, "w") as wf:
        _new_f = _origin_f.replace(_origin_line, _new_line)
        wf.write(_new_f)


def main():
    import fire

    fire.Fire(Help)
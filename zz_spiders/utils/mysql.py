# -*- coding: utf-8 -*-
#mysql 操作类
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from zz_spiders.env import env

class Mysql(object):
    """mysql 操作类"""

#    env = ENV().getDBCfg()['spider_config']  #获取数据库配置信息

    def get_database(self,
                     db_host=env['mysql_config']['db_host'],
                     db_port=env['mysql_config']['db_port'],
                     db_name=env['mysql_config']['db_name'],
                     username=env['mysql_config']['username'],
                     password=env['mysql_config']['password'],
                     charset=env['mysql_config']['charset']
                     ):
        """数据库连接方法

        :param db_host:
            数据连接地址
        :param db_port:
            端口号
        :param db_name:
            要选择的数据库
        :param username:
            用户名
        :param password:
            密码
        :param charset:
            字符集
        :return:
            session: 数据库连接会话
            tables: 数据表的虚拟模型
        """
        engine_str = "mysql+pymysql://%s:%s@%s:%s/%s?charset=%s" % (
        username, password, db_host, db_port, db_name, charset)
        engine = sqlalchemy.create_engine(engine_str)
        session = sessionmaker(bind=engine)()

        # 下面这两句话就完成了ORM映射 Base.classes.XXXX即为映射的类
        # Base.metadata.tables['XXX']即为相应的表

        Base = automap_base()  # 自动加载所有的数据表

        try :
            Base.prepare(engine, reflect=True)
        except Exception as e:
            print(e,'连接失败')
            exit(0)

        tables = Base.classes

        return session,tables

    def make_func(self):
        """外部调用方法（仅作注释用）

        引用
        from zz_spiders.utils.mysql import Mysql
            db_engine, db_table = Mysql().get_database(DB_host='192.168.1.58',DB_name='jupin_erp_test_business')
        添加
            item = db_table.users(name='lxq', password='1234')
            session.add(item)
            session.commit()
        查询
            query_device = session.query(db_table.t_config).filter(db_table.t_config.id < 11).order_by(db_table.t_config.id.desc())
        更新
            user = session.query(db_table.users).filter_by(name="user1").first()
            user.password = "newpassword"
            session.commit()
        删除
            user = session.query(db_table.users).filter_by(name="user1").first()
            session.delete(user)
            session.commit()
        完成之后需要
            session.close()
        """

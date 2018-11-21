# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   date：          2018/11/12
   File Name：     shop_information
   Description:
-------------------------------------------------
"""

from zz_spiders.utils.mysql import Mysql
from zz_spiders.service.get_shop_list import get_shops_list
from zz_spiders.env import env
from zz_spiders.utils.date import Date


class ShopInformation:
    def get_shop(self, shop_name, key, value):
        session, db_table = Mysql().get_database()
        t_shop = db_table.t_shop
        t_shop_rank = db_table.t_shop_rank
        t_shop_category = db_table.t_shop_category
        results = session.query(t_shop, t_shop_rank, t_shop_category)\
            .join(t_shop_rank, t_shop.f_shop_rank == t_shop_rank.f_name)\
            .join(t_shop_category, t_shop.f_shop_category == t_shop_category.f_name)\
            .filter(
            t_shop.f_wangwangid == shop_name,
        )
        session.close()
        for i in results:
            key.append('f_shop_rank')
            value.append(i.t_shop.f_shop_rank)
            key.append('f_shop_category')
            value.append(i.t_shop.f_shop_category)
            key.append('f_shop_rank_id')
            value.append(i.t_shop_rank.id)
            key.append('f_shop_category_id')
            value.append(i.t_shop_category.id)

    def get_task(self, shop_name, key, value):
        session, db_table = Mysql().get_database()
        t_task = db_table.t_task
        t_employee = db_table.t_employee
        results = session.query(t_task, t_employee).join(t_employee, t_task.f_foreign_user_id == t_employee.f_foreign_user_id)\
            .filter(
            t_task.f_copy_wangwangid == shop_name,
            t_task.f_foreign_task_state_id == 2,
        )

        for result in results:
            if shop_name not in value:
                key.append('f_serviced_day')
                value.append(result.t_task.f_serviced_day)
                key.append('f_service_staff_id')
                value.append(result.t_task.f_foreign_user_id)
                key.append('f_service_staff')
                value.append(result.t_employee.f_real_name)
            else:   # 如果有多个合作周期，取最大的那一个
                index = key.index('f_serviced_day')
                v = value[index]
                if v < result.t_task.f_serviced_day:
                    value[index] = result.t_task.f_serviced_day

    def get_shop_name_details(self, shop_name, key, value):
        session, db_table = Mysql().get_database(
            db_host=env['mysql_shop_data']['db_host'],
            db_port=env['mysql_shop_data']['db_port'],
            db_name=env['mysql_shop_data']['db_name'],
            username=env['mysql_shop_data']['username'],
            password=env['mysql_shop_data']['password'],
            charset=env['mysql_shop_data']['charset']
        )
        t_shop_data = db_table.t_shop_data
        yesterday = Date().get_yesterday()
        yesterday = yesterday.strftime('%Y-%m-%d')

        results = session.query(t_shop_data.f_budget).filter(
            t_shop_data.created_at.like(yesterday+'%'),
            t_shop_data.f_nick_name == shop_name,
        )
        if len(results.all()) == 0:
            key.append('f_budget')
            value.append(0)
        session.close()

        for result in results:
            key.append('f_budget')
            value.append(0 if (result.f_budget) == None else result.f_budget)

        self.get_task(shop_name, key, value)
        self.get_shop(shop_name, key, value)

        now = Date().get_time()
        key.append('updated_at')
        value.append(now)

        dict_shop = dict(zip(key, value))

        # 插入数据，如果存在则更新数据
        t_shop_information = db_table.t_shop_information
        shop = session.query(t_shop_information).filter(
            t_shop_information.f_nick_name == shop_name
        )

        if len(shop.all()) == 0:
            # 数据库没有先插入店铺名，然后进行更新
            information = t_shop_information(f_nick_name=shop_name, created_at=now)
            session.add(information)
            session.commit()

        # 更新
        update_information = shop.first()
        if dict_shop:
            for i in dict_shop:
                update_str = 'update_information.{}="{}"'.format(i, dict_shop[i])
                exec(update_str)
            session.commit()
        session.close()

    def get_shop_name(self):
        key = []
        value = []
        zhitongche = get_shops_list(flag='zhitongche')   # 直通车
        no_grant = get_shops_list(flag='no')    # 没有授权
        zuanzhan = get_shops_list(flag='zuanzhan')  # 钻展
        zhizuan = get_shops_list(flag='zhizuan')    # 直钻

        # for shop in no_grant:
        #     key.append('f_cooperation_products')
        #     value.append(0)
        #     self.get_shop_name_details(shop['shop_name'], key, value)

        for shop in zhitongche:
            key.append('f_cooperation_products')
            value.append(1)                 # value.append('直通车')
            self.get_shop_name_details(shop['shop_name'], key, value)

        # for shop in zuanzhan:
        #     key.append('f_cooperation_products')
        #     value.append(2)            # value.append('钻展')
        #     self.get_shop_name_details(shop['shop_name'], key, value)

        for shop in zhizuan:
            key.append('f_cooperation_products')
            value.append(3)            # value.append('直钻')
            self.get_shop_name_details(shop['shop_name'], key, value)


if __name__ == '__main__':
    ShopInformation().get_shop_name()
# -*- coding: utf-8 -*-
# 定时获取店铺数据
from zz_spiders.utils.mysql import Mysql

class UserShop(object):

    def get_sub_task(self):

        session, db_table = Mysql().get_database()
        t_sub_task = db_table.t_sub_task
        results = session.query(t_sub_task).filter(
            t_sub_task.f_foreign_task_state_id == 2,
            t_sub_task.f_task_category_id == 1
        )
        session.close()
        return results

    def generate_shop_list(self):

        users = {}
        sub_tasks = self.get_sub_task()

        # 根据userid生成店铺列表
        for task in sub_tasks:
            if task.f_foreign_user_id in users:
                users[task.f_foreign_user_id].append(task.f_copy_wangwangid)
            else:
                users[task.f_foreign_user_id] = []
                users[task.f_foreign_user_id].append(task.f_copy_wangwangid)

        # 店铺去重
        for user in users:
            users[user] = set(users[user])

        # 重新结构
        result = []
        for key in users:
            #店铺
            for shop in users[key]:
                result.append({
                    'user_id': key,
                    'shop_name': shop,
                })
        return result

    def get(self):
        shops = self.generate_shop_list()
        return shops
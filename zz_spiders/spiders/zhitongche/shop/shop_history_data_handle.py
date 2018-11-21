# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   date：          2018/11/20
   File Name：     shop_history_data_handle
   Description:
-------------------------------------------------
"""
from zz_spiders.utils.mongoDB import Mongodb
import re
from zz_spiders.utils.date import Date
from zz_spiders.utils.mysql import Mysql
from zz_spiders.env import env


class ShopHistoryDataHandle:
    def handle_main(self):
        client_zhitongche = Mongodb('zhitongche_history_data', 'zz_web')
        client_zuanzhan = Mongodb('zuanzhan_history_data', 'zz_web')

        option = {
            'judge': {"created_at": re.compile(Date().get_today())}
        }
        zhitongche = client_zhitongche.find_many(option)
        zuanzhan = client_zuanzhan.find_many(option)

        for ztc in zhitongche:
            dict_ztc = {}
            data = ztc['data']
            if data:
                dict_ztc['f_nick_name'] = ztc['shopname']
                dict_ztc['f_cost'] = data['cost'] if data['cost'] else 0
                dict_ztc['f_cpc'] = data['cpc'] if data['cpc'] else 0
                # dict_ztc['f_roi'] = data['roi'] if data['roi'] else 0
                # dict_ztc['f_alipay'] = data['cpc'] if data['cpc'] else 0
                # dict_ztc['f_cvr'] = data['cpc'] if data['cpc'] else 0
            dict_ztc['f_budget'] = ztc['budget']
            dict_ztc['f_status'] = ztc['status']
            dict_ztc['created_at'] = ztc['created_at']
            dict_ztc['updated_at'] = ztc['updated_at']

            self.save_to_mysql(dict_ztc)

    def save_to_mysql(self, dict_product):
        session, db_table = Mysql().get_database(
            db_host=env['mysql_shop_data']['db_host'],
            db_port=env['mysql_shop_data']['db_port'],
            db_name=env['mysql_shop_data']['db_name'],
            username=env['mysql_shop_data']['username'],
            password=env['mysql_shop_data']['password'],
            charset=env['mysql_shop_data']['charset']
        )

        t_shop_data = db_table.t_shop_data

        # 插入
        exec_str = 'data=t_shop_data('
        for i in dict_product:
            exec_str += '{}="{}" '.format(i, dict_product[i])

        exec_str = exec_str.strip().replace(' ', ',') + ')'
        print(exec_str)

        exec(exec_str)
        add_str = 'session.add(data)'
        exec(add_str)

        session.commit()
        session.close()


if __name__ == '__main__':
    ShopHistoryDataHandle().handle_main()

# -*- coding: utf-8 -*-
# mongoDB 操作类
# $lt         小于
# $lte        小于等于
# $gt         大于
# $gte        大于等于
# $ne         不等于
# $in         in 检查目标属性值是条件表达式中的一员
# $nin        not in
# $set        set(用于 update 语句)
# $unset      与 $set 相反，表示移除文档属性。
# $inc        += (用于 update 语句)
# $exists     exists(判断是否存在，仅有 True 和 False 两个值)
# $all        属性值包含全部条件元素, 注意和 $in 的区别
# $size       匹配数组属性元素的数量
# $type       判断属性类型
# $regex      正则表达式查询
# $elemMatch  子属性里的查询
# $push       向数组属性添加元素
# $pushAll    向数组属性添加元素
# $addToSet   和 $push 类似，不过仅在该元素不存在时才添加(Set 表示不重复元素集合)
# $each       添加多个元素用
# $pop        移除数组属性的元素(按数组下标移除)
# $pull       按值移除
# $pullAll    移除所有符合提交的元素
# $where      用 JS 代码来代替有些丑陋的 $lt、$gt
# 这些操作的更详细用法在可以在MongoDB官方文档找到：
# https://docs.mongodb.com/manual/reference/operator/query/

import pymongo
import traceback
from bson.objectid import ObjectId
from zz_spiders.env import env


# collection 连接集合名称（必填）
class Mongodb:
    host = env['mongodb_config']['host']
    port = env['mongodb_config']['port']
    user = env['mongodb_config']['user']
    password = env['mongodb_config']['password']
    auth_databases = env['mongodb_config']['auth_db']
    data_databases = env['mongodb_config']['data_db']

    client = pymongo.MongoClient(host=host, port=port)
    db = None
    collection = None

    def __init__(self, collection, db):
        self.db = self.client[self.data_databases[db]]

        if self.user and self.password:
            self.db.authenticate(self.user, self.password, self.auth_databases)

        self.collection = self.db[collection]

    # 存储方法 item：需要存储的数据（必填）
    # 如果集合不存在会自动创建

    def save_data(self, item):
        try:
            data = {}
            for fild in item:
                data[fild] = item[fild]
            saveResponse = self.collection.insert_one(data)
            log = "mongoDB.py：数据存储成功，_id【{0}】".format(saveResponse.inserted_id)

            # if(isinstance(item, dict)):
            #     # 单条数据
            #     saveResponse = self.collection.insert_one(item)
            #     self.log.info("mongoDB.py：单条数据存储成功【{0}】".format(saveResponse.inserted_id))
            #     # return saveResponse.inserted_id
            # elif isinstance(item, list):
            #     # 多条数据
            #     saveResponse = self.collection.insert_many(item)
            #     self.log.info("mongoDB.py：多条数据存储成功")
            #     # return saveResponse

        except Exception:
            log = "mongoDB.py：数据存储失败，失败原因：\n{0}，数据：{1}".format(traceback.format_exc(), item)
            return log

    # 查找一条数据方法 judge：查找条件（必填）
    # 如果查找到多条数据 则返回第一条
    # 例：find_one('aa',{'name': 'Mike'})
    # 返回值：{}
    # 未查到时返回 None

    def find_one(self, judge):
        result = self.collection.find_one(judge)
        return result

        # 查找多条数据方法
        # options = {
        # judge：查找条件（必填）[{},{}]
        # count：查询总数 True/False
        # sort：排序字段 aa
        # order：升序（asc）降序（desc）
        # skip: 偏移几个位置，比如偏移2，就忽略前2个元素，得到第三个及以后的元素
        #       ( 最好不用，数据量大的时候容易内存溢出 )
        # limit：指定要取的结果个数

    # }
    # 返回值：[{},{}]
    # 未查到时返回 []

    def find_many(self, options):
        if 'count' in options:
            results = self.collection.find(options['judge']).count()
            return results
        elif 'sort' in options:
            if 'order' in options:
                results = self.collection.find(options['judge']).sort(
                    options['sort'], pymongo.ASCENDING if (options['order'] == 'asc') else pymongo.DESCENDING).skip(
                    int(options['skip']) if 'skip' in options else 0).limit(
                    int(options['limit']) if 'limit' in options else 0)
            else:
                results = self.collection.find(options['judge']).sort(options['sort']).skip(
                    int(options['skip']) if 'skip' in options else 0).limit(
                    int(options['limit']) if 'limit' in options else 0)
        else:
            results = self.collection.find(options['judge']).skip(
                int(options['skip']) if 'skip' in options else 0).limit(
                int(options['limit']) if 'limit' in options else 0)
        response = []
        for result in results:
            response.append(result)
        return response

    def find_exact_shop(self, options):
        '''获取指定店铺数据

        :param options: 请求参数
        :return: 返回店铺数据列表
        '''
        results = self.collection.aggregate(options['judge'])

        response = []
        for result in results:
            response.append(result)
        return response

    # 根据 _id 查找【单条】数据
    # 未查到时返回 None

    def find_one_id(self, id):
        result = self.collection.find_one({'_id': ObjectId(str(id))})
        return result

    # 更新一条数据,只会修改匹配到的第一条数据
    # judge：判断条件、data：更新的数据
    # Mongodb('111').update_one({'aa': {'$eq': '11'}}, {'$set': {'aa': 'sdfsdf'}}) 查询第一个aa=11的数据 然后更新aa的值为sdfsdf
    def update_one(self, judge, data):
        result = self.collection.update_one(judge, data)
        return result

    # 更新多条，更新所有匹配到的数据
    # judge：判断条件、data：更新的数据
    # Mongodb('111').update_many({'aa': {'$eq': '11'}}, {'$set': {'aa': 'sdfsdf'}}) 查询所有aa=11的数据 然后更新aa的值为sdfsdf
    def update_many(self, judge, data):
        result = self.collection.update_many(judge, data)
        return result

    # 删除一条数据,只会删除匹配到的第一条数据
    # judge：判断条件
    # Mongodb('111').delete_one({'aa': '44'})
    def delete_one(self, judge):
        result = self.collection.delete_one(judge)
        return result

    # 删除多条，删除所有匹配到的数据
    # judge：判断条件、data：删除的数据
    # Mongodb('111').delete_many({'aa': '44'})
    def delete_many(self, judge):
        result = self.collection.delete_many(judge)
        return result

    def close(self):
        self.client.close()

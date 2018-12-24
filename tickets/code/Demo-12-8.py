# coding: utf-8

import os
import re
import random
import datetime
from pyltp import *
from collections import OrderedDict

today = datetime.datetime.now()
rand = random.randint(0, 100)

sent_start = ['你好,我是机票精灵,我能为您提供订票服务.', '很高兴为您提供订票服务', '我能为您提供订票服务', '你好,我是机票精灵,我可以为您查机票信息']
sent_restart = ['好的，可以开始重新订票了', '好的，从新开始', '那就重新开始吧', '好，从新开始吧', '好，可以重新开始了', '可以，重新开始了']
sent_error1 = ['不好意思,', '抱歉,', '对不起,', 'sorry,']
sent_error2 = ['我没听懂,请说点订票相关的事吧', '您说点具体订票的事吧', '来聊点具体订票的事', '我不太懂您说的，请您说一些订票相关的问题吧']
sent_topic = {
    'sTime': ['您需要什么时间的机票', '您希望什么时候的机票', '您想要什么时间的机票', '您对出发时间什么要求', '您想要什么时间的票', '您想要什么时间的飞机票'],
    'dCity': ['您想飞去哪里', '请问您想去哪里呢', '请问目的地在哪里', '您想飞往哪里？'],
    'search': ['现在,为您查询到一下结果', '现在,查询结果如下', '现在，为您查到这些机票', '现在，有以下机票供您选择',
               '已经为您查到这些机票信息', '现在，已经有了这些信息', '有如下机票信息', '您有一下几种票可选']}
over = ['请告诉进一步筛选的条件', '如需筛选，请告诉我您的要求', '请告诉我您的筛选条件', '请说一下您的筛选要求']
sent_multiAsk = {
    'sTime': ['我需要您机票的时间', '我想知道您机票的时间', '请告诉我：您机票的时间', '请告诉我：您机票的时间', '请说一下：什么时间的机票',
              '我没有听到更多与时间有关的信息', '我没有听到更多与时间有关的信息'],
    'dCity': ['我需要您的目的地', '您的目的地是哪里', '您的目的地是哪里', '请告诉我您机票的目的地', '我没有听到更多与地点有关的信息', '我没有听到更多有用的信息']}

tickets_set1 = ['票', '机票', '飞机票']
tickets_set3 = ['重新', '重', '还要', '再来']

set_confirm = ['确认', '是的', '确定', '好的', '可以']
set_not_confirm = ['不确定', '不是', '没有', '不行', '不好', '没了', '没']

set_class = ['经济舱', '高端经济舱', '公务舱', '商务舱', '头等舱']
set_flight_type_big = ['B747', '747', 'B757', '757', 'B767', '767', 'B777', '777', 'B787', '787', 'M11', 'K300', 'K310', 'K330', 'K340']
set_flight_type_small = ['B737', '737', 'K320', 'K320', 'M82', 'M90']
set_flight_type_total = ['B737', '737', 'K320', 'K320', 'M82', 'M90', 'B747', '747', 'B757', '757', 'B767', '767', 'B777', '777', 'B787', '787',
                         'M11', 'K300', 'K310', 'K330', 'K340']
set_flight_type_boyin = ['B737', '737', 'B747', '747', 'B757', '757', 'B767', '767', 'B777', '777', 'B787', '787']
set_flight_type_maidao = ['M11', 'M82', 'M90']
set_flight_type_kongke = ['K320', 'K320', 'K300', 'K300', 'K310', 'K310', 'K330', 'K330', 'K340', 'K340']
set_company = ['中国国际航空公司', '国航', '东方航空公司', '东方航空', '东航', '南方航空公司', '南方航空', '南航', '海南航空公司', '幸福航空', '长龙航空', '成都航空',
               '海南航空', '海航', '上海航空公司', '上海航空', '上航', '山东航空公司', '山东航空', '山航', '深圳航空公司', '云南祥鹏航空', '西藏航空', '奥凯航空',
               '深圳航空', '深航', '厦门航空公司', '厦门航空', '厦航', '四川航空公司', '四川航空', '川航', '大新华航空', '大新华', '春秋航空', '吉祥航空',
               '鹰联航空', '华夏航空', '中国联合航空公司', '联合航空', '联航', '西部航空', '成都航空']
set_province = ['江苏省', '江苏', '浙江省', '浙江', '山东省', '山东', '福建省', '福建', '江西省', '江西', '安徽省', '安徽', '河南省', '河南', '四川省', '内蒙古',
                '河北省', '河北', '山西省', '山西', '辽宁省', '辽宁', '吉林省', '吉林', '陕西省', '陕西', '甘肃省', '甘肃', '四川', '云南省', '云南', '宁夏',
                '青海省', '青海', '广东省', '广东', '广西省', '广西', '海南省', '海南', '湖北省', '湖北', '湖南省', '湖南', '贵州省', '贵州', '西藏', '新疆']
set_sub_province = ['上海', '南京', '南通', '无锡', '常州', '徐州', '盐城', '连云港', '杭州', '宁波', '温州', '舟山', '黄岩', '昆明', '丽江', '德宏', '保山',
                    '衢州', '义乌', '济南', '青岛', '威海', '烟台', '临沂', '潍坊', '东营', '济宁', '福州', '厦门', '泉州', '迪庆', '重庆', '万州', '安顺',
                    '龙岩冠', '武夷山', '南昌', '赣州', '九江', '景德镇', '井冈山', '合肥', '黄山', '安庆', '阜阳', '北京', '攀枝花', '南充', '宜宾', '黎平',
                    '天津', '石家庄', '秦皇岛', '太原', '大同', '长治', '运城', '呼和浩特', '海拉尔', '赤峰', '满洲里', '绵阳', '西昌', '广元', '达州', '兴义',
                    '乌兰浩特', '锡林浩特', '乌海', '包头', '通辽', '沈阳', '大连', '锦州', '丹东', '朝阳', '长春', '吉林', '成都', '泸州', '九寨沟', '昌都',
                    '延吉', '哈尔滨', '齐齐哈尔', '佳木斯', '牡丹江', '黑河', '西安', '汉中', '延安', '榆林', '安康', '兰州', '洛阳', '南阳', '常德', '永州',
                    '敦煌', '嘉峪关', '庆阳', '西宁', '格尔木', '银川', '乌鲁木齐', '阿克', '喀什', '伊宁', '塔城', '阿尔泰', '怀化', '郑州', '长沙', '张家界',
                    '库车', '且末', '和田', '库尔勒', '那拉提', '富蕴', '吐鲁番', '广州', '深圳', '珠海', '汕头', '湛江', '襄樊', '恩施', '宜昌', '荆州', '拉萨',
                    '梅县', '南宁', '桂林', '柳州', '北海', '梧州', '海口', '三亚', '武汉', '西双版纳', '文山', '大理', '思茅', '临沧', '昭通', '贵阳', '铜仁']
dict_plane_to_province = {'虹桥机场': '上海', '浦东机场': '上海', '禄口机场': '南京', '兴东机场': '南通', '硕放机场': '无锡', '白莲机场': '柳州',
                          '奔牛机场': '常州', '观音机场': '徐州', '南洋机场': '盐城', '白塔埠机场': '连云港', '萧山机场': '杭州', '塔城机场': '塔城',
                          '栎社机场': '宁波', '永强机场': '温州', '普陀山机场': '舟山', '路桥机场': '黄岩', '衢州机场': '衢州', '伊宁机场': '伊宁',
                          '义乌机场': '义乌', '永安机场': '东营', '济宁机场': '济宁', '云端机场': '保山', '香格里拉机场': '迪庆', '福城机场': '北海',
                          '遥墙机场': '济南', '流亭机场': '青岛', '大水泊机场': '威海', '莱山机场': '烟台', '沐埠岭机场': '临沂', '黄果树机场': '安顺',
                          '长乐机场': '福州', '高崎机场': '厦门', '晋江机场': '泉州', '豸山机场': '龙岩冠', '邦达机场': '昌都', '库尔勒机场': '库尔勒',
                          '武夷山机场': '武夷山', '昌北机场': '南昌', '黄金机场': '赣州', '庐山机场': '九江', '敦煌机场': '敦煌', '嘉峪关机场': '嘉峪关',
                          '罗家机场': '景德镇', '井冈山机场': '井冈山', '骆岗机场': '合肥', '屯溪机场': '黄山', '五里铺机场': '安康', '中川机场': '兰州',
                          '天柱山机场': '安庆', '首都机场': '北京', '南苑机场': '北京', '王村机场': '长治', '关公机场': '运城', '天河机场': '武汉',
                          '滨海机场': '天津', '正定机场': '石家庄', '山海关机场': '秦皇岛', '武宿机场': '太原', '格尔木机场': '格尔木', '河东机场': '银川',
                          '白塔机场': '呼和浩特', '东山机场': '海拉尔', '土城子机场': '赤峰', '西郊机场': '满洲里', '喀什机场': '喀什', '大兴机场': '铜仁',
                          '乌兰浩特机场': '乌兰浩特', '锡林浩特机场': '锡林浩特', '乌海机场': '乌海',  '贡嘎机场': '拉萨', '庆阳机场': '庆阳', '曹家堡机场': '西宁',
                          '二里半机场': '包头', '通辽机场': '通辽', '桃仙机场': '沈阳', '周水子机场': '大连', '怀仁机场': '大同', '大理机场': '大理',
                          '小岭子机场': '锦州', '浪头机场': '丹东', '朝阳机场': '朝阳', '龙嘉机场': '长春', '普者黑机场': '文山', '库车机场': '库车',
                          '二台子机场': '吉林', '朝阳川机场': '延吉', '太平机场': '哈尔滨', '三家子机场': '齐齐哈尔', '地窝铺机场': '乌鲁木齐', '苏温宿机场': '阿克',
                          '东郊机场': '佳木斯', '海浪机场': '牡丹江', '黑河机场': '黑河', '西双版纳机场': '西双版纳', '沙市机场': '荆州', '刘集机场': '襄樊',
                          '咸阳机场': '西安', '西关机场': '汉中', '二十里铺机场': '延安', '西沙机场': '榆林', '思茅机场': '思茅', '美兰机场': '海口',
                          '那拉提机场': '那拉提', '富蕴机场': '富蕴', '吐鲁番机场': '吐鲁番', '白云机场': '广州', '阿尔泰机场': '阿尔泰', '和田机场': '和田',
                          '宝安机场': '深圳', '三灶机场': '珠海', '外砂机场': '汕头', '昭通机场': '昭通', '龙洞堡机场': '贵阳', '长洲岛机场': '梧州',
                          '湛江机场': '湛江', '梅县机场': '梅县', '吴圩机场': '南宁', '两江机场': '桂林', '临沧机场': '临沧', '三峡机场': '宜昌', '且末机场': '且末',
                          '桃花源机场': '常德', '零陵机场': '永州', '芷江机场': '怀化', '新郑机场': '郑州', '北郊机场': '洛阳', '黄花机场': '长沙',
                          '姜营机场': '南阳', '江北机场': '重庆', '五桥机场': '万州', '黎平机场': '黎平', '荷花机场': '张家界', '兴义机场': '兴义',
                          '双流机场': '成都', '蓝田机场': '泸州', '黄龙机场': '九寨沟', '保安营机场': '攀枝花', '凤凰机场': '三亚', '许家坪机场': '恩施',
                          '高坪机场': '南充', '莱坝机场': '宜宾', '南郊机场': '绵阳', '青山机场': '西昌', '盘龙机场': '广元', '河市机场': '达州',
                          '巫家坝机场': '昆明', '三义机场': '丽江', '芒市机场': '德宏'}
nums_map = {'一': 1, '两': 2, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '1': 1, '2': 2, '3': 3, '4': 4,
            '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
time_map = {'下一': 7 - today.weekday(), '下二': 7 - today.weekday() + 1, '下日': 7 - today.weekday() + 6, '下四': 7 - today.weekday() + 3,
            '下三': 7 - today.weekday() + 2, '下天': 7 - today.weekday() + 6, '下六': 7 - today.weekday() + 5, '下五': 7 - today.weekday() + 4,
            '一': 7 - today.weekday(), '六': 7 - today.weekday() + 5, '天':  7 - today.weekday() + 6, '二': 7 - today.weekday() + 1,
            '日': 7 - today.weekday() + 6, '三':  7 - today.weekday() + 2, '四': 7 - today.weekday() + 3, '五': 7 - today.weekday() + 4,
            '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
# time_map1 = {'一': 0 - today.weekday(), '六': 5 - today.weekday(), '天': 6 - today.weekday(), '二': 1 - today.weekday(),
#              '日': 6 - today.weekday(), '三': 2 - today.weekday(), '四': 3 - today.weekday(), '五': 4 - today.weekday(),
#              '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
common_used_numerals_tmp = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '百': 100,
                            '千': 1000, '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15, '十六': 16, '十七': 17, '十八': 18, '十九': 19,
                            '一十': 10, '一十一': 11, '一十二': 12, '一十三': 13, '一十四': 14, '一十五': 15, '一十六': 16,
                            '一十七': 17, '一十八': 18, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                            '一十九': 19, '二十': 20, '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 23}
help_dict = {'sTime': '时间1', 'dTime': '时间2', 'sCity': '地点1', 'dCity': '地点2', 'nTickets': '票数', 'discount': '折扣',
             'price_flag': '价格标记', 'time_flag': '时间标记', 'class': '舱位', 'company': '公司', 'flight_type': '机型', 'flight_price': '价格'}


class Demo:
    def __init__(self, model_path='/home/spurs/ltp_data_v3.4.0/', result_path='/home/spurs/result', sent_path='/home/spurs/sentence', show=True):
        self.show = show
        self.LTP_DATA_DIR = model_path
        self.RES_DIR = result_path
        self.SENT_DIR = sent_path

        self.state = 0
        self.sents = None  # For the input
        self.answer = None  # For the output
        self.topic = None
        self.error = None
        self.ticket_info = OrderedDict({
            'sTime': None,  # 起始时间 时间不能超过两个月 精确到小时 查找前后一小时的内容
            'dTime': None,  # 截止时间 时间不能超过两个月
            'sCity': '广州',  # 始发地 检查始发地是否有机场
            'dCity': None,  # 目的地 检查目的地是否有机场
            'nTickets': 1,  # 数量 订票数量上限是10张
            'class': None,  # 舱位 可以指定一个舱位，或者否定一个舱位
            'company': None,  # 航空公司 可以指定一个公司，或者否定一个公司
            'flight_type': None,  # 机型 指定或者否定一个机型
            'flight_price': None,  # 价格范围
            'discount': None,  # 折扣
            'price_flag': None,
            'time_flag': None})
        self.askInfo_nums = OrderedDict({
            'sTime': 0,
            'dCity': 0})

    def load_model(self):
        cws_model_path = os.path.join(self.LTP_DATA_DIR, 'cws.model')  # 分词
        pos_model_path = os.path.join(self.LTP_DATA_DIR, 'pos.model')  # 词性标注

        # 分词
        self.segmentor = Segmentor()  # 初始化实例
        self.segmentor.load_with_lexicon(cws_model_path, os.path.join(self.LTP_DATA_DIR, 'lexicon'))  # 加载模型

        # 词性标注
        self.postagger = Postagger()  # 初始化模型
        self.postagger.load_with_lexicon(pos_model_path, os.path.join(self.LTP_DATA_DIR, 'post_lexicon'))  # 加载模型

    def _basic_handle(self, sentence):
        self.sentence = sentence.replace('号', '日')
        self.sentence = self.sentence.replace('元', '块钱')
        self.sentence = self.sentence.replace('点', '时')
        self.sentence = self.sentence.replace('今年', '2017年')
        self.sentence = self.sentence.replace('明年', '2018年')
        self.sentence = self.sentence.replace('这个月', '12月')
        self.sentence = self.sentence.replace('订张', '订一张')

        # 替换机型
        self.sentence = self.sentence.replace('麦道', 'M')
        self.sentence = self.sentence.replace('空中客车', 'K')
        self.sentence = self.sentence.replace('空客', 'K')
        self.sentence = self.sentence.replace('波音', 'B')
        self.sentence = self.sentence.replace('波音飞机', 'B')

        result_f = open(self.RES_DIR, 'a', encoding='utf-8')

        self.words = self.segmentor.segment(self.sentence)  # 分词
        temp = '\t'.join(self.words) + '\n'
        result_f.write(temp)
        if self.show:
            print(temp, end='')

        self.postags = self.postagger.postag(self.words)  # 词性标注
        temp = '\t'.join(self.postags) + '\n'
        result_f.write(temp)
        if self.show:
            print(temp, end='')

        result_f.write('\n')
        result_f.close()

    def release_model(self):
        self.segmentor.release()  # 释放模型
        self.postagger.release()

    def _default(self):
        """ 直接重置基本数据 """
        self.state = 0
        self.topic = None
        self.error = None
        self.ticket_info = OrderedDict({
            'sTime': None,  # 起始时间 时间不能超过两个月 精确到小时 查找前后一小时的内容
            'dTime': None,  # 截止时间 时间不能超过两个月
            'sCity': '广州',  # 始发地 检查始发地是否有机场
            'dCity': None,  # 目的地 检查目的地是否有机场
            'nTickets': 1,  # 数量 订票数量上限是10张
            'class': None,  # 舱位 可以指定一个舱位，或者否定一个舱位
            'company': None,  # 航空公司 可以指定一个公司，或者否定一个公司
            'flight_type': None,  # 机型 指定或者否定一个机型
            'flight_price': None,  # 价格范围
            'discount': None,  # 折扣
            'price_flag': None,  # 价格标记
            'time_flag': None})  # 时间标记
        self.askInfo_nums = OrderedDict({
            'sTime': 0,
            'dCity': 0})

    def _chinese2digits(self, chinese):
        common_used_numerals = {}
        for key in common_used_numerals_tmp:
            common_used_numerals[key] = common_used_numerals_tmp[key]
        total = 0
        r = 1  # 表示单位：个十百千...
        for i in range(len(chinese) - 1, -1, -1):
            val = common_used_numerals.get(chinese[i])
            if val >= 10 and i == 0:  # 应对 十三 十四 十*之类
                if val > r:
                    r = val
                    total = total + val
                else:
                    r = r * val
                    # total =total + r * x
            elif val >= 10:
                if val > r:
                    r = val
                else:
                    r = r * val
            else:
                total = total + r * val
        return total

    def _time_help(self):
        """ 将中文数字转为阿拉伯数字 """
        ws = []
        for word in self.words:
            if word in ['点', '时', '月', '日']:
                ws[-1] = ws[-1] + word
            else:
                ws.append(word)
        temp = ''
        for word in ws:
            year = re.search(r"(今|明|[零一二三四五六七八九]{4})年", word)
            month = re.search(r"([零一二三四五六七八九十]{1,2}|下)[个]*月", word)
            day = re.search(r"([零一二三四五六七八九十]{1,3})日", word)
            hour = re.search(r"([零一二三四五六七八九十]{1,3})时", word)
            discount = re.search(r"(^[零一二三四五六七八九]{1,2}$)", word)
            money = re.search(r"(^[零一二三四五六七八九]?[千]?[百]?[十]?$)", word)
            if year:
                y = year.groups()[0]
                if y == '明':
                    temp += '2018'
                elif y == '今':
                    temp += '2017'
                else:
                    temp += str(common_used_numerals_tmp[y[0]]) +str(common_used_numerals_tmp[y[1]]) + str(common_used_numerals_tmp[y[2]]) + str(common_used_numerals_tmp[y[3]])
                temp += '年'
            elif month:
                m = month.groups()[0]
                if m == '下':
                    temp += '2018年1月'
                elif m in common_used_numerals_tmp.keys():
                    temp += str(common_used_numerals_tmp[m])
                else:
                    self.error = (1, '抱歉，您输入的月份我没听懂。')
                    return None
                temp += '月'
            elif day:
                d = day.groups()[0]
                if d in common_used_numerals_tmp.keys():
                    temp += str(common_used_numerals_tmp[d])
                else:
                    self.error = (1, '抱歉，您输入的月份我没听懂。')
                    return None
                temp += '日'
            elif hour:
                h = hour.groups()[0]
                if h in common_used_numerals_tmp.keys():
                    temp += str(common_used_numerals_tmp[h])
                else:
                    self.error = (1, '抱歉，您输入的月份我没听懂。')
                    return None
                temp += '时'
            elif discount:
                dis = discount.groups()[0]
                if len(dis) == 2:
                    temp += str(common_used_numerals_tmp[dis[0]]) + str(common_used_numerals_tmp[dis[1]])
                elif len(dis) == 1:
                    temp += str(common_used_numerals_tmp[dis[0]])
            elif money:
                mo = money.groups()[0]
                temp += str(self._chinese2digits(mo))
            else:
                temp += word
        return temp

    def _time(self):
        """ 判断时间
        返回时间：
        time_1 = [0, 0, 0, 0]
        time_2 = [0, 0, 0, 0]
        (time_1, time_2)
        """
        sent = self._time_help()
        print(sent)
        if self.error:
            return None
        now = datetime.datetime.now()
        flag = False

        y = re.findall(r"(\d{4})年", sent)
        if y:
            flag = True
            if len(y) > 2:
                self.error = (1, "抱歉，您输入的日期有问题。")
                return None
            elif len(y) == 1:
                if int(y[0]) != 2017 and int(y[0]) != 2018:
                    self.error = (1, "不好意思，您输入的日期有问题")
                    return None
                if int(y[0]) == 2017:
                    self.ticket_info['sTime'] = [now.year, now.month, now.day, now.hour]
                    cur = now + datetime.timedelta(5)
                    self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, 23]
                elif int(y[0]) == 2018:
                    self.ticket_info['sTime'], self.ticket_info['dTime'] = [2018, 1, 1, 0], [2018, 1, 5, 23]
            else:
                if int(y[0]) < 2017 or int(y[1]) < 2017 or int(y[0]) > 2018 or int(y[1]) > 2018 or int(y[0]) > int(y[1]):
                    self.error = (1, "不好意思，您输入的日期有点问题")
                    return None
                if int(y[0]) == int(y[1]):
                    if int(y[0]) == 2017:
                        self.ticket_info['sTime'] = [now.year, now.month, now.day, now.hour]
                        cur = now + datetime.timedelta(5)
                        self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, 23]
                    else:
                        self.ticket_info['sTime'], self.ticket_info['dTime'] = [2018, 1, 1, 0], [2018, 1, 5, 23]
                elif int(y[0]) != int(y[1]):
                    self.ticket_info['sTime'], self.ticket_info['dTime'] = [2017, 12, 25, 0], [2018, 1, 1, 23]

        m = re.findall(r"(\d{1,2})月", sent)
        if m:
            flag = True
            if len(m) > 2:
                self.error = (1, '抱歉，您输入的日期有误')
                return None
            elif len(m) == 1:
                if int(m[0]) < 0 or int(m[0]) > 12:
                    self.error = (1, '抱歉，您输入的日期有误')
                    return None
                if self.ticket_info['sTime'] is None:
                    self.ticket_info['sTime'], self.ticket_info['dTime'] = [now.year, int(m[0]), 1, 0], [now.year, int(m[0]), 5, 23]
                else:
                    self.ticket_info['sTime'][1], self.ticket_info['dTime'][1] = int(m[0]), int(m[0])
                    if int(m[0]) == now.month:
                        self.ticket_info['sTime'][2], self.ticket_info['sTime'][3] = now.day, 0
                        try:
                            a = self.ticket_info['sTime']
                            cur = datetime.datetime(a[0], a[1], a[2], a[3]) + datetime.timedelta(5)
                        except ValueError:
                            self.error = (1, '抱歉，您输入的日期有误')
                            return None
                        self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, cur.hour]
            else:
                if int(m[0]) < 0 or int(m[0]) > 12 or int(m[1]) < 0 or int(m[1]) > 12:
                    self.error = (1, '抱歉，您输入的日期有误')
                    return None
                if self.ticket_info['sTime'] is None:
                    if int(m[0]) > int(m[1]):
                        self.ticket_info['sTime'], self.ticket_info['dTime'] = [2017, int(m[0]), 1, 0], [2018, int(m[1]), 1, 23]
                    elif int(m[0]) == int(m[1]):
                        self.ticket_info['sTime'], self.ticket_info['dTime'] = [2017, int(m[0]), 1, 0], [2017, int(m[1]), 5, 23]
                    elif int(m[0]) < int(m[1]):
                        self.ticket_info['sTime'], self.ticket_info['dTime'] = [2017, int(m[0]), 1, 0], [2017, int(m[1]), 1, 23]
                else:
                    self.ticket_info['sTime'][1], self.ticket_info['dTime'][1] = int(m[0]), int(m[1])
                    if int(m[0]) == int(m[1]):
                        if int(m[0]) == now.month:
                            self.ticket_info['sTime'][2], self.ticket_info['sTime'][3] = now.day, 0
                            a = self.ticket_info['sTime']
                            cur = datetime.datetime(a[0], a[1], a[2], a[3]) + datetime.timedelta(5)
                            self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, 23]
                        else:
                            self.ticket_info['sTime'][2:], self.ticket_info['dTime'][2:] = [1, 0], [5, 23]
                    else:
                        if int(m[0]) == now.month:
                            self.ticket_info['sTime'][2:], self.ticket_info['dTime'][2:] = [now.day, 0], [1, 23]
                        else:
                            self.ticket_info['sTime'][2:], self.ticket_info['dTime'][2:] = [1, 0], [1, 23]
            try:
                a, b = self.ticket_info['sTime'], self.ticket_info['dTime']
                cur1, cur2 = datetime.datetime(a[0], a[1], a[2], a[3]), datetime.datetime(b[0], b[1], b[2], b[3])
            except ValueError:
                self.error = (1, "你输入的日期有误")
                return None
            if (cur1 - now).days < -1 or (cur2 - cur1).days < 0 or (cur2 - cur1).days > 60:
                self.error = (1, "你输入的日期有误")
                return None

        d = re.findall(r"(\d{1,2})日[之以]*([前后])*", sent)
        if d:
            flag = True
            if len(d) > 2:
                self.error = (1, '你输入的日期有问题')
                return None
            elif len(d) == 1:
                if int(d[0][0]) < 0 or int(d[0][0]) > 31:
                    self.error = (1, '你输入的日期有问题')
                    return None
                if d[0][1] == '后':
                    if self.ticket_info['sTime'] is None:
                        self.ticket_info['sTime'] = [now.year, now.month, int(d[0][0]), 0]
                        cur = datetime.datetime(now.year, now.month, int(d[0][0])) + datetime.timedelta(5)
                        self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, 23]
                    else:
                        self.ticket_info['sTime'][2], self.ticket_info['sTime'][3] = int(d[0][0]), 0
                        a = self.ticket_info['sTime']
                        try:
                            cur = datetime.datetime(a[0], a[1], a[2], a[3]) + datetime.timedelta(5)
                        except ValueError:
                            self.error = (1, '你输入的日期有问题')
                            return None
                        self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, 23]
                elif d[0][1] == '前':
                    if self.ticket_info['sTime'] is None:
                        self.ticket_info['dTime'] = [now.year, now.month, int(d[0][0]), 23]
                        cur = datetime.datetime(now.year, now.month, int(d[0][0]))
                        if (cur - now).days < 0:
                            self.error = (1, '你输入的日期有问题')
                            return None
                        cur = max(cur - datetime.timedelta(5), now)
                        self.ticket_info['sTime'] = [cur.year, cur.month, cur.day, 0]
                    else:
                        self.ticket_info['dTime'][2], self.ticket_info['dTime'][3] = int(d[0][0]), 23
                        a = self.ticket_info['dTime']
                        try:
                            cur = datetime.datetime(a[0], a[1], a[2], a[3]) - datetime.timedelta(5)
                            cur = max(cur, now)
                        except ValueError:
                            self.error = (1, '你输入的日期有问题')
                            return None
                        self.ticket_info['sTime'] = [cur.year, cur.month, cur.day, 0]
                else:
                    if self.ticket_info['sTime'] is None:
                        self.ticket_info['sTime'], self.ticket_info['dTime'] = [now.year, now.month, int(d[0][0]), 0], [now.year, now.month, int(d[0][0]), 23]
                    else:
                        self.ticket_info['sTime'][2], self.ticket_info['dTime'][2] = int(d[0][0]), int(d[0][0])
                        try:
                            a, b = self.ticket_info['sTime'], self.ticket_info['dTime']
                            cur1, cur2 = datetime.datetime(a[0], a[1], a[2], a[3]), datetime.datetime(b[0], b[1], b[2], b[3])
                        except ValueError:
                            self.error = (1, '你输入的日期有问题')
                            return None
                        if (cur1 - now).days < -1 or (cur2 - cur1).days < 0 or (cur2 - cur1).days > 60:
                            self.error = (1, '你输入的日期有问题')
                            return None
            else:
                a, b = int(d[0][0]), int(d[1][0])
                if a < 0 or a > 31 or b < 0 or b > 31:
                    self.error = (1, '你输入的日期有问题')
                    return None
                if self.ticket_info['sTime'] is None:
                    if (a < now.day and b < now.day) or a > b:
                        self.error = (1, '你输入的日期有问题')
                        return None
                    a = max(a, now.day)
                    self.ticket_info['sTime'], self.ticket_info['dTime'] = [now.year, now.month, a, 0], [now.year, now.month, b, 23]
                else:
                    self.ticket_info['sTime'][2], self.ticket_info['dTime'][2] = a, b
                    A, B = self.ticket_info['sTime'], self.ticket_info['dTime']
                    try:
                        cur1, cur2 = datetime.datetime(A[0], A[1], A[2], A[3]), datetime.datetime(B[0], B[1], B[2], B[3])
                    except ValueError:
                        self.error = (1, '你输入的日期有问题')
                        return None
                    if (cur1 - now).days < -1 or (cur2 - cur1).days < 0 or (cur2 - cur1).days > 60:
                        self.error = (1, '你输入的日期有问题')
                        return None

        w = re.findall(r"(下)*[个]*(星期|周|礼拜)([一二三四五六日天])[之以]*([前后])*", sent)
        if w:
            flag = True
            if len(w) > 2:
                self.error = (1, "对不起，您输入的日期有误。")
                return None
            elif len(w) == 1:
                if time_map[w[0][0]+w[0][2]] < 0:
                    self.error = (1, "对不起，你输入的日期已经过去了。")
                    return None
                cur = now + datetime.timedelta(time_map[w[0][0]+w[0][2]])
                if w[0][3] == '后':
                    if self.ticket_info['sTime'] is None:
                        self.ticket_info['sTime'] = [cur.year, cur.month, cur.day, 0]
                        cur += datetime.timedelta(5)
                        self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, 23]
                    else:
                        self.ticket_info['sTime'] = [cur.year, cur.month, cur.day, 0]
                        temp = self.ticket_info['dTime']
                        if cur > datetime.datetime(temp[0], temp[1], temp[2], temp[3]):
                            self.error = (1, "对不起，您输入的时间有问题")
                            return None
                elif w[0][3] == '前':
                    if self.ticket_info['dTime'] is None:
                        self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, 23]
                        cur = max(cur - datetime.timedelta(5), now)
                        self.ticket_info['sTime'] = [cur.year, cur.month, cur.day, 0]
                    else:
                        self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, 23]
                        temp = self.ticket_info['sTime']
                        if cur < datetime.datetime(temp[0], temp[1], temp[2], temp[3]):
                            self.error = (1, "对不起，您输入的时间有问题")
                            return None
                else:
                    if self.ticket_info['sTime'] is None:
                        self.ticket_info['sTime'] = [cur.year, cur.month, cur.day, 0]
                        self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, 23]
                    else:
                        self.ticket_info['sTime'] = [cur.year, cur.month, cur.day, 0]
                        self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, 23]
            else:
                if time_map[w[0][0]+w[0][2]] < 0 or time_map[w[1][0]+w[1][2]] < 0 or time_map[w[0][0]+w[0][2]] > time_map[w[1][0]+w[1][2]]:
                    self.error = (1, "对不起，你输入的日期已经过去了。")
                    return None
                cur1 = now + datetime.timedelta(time_map[w[0][0]+w[0][2]])
                cur2 = now + datetime.timedelta(time_map[w[1][0]+w[1][2]])
                if self.ticket_info['sTime'] is None:
                    self.ticket_info['sTime'] = [cur1.year, cur1.month, cur1.day, 0]
                else:
                    self.ticket_info['sTime'] = [cur1.year, cur1.month, cur1.day, 0]
                if self.ticket_info['dTime'] is None:
                    self.ticket_info['dTime'] = [cur2.year, cur2.month, cur2.day, 23]
                else:
                    self.ticket_info['dTime'] = [cur2.year, cur2.month, cur2.day, 23]

        d1 = re.findall(r"(今天|明天|大后天|后天)[以之]*([后前])*", sent)
        if d1:
            flag = True
            dict_temp = {'今天': 0, '明天': 1, '后天': 2, '大后天': 3}
            if len(d1) > 2:
                self.error = (1, "对不起，您输入的时间有问题。")
                return None
            elif len(d1) == 1:
                cur = now + datetime.timedelta(dict_temp[d1[0][0]])
                if d1[0][1] == '后':
                    if self.ticket_info['sTime'] is None:
                        self.ticket_info['sTime'] = [cur.year, cur.month, cur.day, 0]
                        cur += datetime.timedelta(5)
                        self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, 23]
                    else:
                        self.ticket_info['sTime'] = [cur.year, cur.month, cur.day, 0]
                        temp = self.ticket_info['dTime']
                        if cur > datetime.datetime(temp[0], temp[1], temp[2], temp[3]):
                            self.error = (1, "对不起，您输入的时间有问题")
                            return None
                elif d1[0][1] == '前':
                    if self.ticket_info['dTime'] is None:
                        self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, 23]
                        self.ticket_info['sTime'] = [now.year, now.month, now.day, 0]
                    else:
                        self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, 23]
                        temp = self.ticket_info['sTime']
                        if cur < datetime.datetime(temp[0], temp[1], temp[2], temp[3]):
                            self.error = (1, "对不起，您输入的时间有问题")
                            return None
                else:
                    if self.ticket_info['sTime'] is None:
                        self.ticket_info['sTime'] = [cur.year, cur.month, cur.day, 0]
                        self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, 23]
                    else:
                        self.ticket_info['sTime'] = [cur.year, cur.month, cur.day, 0]
                        self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, 23]
            else:
                if dict_temp[d1[0][0]] > dict_temp[d1[1][0]]:
                    self.error = (1, "对不起，你输入的日期已经过去了。")
                    return None
                cur1 = now + datetime.timedelta(dict_temp[d1[0][0]])
                cur2 = now + datetime.timedelta(dict_temp[d1[1][0]])
                if self.ticket_info['sTime'] is None:
                    self.ticket_info['sTime'] = [cur1.year, cur1.month, cur1.day, 0]
                else:
                    self.ticket_info['sTime'] = [cur1.year, cur1.month, cur1.day, 0]
                if self.ticket_info['dTime'] is None:
                    self.ticket_info['dTime'] = [cur2.year, cur2.month, cur2.day, 23]
                else:
                    self.ticket_info['dTime'] = [cur2.year, cur2.month, cur2.day, 23]

        d2 = re.search(r"(\d{1,2})[个]*天[之以]*后", sent)
        if d2:
            flag = True
            da = d2.groups()[0]
            if int(da) > 55:
                self.error = (1, "抱歉，我最多只能订查到50天左右的票")
                return None
            cur = now + datetime.timedelta(int(da))

            if self.ticket_info['sTime'] is None:
                self.ticket_info['sTime'] = [cur.year, cur.month, cur.day, 0]
                cur += datetime.timedelta(5)
                self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, 23]
            else:
                self.ticket_info['sTime'] = [cur.year, cur.month, cur.day, 0]
                temp = self.ticket_info['dTime']
                if cur > datetime.datetime(temp[0], temp[1], temp[2], temp[3]):
                    self.error = (1, "对不起，您输入的时间有问题")
                    return None

        h2 = re.search(r"(\d{1,2})[个]*小时[之以]*后", sent)
        if h2:
            flag = True
            ha = h2.groups()[0]
            if int(ha) > 100:
                self.error = (1, '抱歉，既然大于100小时了，就说天数吧')
                return None
            cur = now + datetime.timedelta(hours=int(ha) - 1)
            self.ticket_info['sTime'] = [cur.year, cur.month, cur.day, cur.hour]
            cur += datetime.timedelta(hours=int(ha) + 1)
            self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, cur.hour]

        ma = re.search(r"(早上|中午|上午|下午|晚上)[\d{1,2}时]*[之以]*([前后])*", sent)
        if ma:
            flag = True
            dict_temp3 = {'早上': (0, 6), '中午': (10, 14), '上午': (5, 12), '下午': (12, 19), '晚上': (18, 23)}
            after = {'早上': 5, '中午': 12, '上午': 10, '下午': 19, '晚上': 19}
            before = {'早上': 6, '中午': 12, '上午': 6, '下午': 14, '晚上': 18}
            a, b = ma.groups()[0], ma.groups()[1]
            if b is None:
                if self.ticket_info['sTime'] is None:
                    self.ticket_info['sTime'], self.ticket_info['dTime'] = [now.year, now.month, now.day, dict_temp3[a][0]], \
                                                                           [now.year, now.month, now.day, dict_temp3[a][1]]
                else:
                    self.ticket_info['sTime'][3], self.ticket_info['dTime'][3] = dict_temp3[a][0], dict_temp3[a][1]
            elif b == '前':
                if self.ticket_info['sTime'] is None:
                    self.ticket_info['sTime'], self.ticket_info['dTime'] = [now.year, now.month, now.day, 0], \
                                                                           [now.year, now.month, now.day, before[a]]
                else:
                    self.ticket_info['sTime'][3], self.ticket_info['dTime'][3] = 0, before[a]
            else:
                if self.ticket_info['sTime'] is None:
                    self.ticket_info['sTime'], self.ticket_info['dTime'] = [now.year, now.month, now.day, after[a]], \
                                                                           [now.year, now.month, now.day, 23]
                else:
                    self.ticket_info['sTime'][3], self.ticket_info['dTime'][3] = after[a], 23

        h = re.findall(r"(\d{1,2})时[之以]*([前后])*", sent)
        if h:
            flag = True
            if len(h) > 2:
                self.error = (1, "对不起，您输入的时间有问题")
                return None
            elif len(h) == 1:
                if int(h[0][0]) > 24:
                    self.error = (1, "对不起，一天中最多有24点！")
                    return None
                if h[0][1] == '后':
                    if int(h[0][0]) == 24:
                        h[0][1] = 0
                    if self.ticket_info['sTime'] is None:
                        self.ticket_info['sTime'] = [now.year, now.month, now.day, int(h[0][0])]
                        self.ticket_info['dTime'] = [now.year, now.month, now.day, 23]
                    else:
                        self.ticket_info['sTime'][3] = int(h[0][0])
                elif h[0][1] == '前':
                    hh = int(h[0][0])
                    if hh == 24:
                        hh = 23
                    if self.ticket_info['dTime'] is None:
                        self.ticket_info['dTime'] = [now.year, now.month, now.day, hh]
                        self.ticket_info['sTime'] = [now.year, now.month, now.day, 0]
                    else:
                        self.ticket_info['dTime'][3] = hh
                else:
                    n = int(h[0][0])
                    if n == 24: n = 23
                    left, right = max(n-1, 0), min(n + 1, 23)
                    if self.ticket_info['sTime'] is None:
                        self.ticket_info['sTime'], self.ticket_info['dTime'] = [now.year, now.month, now.day, left], [now.year, now.month, now.day, right]
                    else:
                        self.ticket_info['sTime'][3], self.ticket_info['dTime'][3] = left, right
            else:
                left, right = int(h[0][0]), int(h[1][0])
                if left > 24 or right > 24 or left > right:
                    self.error = (1, "对不起，您的时间可能超过了24点")
                    return None
                if left > right:
                    self.error = (1, "抱歉， 您的时间有问题。")
                    return None
                if left == 24: left = 23
                if self.ticket_info['sTime'] is None:
                    self.ticket_info['sTime'], self.ticket_info['dTime'] = [now.year, now.month, now.day, left], [now.year, now.month, now.day, right]
                else:
                    self.ticket_info['sTime'][3], self.ticket_info['dTime'][3] = left, right

        if flag:
            return True
        else:
            return None

    def _places(self):
        """ 判断地点
        返回地点：
        place_1 = '' # 出发点
        place_2 = '' # 目的地
        (place_1, place_2)
        """
        if self.error:
            return None
        len_sent = len(self.words)
        if 'ns' not in self.postags:
            return None
        temp = ''
        for i in range(len_sent):
            if self.postags[i] == 'ns':
                temp += str(i) + 'ns'
            else:
                temp += self.words[i]
        place_1, place_2 = '', ''
        ed1 = re.search(r"[到去至飞回差](\d{1,2})ns(\d{1,2})ns(\d{1,2})ns", temp)
        ed2 = re.search(r"[到去至飞回差](\d)ns(\d{1,2})ns", temp)
        ed3 = re.search(r"[到去至飞回差](\d{1,2})ns", temp)
        st1 = re.search(r"[从]*(\d{1,2})ns(\d{1,2})ns(\d{1,2})ns[到去至飞回]", temp)
        st2 = re.search(r"[从]*(\d{1,2})ns(\d{1,2})ns[到去至飞回]", temp)
        st3 = re.search(r"[从]*(\d{1,2})ns[到去至飞回]", temp)
        if ed1:
            place_2 = self.words[int(ed1.groups()[2])]
            if place_2 in set_province:
                self.error = (2, "能把您想去的地方再具体一点吗？")
                return None
            elif place_2 in set_sub_province:
                pass
            elif place_2 in dict_plane_to_province.keys() and \
                    self.words[int(ed1.groups()[1])] == dict_plane_to_province[place_2]:
                pass
            else:
                self.error = (2, "抱歉，您想要去的地方可能没有机场供你选择。")
                return None
        elif ed2:
            place_2 = self.words[int(ed2.groups()[1])]
            if place_2 in set_province:
                self.error = (2, "能把您想去的地方再具体一点吗？")
                return None
            elif place_2 in set_sub_province:
                pass
            elif place_2 in dict_plane_to_province.keys() and \
                    self.words[int(ed2.groups()[0])] == dict_plane_to_province[place_2]:
                pass
            else:
                self.error = (2, "抱歉，您想要去的地方可能没有机场供你选择。")
                return None
        elif ed3:
            place_2 = self.words[int(ed3.groups()[0])]
            if place_2 in set_province:
                self.error = (2, "能把您想去的地方再具体一点吗？")
                return None
            elif place_2 in set_sub_province:
                pass
            elif place_2 in dict_plane_to_province.keys():
                pass
            else:
                self.error = (2, "抱歉，您想要去的地方可能没有机场供你选择。")
                return None

        if st1:
            place_1 = self.words[int(st1.groups()[2])]
            if place_1 in set_province:
                self.error = (2, "能把您想去的地方再具体一点吗？")
                return None
            elif place_1 in set_sub_province:
                pass
            elif place_1 in dict_plane_to_province.keys() and \
                    self.words[int(st1.groups()[1])] == dict_plane_to_province[place_1]:
                pass
            else:
                self.error = (2, "抱歉，您的出发地可能没有机场供你选择。")
                return None
        elif st2:
            place_1 = self.words[int(st2.groups()[1])]
            if place_1 in set_province:
                self.error = (2, "能把您想去的地方再具体一点吗？")
                return None
            elif place_1 in set_sub_province:
                pass
            elif place_1 in dict_plane_to_province.keys() and \
                    self.words[int(st2.groups()[0])] == dict_plane_to_province[place_1]:
                pass
            else:
                self.error = (2, "抱歉，您的出发地可能没有机场供你选择。")
                return None
        elif st3:
            place_1 = self.words[int(st3.groups()[0])]
            if place_1 in set_province:
                self.error = (2, "能把您想去的地方再具体一点吗？")
                return None
            elif place_1 in set_sub_province:
                pass
            elif place_1 in dict_plane_to_province.keys():
                pass
            else:
                self.error = (2, "抱歉，您的出发地可能没有机场供你选择。")
                return None

        # 以下是为了应对 单独回答地点的情况
        if place_2 == "":  # 2. 或者这里匹配多个ns
            p3 = re.findall(r"(\d{1,2})ns", temp)
            if p3:
                place_2 = self.words[int(p3[-1])]
                if place_2 in set_province:
                    self.error = (2, "能把您想去的地方再具体一点吗？")
                    return None
                elif place_2 in set_sub_province:
                    pass
                elif place_2 in dict_plane_to_province.keys():
                    pass
                else:
                    self.error = (2, "抱歉，您想要去的地方可能没有机场供你选择。")
                    return None

        if place_1 == '' and place_2 == '':
            return None
        if place_1 != '' and place_1 in dict_plane_to_province.keys():
            place_1 = dict_plane_to_province[place_1]
        if place_2 != '' and place_2 in dict_plane_to_province.keys():
            place_2 = dict_plane_to_province[place_2]
        if place_1 == place_2 or (place_1 == '' and self.ticket_info['sCity'] == place_2):
            self.error = (1, '抱歉，同一城市之间没有飞机航线。')
        return place_1, place_2

    def _nums(self):
        """ 判断数量
        返回数量：
        如果没有 返回None
        如果有 返回int值
        """
        if self.error:
            return None
        len_sent = len(self.words)
        temp = ''
        for i in range(len_sent):
            if i < len_sent - 1 and self.words[i + 1] == '张':
                temp += str(i) + 'Z'
            else:
                temp += self.words[i]

        # 基于匹配的方法
        nums = None
        m = re.search(r"(\d)Z张", temp)
        if m:
            if self.postags[int(m.groups()[0])] == 'v':
                nums = 1
            elif self.words[int(m.groups()[0])] in nums_map.keys():
                nums = nums_map[self.words[int(m.groups()[0])]]
            else:
                self.error = (3, "抱歉，我没听懂，提醒您最多能订十张票。")
                return None
        else:
            n = re.search(r".*(\d)Z张.*", temp)
            if n and self.topic == 'nTickets':
                if self.words[int(n.groups()[0])] in nums_map.keys():
                    nums = nums_map[self.words[int(n.groups()[0])]]
                else:
                    self.error = (3, "囧，我没读懂有几张票。")
                    return None
        if nums is None and self.topic == 'nTickets' and len_sent < 4:
            for word in self.words:
                if word in nums_map.keys():
                    nums = nums_map[word]
        return nums

    def _class(self):
        """ 返回是否包含舱位信息
        如果有: 返回list()
        如果没有： 返回None
        """
        if self.error:
            return None
        len_sent = len(self.words)
        temp = ''
        for i in range(len_sent):
            if self.words[i] in set_class:
                temp += str(i) + 'Z'
            else:
                temp += self.words[i]
        num = 0
        for wo in list(temp):
            if wo == 'Z':
                num += 1
        if num == 0:
            return None

        m1 = re.search(r".*不.*[要坐用].*(\d)Z和(\d)Z.*", temp)
        m2 = re.search(r".*不.*[要坐用].*(\d)Z.*", temp)
        m3 = re.search(r".*(\d)Z和(\d)Z.*", temp)
        m4 = re.search(r".*(\d)Z.*", temp)
        if not self.ticket_info['class']:
            temp = set(set_class)
        else:
            temp = self.ticket_info['class']
        class1, class2 = set(), set()
        if m1:
            class1 = set([self.words[int(m1.groups()[0])], self.words[int(m1.groups()[1])]])
        elif m2:
            class1 = set([self.words[int(m2.groups()[0])]])
        elif m3:
            class2 = set([self.words[int(m3.groups()[0])], self.words[int(m3.groups()[1])]])
        elif m4:
            class2 = set([self.words[int(m4.groups()[0])]])

        if class2 != set():
            temp = temp.intersection(class2)
        if self.ticket_info['class'] is not None and self.ticket_info['class'] != temp.difference(class1):
            print('舱位已经设好了')
        self.ticket_info['class'] = temp.difference(class1)
        return True

    def _flight_type(self):
        """ None or list()"""
        if self.error:
            return None
        len_sent = len(self.words)
        temp = ''
        for i in range(len_sent):
            if self.words[i] in ['大飞机', '大型飞机']:
                temp += str(i) + 'B'
            elif self.words[i] in ['小飞机', '小型飞机', '中型飞机']:
                temp += str(i) + 'X'
            elif self.words[i] in set_flight_type_total:
                temp += str(i) + 'Z'
            elif self.words[i] == 'B':
                temp += str(i) + 'O'
            elif self.words[i] == 'K':
                temp += str(i) + 'K'
            elif self.words[i] == 'M':
                temp += str(i) + 'M'
            else:
                temp += self.words[i]
        num = 0
        for wo in list(temp):
            if wo in ['B', 'Z', 'O', 'K', 'M', 'X']:
                num += 1
        if num == 0:
            return None

        b1 = re.search(r"不[要坐用].*(\d)B", temp)
        b2 = re.search(r"(\d)B", temp)

        M1 = re.search(r"不[要坐用].*(\d)M", temp)
        M2 = re.search(r"(\d)M", temp)

        o1 = re.search(r"不[要坐用].*(\d)O", temp)
        o2 = re.search(r"(\d)O.*", temp)

        k1 = re.search(r"不[要坐用].*(\d)K.", temp)
        k2 = re.search(r"(\d)K.*", temp)

        x1 = re.search(r"不[要坐用].*(\d)X", temp)
        x2 = re.search(r"(\d)X", temp)

        m1 = re.search(r"不[要坐用].*(\d)Z和(\d)Z", temp)
        m2 = re.search(r"不[要坐用].*(\d)Z", temp)
        m3 = re.search(r"(\d)Z和(\d)Z", temp)
        m4 = re.search(r"(\d)Z", temp)

        if not self.ticket_info['flight_type']:
            temp = set(set_flight_type_total)
        else:
            temp = self.ticket_info['flight_type']
        temp1, temp2 = set(), set()
        if b1:
            temp1 = temp1.union(set_flight_type_big)
        elif b2:
            temp2 = temp2.union(set_flight_type_big)
        if x1:
            temp1 = temp1.union(set_flight_type_small)
        elif x2:
            temp2 = temp2.union(set_flight_type_small)
        if M1:
            temp1 = temp1.union(set_flight_type_maidao)
        elif M2:
            temp2 = temp2.union(set_flight_type_maidao)
        if o1:
            temp1 = temp1.union(set_flight_type_boyin)
        elif o2:
            temp2 = temp2.union(set_flight_type_boyin)
        if k1:
            temp1 = temp1.union(set_flight_type_kongke)
        elif k2:
            temp2 = temp2.union(set_flight_type_kongke)
        if m1:
            word1, word2 = self.words[int(m1.groups()[0])], self.words[int(m1.groups()[1])]
            temp1 = temp1.union([word1, word2])
            if word1[0] in ['B', 'K', 'M'] and word1[1:] in set_flight_type_total:
                temp1 = temp1.union([word1[1:]])
            elif word1[0] not in ['B', 'K', 'M']:
                temp1 = temp1.union(['B'+word1, 'K'+word1, 'M'+word1])
            if word2[0] in ['B', 'K', 'M'] and word2[1:] in set_flight_type_total:
                temp1 = temp1.union([word2[1:]])
            elif word2[0] not in ['B', 'K', 'M']:
                temp1 = temp1.union(['B' + word2, 'K' + word2, 'M' + word2])
        elif m2:
            word1 = self.words[int(m2.groups()[0])]
            temp1 = temp1.union([word1])
            if word1[0] in ['B', 'K', 'M'] and word1[1:] in set_flight_type_total:
                temp1 = temp1.union([word1[1:]])
            elif word1[0] not in ['B', 'K', 'M']:
                temp1 = temp1.union(['B'+word1, 'K'+word1, 'M'+word1])
        elif m3:
            word1, word2 = self.words[int(m3.groups()[0])], self.words[int(m3.groups()[1])]
            temp2 = temp2.union([word1, word2])
            if word1[0] in ['B', 'K', 'M'] and word1[1:] in set_flight_type_total:
                temp2 = temp2.union([word1[1:]])
            elif word1[0] not in ['B', 'K', 'M']:
                temp2 = temp2.union(['B'+word1, 'K'+word1, 'M'+word1])
            if word2[0] in ['B', 'K', 'M'] and word2[1:] in set_flight_type_total:
                temp2 = temp2.union([word2[1:]])
            elif word2[0] not in ['B', 'K', 'M']:
                temp2 = temp2.union(['B' + word2, 'K' + word2, 'M' + word2])
        elif m4:
            word1 = self.words[int(m4.groups()[0])]
            temp2 = temp2.union([word1])
            if word1[0] in ['B', 'K', 'M'] and word1[1:] in set_flight_type_total:
                temp2 = temp2.union([word1[1:]])
            elif word1[0] not in ['B', 'K', 'M']:
                temp2 = temp2.union(['B'+word1, 'K'+word1, 'M'+word1])

        if temp2 != set():
            temp = temp.intersection(temp2)
        if self.ticket_info['flight_type'] is not None and self.ticket_info['flight_type'] != temp.difference(temp1):
            print('飞机机型信息更新了')
        self.ticket_info['flight_type'] = temp.difference(temp1)
        return True

    def _company(self):
        """ 判断公司 一律认为是nh
        None or list()
        error = 6
        """
        if self.error:
            return None
        len_sent = len(self.words)

        temp = ''
        for i in range(len_sent):
            if self.words[i] in set_company:
                temp += str(i) + 'Z'
            else:
                temp += self.words[i]
        num = 0
        for wo in list(temp):
            if wo == 'Z':
                num += 1
        if num == 0:
            return None
        m1 = re.search(r".*不.*[要坐用].*(\d)Z和(\d)Z.*", temp)
        m2 = re.search(r".*不.*[要坐用].*(\d)Z.*", temp)
        m3 = re.search(r".*(\d)Z和(\d)Z.*", temp)
        m4 = re.search(r".*(\d)Z.*", temp)
        if not self.ticket_info['company']:
            temp = set(set_company)
        else:
            temp = self.ticket_info['company']
        company1, company2 = set(), set()
        if m1:
            company1 = set([self.words[int(m1.groups()[0])], self.words[int(m1.groups()[1])]])
        elif m2:
            company1 = set([self.words[int(m2.groups()[0])]])
        elif m3:
            company2 = set([self.words[int(m3.groups()[0])], self.words[int(m3.groups()[1])]])
        elif m4:
            company2 = set([self.words[int(m4.groups()[0])]])

        if company2 != set():
            temp = temp.intersection(company2)
        if self.ticket_info['company'] is not None and self.ticket_info['company'] != temp.difference(company1):
            print('公司信息更改好了')
        self.ticket_info['company'] = temp.difference(company1)
        return True

    def _price(self):
        """ 价格处理 """
        if self.error:
            return None
        sent = self._time_help()

        m1 = re.search(r"[低少]于(\d{2,})", sent)
        m2 = re.search(r"(\d{2,})(块钱|块)[之以]*下", sent)

        # w1 = re.search(r"[高多]于(\d)Z", temp)
        # w2 = re.search(r"(\d)Z.*[之以]*上", temp)

        b1 = re.search(r"(\d{2,})(块钱|块)*[到至](\d{2,})(块钱|块)", sent)

        if m1:
            w = m1.groups()[0]
            try:
                low, high = 0, int(w)
            except ValueError:
                self.error = (1, "抱歉，您输入的钱数我没听懂")
                return None
            return low, high
        elif m2:
            w = m2.groups()[0]
            try:
                low, high = 0, int(w)
            except ValueError:
                self.error = (1, "抱歉，您输入的钱数我没听懂")
                return None
            return low, high
        #
        # if w1:
        #     w = self.words[int(m1.groups()[0])]
        #     a, b = 0, 0
        #     for c in w:
        #         if c in dic_1:
        #             a += 1
        #         elif c in dic_2:
        #             b += 1
        #     if a == len(w):
        #         low, high = 0, self._chinese2digits(w)
        #     elif b == len(w):
        #         low, high = 0, int(w)
        #     else:
        #         self.error = (1, "抱歉，您输入的钱数我没听懂")
        #         return None
        #     low, high = int(self.words[int(w1.groups()[0])]), 10000
        #     return low, high
        # elif w2:
        #     low, high = int(self.words[int(w2.groups()[0])]), 10000
        #     return low, high

        if b1:
            w1, w2 = b1.groups()[0], b1.groups()[2]
            try:
                low, high = int(w1), int(w2)
            except ValueError:
                self.error = (1, "抱歉，你输入的钱数我没听懂")
                return None
            if low > high:
                self.error = (1, '抱歉，您的价格区间有点问题')
                return None
            return low, high

        return None

    def _discount(self):
        """ 不识别 九十五折 之类的"""
        if self.error:
            return None
        sent = self.sentence.replace('折扣', '折')

        for i in range(len(self.words)):
            if self.words[i] in ['折'] and len(self.words[i-1]) > 3:
                return None

        m1 = re.search(r"([一二三四五六七八九123456789]+)折[之以]下", sent)
        m2 = re.search(r"低于([一二三四五六七八九123456789]+)折", sent)
        m3 = re.search(r"([一二三四五六七八九123456789]+)折", sent)

        result = None
        if m1:
            word = m1.groups()[0]
            len_word = len(word)
            if len_word > 2:
                return None
            elif len_word == 2:
                if word[0] in nums_map.keys() and word[1] in nums_map.keys():
                    result = str(nums_map[word[0]]) + str(nums_map[word[1]])
                else:
                    self.error = (11, '您输入的折扣有问题')
                    return None
            elif len_word == 1:
                if word[0] in nums_map.keys():
                    result = str(nums_map[word[0]])
                else:
                    self.error = (11, '您输入的折扣信息有问题')
                    return None
        elif m2:
            word = m2.groups()[0]
            len_word = len(word)
            if len_word > 2:
                return None
            elif len_word == 2:
                if word[0] in nums_map.keys() and word[1] in nums_map.keys():
                    result = str(nums_map[word[0]]) + str(nums_map[word[1]])
                else:
                    self.error = (11, '您输入的折扣有问题')
                    return None
            elif len_word == 1:
                if word[0] in nums_map.keys():
                    result = str(nums_map[word[0]])
                else:
                    self.error = (11, '您输入的折扣信息有问题')
                    return None
        elif m3:
            word = m3.groups()[0]
            len_word = len(word)
            if len_word > 2:
                return None
            elif len_word == 2:
                if word[0] in nums_map.keys() and word[1] in nums_map.keys():
                    result = str(nums_map[word[0]]) + str(nums_map[word[1]])
                else:
                    self.error = (11, '抱歉，你输入的折扣有问题。')
                    return None
            elif len_word == 1:
                if word[0] in nums_map.keys():
                    result = str(nums_map[word[0]])
                else:
                    self.error = (11, '你输入的折扣有点问题')
                    return None

        return result

    def _flag(self):
        """ 最便宜 贵 最早 最晚
        没有： None
        最便宜， 最早： True
        最贵， 最晚： False
        """
        if self.error:
            return None
        sent = self.sentence

        m1 = re.search(r"(最便宜|最贵)", sent)
        m2 = re.search(r"(最早|最晚)", sent)
        price, time = None, None
        if m1:
            if m1.groups()[0] == '最便宜':
                price = True
            else:
                price = False
        if m2:
            if m2.groups()[0] == '最早':
                time = True
            else:
                time = False
        if price is not None or time is not None:
            return price, time
        else:
            return None

    def _is_relate(self, sent):
        """通过 词典 确定是否订票相关"""
        self._basic_handle(sent)

        self.time = self._time()
        self.places = self._places()
        self.nums = self._nums()
        self.classes = self._class()
        self.flight_type = self._flight_type()
        self.company = self._company()
        self.price = self._price()
        self.discount = self._discount()
        self.flag = self._flag()

        if self.error or self.nums or self.places or self.time or self.company or self.classes or self.flight_type or \
                self.price or self.discount or self.flag:
            return True

        for word in self.sentence:
            if word in tickets_set1 or word in tickets_set3:
                return True

        return False

    def _is_new_task(self):
        """ 通过某种方式判断是否是一个新的任务 """
        if self.error:
            print(self.error[1])
            self.error = None
            return True
        global rand
        rand = random.randint(0, 10)
        m = re.search(r"([再重还].*[新来订要]).*(开始|票|张)", self.sentence)
        if m:
            print(sent_restart[rand % len(sent_restart)])
            self._default()
            return True
        return False

    def _is_new_topic(self):
        """ 如果没有提到旧的话题， 那么就认为来了新话题 """
        global rand
        rand = random.randint(0, 10)
        flag = False
        if self.state == 0:
            return False

        if self.topic == 'sTime' and self.time:
            return False
        elif self.topic == 'dCity' and self.places and self.places[1]:
            return False

        if self.time:
            pass

        if self.nums and self.nums != 1:
            self.ticket_info['nTickets'] = self.nums

        if self.places and self.places[0]:
            self.ticket_info['sCity'] = self.places[0]

        if self.places and self.places[1]:
            self.ticket_info['dCity'] = self.places[1]

        if self.classes:
            pass

        if self.company:
            pass

        if self.flight_type:
            pass

        if self.price:
            flag = True
            self.ticket_info['flight_price'] = self.price

        if self.discount:
            flag = True
            self.ticket_info['discount'] = self.discount

        if self.flag and self.flag[0] is not None:
            flag = True
            self.ticket_info['price_flag'] = self.flag[0]

        if self.flag and self.flag[1] is not None:
            flag = True
            self.ticket_info['time_flag'] = self.flag[1]

        for key in ['sTime', 'dCity']:
            if self.ticket_info[key] is None:
                self.askInfo_nums[key] += 1
                if self.askInfo_nums[key] > 2:
                    print(sent_multiAsk[key][rand % len(sent_multiAsk[key])])  # 句子有待扩展
                    break
                print(sent_topic[self.topic][rand % len(sent_topic[self.topic])])
                break
        if self.topic == 'search':
            print('那' + sent_topic[self.topic][rand % len(sent_topic[self.topic])])
            print(over[rand % len(over)])

        return True

    def _writeinfo(self):
        global rand
        rand = random.randint(0, 10)

        if self.topic == 'sTime':
            pass
        elif self.topic == 'dCity':
            self.ticket_info['dCity'] = self.places[1]

        if self.topic != 'sTime' and self.time:
            pass

        if self.nums:
            if self.ticket_info['nTickets'] != 1 and self.ticket_info['nTickets'] != self.nums:
                print('好的,票数已经改了')
            self.ticket_info['nTickets'] = self.nums

        if self.places and self.places[0]:
            if self.ticket_info['sCity'] != '广州' and self.ticket_info['sCity'] != self.places[0]:
                print('好的, 出发地改为', self.places[0], '了')
            self.ticket_info['sCity'] = self.places[0]

        if self.topic != 'dCity' and self.places and self.places[1]:
            if self.ticket_info['dCity'] and self.ticket_info['dCity'] != self.places[1]:
                print('您以前是想去' + self.ticket_info['dCity'] + '现在变成飞' + self.places[1] + '咯')
            self.ticket_info['dCity'] = self.places[1]

        if self.classes or self.company or self.flight_type:
            pass

        if self.price:
            if self.ticket_info['flight_price'] and self.ticket_info['flight_price'] != self.price:
                print('已经将价格设置好了')
            self.ticket_info['flight_price'] = self.price

        if self.discount:
            if self.ticket_info['discount'] and self.ticket_info['discount'] != self.discount:
                print('已将折扣设置好了')
            self.ticket_info['discount'] = self.discount

        if self.flag and self.flag[0] is not None:
            if self.ticket_info['price_flag'] and self.ticket_info['price_flag'] != self.flag[0]:
                print('价格好了')
            self.ticket_info['price_flag'] = self.flag[0]

        if self.flag and self.flag[1] is not None:
            if self.ticket_info['time_flag'] and self.ticket_info['time_flag'] != self.flag[1]:
                print('时间好了')
            self.ticket_info['time_flag'] = self.flag[1]

        self.state = 1
        self.topic = None
        flag = True
        for key in ['sTime', 'dCity']:
            if self.ticket_info[key] is None:
                flag = False
                self.askInfo_nums[key] += 1
                if self.askInfo_nums[key] > 2:
                    print(sent_multiAsk[key][rand % len(sent_multiAsk[key])])  # 句子有待扩展
                    break
                self.topic = key
                print(sent_topic[self.topic][rand % len(sent_topic[self.topic])])
                break
        if flag:
            self.state = 2
            self.topic = 'search'
            print(sent_topic[self.topic][rand % len(sent_topic[self.topic])])
            print(over[rand % len(over)])

    def _book(self):
        """ 去网站查询票信息 """
        if self.topic != 'search':
            return False
        self._default()
        print('本次查询结束，谢谢！')
        return True

    def _start(self):
        """ 用于处理 特殊的问句 """
        sent = self.sentence

        m1 = re.search(r"(你是谁)", sent)
        m2 = re.search(r"(你能干什么)", sent)
        m3 = re.search(r"(你叫什么)", sent)

        if m1:
            if self.topic == 'search':
                self._default()
                print('本次查询结束，谢谢！')
            print("我是机票精灵，我能为您提供机票信息")
            return True
        elif m2:
            if self.topic == 'search':
                self._default()
                print('本次查询结束，谢谢！')
            print("作为订票助手，我能为您提供机票信息")
            return True
        elif m3:
            if self.topic == 'search':
                self._default()
                print('本次查询结束，谢谢！')
            print("我是机票精灵")
            return True
        else:
            return False

    def booking(self):
        """ 订票功能: 每次输入一个句子，从语音而来 """
        global rand
        error_times = 0
        f = open(self.SENT_DIR, 'a')
        f.write('start\n')

        print('你好，我是机票精灵。(q:退出, r:重启, c:清洁输出, f:输出测试)')
        while True:
            sent = input('=> ')

            if sent == 'q':
                f.write('end\n\n')
                f.close()
                print('程序结束')
                return
            elif sent == 'r':
                f.write('end\n\nstart\n')
                f.flush()
                self._default()
                print('已重启，请开始')
                print('你好，我是机票精灵。(q:退出, r:重启, c:清洁输出, f:输出测试)')
                continue
            elif sent == 'c':
                self.show = False
                print('已经清洁输出了，输出测试请输入(f)')
                continue
            elif sent == 'f':
                self.show = True
                print('已经输出测试了，清洁输出请输入(c)')
                continue
            f.write('1=> ' + sent + '\n')

            if self._is_relate(sent):
                error_times = 0
                if self._is_new_task():
                    pass
                elif self._is_new_topic():
                    pass
                else:
                    self._writeinfo()
            else:
                if self._start() or self._book():
                    continue
                rand = random.randint(0, 15)
                print(sent_error1[rand % len(sent_error1)] + sent_error2[rand % len(sent_error2)])
                error_times += 1
                if error_times == 2:
                    print(sent_start[rand % len(sent_start)])
                    error_times = 0

            if self.show:
                temp = '>> '
                for key in ['sTime', 'dTime', 'sCity', 'dCity', 'nTickets', 'discount', 'price_flag', 'time_flag', 'class', 'company',
                            'flight_type', 'flight_price']:
                    if self.ticket_info[key] is not None:
                        temp += help_dict[key] + ":" + str(self.ticket_info[key]) + ' | '
                temp += "state:" + str(self.state) + " | " + "topic:" + str(self.topic) + " |"
                f.write(temp + '\n')
                print(temp)


if __name__ == '__main__':
    demo = Demo()
    demo.load_model()
    demo.booking()
    demo.release_model()

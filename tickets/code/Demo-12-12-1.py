# coding: utf-8
import os
import re
import hashlib
import time
import copy
import random
import datetime
from pyltp import *
from urllib import parse, request
from collections import OrderedDict

today = datetime.datetime.now()

sent_start = ['你好,我是机票精灵,我能为您提供订票服务.', '很高兴为您提供订票服务', '我能为您提供订票服务', '你好,我是机票精灵,我可以为您查机票信息']
sent_restart = ['好的，可以开始重新订票了', '好的，已经重新开始', '那就重新开始吧', '好，开始吧', '好，可以重新开始了', '可以，重新开始了']
sent_error1 = ['不好意思,', '抱歉,', '对不起,', 'sorry,']
sent_error2 = ['我没听懂,请说点订票相关的事吧', '您说点具体订票的事吧', '来聊点具体订票的事', '我不太懂您说的，请您说一些订票相关的问题吧']
sent_topic = {
    'sTime': ['您需要什么时间的机票', '您希望什么时候的机票', '您想要什么时间的机票', '您对出发时间什么要求', '您想要什么时间的票', '您想要什么时间的飞机票'],
    'dCity': ['您想飞去哪里', '请问您想去哪里呢', '请问目的地在哪里', '您想飞往哪里？'],
    'search': ['现在,为您查询到以下结果', '查询结果如下', '那现在，为您查到这些机票', '有以下机票供您选择', '已经为您查到这些机票信息',
               '现在，已经有了这些信息', '有如下机票信息', '您有以下几种票可选']}
over = ['请告诉我进一步筛选的条件', '如需筛选，请告诉我您的要求', '请告诉我您的筛选条件', '请说一下您的筛选要求']
sent_multiAsk = {
    'sTime': ['我需要您机票的时间', '我想知道您机票的时间', '请告诉我：您机票的时间', '请告诉我：您机票的时间', '请说一下：什么时间的机票',
              '我没有听到更多与时间有关的信息', '我没有听到更多与时间有关的信息'],
    'dCity': ['我需要您的目的地', '您的目的地是哪里', '您的目的地是哪里', '请告诉我您机票的目的地', '我没有听到更多与地点有关的信息', '我没有听到更多有用的信息']}

tickets_set1 = ['票', '机票', '飞机票']
tickets_set3 = ['重新', '重', '还要', '再来']

set_flight_type_big = ['B747', '747', 'B757', '757', 'B767', '767', 'B777', '777', 'B787', '787', 'M11', 'K300', 'K310', 'K330', 'K340']
set_flight_type_small = ['B737', '737', 'K320', 'M82', 'M90', 'K321', 'B738', '738']
set_flight_type = ['B737', '737', 'K320', 'M82', 'M90', 'B747', '747', 'B757', '757', 'B767', '767', 'B777', '777', 'B787', '787',
                   'M11', 'K300', 'K310', 'K330', 'K340', 'B738', '738']
set_flight_type_boyin = ['B737', '737', 'B747', '747', 'B757', '757', 'B767', '767', 'B777', '777', 'B787', '787', 'B738', '738']
set_flight_type_maidao = ['M11', 'M82', 'M90']
set_flight_type_kongke = ['K320', 'K320', 'K300', 'K300', 'K310', 'K310', 'K330', 'K330', 'K340', 'K340', 'K321']

set_company = ['中国国际航空公司', '国航', '东方航空公司', '东方航空', '东航', '南方航空公司', '南方航空', '南航', '海南航空公司', '幸福航空', '长龙航空', '成都航空',
               '海南航空', '海航', '上海航空公司', '上海航空', '上航', '山东航空公司', '山东航空', '山航', '深圳航空公司', '云南祥鹏航空', '西藏航空', '奥凯航空',
               '深圳航空', '深航', '厦门航空公司', '厦门航空', '厦航', '四川航空公司', '四川航空', '川航', '大新华航空', '大新华', '春秋航空', '吉祥航空',
               '鹰联航空', '华夏航空', '中国联合航空公司', '联合航空', '联航', '西部航空']
dict_company_to_code = {'中国国际航空公司':'CA', '国航':'CA', '东方航空公司':'MU', '东方航空':'MU', '东航':'MU', '南方航空公司':'CZ', '南方航空':'CZ',
                        '南航':'CZ', '海南航空公司':'HU', '海南航空':'HU', '海航':'HU', '上海航空公司':'FM', '上海航空':'FM', '上航':'FM', '山东航空公司':'SC',
                        '山东航空':'SC', '山航':'SC', '深圳航空公司':'ZH', '深圳航空':'ZH', '深航':'ZH', '厦门航空公司':'MF', '厦门航空':'MF', '厦航':'MF',
                        '四川航空公司':'3U', '四川航空':'3U', '川航':'3U', '大新华航空':'CN', '大新华':'CN', '九云航空':'AQ', '春秋航空':'9C', '吉祥航空':'HO',
                        '奥凯航空':'BK', '鹰联航空':'EU', '华夏航空':'G5', '中国联合航空公司':'KN', '联合航空':'KN', '联航':'KN', '幸福航空':'JR',
                        '长龙航空':'GJ', '云南祥鹏航空':'8L', '西藏航空':'TV', '西部航空':'PN', '成都航空':'EU',}
dict_type_to_code = {'B737': '波音737(中)', '737': '波音737(中)', 'K320': '空客320(中)', 'M82': '麦道82(中)', 'M90': '麦道90(中)', 'B747': '波音747(宽)',
                     '747': '波音747(宽)', 'B757': '波音757(宽)', '757': '波音757(宽)', 'B767': '波音767(宽)', '767': '波音767(宽)', 'B777': '波音777(宽)',
                     '777': '波音777(宽)', 'B787': '波音787(宽)', '787': '波音787(宽)', 'M11': '麦道11(宽)', 'K300': '空客300(宽)', 'K310': '空客310(宽)',
                     'K330': '空客330(宽)', 'K340': '空客340(宽)', 'B738': '波音738(中)', '738': '波音738(中)'}
dict_city_to_code = {'北京':['PEK', 'NAY'], '上海':['PVG', 'SHA'], '广州':['CAN'], '安庆':['AQG'],'蚌埠':['BFU'],'阜阳':['FUG'],'合肥':['HFE'],
                     '黄山':['TXN'],'北京南苑':['NAY'],'北京首都':['PEK'],'福州':['FOC'],'晋江':['JJN'],'连城':['LCX'],
                     '武夷山':['WUS'],'厦门':['XMN'],'酒泉':['CHW'],'敦煌':['DNH'],'庆阳':['IQN'],'嘉峪关':['JGN'],'兰州':['LHW'],
                     '佛山':['FUO'],'梅县':['MXZ'],'汕头':['SWA'],'深圳':['SZX'],'湛江':['ZHA'],'珠海':['ZUH'],'北海':['BHY'],'桂林':['KWL'],'柳州':['LZH'],
                     '南宁':['NNG'],'梧州':['WUZ'],'兴义':['ACX'],'百色':['AEB'],'贵阳':['KWE'],'铜仁':['TEN'],'遵义':['ZYI'],'黎平':['HZH'],'安顺':['AVA'],
                     '海口':['HAK'],'三亚':['SYX'],'邯郸':['HDG'],'秦皇岛':['SHP'],'石家庄':['SJW'],'安阳':['AYN'],'郑州':['CGO'],'洛阳':['LYA'],
                     '南阳':['NNY'],'大庆':['DQA'],'黑河':['HEK'],'哈尔滨':['HRB'],'佳木斯':['JMU'],'牡丹江':['MDG'],'齐齐哈尔':['NDG'],'恩施':['ENH'],
                     '武汉':['WUH'],'襄樊':['XFN'],'宜昌':['YIH'],'荆州':['SHS'],'常德':['CGD'],'长沙':['CSX'],'张家界':['DYG'],'芷江':['HJJ'],
                     '永州':['LLF'],'长春':['CGQ'],'吉林':['JIL'],'通化':['TNH'],'延吉':['YNJ'],'常州':['CZX'],'连云港':['LYG'],'南京':['NKG'],
                     '南通':['NTG'],'无锡':['WUX'],'徐州':['XUZ'],'淮安':['HIA'],'盐城':['YNZ'],'景德镇':['JDZ'],'井冈山':['JGS'],'九江':['JIU'],
                     '南昌':['KHN'],'赣州':['KOW'],'鞍山':['AOG'],'朝阳':['CHG'],'长海':['CNI'],'丹东':['DDG'],'大连':['DLC'],'锦州':['JNZ'],'沈阳':['SHE'],
                     '包头':['BAV'],'赤峰':['CIF'],'鄂尔多斯':['DSN'],'呼和浩特':['HET'],'海拉尔':['HLD'],'乌兰浩特':['HLH'],'满洲里':['NZH'],'通辽':['TGO'],
                     '乌海':['WUA'],'锡林浩特':['XIL'],'银川':['INC'],'格尔木':['GOQ'],'西宁':['XNN'],'东营':['DOY'],'济宁':['JNG'],'青岛':['TAO'],
                     '济南':['TNA'],'潍坊':['WEF'],'威海':['WEH'],'烟台':['YNT'],'临沂':['LYI'],'长治':['CIH'],'大同':['DAT'],'太原':['TYN'],'运城':['YCU'],
                     '安康':['AKA'],'延安':['ENY'],'汉中':['HZG'],'榆林':['UYN'],'西安':['XIY'],'上海浦东':['PVG'],'上海虹桥':['SHA'],
                     '成都':['CTU'],'达县':['DAX'],'广元':['GNY'],'九寨沟':['JZH'],'泸州':['LZO'],'绵阳':['MIG'],'南充':['NAO'],'攀枝花':['PZI'],
                     '万州':['WXN'],'西昌':['XIC'],'宜宾':['YBP'],'天津':['TSN'],'昌都':['BPX'],'拉萨':['LXA'],'阿克苏':['AKU'],'富蕴':['FYN'],
                     '哈密':['HMI'],'阿勒泰':['AAT'],'和田':['HTN'],'且末':['IQM'],'库车':['KCA'],'喀什':['KHG'],'库尔勒':['KRL'],'克拉玛依':['KRY'],
                     '塔城':['TCG'],'新源':['NLT'],'乌鲁木齐':['URC'],'伊宁':['YIN'],'吐鲁番':['TLQ'],'保山':['BSD'],'迪庆香格里拉':['DIG'],'大理':['DLU'],
                     '西双版纳':['JHG'],'昆明':['KMG'],'丽江':['LJG'],'临沧':['LNJ'],'德宏芒市':['LUM'],'思茅':['SYM'],'昭通':['ZAT'],'文山':['WNH'],
                     '杭州':['HGH'],'舟山':['HSN'],'台州/黄岩':['HYN'],'衢州':['JUZ'],'宁波':['NGB'],'温州':['WNZ'],'义乌':['YIW'],'重庆':['CKG','WXN'],
                     '香港':['HKG'],'澳门':['MFM'],}
dict_plane_to_code = {'虹桥机场':['SHA'], '浦东机场':['PVG'], '首都机场':['PEK'], '天柱山机场': ['AQG'],
                      '蚌埠机场': ['BFU'],'西关机场': ['FUG'],'骆岗机场': ['HFE'],'屯溪机场': ['TXN'],'南苑机场': ['NAY'],'首都国际机场': ['PEK'],
                      '长乐国际机场': ['FOC'],'长乐机场': ['FOC'],'晋江机场': ['JJN'],'连城机场': ['LCX'],'武夷山机场': ['WUS'],
                      '高崎国际机场': ['XMN'],'高崎机场': ['XMN'],'酒泉机场': ['CHW'],'敦煌机场': ['DNH'],'西峰镇机场': ['IQN'],'嘉峪关机场': ['JGN'],
                      '中川机场': ['LHW'],'白云国际机场': ['CAN'],'白云机场': ['CAN'],'沙堤机场': ['FUO'],'梅县机场': ['MXZ'],'外砂机场': ['SWA'],
                      '宝安国际机场': ['SZX'],'宝安机场': ['SZX'],'湛江机场': ['ZHA'],'三灶机场': ['ZUH'],'福城机场': ['BHY'],'两江国际机场': ['KWL'],
                      '两江机场': ['KWL'],'白莲机场': ['LZH'],'吴墟机场': ['NNG'],'长州岛机场': ['WUZ'],'兴义机场': ['ACX'],'田阳机场': ['AEB'],
                      '龙洞堡机场': ['KWE'],'大兴机场': ['TEN'],'遵义机场': ['ZYI'],'黎平机场': ['HZH'],'黄果树机场': ['AVA'],'美兰国际机场': ['HAK'],
                      '凤凰国际机场': ['SYX'],'邯郸机场': ['HDG'],'山海关机场': ['SHP'],'正定机场': ['SJW'],'安阳机场': ['AYN'],'新郑国际机场': ['CGO'],
                      '北郊机场': ['LYA'],'姜营机场': ['NNY'],'萨尔图机场': ['DQA'],'黑河机场': ['HEK'],'太平国际机场': ['HRB'],'东郊机场': ['JMU'],
                      '海浪机场': ['MDG'],'三家子机场': ['NDG'],'许家坪机场': ['ENH'],'天河国际机场': ['WUH'],'刘集机场': ['XFN'],'三峡机场': ['YIH'],
                      '沙市机场': ['SHS'],'桃花机场': ['CGD'],'黄花国际机场': ['CSX'],'荷花机场': ['DYG'],'芷江机场': ['HJJ'],'零陵机场': ['LLF'],
                      '龙嘉国际机场': ['CGQ'],'二台子机场': ['JIL'],'通化机场': ['TNH'],'朝阳川机场': ['YNJ'],'奔牛机场': ['CZX'],'白塔埠机场': ['LYG'],
                      '禄口国际机场': ['NKG'],'兴东机场': ['NTG'],'无锡机场': ['WUX'],'观音机场': ['XUZ'],'涟水机场': ['HIA'],'南洋机场': ['YNZ'],
                      '罗家机场': ['JDZ'],'井冈山机场': ['JGS'],'庐山机场': ['JIU'],'昌北机场': ['KHN'],'黄金机场': ['KOW'],'腾鳌机场': ['AOG'],
                      '朝阳机场': ['CHG'],'大长山岛机场': ['CNI'],'浪头机场': ['DDG'],'周水子机场': ['DLC'],'小岭子机场': ['JNZ'],'桃仙机场': ['SHE'],
                      '海兰泡机场': ['BAV'],'土城子机场': ['CIF'],'鄂尔多斯机场': ['DSN'],'白塔国际机场': ['HET'],'东山机场': ['HLD'],'乌兰浩特机场': ['HLH'],
                      '西郊机场': ['NZH'],'通辽机场': ['TGO'],'乌海机场': ['WUA'],'锡林浩特机场': ['XIL'],'河东机场': ['INC'],'格尔木机场': ['GOQ'],
                      '曹家堡机场': ['XNN'],'永安机场': ['DOY'],'曲阜机场': ['JNG'],'流亭国际机场': ['TAO'],'遥墙国际机场': ['TNA'],
                      '大水泊机场': ['WEH'],'莱山机场': ['YNT'],'临沂机场': ['LYI'],'王村机场': ['CIH'],'怀仁机场': ['DAT'],'武宿机场': ['TYN'],
                      '关公机场': ['YCU'],'五里铺机场': ['AKA'],'二十里铺机场': ['ENY'],'西沙机场': ['UYN'],'咸阳国际机场': ['XIY'],
                      '浦东国际机场': ['PVG'],'虹桥国际机场': ['SHA'],'双流国际机场': ['CTU'],'河市霸机场': ['DAX'],'广元机场': ['GNY'],'黄龙机场': ['JZH'],
                      '萱田机场': ['LZO'],'南郊机场': ['MIG'],'都尉坝机场': ['NAO'],'攀枝花机场': ['PZI'],'万县机场': ['WXN'],'青山机场': ['XIC'],
                      '菜坝机场': ['YBP'],'滨海国际机场': ['TSN'],'昌都马草机场': ['BPX'],'贡嘎机场': ['LXA'],'温宿机场': ['AKU'],'可可托托海机场': ['FYN'],
                      '哈密机场': ['HMI'],'阿勒泰机场': ['AAT'],'和田机场': ['HTN'],'且末机场': ['IQM'],'库车机场': ['KCA'],'喀什机场': ['KHG'],
                      '库尔勒机场': ['KRL'],'克拉玛依机场': ['KRY'],'塔城机场': ['TCG'],'那拉提机场': ['NLT'],'地窝堡国际机场': ['URC'],'伊宁机场': ['YIN'],
                      '交河机场': ['TLQ'],'保山机场': ['BSD'],'迪庆机场': ['DIG'],'大理机场': ['DLU'],'景洪机场': ['JHG'],'巫家坝国际机场': ['KMG'],
                      '丽江机场': ['LJG'],'临沧机场': ['LNJ'],'芒市机场': ['LUM'],'思茅机场': ['SYM'],'昭通机场': ['ZAT'],'文山普者黑机场': ['WNH'],
                      '萧山国际机场': ['HGH'],'普陀山机场': ['HSN'],'路桥机场': ['HYN'],'衢州机场': ['JUZ'],'栎社机场': ['NGB'],'永强机场': ['WNZ'],
                      '义乌机场': ['YIW'],'江北国际机场': ['CKG'],'五桥机场': ['WXN'],'香港国际机场': ['HKG'],'澳门国际机场': ['MFM'], '美兰机场': ['HAK'],
                      '凤凰机场': ['SYX'],'新郑机场': ['CGO'],'太平机场': ['HRB'],'天河机场': ['WUH'],'黄花机场': ['CSX'],'龙嘉机场': ['CGQ'],
                      '禄口机场': ['NKG'],'白塔机场': ['HET'],'流亭机场': ['TAO'],'遥墙机场': ['TNA'],'咸阳机场': ['XIY'],
                      '双流机场': ['CTU'],'滨海机场': ['TSN'],'地窝堡机场': ['URC'],'巫家坝机场': ['KMG'],'萧山机场': ['HGH'],
                      '江北机场': ['CKG'],'香港机场': ['HKG'],'澳门机场': ['MFM']}
set_class = ['经济舱', '高端经济舱', '公务舱', '商务舱', '头等舱']
dict_class_to_code = {'经济舱': ['Y','B','M','E','H','K','L','N','R','S','V','T','X','G','Z','U'],
                      '高端经济舱': ['Y','B','M','E','H','K','L','N','R','S','V','T','X','G','Z','U'],
                      '公务舱': ['C','J','D','I','O'],
                      '商务舱': ['C','J','D','I','O'],
                      '头等舱': ['F','P','A','W']}
dict_plane_to_province = {'禄口机场': '南京', '兴东机场': '南通', '硕放机场': '无锡', '白莲机场': '柳州','萧山机场': '杭州', '塔城机场': '塔城','伊宁机场': '伊宁',
                          '济宁机场': '济宁', '云端机场': '保山', '香格里拉机场': '迪庆','遥墙机场': '济南', '流亭机场': '青岛','沐埠岭机场': '临沂',
                          '长乐机场': '福州', '高崎机场': '厦门','豸山机场': '龙岩冠', '邦达机场': '昌都', '库尔勒机场': '库尔勒','白云机场': '广州',
                          '首都机场': '北京', '南苑机场': '北京', '王村机场': '长治','天河机场': '武汉','滨海机场': '天津', '可可托托海机场': '富蕴',
                          '白塔机场': '呼和浩特','喀什机场': '喀什','锡林浩特机场': '锡林浩特','贡嘎机场': '拉萨', '庆阳机场': '庆阳','二里半机场': '包头',
                          '龙嘉机场': '长春', '普者黑机场': '文山', '库车机场': '库车','阿尔泰机场': '阿尔泰', '和田机场': '和田', '哈密机场': '哈密',
                          '太平机场': '哈尔滨','地窝铺机场': '乌鲁木齐', '苏温宿机场': '阿克','西双版纳机场': '西双版纳', '阿勒泰机场': '阿勒泰','温宿机场': '阿克苏',
                          '咸阳机场': '西安','西沙机场': '榆林','美兰机场': '海口','那拉提机场': '那拉提', '富蕴机场': '富蕴', '吐鲁番机场': '吐鲁番',
                          '宝安机场': '深圳','长洲岛机场': '梧州','吴圩机场': '南宁', '两江机场': '桂林','且末机场': '且末','桃花源机场': '常德','新郑机场': '郑州',
                          '江北机场': '重庆','双流机场': '成都', '蓝田机场': '泸州','保安营机场': '攀枝花', '凤凰机场': '三亚','黄花机场': '长沙',
                          '高坪机场': '南充', '莱坝机场': '宜宾','盘龙机场': '广元', '河市机场': '达州','巫家坝机场': '昆明', '三义机场': '丽江',
                          '天柱山机场':'安庆', '蚌埠机场': '蚌埠','骆岗机场': '合肥', '屯溪机场': '黄山', '首都国际机场': '北京', '敦煌机场': '敦煌',
                          '长乐国际机场': '福州', '晋江机场': '晋江', '连城机场': '连城', '武夷山机场': '武夷山', '高崎国际机场': '厦门', '酒泉机场': '酒泉',
                          '西峰镇机场': '庆阳', '嘉峪关机场': '嘉峪关', '中川机场': '兰州', '白云国际机场': '广州', '沙堤机场': '佛山', '梅县机场': '梅县',
                          '宝安国际机场': '深圳', '湛江机场': '湛江', '三灶机场': '珠海', '福城机场': '北海', '两江国际机场': '桂林','吴墟机场': '南宁',
                          '长州岛机场': '梧州', '兴义机场': '兴义', '田阳机场': '百色', '龙洞堡机场': '贵阳', '大兴机场': '铜仁', '遵义机场': '遵义',
                          '美兰国际机场': '海口', '凤凰国际机场': '三亚', '邯郸机场': '邯郸', '山海关机场': '秦皇岛', '正定机场': '石家庄', '安阳机场': '安阳',
                          '新郑国际机场': '郑州', '北郊机场': '洛阳', '姜营机场': '南阳', '萨尔图机场': '大庆', '黑河机场': '黑河', '太平国际机场': '哈尔滨',
                          '东郊机场': '佳木斯', '海浪机场': '牡丹江', '三家子机场': '齐齐哈尔', '许家坪机场': '恩施', '天河国际机场': '武汉', '刘集机场': '襄樊',
                          '三峡机场': '宜昌', '沙市机场': '荆州', '桃花机场': '常德', '黄花国际机场': '长沙', '荷花机场': '张家界', '芷江机场': '芷江',
                          '零陵机场': '永州', '龙嘉国际机场': '长春', '二台子机场': '吉林', '通化机场': '通化', '朝阳川机场': '延吉', '奔牛机场': '常州',
                          '白塔埠机场': '连云港', '禄口国际机场': '南京','无锡机场': '无锡', '观音机场': '徐州', '涟水机场': '淮安', '外砂机场': '汕头',
                          '南洋机场': '盐城', '罗家机场': '景德镇', '井冈山机场': '井冈山', '庐山机场': '九江', '昌北机场': '南昌', '黄金机场': '赣州',
                          '腾鳌机场': '鞍山', '朝阳机场': '朝阳', '大长山岛机场': '长海', '浪头机场': '丹东', '周水子机场': '大连', '小岭子机场': '锦州',
                          '桃仙机场': '沈阳', '海兰泡机场': '包头', '土城子机场': '赤峰', '鄂尔多斯机场': '鄂尔多斯', '白塔国际机场': '呼和浩特',
                          '东山机场': '海拉尔', '乌兰浩特机场': '乌兰浩特', '西郊机场': '满洲里', '通辽机场': '通辽', '乌海机场': '乌海','香港机场': '香港',
                          '河东机场': '银川', '格尔木机场': '格尔木', '曹家堡机场': '西宁', '永安机场': '东营', '曲阜机场': '济宁', '流亭国际机场': '青岛',
                          '遥墙国际机场': '济南', '大水泊机场': '威海', '莱山机场': '烟台', '临沂机场': '临沂','黎平机场': '黎平', '黄果树机场': '安顺',
                          '怀仁机场': '大同', '武宿机场': '太原', '关公机场': '运城', '五里铺机场': '安康', '二十里铺机场': '延安', '澳门机场': '澳门',
                          '咸阳国际机场': '西安', '浦东国际机场': '上海', '虹桥国际机场': '上海', '双流国际机场': '成都', '河市霸机场': '达县',
                          '广元机场': '广元', '黄龙机场': '九寨沟', '萱田机场': '泸州', '南郊机场': '绵阳', '都尉坝机场': '南充', '攀枝花机场': '攀枝花',
                          '万县机场': '万州', '青山机场': '西昌', '菜坝机场': '宜宾', '滨海国际机场': '天津', '昌都马草机场': '昌都', '大理机场': '大理',
                          '克拉玛依机场': '克拉玛依','地窝堡国际机场': '乌鲁木齐','交河机场': '吐鲁番', '保山机场': '保山', '迪庆机场': '迪庆香格里拉',
                          '景洪机场': '西双版纳', '巫家坝国际机场': '昆明', '丽江机场': '丽江', '临沧机场': '临沧', '芒市机场': '德宏芒市', '思茅机场': '思茅',
                          '昭通机场': '昭通', '文山普者黑机场': '文山', '萧山国际机场': '杭州', '普陀山机场': '舟山', '路桥机场': '台州/黄岩', '衢州机场': '衢州',
                          '栎社机场': '宁波', '永强机场': '温州', '义乌机场': '义乌', '江北国际机场': '重庆', '五桥机场': '重庆', '香港国际机场': '香港',
                          '澳门国际机场': '澳门','浦东机场': '上海', '虹桥机场': '上海','地窝堡机场': '乌鲁木齐'}
set_province = ['江苏省', '江苏', '浙江省', '浙江', '山东省', '山东', '福建省', '福建', '江西省', '江西', '安徽省', '安徽', '河南省', '河南', '四川省', '内蒙古',
                '河北省', '河北', '山西省', '山西', '辽宁省', '辽宁', '吉林省', '吉林', '陕西省', '陕西', '甘肃省', '甘肃', '四川', '云南省', '云南', '宁夏',
                '青海省', '青海', '广东省', '广东', '广西省', '广西', '海南省', '海南', '湖北省', '湖北', '湖南省', '湖南', '贵州省', '贵州', '西藏', '新疆']
set_sub_province = ['安庆','蚌埠','阜阳','合肥','黄山','北京南苑','北京', '北京首都','福州','晋江','连城','武夷山','厦门','酒泉','敦煌','庆阳','嘉峪关','兰州',
                    '广州','佛山','梅县','汕头','深圳','湛江','珠海','北海','桂林','柳州','南宁','梧州','兴义','百色','贵阳','铜仁','遵义','黎平','安顺','海口',
                    '三亚','邯郸','秦皇岛','石家庄','安阳','郑州','洛阳','南阳','大庆','黑河','哈尔滨','佳木斯','牡丹江','齐齐哈尔','恩施','武汉','襄樊','宜昌',
                    '荆州','常德','长沙','张家界','芷江','永州','长春','吉林','通化','延吉','常州','连云港','南京','南通','无锡','徐州','淮安','盐城','景德镇',
                    '井冈山','九江','南昌','赣州','鞍山','朝阳','长海','丹东','大连','锦州','沈阳','包头','赤峰','鄂尔多斯','呼和浩特','海拉尔','乌兰浩特','满洲里',
                    '通辽','乌海','锡林浩特','银川','格尔木','西宁','东营','济宁','青岛','济南','潍坊','威海','烟台','临沂','长治','大同','太原','运城','安康',
                    '延安','汉中','榆林','西安','上海浦东','上海虹桥','成都','达县','广元','九寨沟','泸州','绵阳','南充','攀枝花','万州','西昌','宜宾','天津',
                    '昌都','拉萨','阿克苏','富蕴','哈密','阿勒泰','和田','且末','库车','喀什','库尔勒','克拉玛依','塔城','新源','乌鲁木齐','伊宁','吐鲁番','保山',
                    '迪庆香格里拉','大理','西双版纳','昆明','丽江','临沧','德宏芒市','思茅','昭通','文山','杭州','舟山','台州/黄岩','衢州','宁波','温州','义乌',
                    '重庆','重庆','香港','澳门','北京首都','福州','厦门','广州','深圳','桂林','海口','三亚','郑州','哈尔滨','武汉','长沙','长春','南京','呼和浩特',
                    '青岛','济南','西安', '上海','上海浦东','上海虹桥','成都','天津','乌鲁木齐','昆明','杭州','重庆','香港','澳门',]
nums_map = {'一': 1, '两': 2, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '1': 1, '2': 2, '3': 3, '4': 4,
            '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
time_map = {'下一': 7 - today.weekday(), '下二': 7 - today.weekday() + 1, '下日': 7 - today.weekday() + 6, '下四': 7 - today.weekday() + 3,
            '下三': 7 - today.weekday() + 2, '下天': 7 - today.weekday() + 6, '下六': 7 - today.weekday() + 5, '下五': 7 - today.weekday() + 4,
            '一': 7 - today.weekday(), '六': 7 - today.weekday() + 5, '天':  7 - today.weekday() + 6, '二': 7 - today.weekday() + 1,
            '日': 7 - today.weekday() + 6, '三':  7 - today.weekday() + 2, '四': 7 - today.weekday() + 3, '五': 7 - today.weekday() + 4,
            '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
common_used_numerals_tmp = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '百': 100,
                            '千': 1000, '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15, '十六': 16, '十七': 17, '十八': 18, '十九': 19,
                            '一十': 10, '一十一': 11, '一十二': 12, '一十三': 13, '一十四': 14, '一十五': 15, '一十六': 16,
                            '一十七': 17, '一十八': 18, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                            '一十九': 19, '二十': 20, '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 23}
help_dict = {'sTime': '时间1', 'dTime': '时间2', 'sCity': '地点1', 'dCity': '地点2', 'nTickets': '票数', 'discount': '折扣',
             'price_flag': '价格标记', 'time_flag': '时间标记', 'class': '舱位', 'company': '公司', 'flight_type': '机型', 'flight_price': '价格'}


class Demo:
    def __init__(self, model_path='./ltp_data_v3.4.0/', result_path='./result', sent_path='./sentence', show=True):
        self.show = show
        self.RES_DIR = result_path
        self.SENT_DIR = sent_path

        self.state = 0
        self.answer = []
        self.total_flight = []
        self.cur_flight = []
        self.total_nums = 0
        self.topic = None
        self.error = None
        self.change = False
        self.bk_time = [0, 0, 0]
        self.bk_sCity = None
        self.bk_dCity = None
        self.error_times = 0
        self.ticket_info = OrderedDict({
            'sTime': None,
            'dTime': None,
            'sCity': '广州',
            'dCity': None,
            'nTickets': 1,
            'class': None,
            'company': None,
            'flight_type': None,
            'flight_price': None,
            'discount': None,
            'price_flag': None,
            'time_flag': None})
        self.first_time = 0
        self.bk_ticket_info = OrderedDict({
            'sTime': None,
            'dTime': None,
            'sCity': '广州',
            'dCity': None,
            'nTickets': 1,
            'class': None,
            'company': None,
            'flight_type': None,
            'flight_price': None,
            'discount': None,
            'price_flag': None,
            'time_flag': None})
        self.askInfo_nums = OrderedDict({
            'sTime': 0,
            'dCity': 0})

        # 加载模型
        cws_model_path = os.path.join(model_path, 'cws.model')  # 分词
        pos_model_path = os.path.join(model_path, 'pos.model')  # 词性标注
        self.segmentor = Segmentor()  # 初始化实例
        self.segmentor.load_with_lexicon(cws_model_path, os.path.join(model_path, 'lexicon'))  # 加载模型
        self.postagger = Postagger()  # 初始化模型
        self.postagger.load_with_lexicon(pos_model_path, os.path.join(model_path, 'post_lexicon'))  # 加载模型

    def __del__(self):
        self.segmentor.release()
        self.postagger.release()

    def _default(self):
        """ 直接重置基本数据 """
        self.state = 0
        self.answer = []
        self.total_flight = []
        self.cur_flight = []
        self.total_nums = 0
        self.topic = None
        self.error = None
        self.change = False
        self.bk_time = [0, 0, 0]
        self.bk_sCity = None
        self.bk_dCity = None
        self.error_times = 0
        self.ticket_info = OrderedDict({
            'sTime': None,
            'dTime': None,
            'sCity': '广州',
            'dCity': None,
            'nTickets': 1,
            'class': None,
            'company': None,
            'flight_type': None,
            'flight_price': None,
            'discount': None,
            'price_flag': None,
            'time_flag': None})
        self.first_time = 0
        self.bk_ticket_info = OrderedDict({
            'sTime': None,
            'dTime': None,
            'sCity': '广州',
            'dCity': None,
            'nTickets': 1,
            'class': None,
            'company': None,
            'flight_type': None,
            'flight_price': None,
            'discount': None,
            'price_flag': None,
            'time_flag': None})
        self.askInfo_nums = OrderedDict({
            'sTime': 0,
            'dCity': 0})

    def _basic_handle(self, sentence):
        self.sentence = sentence.replace('号', '日')
        self.sentence = self.sentence.replace('元', '块钱')
        self.sentence = self.sentence.replace('点', '时')
        self.sentence = self.sentence.replace('今年', '2017年')
        self.sentence = self.sentence.replace('明年', '2018年')
        self.sentence = self.sentence.replace('这个月', '12月')
        self.sentence = self.sentence.replace('订张', '订一张')

        # 替换下午时间
        map_to = {'一': '13', '二': '14', '三': '15', '四': '16', '五': '17', '六': '18', '七': '19', '八': '20', '九': '21', '十': '22', '1': '13',
                  '2': '14', '3': '15', '4': '16', '5': '17', '6': '18', '7': '19'}
        m = re.search(r'下午([一二三四五六七01234567])时到(.)([一二三四五六七八九十0123456789])时', self.sentence)
        if m:
            self.sentence = self.sentence.replace('下午' + m.groups()[0] + '时' + m.groups()[1] + m.groups()[2] + '时',
                                                  '下午' + map_to[m.groups()[0]] + '时' + m.groups()[1] + map_to[m.groups()[2]] + '时')
        m = re.search(r'下午([一二三四五六七01234567])时', self.sentence)
        if m:
            self.sentence = self.sentence.replace('下午' + m.groups()[0] + '时', '下午' + map_to[m.groups()[0]] + '时')

        # 替换晚上
        map_to = {'零': '23','七': '19','八': '20','九': '21','十': '22','十一': '23','十二': '23','0': '23','7': '19','8': '20','9': '21','10': '22',
                  '11': '23','12': '23',}
        m = re.search(r"晚上(零|七|八|九|十|十一|十二|0|7|8|9|10|11|12)时(.)(零|七|八|九|十|十一|十二|0|7|8|9|10|11|12)时", self.sentence)
        if m:
            self.sentence = self.sentence.replace('晚上' + m.groups()[0] + '时' + m.groups()[1] + m.groups()[2] + '时',
                                                  '晚上' + map_to[m.groups()[0]] + '时' + m.groups()[1] + map_to[m.groups()[2]] + '时')
        m = re.search(r'晚上(零|七|八|九|十|十一|十二|0|7|8|9|10|11|12)时', self.sentence)
        if m:
            self.sentence = self.sentence.replace('晚上' + m.groups()[0] + '时', '晚上' + map_to[m.groups()[0]] + '时')

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
                    temp += str(common_used_numerals_tmp[y[0]]) +str(common_used_numerals_tmp[y[1]]) + str(common_used_numerals_tmp[y[2]]) + \
                            str(common_used_numerals_tmp[y[3]])
                temp += '年'
            elif month:
                m = month.groups()[0]
                if m == '下':
                    temp += '2018年1'
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
                # if dict_temp[d1[0][0]] > dict_temp[d1[1][0]]:
                #     self.error = (1, "对不起，你输入的日期已经过去了。")
                #     return None
                # cur1 = now + datetime.timedelta(dict_temp[d1[0][0]])
                cur2 = now + datetime.timedelta(dict_temp[d1[1][0]])
                if self.ticket_info['sTime'] is None:
                    self.ticket_info['sTime'] = [cur2.year, cur2.month, cur2.day, 0]
                    self.ticket_info['dTime'] = [cur2.year, cur2.month, cur2.day, 23]
                else:
                    self.ticket_info['sTime'] = [cur2.year, cur2.month, cur2.day, 0]
                    self.ticket_info['dTime'] = [cur2.year, cur2.month, cur2.day, 23]

        d2 = re.search(r"(\d{1,2})[个]*天[之以]*后", sent)
        if d2:
            flag = True
            da = d2.groups()[0]
            if int(da) > 55:
                self.error = (1, "抱歉，我只能查到60天以内的票")
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
            if cur.hour == 22:
                cur = now + datetime.timedelta(hours=int(ha) + 1)
            if cur.hour == 23:
                cur = now + datetime.timedelta(hours=int(ha))
            self.ticket_info['sTime'] = [cur.year, cur.month, cur.day, cur.hour]
            # cur += datetime.timedelta(hours=int(ha) + 1)
            self.ticket_info['dTime'] = [cur.year, cur.month, cur.day, 23]

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

        place_2, place_1, place_3 = '', '', ''
        dict_place, s, j = {}, '', 0
        for i in range(len_sent):
            if self.postags[i] == 'ns':
                s += chr( 97 + j )
                dict_place[chr(97 + j)] = self.words[i]
                j += 1
            else:
                s += self.words[i]
        for i in range(len(s)):
            if s[i] in list('qwertyuiopasdfghjklzxcvbnm'):
                j = 1
                while i - j >= 0 and s[i - j] in list('qwertyuiopasdfghjklzxcvbnm'):
                    j += 1
                if i - j < 0:
                    place_3 = s[i]
                    print(place_3)
                l1, l2 = max(i-j-3, 0), i-j+1
                if '不' in list(s[l1:l2]):
                    continue
                set1 = set('到去至飞回差')
                set3 = set('从')
                set2 = set(s[l1:l2])
                print(set2, "|", set1, "|", set3)
                if set1.intersection(set2):
                    place_2 = s[i]
                elif set3.intersection(set2):
                    place_1 = s[i]
                else:
                    place_3 = s[i]
        print(place_1, "|", place_2, "|", place_3)
        if place_3:
            if place_2:
                place_1 = place_3
            else:
                place_2 = place_3
        if place_1:
            place_1 = dict_place[place_1]
        if place_2:
            place_2 = dict_place[place_2]
        print(place_1, "|", place_2, "|", place_3)

        if place_1 == '' and place_2 == '':
            return None
        return place_1, place_2

    def _nums(self):
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
        m = re.search(r"(\d{1,2})Z张", temp)
        if m:
            if self.postags[int(m.groups()[0])] == 'v':
                nums = 1
            elif self.words[int(m.groups()[0])] in nums_map.keys():
                nums = nums_map[self.words[int(m.groups()[0])]]
            else:
                self.error = (3, "抱歉，我最多能订十张票。")
                return None
        else:
            n = re.search(r"(\d{1,2})Z张", temp)
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
        sent = self.sentence
        sent = sent.replace('高端经济舱', 'W')
        sent = sent.replace('经济舱', 'N')
        sent = sent.replace('商务舱', 'E')
        sent = sent.replace('公务舱', 'V')
        sent = sent.replace('头等舱', 'C')

        class1, class2, flag = set(), set(), []
        for i in range(len(sent)):
            if sent[i] in ['W', 'N', 'E', 'V', 'C']:
                l1, l2 = max(i-3, 0), i
                if i == 0:
                    class2 = class2.union([sent[i]])
                    flag.append('2')
                    continue
                if sent[i-1] == '和':
                    if flag[-1] == '1':
                        class1 = class1.union([sent[i]])
                        flag.append('1')
                    else:
                        class2 = class2.union([sent[i]])
                        flag.append('2')
                    continue
                if '不' in list(sent[l1:l2]):
                    class1 = class1.union([sent[i]])
                    flag.append('1')
                else:
                    class2 = class2.union([sent[i]])
                    flag.append('2')
        if class1 == set() and class2 == set():
            return None
        dict_class = {'W': '高端经济舱', 'N': '经济舱', 'E': '商务舱', 'V': '公务舱', 'C': '头等舱'}
        c1, c2 = set(), set()
        for i in class1:
            c1 = c1.union([dict_class[i]])
        for i in class2:
            c2 = c2.union([dict_class[i]])
        if not self.ticket_info['class']:
            temp = set(set_class)
        else:
            temp = self.ticket_info['class']
        if c2 != set():
            temp = temp.intersection(c2)
        self.ticket_info['class'] = temp.difference(c1)

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
            elif self.words[i] in set_flight_type:
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

        b1 = re.search(r"不.{0,3}[要坐用](\d{1,2})B", temp)
        b2 = re.search(r"(\d{1,2})B", temp)

        M1 = re.search(r"不.{0,3}[要坐用](\d{1,2})M", temp)
        M2 = re.search(r"(\d{1,2})M", temp)

        o1 = re.search(r"不.{0,3}[要坐用](\d{1,2})O", temp)
        o2 = re.search(r"(\d{1,2})O.*", temp)

        k1 = re.search(r"不.{0,3}[要坐用](\d{1,2})K.", temp)
        k2 = re.search(r"(\d{1,2})K", temp)

        x1 = re.search(r"不.{0,3}[要坐用](\d{1,2})X", temp)
        x2 = re.search(r"(\d{1,2})X", temp)

        m1 = re.search(r"不.{0,3}[要坐用](\d{1,2})Z和(\d{1,2})Z", temp)
        m2 = re.search(r"不.{0,3}[要坐用](\d{1,2})Z", temp)
        m3 = re.search(r"(\d{1,2})Z和(\d{1,2})Z", temp)
        m4 = re.search(r"(\d{1,2})Z", temp)

        if not self.ticket_info['flight_type']:
            temp = set(set_flight_type)
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
            if word1[0] in ['B', 'K', 'M'] and word1[1:] in set_flight_type:
                temp1 = temp1.union([word1[1:]])
            elif word1[0] not in ['B', 'K', 'M']:
                temp1 = temp1.union(['B'+word1, 'K'+word1, 'M'+word1])
            if word2[0] in ['B', 'K', 'M'] and word2[1:] in set_flight_type:
                temp1 = temp1.union([word2[1:]])
            elif word2[0] not in ['B', 'K', 'M']:
                temp1 = temp1.union(['B' + word2, 'K' + word2, 'M' + word2])
        elif m2:
            word1 = self.words[int(m2.groups()[0])]
            temp1 = temp1.union([word1])
            if word1[0] in ['B', 'K', 'M'] and word1[1:] in set_flight_type:
                temp1 = temp1.union([word1[1:]])
            elif word1[0] not in ['B', 'K', 'M']:
                temp1 = temp1.union(['B'+word1, 'K'+word1, 'M'+word1])
        elif m3:
            word1, word2 = self.words[int(m3.groups()[0])], self.words[int(m3.groups()[1])]
            temp2 = temp2.union([word1, word2])
            if word1[0] in ['B', 'K', 'M'] and word1[1:] in set_flight_type:
                temp2 = temp2.union([word1[1:]])
            elif word1[0] not in ['B', 'K', 'M']:
                temp2 = temp2.union(['B'+word1, 'K'+word1, 'M'+word1])
            if word2[0] in ['B', 'K', 'M'] and word2[1:] in set_flight_type:
                temp2 = temp2.union([word2[1:]])
            elif word2[0] not in ['B', 'K', 'M']:
                temp2 = temp2.union(['B' + word2, 'K' + word2, 'M' + word2])
        elif m4:
            word1 = self.words[int(m4.groups()[0])]
            temp2 = temp2.union([word1])
            if word1[0] in ['B', 'K', 'M'] and word1[1:] in set_flight_type:
                temp2 = temp2.union([word1[1:]])
            elif word1[0] not in ['B', 'K', 'M']:
                temp2 = temp2.union(['B'+word1, 'K'+word1, 'M'+word1])

        if temp2 != set():
            temp = temp.intersection(temp2)
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
        dict_company, s, j = {}, '', 0
        for i in range(len_sent):
            if self.words[i] in set_company:
                s += chr(97 + j)
                dict_company[chr(97 + j)] = self.words[i]
                j += 1
            else:
                s += self.words[i]
        company1, company2, flag = set(), set(), []
        for i in range(len(s)):
            if s[i] in list('qwertyuioplkjhgfdsaxzcvbnm'):
                l1, l2 = max(i - 3, 0), i
                if i == 0:
                    company2 = company2.union([s[i]])
                    flag.append('2')
                    continue
                if s[i - 1] == '和':
                    if flag[-1] == '1':
                        company1 = company1.union([s[i]])
                        flag.append('1')
                    else:
                        company2 = company2.union([s[i]])
                        flag.append('2')
                    continue
                if '不' in list(s[l1:l2]):
                    company1 = company1.union([s[i]])
                    flag.append('1')
                else:
                    company2 = company2.union([s[i]])
                    flag.append('2')
        if company2 == set() and company1 == set():
            return None
        # print(company2, "|", company1)
        c1, c2 = set(), set()
        for i in company1:
            c1 = c1.union([dict_company[i]])
        for i in company2:
            c2 = c2.union([dict_company[i]])
        # print(c1, "|", c2)
        for kk in [set(['中国国际航空公司', '国航']),set(['东方航空公司', '东方航空', '东航']),set(['南方航空公司', '南方航空', '南航']),set(['海南航空公司', '海南航空', '海航']),
                   set(['上海航空公司', '上海航空', '上航']),set(['山东航空公司', '山东航空', '山航']),set(['深圳航空公司', '深圳航空', '深航']),set(['厦门航空公司', '厦门航空', '厦航']),
                   set(['中国联合航空公司', '联合航空']),set(['四川航空公司', '四川航空', '川航']),set(['大新华航空', '大新华'])]:
            if kk.intersection(c1):
                c1 = c1.union(kk)
            elif kk.intersection(c2):
                c2 = c2.union(kk)
        # print(c1, "|", c2)
        if not self.ticket_info['company']:
            temp = set(set_company)
        else:
            temp = self.ticket_info['company']
        if c2 != set():
            temp = temp.intersection(c2)
        self.ticket_info['company'] = temp.difference(c1)
        return True

    def _price(self):
        """ 价格处理 """
        if self.error:
            return None
        sent = self._time_help()

        m1 = re.search(r"[低少]于(\d{2,})", sent)
        m2 = re.search(r"(\d{2,})(块钱|块)[之以]*下", sent)

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
                    result = str(nums_map[word[0]]) + '0'
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
                    result = str(nums_map[word[0]]) + '0'
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
                    result = str(nums_map[word[0]]) + '0'
                else:
                    self.error = (11, '你输入的折扣有点问题')
                    return None

        return result

    def _flag(self):
        if self.error:
            return None
        sent = self.sentence

        m1 = re.search(r"(最便宜|最贵)", sent)
        m2 = re.search(r"(最早|最晚)", sent)
        m3 = re.search(r"(价格)", sent)
        m4 = re.search(r"(最低)", sent)
        price, time = None, None
        if m1:
            if m1.groups()[0] == '最便宜':
                price = True
            else:
                price = False
        elif m3 and m4:
            price = True

        if m2:
            if m2.groups()[0] == '最早':
                time = True
            else:
                time = False

        if price is not None or time is not None:
            return price, time
        else:
            return None

    def _flights(self, start, end):
        md = hashlib.md5()
        url = 'http://qae.qunar.com/api/router'
        createTime = int(round(time.time() * 1000))
        key = 'f080fdcb118be76df8ca0cee70b51047'
        t = self.ticket_info['sTime']
        tag = 'flight.national.supply.sl.searchflight'
        token = 'e2d43dd7f897f3e26c6c72b303abdd32'
        concat = 'createTime=%skey=%sparams={"dpt":"%s","arr":"%s","date":"%d-%02d-%02d","ex_track":"tehui"}tag=%stoken=%s' % \
                 (createTime, key, start, end, t[0], t[1], t[2], tag, token)
        md.update(concat.encode('utf-8'))
        sign = md.hexdigest()
        data = OrderedDict({
            'sign': sign,
            'tag': tag,
            'token': token,
            'createTime': createTime,
            'params': '{"dpt":"%s","arr":"%s","date":"%d-%02d-%02d","ex_track":"tehui"}' % (start, end,  t[0], t[1], t[2]),
        })
        postdata = parse.urlencode(data).encode('utf-8')
        req = request.Request(url, postdata)
        r = request.urlopen(req)
        result = r.read().decode('utf-8')

        result = result.replace("null", 'None')
        result = result.replace('false', 'False')
        result = result.replace('true', 'True')

        result = eval(result)
        return result

    def _is_relate(self, sent):
        """通过 词典 确定是否订票相关"""
        self._basic_handle(sent)

        # 一开始的检查是否是订票相关问题 只要当有票时候才认为是在订票
        # if self.state == 0:
        #     m = re.search(r"(票)", sent)
        #     if not m:
        #         return False

        self.bk_ticket_info = copy.deepcopy(self.ticket_info)      # 备份信息

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
            self.answer.append(self.error[1])
            self.error = None
            return True

        rand = random.randint(0, 10)
        m = re.search(r"([再重还].*[新来订要]).*(开始|票|张|查询)", self.sentence)
        m1 = re.search(r"(重查|重来)", self.sentence)
        if m or m1:
            self.answer.append(sent_restart[rand % len(sent_restart)])
            self._default()
            return True
        return False

    def _is_new_topic(self):
        """ 如果没有提到旧的话题， 那么就认为来了新话题 """
        if self.state == 0:
            return False

        if self.topic == 'sTime' and self.time:
            return False
        elif self.topic == 'dCity' and self.places and self.places[1]:
            return False

        if self.nums and self.nums != 1:
            self.ticket_info['nTickets'] = self.nums

        if self.time:
            if self.bk_time != self.ticket_info['sTime'][:3]:
                self.change = True
            self.bk_time = self.ticket_info['sTime'][:3]
        if self.classes or self.company or self.flight_type:
            pass

        if self.price:
            self.ticket_info['flight_price'] = self.price

        if self.discount:
            self.ticket_info['discount'] = self.discount

        if self.flag and self.flag[0] is not None:
            self.ticket_info['price_flag'] = self.flag[0]
            self.ticket_info['time_flag'] = None

        if self.flag and self.flag[1] is not None:
            self.ticket_info['time_flag'] = self.flag[1]
            self.ticket_info['price_flag'] = None

        if self.places and self.places[0]:
            if self.bk_sCity != self.places[0]:
                self.change = True  # 表示需重新加载数据
            self.bk_sCity = self.places[0]
            self.ticket_info['sCity'] = self.places[0]
            if self.ticket_info['dCity'] and self.ticket_info['sCity'] == self.ticket_info['dCity']:
                self.answer.append('抱歉，出发地和目的地相同。')
                return True

        if self.places and self.places[1]:
            if self.bk_dCity != self.places[1]:
                self.change = True  # 表示需重新加载数据
            self.bk_dCity = self.places[1]
            self.ticket_info['dCity'] = self.places[1]
            if self.ticket_info['sCity'] and self.ticket_info['sCity'] == self.ticket_info['dCity']:
                self.answer.append('抱歉，出发地和目的地相同。')
                return True

        rand = random.randint(0, 10)
        self.state = 1
        self.topic = None
        for key in ['sTime', 'dCity']:
            if self.ticket_info[key] is None:
                self.topic = key
                self.askInfo_nums[key] += 1
                if self.askInfo_nums[key] > 2:
                    self.answer.append(sent_multiAsk[key][rand % len(sent_multiAsk[key])])  # 句子有待扩展
                    break
                self.answer.append(sent_topic[key][rand % len(sent_topic[key])])
                break
        if self.topic is None:
            self.state = 2
            self.topic = 'search'
            self.answer.append(sent_topic[self.topic][rand % len(sent_topic[self.topic])])
            self.answer.append(over[rand % len(over)])

        return True

    def _writeinfo(self):

        if self.topic == 'sTime':
            if self.bk_time != self.ticket_info['sTime'][:3]:
                self.change = True
            self.bk_time = self.ticket_info['sTime'][:3]
        elif self.topic == 'dCity':
            if self.bk_dCity != self.places[1]:
                self.change = True  # 表示需重新加载数据
            self.bk_dCity = self.places[1]
            self.ticket_info['dCity'] = self.places[1]

        if self.topic != 'sTime' and self.time:
            if self.bk_time != self.ticket_info['sTime'][:3]:
                self.change = True
            self.bk_time = self.ticket_info['sTime'][:3]

        if self.nums:
            self.ticket_info['nTickets'] = self.nums

        if self.classes or self.company or self.flight_type:
            pass

        if self.price:
            self.ticket_info['flight_price'] = self.price

        if self.discount:
            self.ticket_info['discount'] = self.discount

        if self.flag and self.flag[0] is not None:
            self.ticket_info['price_flag'] = self.flag[0]
            self.ticket_info['time_flag'] = None

        if self.flag and self.flag[1] is not None:
            self.ticket_info['time_flag'] = self.flag[1]
            self.ticket_info['price_flag'] = None

        if self.places and self.places[0]:
            if self.bk_sCity != self.places[0]:
                self.change = True  # 表示需重新加载数据
            self.bk_sCity = self.places[0]
            self.ticket_info['sCity'] = self.places[0]
            if self.ticket_info['dCity'] and self.ticket_info['sCity'] == self.ticket_info['dCity']:
                self.answer.append('抱歉，出发地和目的地相同。')
                return True

        if self.topic != 'dCity' and self.places and self.places[1]:
            if self.bk_dCity != self.places[1]:
                self.change = True  # 表示需重新加载数据
            self.bk_dCity = self.places[1]
            self.change = True  # 表示需重新加载数据
            self.ticket_info['dCity'] = self.places[1]
            if self.ticket_info['sCity'] and self.ticket_info['sCity'] == self.ticket_info['dCity']:
                self.answer.append('抱歉，出发地和目的地相同。')
                return True

        rand = random.randint(0, 10)
        self.state = 1
        self.topic = None
        for key in ['sTime', 'dCity']:
            if self.ticket_info[key] is None:
                self.topic = key
                self.askInfo_nums[key] += 1
                if self.askInfo_nums[key] > 2:
                    self.answer.append(sent_multiAsk[key][rand % len(sent_multiAsk[key])])  # 句子有待扩展
                    break
                self.answer.append(sent_topic[key][rand % len(sent_topic[key])])
                break
        if self.topic is None:
            self.state = 2
            self.topic = 'search'
            self.answer.append(sent_topic[self.topic][rand % len(sent_topic[self.topic])])
            self.answer.append(over[rand % len(over)])

    def _book(self):
        """ 去网站查询票信息 """
        if self.topic != 'search':
            return False
        self._default()
        self.answer.append('本次查询结束，谢谢！')
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
                self.answer.append('本次查询结束，谢谢！')
            self.answer.append("我是机票精灵，我能为您提供机票信息")
            return True
        elif m2:
            if self.topic == 'search':
                self._default()
                self.answer.append('本次查询结束，谢谢！')
            self.answer.append("作为订票助手，我能为您提供机票信息")
            return True
        elif m3:
            if self.topic == 'search':
                self._default()
                self.answer.append('本次查询结束，谢谢！')
            self.answer.append("我是机票精灵")
            return True
        else:
            return False

    def _response(self):
        temp = '>> '
        if self.show:
            for key in ['sTime', 'dTime', 'sCity', 'dCity', 'nTickets', 'discount', 'price_flag', 'time_flag', 'class', 'company',
                        'flight_type', 'flight_price']:
                if self.ticket_info[key] is not None:
                    temp += help_dict[key] + ":" + str(self.ticket_info[key]) + ' | '
            temp += "state:" + str(self.state) + " | " + "topic:" + str(self.topic) + " |"
            print(temp)

        if self.topic != 'search':
            return
        self.first_time += 1
        if self.total_flight == []:
            self.change = False
            a, b = self.ticket_info['sCity'], self.ticket_info['dCity']
            if a in dict_city_to_code.keys(): set1 = dict_city_to_code[a]
            elif a in dict_plane_to_code.keys(): set1 = dict_plane_to_code[a]
            else: set1 = []
            if b in dict_city_to_code.keys(): set2 = dict_city_to_code[b]
            elif b in dict_plane_to_code.keys(): set2 = dict_plane_to_code[b]
            else: set2 = []
            if set1 == []:
                self.answer = ['暂时不支持查询从' + self.ticket_info['sCity'] + '出发的飞机航线']
                return
            if set2 == []:
                self.answer = ['暂时不支持查询到达', self.ticket_info['dCity'], '的飞机航线']
                return
            for start in set1:
                for end in set2:
                    temp = self._flights(start, end)
                    if temp and temp['result']:
                        self.total_flight.extend(temp['result']['flightInfos'])

        if self.total_flight and self.change:
            self.change = False
            self.total_flight = []
            a, b = self.ticket_info['sCity'], self.ticket_info['dCity']
            if a in dict_city_to_code.keys(): set1 = dict_city_to_code[a]
            elif a in dict_plane_to_code.keys(): set1 = dict_plane_to_code[a]
            else: set1 = []
            if b in dict_city_to_code.keys(): set2 = dict_city_to_code[b]
            elif b in dict_plane_to_code.keys(): set2 = dict_plane_to_code[b]
            else: set2 = []
            if set1 == []:
                self.answer = ['暂时不支持查询从', self.ticket_info['sCity'], '出发的飞机航线']
                return
            if set2 == []:
                self.answer = ['暂时不支持查询到达', self.ticket_info['dCity'], '的飞机航线']
                return
            for start in set1:
                for end in set2:
                    temp = self._flights(start, end)
                    if temp and temp['result']:
                        self.total_flight.extend(temp['result']['flightInfos'])

        if self.total_flight == []:
            self._default()
            self.answer = ['暂无当天航班供您选择', '请您重新查询机票信息']
            return

        print(len(self.total_flight))
        set1, set2, set3 = [], [], []
        if self.ticket_info['class']:
            for c in self.ticket_info['class']:
                set1.extend(dict_class_to_code[c])
        if self.ticket_info['company']:
            for c in self.ticket_info['company']:
                set2.append(dict_company_to_code[c])
        if self.ticket_info['flight_type']:
            for c in self.ticket_info['flight_type']:
                set3.append(dict_type_to_code[c])
        # 筛选self.total_flight
        self.cur_flight = []
        for flight in self.total_flight:
            if set1:
                if flight['cabin'] not in set1:
                    continue
            if set2:
                if flight['carrier'] not in set2:
                    continue
            if set3:
                if flight['flightTypeFullName'] not in set3:
                    continue
            if self.ticket_info['flight_price']:
                price = int(flight['barePrice'])
                if price < self.ticket_info['flight_price'][0] or price > self.ticket_info['flight_price'][1]:
                    continue
            if self.ticket_info['discount']:
                dis = int(flight['discount'] * 10)
                if dis > int(self.ticket_info['discount'][1]):
                    continue
            t1, t2 = self.ticket_info['sTime'][3], self.ticket_info['dTime'][3]
            if t1 <= int(flight['dptTime'][:2]) <= t2:
                self.cur_flight.append(flight)

        if self.cur_flight == []:
            if self.first_time == 1:
                self._default()
                self.answer = ['暂无满足条件的航班供您选择', '请您重新开始订票']
                self.total_nums = 0
            else:
                self.ticket_info = copy.deepcopy(self.bk_ticket_info)
                self.answer = ['暂无满足条件的航班供您选择', '请重说筛选条件']
                set1, set2, set3 = [], [], []
                if self.ticket_info['class']:
                    for c in self.ticket_info['class']:
                        set1.extend(dict_class_to_code[c])
                if self.ticket_info['company']:
                    for c in self.ticket_info['company']:
                        set2.append(dict_company_to_code[c])
                if self.ticket_info['flight_type']:
                    for c in self.ticket_info['flight_type']:
                        set3.append(dict_type_to_code[c])
                for flight in self.total_flight:
                    if set1:
                        if flight['cabin'] not in set1:
                            continue
                    if set2:
                        if flight['carrier'] not in set2:
                            continue
                    if set3:
                        if flight['flightTypeFullName'] not in set3:
                            continue
                    if self.ticket_info['flight_price']:
                        price = int(flight['barePrice'])
                        if price < self.ticket_info['flight_price'][0] or price > self.ticket_info['flight_price'][1]:
                            continue
                    if self.ticket_info['discount']:
                        dis = int(flight['discount'] * 10)
                        if dis > int(self.ticket_info['discount'][1]):
                            continue
                    t1, t2 = self.ticket_info['sTime'][3], self.ticket_info['dTime'][3]
                    if t1 <= int(flight['dptTime'][:2]) <= t2:
                        self.cur_flight.append(flight)
                if self.ticket_info['price_flag'] is not None:
                    self.cur_flight = sorted(self.cur_flight, key=lambda item: int(item['barePrice']))
                    if not self.ticket_info['price_flag']:
                        self.cur_flight = list(reversed(self.cur_flight))
                    l = min(len(self.cur_flight), 4)
                    self.cur_flight = self.cur_flight[:l]
                elif self.ticket_info['time_flag'] is not None:
                    self.cur_flight = sorted(self.cur_flight,
                                             key=lambda item: datetime.datetime(2017, 12, 12, int(item['dptTime'][:2]), int(item['dptTime'][-2:])))
                    if not self.ticket_info['time_flag']:
                        self.cur_flight = list(reversed(self.cur_flight))
                    l = min(len(self.cur_flight), 4)
                    self.cur_flight = self.cur_flight[:l]
                self.total_nums = len(self.cur_flight)
        else:
            if self.ticket_info['price_flag'] is not None:
                self.cur_flight = sorted(self.cur_flight, key=lambda item: int(item['barePrice']))
                if not self.ticket_info['price_flag']:
                    self.cur_flight = list(reversed(self.cur_flight))
                l = min(len(self.cur_flight), 4)
                self.cur_flight = self.cur_flight[:l]
            elif self.ticket_info['time_flag'] is not None:
                self.cur_flight = sorted(self.cur_flight, key=lambda item: datetime.datetime(2017,12,12,int(item['dptTime'][:2]), int(item['dptTime'][-2:])))
                if not self.ticket_info['time_flag']:
                    self.cur_flight = list(reversed(self.cur_flight))
                l = min(len(self.cur_flight), 4)
                self.cur_flight = self.cur_flight[:l]
            self.total_nums = len(self.cur_flight)

    def booking(self, sent):
        """ 订票功能: 每次输入一个句子，从语音而来 """
        temp = '>> '
        if sent == 'clear':
            self._default()
            return self.answer, self.ticket_info, self.total_nums, self.cur_flight, temp+'None', len(self.total_flight)
        self.answer = []

        if self._is_relate(sent):
            self.error_times = 0
            if self._is_new_task():
                pass
            elif self._is_new_topic():
                pass

            else:
                self._writeinfo()
            self._response()
        else:
            if self._start() or self._book():
                self._response()
            else:
                rand = random.randint(0, 15)
                self.answer.append(sent_error1[rand % len(sent_error1)] + sent_error2[rand % len(sent_error2)])
                self.error_times += 1
                if self.error_times == 2:
                    self.answer.append(sent_start[rand % len(sent_start)])
                    self.error_times = 0
                self._response()
        if self.show:
            for key in ['sTime', 'dTime', 'sCity', 'dCity', 'nTickets', 'discount', 'price_flag', 'time_flag', 'class', 'company',
                        'flight_type', 'flight_price']:
                if self.ticket_info[key] is not None:
                    temp += help_dict[key] + ":" + str(self.ticket_info[key]) + ' | '
            temp += "state:" + str(self.state) + " | " + "topic:" + str(self.topic) + " |"

        return self.answer, self.ticket_info, self.total_nums, self.cur_flight, temp, len(self.total_flight)


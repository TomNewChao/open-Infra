# -*- coding: utf-8 -*-
# @Time    : 2022/10/25 11:15
# @Author  : Tom_zc
# @FileName: utils_extractor.py
# @Software: PyCharm
import re
from itertools import groupby


class Extractor(object):
    def __init__(self):
        pass

    # noinspection PyMethodMayBeStatic
    def replace_chinese(self, text):
        """
        remove all the chinese characters in text
        eg: replace_chinese('我的email是ifee@baidu.com和dsdsd@dsdsd.com,李林的邮箱是eewewe@gmail.com哈哈哈')


        :param: raw_text
        :return: text_without_chinese<str>
        """
        filtrate = re.compile(u'[\u4E00-\u9FA5]')
        text_without_chinese = filtrate.sub(r' ', text)
        return text_without_chinese

    def extract_email(self, text):
        """
        extract all email addresses from texts<string>
        eg: extract_email('我的email是ifee@baidu.com和dsdsd@dsdsd.com,李林的邮箱是eewewe@gmail.com哈哈哈')


        :param: raw_text
        :return: email_addresses_list<list>
        """
        eng_texts = self.replace_chinese(text)
        eng_texts = eng_texts.replace(' at ', '@').replace(' dot ', '.')
        sep = ',!?:; ，。！？《》、|\\/'
        eng_split_texts = [''.join(g) for k, g in groupby(eng_texts, sep.__contains__) if not k]

        email_pattern = r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$'

        emails = []
        for eng_text in eng_split_texts:
            result = re.match(email_pattern, eng_text, flags=0)
            if result:
                emails.append(result.string)
        return emails

    def extract_cellphone(self, text, nation):
        """
        extract all cell phone numbers from texts<string>
        eg: extract_email('my email address is sldisd@baidu.com and dsdsd@dsdsd.com,李林的邮箱是eewewe@gmail.com哈哈哈')


        :param: raw_text
        :return: email_addresses_list<list>
        """
        eng_texts = self.replace_chinese(text)
        sep = ',!?:; ：，。！？《》、|\\/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        eng_split_texts = [''.join(g) for k, g in groupby(eng_texts, sep.__contains__) if not k]
        eng_split_texts_clean = [ele for ele in eng_split_texts if len(ele) >= 7 and len(ele) < 17]
        if nation == 'CHN':
            phone_pattern = '((\+86)?([- ])?)?(|(13[0-9])|(14[0-9])|(15[0-9])|(17[0-9])|(18[0-9])|(19[0-9]))([- ])?\d{3}([- ])?\d{4}([- ])?\d{4}'
        else:
            phone_pattern = '((\+86)?([- ])?)?(|(13[0-9])|(14[0-9])|(15[0-9])|(17[0-9])|(18[0-9])|(19[0-9]))([- ])?\d{3}([- ])?\d{4}([- ])?\d{4}'
        phones = []
        for eng_text in eng_split_texts_clean:
            result = re.match(phone_pattern, eng_text, flags=0)
            if result:
                phones.append(result.string.replace('+86', '').replace('-', ''))
        return phones

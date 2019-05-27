#! usr/vin/env python3
# -*- coding: utf-8 -*-


from lxml import etree
import html
import os


class TOXML:
    '''
        用于将字典结构转换为xml或者html。字典的嵌套结构满足于树形文件节点的父子结构，
        对于具有同级同名标签的情况，需要以列表或元组的形式映射到一个键值上，例如：
            >>> d = {
                'documents':{
                    'document1':[
                        {'node1':'text1'},
                        {'node2':'text2'}
                    ],
                    'document2':{
                        'node3':{
                            'node4':'text3'
                        }
                    }
                }
            }
            >>> t2x = TOXML()
            >>> t2x.turn2xml(d)
            >>> t2x.storage()
        包含的方法：
        :turn2xml(self, nodes_dict)
            将字典转换为树形文件对象。
            params:
                :nodes_dict: 一个定义标签层级的字典。
        :tostring(self, pretty_print=True, xml_declaration=True, encoding='utf-8',
                  method='xml')
            返回一个树形对象的规格化字符串，默认编码为utf-8，转换类型为xml。
            params:
                :pretty_print: 格式化输出，默认为Ture；
                :xml_declaration: xml声明，默认为Ture；
                :encoding: 字符串编码，默认为utf-8；
                :method: 转换类型，默认为xml，可选为html。
        :storage(self, file_name='', file_path='', encoding='utf-8', unescape=False,
                 method='xml)
            用于将转换得到的树形对象存储为文本。
            params:
                :file_name: 该文件名，不传参数使用默认值；
                :file_path: 文件存储文件夹，默认值为当前文件夹；
                :encoding: 文件编码；
                :unescape: 是否对某些符号转换实体引用，默认为转换；
                :method: 转换文件类型，默认为xml，可选为html。
        :set_attr(self, xpath_exp, name, value)
            用于对特定标签设置属性。
            params:
                :xpath_exp: xpath表达式，用于定位标签；
                :name: 设置的属性名；
                :value: 设置的属性值。
    '''
    def __init__(self):
        self.count = 1

    def turn2xml(self, nodes_dict):
        for root, nodes in nodes_dict.items():
            self.root = etree.Element(root)
            self.__xmlnodesparse(self.root, nodes)
            self.tree = etree.ElementTree(self.root)

    def __xmlnodesparse(self, pre_node, nodes):
        for k,v in nodes.items():
            if isinstance(v, (str, int, float)):
                etree.SubElement(pre_node, k).text = v
            elif isinstance(v, (list, tuple)):
                for vone in v:
                    cur_node = etree.SubElement(pre_node, k)
                    self.__xmlnodesparse(cur_node, vone)
            elif isinstance(v, dict):
                cur_node = etree.SubElement(pre_node, k)
                self.__xmlnodesparse(cur_node, v)

    def tostring(self, pretty_print=True, xml_declaration=True, encoding='utf-8',
                 method='xml'):
        string = etree.tostring(self.root, pretty_print=pretty_print,
                                xml_declaration=xml_declaration, encoding=encoding,
                                method=method)
        return string.decode(encoding)

    def storage(self, file_name='', file_path='', encoding='utf-8', unescape=False,
                method='xml'):
        file_name = ''.join([file_name, '.', method]) if file_name else 'xml%d.%s' % (self.count, method)
        cur_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(cur_path, file_path) if file_path else os.path.dirname(os.path.abspath(__file__))
        self.__create_dirs(file_path)
        if not unescape:
            self.tree.write(os.path.join(file_path, file_name), encoding=encoding,
                            pretty_print=True, xml_declaration=True, method=method)
        elif unescape:
            self.__storage_with_unescape(file_name, file_path, method=method,
                                         encoding=encoding)
        self.count += 1

    def set_attr(self, xpath_exp, name, value):
        node_list = self.root.xpath(xpath_exp)
        for node in node_list:
            node.set(name, value)

    def __storage_with_unescape(self, file_name, file_path, method, encoding):
        with open(os.path.join(file_path, file_name), mode='w', encoding=encoding) as f:
            string = self.tostring(pretty_print=True, xml_declaration=True,
                                   encoding=encoding, method=method)
            string = html.unescape(string)
            f.write(string)

    def __create_dirs(self, file_path):
        if not os.path.exists(file_path):
            os.makedirs(file_path)


if __name__ == '__main__':
    nodes = {
                'documents':{
                    'document1':[
                        {'node1':'text1'},
                        {'node2':'text2'}
                    ],
                    'document2':{
                        'node3':{
                            'node4':'text3'
                        }
                    }
                }
            }
    test = TOXML()
    test.turn2xml(nodes)
    test.set_attr('//node1', 'RealValue', 'True')
    s = test.tostring(pretty_print=True, xml_declaration=True, encoding='utf-8', method='xml')
    # test.storage(unescape=True)
    test.storage()
    print(s)

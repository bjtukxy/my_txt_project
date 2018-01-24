# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 14:07:52 2018

@author: lenovo-cy
"""
import os
import shutil 
import my_pLSA as plsa
import pandas as pd
import jieba
import codecs
import sys  
reload(sys)  
sys.setdefaultencoding('utf-8')
class Cla_statistics():
    def __init__(self, path = 'D:/python/New_study/20180119', num_topic = 2):
        self.path = path #需分类文件地址
        self.num_topic = num_topic
        self.dictionary_path = r"D:\\python\New_study\vocar.txt" #词库地址
        self.Top_doc_path = r"D:\\python\New_study\classified result\topic_doc.txt"
        self.Word_top_path = r"D:\\python\New_study\classified result\word_topic.txt"
        self.path_1 = r"D:\\python\New_study"#分类文本存储文件夹前路径
        
    def file_classify(self):        
#        path = self.path#'D:/python/New_study/20180119'#文件夹路径
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        name_list=os.listdir(self.path)#路径文件夹中所有文件的名称，返回列表  
        
        fn_list=[]
        for i in xrange(0,len(name_list)): #获得各文件的绝对路径       
            path_file=os.path.join(self.path, name_list[i])#连接目录和文件名，返回字符串
            fn_list.append(path_file)        
        
        #分类文本
        _plsa = plsa.pLSA_lph(self.num_topic)
        _plsa.build_dictionary(self.dictionary_path)
        _plsa.load_text(fn_list)
        _plsa.initialization()
        _plsa.train()
        _plsa.printTopicOfDoc()
        _plsa.printWordOfTopic()
        _plsa.saveTopicOfDoc(self.Top_doc_path)
        _plsa.saveWordOfTopic(self.Word_top_path)
        
        #将分类的文本存储到指定位置
        td_index=_plsa.give_index() 
        addres = 201800
        for i in xrange(len(fn_list)):
            Addres = addres + td_index[i]
            Addres = '\%s' %Addres
            save_ad = '%s%s' %(self.path_1, Addres)
            if not os.path.exists(save_ad):
                os.mkdir(save_ad)
            shutil.copy(fn_list[i], save_ad)
            
    def exc_txt(self,_add, _addres,_text_name):
        add=_add
        title_list = [u'日期', u'车载/地面', u'软/硬件故障', u'故障情况概述',u'分析结果']#选择信息所属列
        catering_sale=str(add).decode('utf-8')
        data=pd.read_excel(catering_sale)
                #计算有效信息数量
        A=data.loc[:,u'月份']
        A_noempty=A.fillna('mis') 
        i=0
        while A_noempty[i] != 'mis': 
            i += 1
        num_info = i
        #将信息合成
        Syn_info = []
        for i in xrange(num_info):    
            _syn_info = '%s %s %s %s %s' %( data.loc[i,title_list[0]],
                                            data.loc[i,title_list[1]],
                                            data.loc[i,title_list[2]],
                                            data.loc[i,title_list[3]], 
                                            data.loc[i,title_list[4]]
                                            )
            Syn_info.append(_syn_info)
       #删除不相关的text 
        stop_words = [u'软件', u'非责', u'误操作', u'其它', u'自然灾害', u'电磁干扰',u'机务',u'车辆问题'
                u'车地匹配', u'车辆原因', u'非车载', u'地面故障']#u'非责', u'其它', u'误操作', u'自然灾害', u'电磁干扰', u'非车载', u'外界干扰', u'干扰', u'地面故障',u'机务', u'车辆问题', u'车辆'
        stop_punct = [u'，', u'。', u'、', u'（', u'）', u'(', u')', u'·', u'！', u' ', u'：', u'“', u'”', u'\n']

        file_name=r'D:\\python\jieba_dic\load.txt'#导入自定义词汇
        jieba.load_userdict(file_name)
        j = 0
        while j < len(Syn_info):
            text = ''.join(Syn_info[j].split())
            text = ''.join(Syn_info[j].split('\n'))
            seg_generator = jieba.cut(text)
            seg_list = [i for i in seg_generator if i not in stop_punct] 
            for k in seg_list:
                if k in stop_words:            
                    Syn_info.pop(j)
                    j=j-1
            j=j+1
            
           #将各信息输出为文本
        addres = _addres#u'D:/python/2014列控故障文本'
        text_name = _text_name#20140000
        shutil.rmtree(addres)  #删除文件夹
        if not os.path.exists(addres):
            os.mkdir(addres)
        for i in xrange(len(Syn_info)):
            Text_name = ('%s%s' %(str(text_name), '.txt'))
            path_file = os.path.join(addres, Text_name)#连接目录和文件名，返回字符串
            f = codecs.open(path_file, 'w')
            f.write("%s" %Syn_info[i])
            f.close()
            text_name = text_name + 1
        
            
if __name__=="__main__":
    _Clsa=Cla_statistics()
    #_Clsa.file_classify()
#    _add = r'C:/Users/lenovo-cy/Documents/毕设数据/2014年ATP故障统计.xls'
#    _addres = u'D:/python/2014列控故障文本'
#    _text_name = 20140000
#    _Clsa.exc_txt(_add,_addres,_text_name)#目标文件地址、存储文件夹地址、文件名。
    
    
    
    
    
    
    
    
    
    
    
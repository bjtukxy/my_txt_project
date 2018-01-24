# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 17:06:14 2018

@author: lenovo-cy
"""
import os
import math
import random
import jieba
import codecs
import datetime
import sys  
reload(sys)  
sys.setdefaultencoding('utf-8')

class pLSA_lph():
    def __init__(self, ntopic = 5):
        self.n_doc = 0
        self.n_word = 0
        self.n_topic = ntopic
        self.corpus = None  
        self.p_z_dw = None
        self.p_w_z = None
        self.p_z_d = None
        self.likelihood = 0
        self.vocab = None    #主题词库
        self.stop_words = [u'，', u'。', u'、', u'（', u'）', u'·', u'！', u' ', u'：', u'“', u'”', u'\n']
       
       # 每行和为1的正实数，概率分布;
    def _rand_mat(self, sizex, sizey):
        ret = []
        for i in xrange(sizex):
            ret.append([])
            for _ in xrange(sizey):
                ret[-1].append(random.random())
            norm = sum(ret[-1])
            for j in xrange(sizey):
                ret[-1][j] /= norm
        return ret
        
        #生成主题词库
    def build_dictionary(self,fn):
        f = open(fn, 'r')
        text = f.readlines()   #读取所有行(直到结束符 EOF)并返回列表
        text = r' '.join(text) #将text中的元素以指定的字符" "连接生成一个新的字符串
        
        seg_generator = jieba.cut(text)#以默认模式将text拆分为词组组合
        seg_list = [i for i in seg_generator if i not in self.stop_words]#除去text中不需要的字符
        seg_list = r' '.join(seg_list)
        
        # 切割统计所有出现的词纳入词典
        seglist = seg_list.split(" ")#通过指定分隔符对字符串进行切片,默认为所有的空字符，包括空格、换行(\n)、制表符(\t)等。
        self.vocab = []
        for word in seglist:
            if (word != u' ' and word not in self.vocab):#去除重复词及空格
                self.vocab.append(word)
        self.n_word =len(self.vocab)
        f.close()
   
    def load_text(self, fn_list):
        CountMatrix = []
        for fn in fn_list:
            f = open(fn, 'r')
            text = f.readlines()   #读取所有行(直到结束符 EOF)并返回列表
            text = r''.join(text) #将text中的元素以指定的字符" "连接生成一个新的字符串
            text = text.replace(" ","")#用于移除字符串空格
            text = text.replace("/n","")#用于移除字符串回车
        
#        CountMatrix = []
#        f.seek(0, 0) #用于移动文件读取指针到指定位置
        # 统计每个文档中出现的词频
            # 置零
            count = [0 for i in range(len(self.vocab))]
            # 但还是要先分词
            seg_generator = jieba.cut(text)
            seg_list = [i for i in seg_generator if i not in self.stop_words]
            seg_list = r' '.join(seg_list)
            seglist = seg_list.split(" ")
            # 查询词典中的词出现的词频
            for word in seglist:
                if word in self.vocab:
                    count[self.vocab.index(word)] += 1#将词组对应位置计数值加1
            CountMatrix.append(count)
            f.close()
        self.corpus = CountMatrix
        self.n_doc = len(CountMatrix) #文档的数量
    
    #初始化参数
    def initialization(self):
        self.p_z_d = self._rand_mat(self.n_topic, self.n_doc)
        self.p_w_z = self._rand_mat(self.n_word, self.n_topic)
        self.p_z_dw =[]
        for k in range(self.n_topic):
            self.p_z_dw.append(self._rand_mat(self.n_doc, self.n_word))
    
    def _e_step(self):
        for k in range(self.n_topic):
            for d in range(self.n_doc):
                for j in range(self.n_word):
                    _d_wz_zd = 0
                    for kk in range(self.n_topic):
                        _d_wz_zd += self.p_w_z[j][kk]*self.p_z_d[kk][d]
                    if _d_wz_zd <= 0:
                        _d_wz_zd = 1e-6
                    self.p_z_dw[k][d][j] = self.p_w_z[j][k]*self.p_z_d[k][d]/_d_wz_zd

    def _m_step(self):
        print "updating Pn(Wj|Zk)...\r"
        for j in range(self.n_word):
            for k in range(self.n_topic):
                _d_dw_zdw = 0
                for d in range(self.n_doc):
                    _d_dw_zdw += self.corpus[d][j]*self.p_z_dw[k][d][j]

                _d_dw_zdw_sum = 0
                for jj in range(self.n_word):
                    _d_dw_zdw_i = 0
                    for d in range(self.n_doc):
                        _d_dw_zdw_i += self.corpus[d][jj]*self.p_z_dw[k][d][jj]
                    _d_dw_zdw_sum += _d_dw_zdw_i

                if _d_dw_zdw_sum <= 0:
                    _d_dw_zdw_sum = 1e-6
                self.p_w_z[j][k] = _d_dw_zdw/_d_dw_zdw_sum

        print "updating Pn(Zk|Di)...\r"
        for k in range(self.n_topic):
            for d in range(self.n_doc):
                _d_dw_zdw = 0
                for j in range(self.n_word):
                    _d_dw_zdw += self.corpus[d][j]*self.p_z_dw[k][d][j]

                _d_dw_zdw_sum = 0
                for kk in range(self.n_topic):
                    _d_dw_zdw_i = 0
                    for j in range(self.n_word):
                        _d_dw_zdw_i += self.corpus[d][j]*self.p_z_dw[kk][d][j]

                    _d_dw_zdw_sum += _d_dw_zdw_i

                if _d_dw_zdw_sum <= 0:
                    _d_dw_zdw_sum = 1e-6
                self.p_z_d[k][d] = _d_dw_zdw/_d_dw_zdw_sum
        #计算最大似然值
    def _cal_max_likelihood(self):
        self.likelihood = 0
        for d in range(self.n_doc):
            for j in range(self.n_word):
                _dP_wjdi = 0
                for k in range(self.n_topic):
                    _dP_wjdi += self.p_w_z[j][k]*self.p_z_d[k][d]
                _dP_wjdi = 1.0/self.n_doc*_dP_wjdi# 1/self.n_doc表示选中文档的概率
                self.likelihood += self.corpus[d][j]*math.log(_dP_wjdi)
        #迭代训练
    def train(self, n_iter = 100, d_delta = 1e-6,log_fn = "log.log"):
        itr = 0
        delta =10e9
        _likelihood = 0
        f = open(log_fn, 'w')
        while itr < n_iter and delta > d_delta:
            _likelihood = self.likelihood
            self._e_step()
            self._m_step()
            self._cal_max_likelihood()
            itr += 1
            delta = abs(self.likelihood - _likelihood)
            t1 = datetime.datetime.now().strftime('%Y-%m-%d-%y %H:%M:%S');#输出'2015-04-07 19:11:21'，strftime是datetime类的实例方法。
            f.write("%s  iteration %d, max-likelihood = %.6f\n"%(t1, itr, self.likelihood))#%s字符串,%d十进制整数,%f浮点数
            print "%s  iteration %d, max-likelihood = %.6f"%(t1, itr, self.likelihood)
        f.close()
    
    def printVocabulary(self):#打印词典中的词
        print "vocabulary:"
        for word in self.vocab:
            print word,
        print

    def saveVocabulary(self, fn):#以utf-8格式存储词典中的词
        f = codecs.open(fn, 'w', 'utf-8')
        for word in self.vocab:
            f.write("%s ,"%word)#回车，光标在下一行
        f.close()

    def printWordOfTopic(self):#打印word/topic概率
        for k in range(self.n_topic):
            print "Topic %d"%k,
            for j in range(self.n_word):
                print self.p_w_z[j][k],
            print

    def saveWordOfTopic(self,fn):
        f = open(fn, 'w')
        for j in range(self.n_word):
            f.write(", w%d"%j)
        f.write("\n")
        for k in range(self.n_topic):
            f.write("topic %d"%k)
            for j in range(self.n_word):
                f.write(", %.6f"%self.p_w_z[j][k])
            f.write("\n")
        f.close()

    def printTopicOfDoc(self):#打印topic/doc概率
        for d in range(self.n_doc):
            print "Doc %d"%d,
            for k in range(self.n_topic):
                print self.p_z_d[k][d],
            print

    def saveTopicOfDoc(self, fn):
        f = codecs.open(fn, 'w')
        for k in range(self.n_topic):
            f.write(", z%d" %k)
        f.write("\n")
        for d in range(self.n_doc):
            f.write("doc %d" %d)
            for k in range(self.n_topic):
                f.write(", %.6f" %self.p_z_d[k][d])
            f.write("\n")
        f.close()
    
    def give_index(self):#求文档对应的主题
        topicdoc_T=[]        
        for d in range(self.n_doc):
            topic_T=[]
            for k in range(self.n_topic):
                topic_T.append(self.p_z_d[k][d])
            topicdoc_T.append(topic_T)
        
        list_index=[]
        for i in xrange(0,len(topicdoc_T)):
            max_td=topicdoc_T[i].index(max(topicdoc_T[i]))
            list_index.append(max_td)
        return list_index
    
if __name__=="__main__":
    fn_list=[]
    path='D:/python/New_study/20180119'#文件夹路径
    if not os.path.exists(path):
        os.mkdir(path)
    name_list=os.listdir(path)#路径文件夹中所有文件的名称，返回列表  
    
    for i in xrange(0,len(name_list)): #获得各文件的绝对路径       
        path_file=os.path.join(path, name_list[i])#连接目录和文件名，返回字符串
        fn_list.append(path_file)        
    
    _plsa = pLSA_lph(2)
    _plsa.build_dictionary(r"D:\python\New_study\vocar.txt")
    _plsa.load_text(fn_list)
    _plsa.initialization()
    _plsa.train()
    _plsa.printTopicOfDoc()
    _plsa.printWordOfTopic()
    _plsa.saveTopicOfDoc(r"D:\\python\New_study\classified result\topic_doc.txt")
    _plsa.saveWordOfTopic(r"D:\\python\New_study\classified result\word_topic.txt")
#    a=_plsa.give_index()
    
        


from sklearn.model_selection import StratifiedShuffleSplit
import pandas as pd
import util.Global as gol


def tips(groups,train_ratio,test_ratio,verification_ratio,test_data):
    '''
    test_data指的是新的测试集数据的 gol 的 key
    '''
    if len(groups)!=2:
        return False,"分组数量不为2,为："+str(len(groups))
    if train_ratio>0:
        if test_ratio< 1e-6 and gol.get_value(test_data) is None:
            return False,"当没有新的测试数据时，测试集比例不能为0"
        if train_ratio>test_ratio and train_ratio>verification_ratio:
            group1_len = len(groups[0])
            group2_len = len(groups[1])
            result = ""
            if group1_len/group2_len>2 or group1_len/group2_len<0.5:
                result+="阴性组和阳性组的样本分布不均衡；"
            total_sum = group1_len+group2_len
            if total_sum<10:
                result+="样本数量不足10个，分类效果会大打折扣；"
            if verification_ratio>0 and total_sum<60:
                if gol.get_value(test_data) is None:
                    result+="当样本数量不足60时，不适合拆分出验证集；"
            return True,result
        else:
            return False, "训练集的比例应该大于测试集和验证集的比例"
    else:
        return False,"训练集比例不能为0"


def get_class(index,ngroup_list,pgroup_list):
    if index in ngroup_list:
        return 0
    elif index in pgroup_list:
        return 1
    else:
        raise  Exception("有异常样本："+index)


def dataset_split(ori_data,test_ratio,verification_ratio,train_ratio,ngroup,pgroup,groups_dict):
    data=pd.DataFrame(ori_data.values.T, index=ori_data.columns, columns=ori_data.index)
    data["class"] = data.apply(lambda row:get_class(row.name,groups_dict[ngroup],groups_dict[pgroup]),axis=1)
    # 分层拆分成测试与训练数据集
    if test_ratio < 1e-6:
        train_set = data
        test_set = None
    else:
        split = StratifiedShuffleSplit(n_splits=1, test_size=test_ratio, random_state=42)
        for train_index, test_index in split.split(data, data["class"]):
            train_set = data.iloc[train_index]
            test_set = data.iloc[test_index]
    if verification_ratio < 1e-6:
        return train_set, None,test_set
    else:
        # 将训练集拆分出训练集和验证集
        split1 = StratifiedShuffleSplit(n_splits=1, test_size=(verification_ratio/train_ratio), random_state=42)
        for train_index1, verification_index in split1.split(train_set, train_set["class"]):
            verification_set = train_set.iloc[verification_index]
            train_set1 = train_set.iloc[train_index1]
            return train_set1,verification_set,test_set


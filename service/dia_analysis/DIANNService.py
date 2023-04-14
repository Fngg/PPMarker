import numpy as np
import pandas as pd
from numpy.linalg import solve


def maxlfq_solve(piv,margin= -10.0001):
    samples =piv.shape[1]
    peptides =piv.shape[0]

    ref = piv.max()
    ref[ref<margin]=-1000000.0

    A = np.zeros((samples,samples))
    B = np.zeros((samples,1))

    for i in range(samples):
        for j in range(i+1,samples):
            ratios = []
            pi = piv.iloc[:,i]
            pj = piv.iloc[:,j]
            for k in range(peptides):
                if pi[k]>margin and pj[k]>margin:
                    ratios.append(pi[k]-pj[k])
            if len(ratios):
                median = np.median(ratios)
                A[i,i] = A[i,i]+1
                A[j,j] = A[j,j]+1
                A[i,j] =-1
                A[j, i] = -1
                B[i,0] = B[i,0]+median
                B[j,0] = B[j,0] - median
    for i in range(samples):
        reg = 0.0001*(A[i,i] if A[i,i]>=1 else 1)
        A[i,i] = A[i,i]+reg
        B[i,0] = B[i,0] +ref[i]*reg

    data = solve(A,B)
    data_list = []
    for i in  range(samples):
        data_list.append(data[i,0])
    result = pd.Series(data_list)
    return result



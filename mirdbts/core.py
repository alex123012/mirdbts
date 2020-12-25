"""
            Functions for investgations

its a few funcs to solve some problems with comparison
    prediction datasets from TargetScan and miRDB
                with some features

"""

import pandas as pd
import numpy as np
import re

def hsa_del(df, column):
    df1 = df.copy()
    df1[f'{column}'] = df1[f'{column}'].apply(lambda x: x.replace('hsa-', ''))
    return df1

def hsa_add(df, column):
    df1 = df.copy()
    for ind, row in df.iterrows():
        x = row[f'{column}']
        if 'hsa-' in x or 'let-' in x:
            continue
        else:
            df1.loc[ind, f'{column}'] = 'hsa-' + x
    return df1

def mirname_remake(df,column, new_col_name):
    df1 = df.copy()
    list_temp = []
    for ind, row in df1.iterrows():
        for name in row[f'{column}'].split('/'):
            new_name = "miR-" + name if name[0].isdigit() else name
            new_name = 'hsa-' + new_name if 'let-' not in new_name and 'hsa-' not in new_name else new_name
            list_temp.append([new_name] + [i for i in row])
    result_df = pd.DataFrame(list_temp,
            columns=[new_col_name]+df.columns.tolist())
    result_df.drop(f'{column}', 1, inplace=True)
    
    return result_df


def comp_predict(df_miRDB, df_TargetScan, column_miRDB='miRNA Name', column_ts='miRNA_family_ID'):

    target_scores = {miRNA: score for miRNA, score in zip(df_miRDB["miRNA Name"], df_miRDB["Target Score"])}
    result_list = []
    for ind, row in df_TargetScan.iterrows():
        gene = row['a_Gene_ID']
        for name in row[column_ts].split("/"):
            new_name = "miR-" + name if name[0].isdigit() else name
            new_name = "hsa-" + new_name if 'let-' not in new_name and 'hsa-' not in new_name else new_name

            if new_name not in target_scores:  # Intersect with miRDB
                continue

            target_score = target_scores[new_name]
            result_list.append([new_name, gene, row["MSA_start"], row["MSA_end"], row["Site_type"], target_score])

    return pd.DataFrame(result_list, columns = ["miRNA", "a_Gene_ID", "Start", "End", "Site type", "Target Score"])

def concat_predict(df, miRNA_column):
    ls = np.unique(df[f'{miRNA_column}'])
    column_df = df.columns.tolist()
    df1 = df.copy()
    result_list = []
    for i in ls:
        temp_df = df1[df1[f'{miRNA_column}'] == i]
        temp_list = []
        for j in column_df:
            if temp_df[j].tolist() == []:
                continue
            x = np.unique(temp_df[j]).tolist()
            if len(x) == 1:
                x = x[0]
            temp_list.append(x)
        result_list.append(temp_list)

    return pd.DataFrame(result_list, columns=column_df)

def top_score(df, column, percent):
    return df.drop(np.where(df[f'{column}'] < percent)[0])

print('{!python --version}')
import pandas as pd
import os
import csv
import re

def csv_file_add_header(source_file):
    df = pd.read_csv(source_file, header=None, names=['Repo Name', 'Description', 'URL', 'Languages', 'Stars', 'suitLangNum'])
    df.to_csv(source_file, index=False)

def csv_file_deduplicated(source_file,res_file):
    df = pd.read_csv(source_file)
    df.drop_duplicates(subset=['Repo Name', 'URL'], inplace=True)
    df.to_csv(res_file, index=False)


def csv_file_merged(csv_file1,csv_file2,res_file):

    df1 = pd.read_csv(csv_file1)
    df2 = pd.read_csv(csv_file2)

    merged_df = pd.concat([df1, df2])
    merged_df.to_csv(res_file, index=False)




def all_files_deduplicated():
    file_names = ['repo_C.csv', 'repo_C++.csv', 'repo_Java.csv', 'repo_Python.csv']
    source_file_base = 'D:\\'
    for file_name in file_names:
        source_file = source_file_base+file_name

        if os.path.exists(source_file):
            print(f'{source_file} 存在！')
        else:
            print(f'{source_file} 不存在！')
            return

        res_file = source_file_base + 'deduplicated_'+file_name
        print(f'res_file:{res_file}')
        csv_file_deduplicated(source_file,res_file)


def get_two_lang_repos():
    input_file = 'D:\\'
    output_file = 'D:\\'

    with open(input_file, mode='r', newline='',encoding='utf-8') as infile, \
            open(output_file, mode='w', newline='',encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in reader:
            pattern1 = r'\bJava\b\((\d+\.\d+)%\)'
            pattern2 = r'\bPython\b\((\d+\.\d+)%\)'
            langinfo = row['Languages']
            print(langinfo)
            match1 = re.search(pattern1, langinfo)
            match2 = re.search(pattern2, langinfo)
            if match1 and match2:
                print(f"language1: {match1.group(0)},language1: {match2.group(0)}")
                writer.writerow(row)


if __name__ == '__main__':
    source_file = ''
    res_file = ''
    csv_file_deduplicated(source_file,res_file)


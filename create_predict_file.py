#!/usr/bin/env python
import sys
import mysql.connector
import re
import time
import datetime
from dateutil.relativedelta import relativedelta
import sys

db=mysql.connector.connect(host="localhost", user="test")
cursor=db.cursor()
cursor.execute("USE nomlab_db")
db.commit()

def get_data():
    # データを取得
    cursor.execute('SELECT * FROM pulls')
    rows = cursor.fetchall()
    return rows

# ３ヵ月分のcommitを集める
# sha, file, branch
def get_commit_list():
    cursor.execute('SELECT sha, filename, created_at FROM project_commits')
    rows = cursor.fetchall()

    return rows

# 3ヵ月分のcommitを調べる
# pullreqに含まれるcommitの変更したファイルを調べる
# ファイルを変更しているcommitが３ヵ月以内であれば取り出す
def commits_on_files_touched(pr):
    months_back = 3
    sql = 'SELECT * FROM pull_commits WHERE pr_id = %s;'
    cursor.execute(sql, (pr[0],))
    commits = cursor.fetchall()
    tc = pr[4]
    file_list = []
    com = []

    for commit in commits:
        sql = "SELECT filename FROM project_commits WHERE sha = %s;"
        cursor.execute(sql, (commit[0],))
        file_list = file_list + cursor.fetchall()

    for file in file_list:
        sql = "SELECT * FROM project_commits WHERE filename = %s;"
        cursor.execute(sql, (file[0],))
        com = com + cursor.fetchall()

    activity = 0
    for c in com:
        activity = activity + 1.0 - (tc - c[3]).total_seconds() / (3600.0 * 24 * 30 * months_back)

    print(activity)
    return activity

# 3ヵ月分のcommitを調べる
# pullreqに含まれるcommitの変更したブランチを調べる
# ブランチを変更しているcommitが３ヵ月以内であれば取り出す
# できてない
def branch_hotness(pr):
    months_back = 12
   # sql = 'SELECT * FROM pull_commits WHERE pr_id = %s;'
   # cursor.execute(sql, (pr[0],))
   # commits = cursor.fetchall()
    tc = pr[4]
    com = []

    # 3ヵ月いないのをブランチごとに取り出す pr[7]のブランチの情報でwhere
    sql = "SELECT * FROM project_commits;"
    cursor.execute(sql)
    com = com + cursor.fetchall()

    activity = 0
    for c in com:
        activity = activity + 1.0 - (tc - c[3]).total_seconds() / (3600.0 * 24 * 30 * months_back)

    print(activity)
    return activity

def main():
    path = 'predict.csv'
    s = "github_id,requester,num_commits_open,lines_modified_open,files_modified_open,commits_on_files_touched,branch_hotness\n"
    with open(path, mode='w') as f:
        f.write(s)

    pulls = get_data()

    for pull in pulls:
        commit_touched = commits_on_files_touched(pull)
        hotness = branch_hotness(pull)
        print(pull[1], pull[2], pull[8], pull[9]+pull[10],pull[11], commit_touched, hotness)
        s = f"{pull[1]},{pull[2]},{pull[8]},{pull[9]+pull[10]},{pull[11]},{commit_touched},{hotness}\n"
        with open(path, mode='a') as f:
            f.write(s)

if __name__ == "__main__":
    main()
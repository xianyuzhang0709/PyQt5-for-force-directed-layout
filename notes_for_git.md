##【 2020.2.16】

####1 撤销add和commit

Git push之后，文件太大，且没必要上传env文件夹，暂停：Ctrl+C

撤销`git commit`不撤销`git add`: git reset --soft HEAD^

撤销`git add`: git reset --mixed

这时候保留了你的修改，并且只清除了你的add和commit。

####2 contribution showing up on my profile:

修改global信息

* `git config --global user.name "xxx xx"`

* `git config --global user.email "email@address.com"`

verify account emails.
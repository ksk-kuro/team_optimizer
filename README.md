# Team Optimizer manual
このアプリケーションは、ダンスショーケースのタイムテーブルを最適化することを目的としています。

# 最新版のダウンロード方法
**①**まずは、このホームページの右上にある緑色のボタンで、「< > Code ▽」と書いてあるところをクリックします。

**②**「Download ZIP」をクリック

**③**自分のパソコンに落としたら解凍して、中身を見てみましょう。ウイルス検知ソフトに引っかかると思いますが、**最新版をダウンロードしている限り**僕を信頼してください。内訳は以下の通りです。

・**README.md**:この文書です。説明書です。

・**Team_Optimizer**(.exe):本体の実行ファイルです。

・**Team_Sample_Data.xlsx**:このアプリがちゃんと動くか確かめるための、架空のチーム情報をまとめたテストデータです。

・**Team_Template.xlsx**:チーム情報をまとめるxlsxのテンプレートです。これをチームの代表者に配ってください。

・team_optimizer.py/time_getter_gui.py:プログラムの本体(ソースコード)です。コード書かない人は無視して結構です。

**④**おすすめは自分のpython環境でteam_optimizer.pyを実行すること(動作が速くウイルス検知にも引っかからないので)ですが、何言ってんのか全然わかんない人は「Team_Optimizer」をダブルクリックしてください。

**⑤**ウイルス検知ソフトに引っかかると思いますが、設定を変えてなんとか実行してください。**このページからダウンロードした最新版の安全性に関しては**僕が保証しています。

**⑥**黒い画面も出ますが気にしないでください。20秒ほど待つとアプリが立ち上がるので、下の仕様に従って使うことができます。

# 仕様
1.起動するとまず初めに黒い画面が出ますが気にしないでください。20秒ほど待つと、最終的なタイムテーブルの開始時刻を指定するか、終了時刻を指定するかを尋ねるウインドウが立ち上がります。好きな方のボタンをクリックしてください。

2.開始時刻/終了時刻を入力するウインドウが立ち上がるので、画面に従って入力してください。

3.ショーケース間の転換時間を入力するウインドウが立ち上がるので、画面に従って入力してください。

4.後述する入力フォーマットに従った、チーム情報をまとめたxlsxファイルを選ぶダイアログが表示されるので、読み込みたいxlsxファイルを選んでください。(初めは、同梱してあるTeam_Sample_Data.xlsxを試してみてください。)

5.アルゴリズムによって最適化が行われます。チーム数が多いと少々時間がかかるかもしれません。

6.後述する出力フォーマットに従ったxlsxファイルを保存するダイアログが表示されるので、好きな場所に保存してください。

# 入力
## 以下のフォーマットに従うxlsxファイルを入力として受け取ります。
チーム情報をまとめたシートを複数枚持つxlsxファイル。各シートのフォーマットは以下の通り。同梱のTeam_Sample_Data.xlsxや、Team_Templete.xlsxを見るとわかりやすいと思います。

**1行目**:2行目のインデックス

**2行目**:__1列目__;チーム・ナンバー名,  __2列目__;ショーケース時間,  __3列目__;開始順希望,    __4列目__;終了順希望,    __5列目__;開始時間希望,  __6列目__;終了時間希望

**3行目**:空行

**4行目**:5行目のインデックス

**5行目以降**:__1列目__;代,    __2列目__;ジャンル(英字),    __3列目__;姓(カナ),    __4列目__:名(カナ)

## 2行目の各パラメータについて
### 2列目:ショーケース時間
「**分:秒**」あるいは、「**0:分:秒**」の形式で入力してください。例:5分32秒の場合3:32もしくは0:03:32と入力してください。

### 3列目:開始順希望
「__この順番以降に出演したい!__」という順番をここで指定できます。例:5番目以降に出演したかったら、5と**整数で入力してください**。なお、**負の数を入れると、「後ろから何番目」かを指定することができます**。
つまり、後ろから４番目以降に出演したい場合は、-4と整数で入力してください。**特に希望がない場合は、空欄でok**です。

### 4列目:終了順希望
「__この順番以前に出演したい!__」という順番をここで指定できます。入力フォーマットは開始順希望と同じです。

### 5列目:開始時間希望
「__この時間以降に出演したい!__」という時間をここで指定できます。遅刻するメンバーがいる時などに活用してください。「**時:分:秒**」の形式で、**24時間方式で**記入してください。例:午後5時30分以降に出演したければ、「17:30:00」と入力してください。**特に希望がない場合は、空欄でokです**。

### 6列目:終了時間希望
「__この時間以前に出演したい!__」という順番をここで指定できます。早退するメンバーがいる時などに活用してください。入力フォーマットは開始時間希望と同じです。

## 優先的に考慮する条件の設定
このアルゴリズムは、すべての条件を満たす順列が存在しなかった場合、一つずつ条件を無視して最適な順列を見つけ出します。しかし、その際にどうしても無視されたくない条件があると思います(ジャンルショーケースのトリ指定や、遅刻者用の開始時間希望など)。その場合は、条件の入力の末尾に、「**j**」を付けることで、その条件を**優先的に考慮する条件**として設定できます。順番の希望であれば、5jのように'整数j'の形で、時間の希望であれば、17:30:00jのように、'時:分:秒j'のように入力してください。

# 出力
## 以下のフォーマットに従うxlsxファイルを出力します。
**シート一枚目**

最適化後のタイムテーブルです。1列目にタイムスタンプ、2列目にチーム名、3列目にショーケース時間、4列目に転換時間が書かれています。

**シート2枚目〜n枚目**

全転換における早着替えメンバーをリストアップしています。

**最終シート**

2行目の値は無視された制約の数を、3行目の配列は早着替えの人数をリストにしたものです。4行目以降には、無視された制約がリストアップされています。

# 画像アップロード：AGMサーチ

# アップロード
- 画像ファイルを一つに統合してXサーバのパブリックアクセス可能なフォルダにアップロード
- AGMサーチへのアップロードが終了したら、削除すること
    - フォルダに別れた画像ファイルの統合
    $ cp */*.webp upload


# インポート用CSV作成
- インポート用CSVファイルの作成
    - サムネイルは該当の*パッケージ*に、作業用画像ファイルは*個別資料*に対応させる
    - *パッケージ*の内部IDと個別資料の内部IDの対応表は下記から作成
        - [SPARQLクエリ](https://collection.rcgs.jp/sparql/#query=PREFIX%20dcterms%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0APREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0APREFIX%20ag%3A%20%3Chttps%3A%2F%2Fwww.analoggamemuseum.org%2Fontology%2F%3E%0APREFIX%20o%3A%20%3Chttp%3A%2F%2Fomeka.org%2Fs%2Fvocabs%2Fo%23%3E%0Aselect%20%3FitemID%20%3Fitem_oID%20%3Finstance_oID%20%7B%0A%20%20%3Fs%20rdf%3Atype%20ag%3AItem%20%3B%0A%20%20%20%20%20o%3Aid%20%3Fitem_oID%20%3B%0A%20%20%20%20%20ag%3Aidentifier%20%3FitemID%20%3B%0A%20%20%20%20%20ag%3AexemplarOf%20%3Finstance%20.%0A%20%20%3Finstance%20o%3Aid%20%3Finstance_oID%20.%0A%7D&endpoint=https%3A%2F%2Fdydra.com%2Ffukudakz%2Fagmsearchendpoint%2Fsparql&requestMethod=POST&tabTitle=Query&headers=%7B%7D&contentTypeConstruct=text%2Fturtle%2C*%2F*%3Bq%3D0.9&contentTypeSelect=application%2Fsparql-results%2Bjson%2C*%2F*%3Bq%3D0.9&outputFormat=table) （RCGS SPARQLを間借り）
        - Download result からCSV取得可能（下記ファイル）
        - xlookupなど使ってjoinする

[SPARQLクエリで生成するサンプルファイル](https://github.com/fukudakz/analoggamemuseum/blob/main/docs/assets/files/itemIDs.csv)

- インポート用CSVは下記のような形式とする。
    - dcterms:title 画像のタイトル
    - url メディアのソース
    - resourceID AGMサーチのリソースの内部ID

```
dcterms:title,url,itemID,resourceID
b624-001_work.webp,https://analoggamemuseum.org/temp/b624-001_work.webp,b624,3917
b621-001_work.webp,https://analoggamemuseum.org/temp/b621-001_work.webp,b621,3921
b620-001_work.webp,https://analoggamemuseum.org/temp/b620-001_work.webp,b620,3914
```
[CSV Import 登録用サンプルファイル](https://github.com/fukudakz/analoggamemuseum/blob/main/docs/assets/files/import_bulk_images.csv)

# Omeka Sへのインポート
- モジュール「Bulk Import」を選択する
- 「CSV - Medias」の右の「インポート」（雲のマーク）を選択する
- CSV Fileでインポート用のCSVファイルを選択する
    - その他のオプションは該当のCSVの形式による
- 以下の画像（Start importの設定）の通りの設定を入力し「Continue」を選択する
- 次のページで「Start import」を選択する

![Start importの設定](https://paper-attachments.dropboxusercontent.com/s_FFFBA7AEB78B4CE5E928713954EB0886EE55D3FDBFC7C15283916AD7247176A2_1674397262393_Screenshot+2023-01-22+at+23-20-05+Start+import++Bulk+import++agm.png)



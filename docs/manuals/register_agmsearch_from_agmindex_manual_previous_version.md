# AGMサーチデータ登録手順 from AGMインデックス

# AGMインデックスからAGMサーチへのインポート
## テーブルトップゲームのCSVデータを作成しAGMサーチに登録する

*AGMサーチ**のデータモデルでは、ゲーム資料や図書資料の「インスタンス」（複製資料の種類、または特定製品の集合）と、資料現物及びその管理単位を単位とする「個別資料」を別のクラス（リソース種別）として定義しています。ここでは、テーブルトップゲームの書誌について、AGMインデックスからインスタンスのメタデータを登録します。他の資料との重複があり得るため、その削除や管理および、AGMサーチを稼働するシステムであるOmeka Sでの採番（ID）をAGMインデックスに反映させる作業を実施します。*


1. J列「バーコード重複チェック」を全レコードに反映させる。「2」かそれ以上の整数が値として表示される場合、バーコードが重複しており、同じ製品がある。すでにインスタンスIDが登録されている場合、その値を「インスタンスID - AGMサーチ」の列にその値を登録する。それがない場合は、後ほどインスタンスIDが重複しないようにする（後述）。
    - =countif(D:D,D[行番号])
2. AGMインデックスのデータをエクスポートする。
3. 登録するレコード（未登録で種別「テーブルトップゲーム」のものだけを選択し作成する）を抽出し（それ以外を削除）、ラベル（dcterms:title）・バーコード（ag:barcode）の列のデータを切り出す
    - カッコ内はマッピング先
    - インスタンスIDが記録されているものはすでに登録済なので、それは登録済であり、このときに対象としてはいけない。
4. 説明やバーコードによる重複（同じゲームパッケージの複数登録）を削除する
    1. 削除したものがわかるようにA列のIDをメモしておく
5. CSV（UTF-8）で出力し、そのファイルでAGMサーチの管理画面のモジュール「CSVインポート」から登録する
    - 複数の種別（冊子・テーブルトップゲーム、など）がある場合はそれぞれ別のCSVとして登録する必要がある。
            - ラベルをダブリンコアのタイトル（dcterm:title）にバーコードをアナログゲームオントロジーのバーコードに（ag:barcode）をマッピングする
            - 基本設定：リソーステンプレート「テーブルトップゲーム」、クラス「テーブルトップゲーム」、所有者（自身のアカウント）、可視性「公開」、アイテムセット「インスタンス」を選択する
        - 高度な設定：Action「新規リソースの作成」、Number of rows to process by batch「20」のまま
    - CSV Importモジュール 公式マニュアル https://omeka.org/s/docs/user-manual/modules/csvimport/
6. 重複を踏まえ、AGMインデックスのインスタンスIDを補完する
## 冊子のCSVデータを作成しAGMサーチに登録する

*ここでは、前節に引き続き、「図書」のインスタンスを登録します。*

上記の「テーブルトップゲームのCSVデータを作成する」と同様。ただし登録するレコードの抽出は未登録で種別「テーブルトップゲーム」のもので、CSVインポートの際、リソーステンプレート「冊子」を選択すること。

## 個別資料のCSVデータを作成しAGMサーチに登録する

*個別資料のリソースを登録します。ここでは、「テーブルトップゲーム」と「図書」の例示（コピーの具体例）として個別資料を登録します。そのうち、AGMインデックスの記述単位（各列）がデータ登録対象です。Omeka Sで採番したIDを例示元のインスタンスと関連付ける点が若干むずかしいポイントであり、ハイライトになります。*


1. AGMインデックスのデータをエクスポートし、登録分レコード以外を削除し、個別資料ID（dcterms:title）、説明（ag:description）、由来（ag:provenance）、登録日（ag:available）、インスタンスID - AGMサーチ（ag:exemplarOf, 例示するインスタンス）の列データを切り出す
    - カッコ内はマッピング先
2. 説明のうち重複に関する情報は削除する
    - データ構造で説明されるため
3. 識別子（ag:identifier）を列追加、dcterms:titleと同じ値とする。新規項目として「ag:holdingAgent」は値を「211」、「ag:isPartOf」は値を「4886」として、列を追加する。
    - ここまでの処理についてはAGMインデックスのシート「240428個別資料登録分」を参考のこと
4. CSV（UTF-8）で出力し、そのファイルでAGMサーチの管理画面から登録する
    - ag:exemplarOf、ag:holdingAgent、ag:isPartOfは「Omekaリソース」を参照する設定とする
    - スパナマークから選択できる
        - 基本設定：リソーステンプレート「個別資料」、クラス「（Analog Game Ontology）個別資料」、所有者（自身のアカウント）、可視性「公開」、アイテムセット「インスタンス」を選択
            これ以外の項目は空でよい。
        - 高度な設定：Action「新規リソースの作成」、Number of rows to process by batch「20」のまま
## 登録したデータを検索可能にする

*Omeka Sに新規に登録したデータはまだ検索や表示できる状態のデータとしてAGMサーチサイトに認識されていません。この手続きで、AGMサーチで検索や表示ができる状態にしましょう。*


1. 管理画面でAGMサーチの管理画面にアクセスする
    1. サイト一覧を選択し、AGMサーチの右に表示される鉛筆のアイコンを選択する
2. リソース一覧のページを選択する
3. ReplaceとSearch queryが下の画像の通りになっていることを確認する。
4. 保存する。
    1. その後、念の為AGMサーチで該当のリソースが検索できるか確認してみる。
![](https://paper-attachments.dropboxusercontent.com/s_4FD8B749DABF28062A2D488C1C7371DC63159C0B21C17BDD3F3BECD7EC905B27_1728565227006_Screenshot+2024-10-10+at+21-59-43+++++agm.png)

## JSON出力とLinked Data変換

*ウェブの一つの標準であるLinked Data形式で出力し、不要な情報を削除し、公開できるデータセットを作成します。*


1. 管理画面でサイドバーからアイテムを選択し、下段のエクスポートから「json」を押下する。全データダンプされるので少し待たなければならないが、ダンプファイルが出力される。
2. Python（rdflib）とJupyter Notebookが動くPCで以下をロードする。1. のファイルを同ファイルのフォルダにコピーする（もしくはパスをメモしておく）。Pythonのライブラリ「rdflib」もインストールしておく。
https://www.dropbox.com/scl/fi/kuo6qn6apyodxjtyd9jat/AGMjson2ttl-1.ipynb?rlkey=8fkku280ioqnnbjrwfjw503q7&dl=0

3. 「g.parse("id.analoggamemuseum.org-items-20240427-171500.json", format='json-ld')」のjsonファイル名を1. で出力したファイル名に変更する。また、「g.serialize(destination='agmsearch20240428.ttl', format='turtle')」のagmsearch20240428.ttlは出力ファイル名であり、任意に変更できる。
4. 順番に実行すると、登録用のLinked Dataファイルが生成される。
## SPARQLエンドポイント登録

*誰しもが登録できるデータとして前節で作成したLinked Dataのデータセットをエンドポイントに登録し、公開します。*


1. SPARQLエンドポイントはDYDRAを用いている。サービスのURLは以下。
    - https://dydra.com/fukudakz/agmsearchendpoint
    - このアクセスポイントの管理は権限付与「Contributors」を設定する必要あり
2. ログインし、Manage → Clearで既存データを削除する。
3. インポートから、Upload a local fileのタブを選択し、前項で生成した.ttlファイルをローカルから選択する。形式はTurtle、Specify the base URI to use for this import *は「https://id.analoggamemuseum.org」を入力し、Optionally…は入力なしで、Importをクリックし、インポートする。
4. オントロジーもインポートする必要がある。もう一度インポートを選択し、Fetch from the webのタブを選択する。URLは「https://raw.githubusercontent.com/fukudakz/agmsearch/main/ontology/agmont.owl」（githubで公開するオントロジーファイル）、データフォーマットはTurtle、Specify the graph to import into *で「The default graph」を選び、Importをクリックしインポートする。
5. 完了
## GitHubへのデータセット登録

*データセットのアーカイブをGitHubに登録します。同サービスによりバージョンごとにデータをバックアップします。*


1. SPARQLエンドポイントに登録したデータセットのファイル名を “agmsearchYYYYMMDD.ttl” として保存する。
2. https://github.com/fukudakz/agmsearch にアクセスする。必要に応じて、アクセス権限を付与する。
3. backupのフォルダに保存する。
## 関連リンク
- AGMインデックス https://docs.google.com/spreadsheets/d/1IaVGwemBbPaGQNrSQUsOpOmFbNhKKmF_1mfQ0cFIX0I/edit?usp=sharing
- AGMサーチログインページ https://id.analoggamemuseum.org/login
## 作業メモ
- 2043以下は個別資料登録未了 / 図書など未登録だったインスタンスは登録した


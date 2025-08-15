#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGMインデックスからAGMサーチへのデータ登録処理スクリプト
手順に従って段階的に処理を行います
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import requests
import json
import time

class AGMIndexProcessor:
    def __init__(self, csv_file='./source/AGMIndex_20250722.csv', api_base_url=None, api_key=None):
        """初期化"""
        self.csv_file = csv_file
        self.df = None
        self.api_base_url = api_base_url or 'https://id.analoggamemuseum.org/api'
        self.api_key = api_key
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })
        
        self.load_data()
        
    def load_data(self):
        """CSVファイルを読み込み"""
        try:
            self.df = pd.read_csv(self.csv_file, encoding='utf-8')
            
            # 全角スペースを半角スペースに置換
            self.df = self.clean_fullwidth_spaces(self.df)
            
            print(f"データ読み込み完了: {len(self.df)}件")
            print(f"列名: {list(self.df.columns)}")
        except Exception as e:
            print(f"エラー: {e}")
            return False
        return True
    
    def clean_fullwidth_spaces(self, df):
        """全角スペースを半角スペースに置換する関数"""
        print("全角スペースを半角スペースに置換中...")
        
        # 文字列型の列のみを対象とする
        string_columns = df.select_dtypes(include=['object']).columns
        
        # 全角スペース（\u3000）を半角スペース（\u0020）に置換
        for col in string_columns:
            if df[col].dtype == 'object':  # 文字列型の場合のみ
                # NaNを空文字列に変換
                df[col] = df[col].fillna('')
                # 全角スペースを半角スペースに置換
                df[col] = df[col].astype(str).str.replace('\u3000', '\u0020')
                # 連続する半角スペースを1つに統一（オプション）
                df[col] = df[col].str.replace(' +', ' ', regex=True)
                # 'nan'文字列を空文字列に変換
                df[col] = df[col].replace('nan', '')
        
        print("全角スペース置換完了")
        return df
    
    def step1_update_barcode_duplicates(self):
        """ステップ1: バーコード重複チェックを全レコードに反映"""
        print("\n=== ステップ1: バーコード重複チェック更新 ===")
        
        # バーコード列の重複をカウント
        barcode_counts = self.df['バーコード'].value_counts()
        
        # 各行のバーコード重複数を計算
        self.df['バーコード重複チェック'] = self.df['バーコード'].map(barcode_counts)
        
        # 空のバーコードは0に設定
        self.df.loc[self.df['バーコード'].isna(), 'バーコード重複チェック'] = 0
        
        print(f"バーコード重複チェック更新完了")
        print(f"重複件数分布:\n{self.df['バーコード重複チェック'].value_counts().sort_index()}")
        
        # 重複があるレコードを表示
        duplicates = self.df[self.df['バーコード重複チェック'] >= 2]
        if len(duplicates) > 0:
            print(f"\n重複バーコードを持つレコード ({len(duplicates)}件):")
            for _, row in duplicates.head(10).iterrows():
                print(f"  No.{row['No.']}: {row['ラベル']} (バーコード: {row['バーコード']}, 重複数: {row['バーコード重複チェック']})")
    
    def create_item_via_api(self, title, barcode=None, resource_template_id=None, resource_class_id=None):
        """Omeka S APIを使用してアイテムを作成"""
        if not self.api_key:
            print("APIキーが設定されていません")
            return None
            
        item_data = {
            "o:resource_template": {"o:id": resource_template_id},
            "o:resource_class": {"o:id": resource_class_id},
            "o:is_public": True,
            "dcterms:title": [{"@value": title, "type": "literal"}]
        }
        
        if barcode and pd.notna(barcode):
            item_data["ag:barcode"] = [{"@value": str(barcode), "type": "literal"}]
        
        try:
            response = self.session.post(f"{self.api_base_url}/items", json=item_data)
            response.raise_for_status()
            
            created_item = response.json()
            item_id = created_item.get('o:id')
            
            print(f"アイテム作成成功: ID {item_id} - {title}")
            return item_id
            
        except requests.exceptions.RequestException as e:
            print(f"APIエラー: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"レスポンス: {e.response.text}")
            return None
    
    def step2_create_tabletop_games_via_api(self):
        """ステップ2: テーブルトップゲームをAPIで登録"""
        print("\n=== ステップ2: テーブルトップゲームAPI登録 ===")
        
        if not self.api_key:
            print("APIキーが設定されていないため、CSVファイルのみ作成します")
            return self.step2_create_tabletop_games_csv()
        
        # 未登録で種別「テーブルトップゲーム」のレコードを抽出（バーコードの有無に関係なく）
        tabletop_games = self.df[
            (self.df['種別'] == 'テーブルトップゲーム') & 
            (self.df['インスタンスID - AGMサーチ'].isna())
        ].copy()
        
        print(f"テーブルトップゲーム未登録件数: {len(tabletop_games)}件")
        
        if len(tabletop_games) == 0:
            print("登録対象のテーブルトップゲームがありません")
            return None
        
        # 重複チェック情報を表示（過去データとの重複確認のみ）
        barcode_duplicates = tabletop_games[tabletop_games['バーコード重複チェック'] >= 2]
        if len(barcode_duplicates) > 0:
            print(f"過去データとの重複があるレコード: {len(barcode_duplicates)}件")
            for _, row in barcode_duplicates.head(5).iterrows():
                print(f"  No.{row['No.']}: {row['ラベル']} (バーコード: {row['バーコード']}, 重複数: {row['バーコード重複チェック']})")
        
        # APIで登録（重複削除は行わない）
        created_items = []
        failed_items = []
        
        # テーブルトップゲームのリソーステンプレートIDとクラスID（要確認）
        resource_template_id = 1  # テーブルトップゲームのテンプレートID
        resource_class_id = 1     # テーブルトップゲームのクラスID
        
        for _, row in tabletop_games.iterrows():
            item_id = self.create_item_via_api(
                title=row['ラベル'],
                barcode=row['バーコード'],
                resource_template_id=resource_template_id,
                resource_class_id=resource_class_id
            )
            
            if item_id:
                created_items.append({
                    'No.': row['No.'],
                    'ラベル': row['ラベル'],
                    'バーコード': row['バーコード'],
                    'インスタンスID - AGMサーチ': item_id
                })
                # 元のデータフレームも更新
                self.df.loc[self.df['No.'] == row['No.'], 'インスタンスID - AGMサーチ'] = item_id
            else:
                failed_items.append({
                    'No.': row['No.'],
                    'ラベル': row['ラベル'],
                    'バーコード': row['バーコード'],
                    'エラー': 'API登録失敗'
                })
            
            # APIレート制限を避けるため少し待機
            time.sleep(0.5)
        
        # 結果をCSVに出力
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # outputディレクトリが存在しない場合は作成
        os.makedirs('./output', exist_ok=True)
        
        if created_items:
            success_df = pd.DataFrame(created_items)
            success_filename = f'./output/tabletop_games_api_success_{timestamp}.csv'
            success_df.to_csv(success_filename, index=False, encoding='utf-8')
            print(f"成功したアイテム: {len(created_items)}件 -> {success_filename}")
        
        if failed_items:
            failed_df = pd.DataFrame(failed_items)
            failed_filename = f'./output/tabletop_games_api_failed_{timestamp}.csv'
            failed_df.to_csv(failed_filename, index=False, encoding='utf-8')
            print(f"失敗したアイテム: {len(failed_items)}件 -> {failed_filename}")
        
        # 更新されたデータを保存
        backup_filename = f'./output/agm_index_api_updated_{timestamp}.csv'
        self.df.to_csv(backup_filename, index=False, encoding='utf-8')
        print(f"更新済みデータ保存: {backup_filename}")
        
        return len(created_items), len(failed_items)
    
    def step2_create_tabletop_games_csv(self):
        """ステップ2: テーブルトップゲームのCSVデータを作成"""
        print("\n=== ステップ2: テーブルトップゲームCSV作成 ===")
        
        # 未登録で種別「テーブルトップゲーム」のレコードを抽出（バーコードの有無に関係なく）
        tabletop_games = self.df[
            (self.df['種別'] == 'テーブルトップゲーム') & 
            (self.df['インスタンスID - AGMサーチ'].isna())
        ].copy()
        
        print(f"テーブルトップゲーム未登録件数: {len(tabletop_games)}件")
        
        if len(tabletop_games) == 0:
            print("登録対象のテーブルトップゲームがありません")
            return None
        
        # 重複チェック情報を表示（過去データとの重複確認のみ）
        barcode_duplicates = tabletop_games[tabletop_games['バーコード重複チェック'] >= 2]
        if len(barcode_duplicates) > 0:
            print(f"過去データとの重複があるレコード: {len(barcode_duplicates)}件")
            for _, row in barcode_duplicates.head(5).iterrows():
                print(f"  No.{row['No.']}: {row['ラベル']} (バーコード: {row['バーコード']}, 重複数: {row['バーコード重複チェック']})")
        
        # 必要な列を抽出（元データのNo.を含める）
        export_df = tabletop_games[['No.', 'ラベル', 'バーコード']].copy()
        export_df.columns = ['dcterms:identifier', 'dcterms:title', 'ag:barcode']
        
        # バーコード列のNaNを空文字列に変換
        export_df['ag:barcode'] = export_df['ag:barcode'].fillna('')
        
        # 出力前に全角スペースを半角スペースに置換
        export_df = self.clean_fullwidth_spaces(export_df)
        
        # ファイル名を生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'./output/tabletop_games_export_{timestamp}.csv'
        
        # outputディレクトリが存在しない場合は作成
        os.makedirs('./output', exist_ok=True)
        
        # CSV出力
        export_df.to_csv(filename, index=False, encoding='utf-8')
        print(f"テーブルトップゲームCSV出力完了: {filename}")
        print(f"出力件数: {len(export_df)}件")
        print(f"元データNo.がdcterms:identifierとして含まれています")
        
        return filename, tabletop_games['No.'].tolist()
    
    def step3_create_books_csv(self):
        """ステップ3: 冊子のCSVデータを作成"""
        print("\n=== ステップ3: 冊子CSV作成 ===")
        
        # 未登録で種別「冊子」のレコードを抽出（バーコードの有無に関係なく）
        books = self.df[
            (self.df['種別'] == '冊子') & 
            (self.df['インスタンスID - AGMサーチ'].isna())
        ].copy()
        
        print(f"冊子未登録件数: {len(books)}件")
        
        if len(books) == 0:
            print("登録対象の冊子がありません")
            return None
        
        # 重複チェック情報を表示（過去データとの重複確認のみ）
        barcode_duplicates = books[books['バーコード重複チェック'] >= 2]
        if len(barcode_duplicates) > 0:
            print(f"過去データとの重複があるレコード: {len(barcode_duplicates)}件")
            for _, row in barcode_duplicates.head(5).iterrows():
                print(f"  No.{row['No.']}: {row['ラベル']} (バーコード: {row['バーコード']}, 重複数: {row['バーコード重複チェック']})")
        
        # 必要な列を抽出（元データのNo.を含める）
        export_df = books[['No.', 'ラベル', 'バーコード']].copy()
        export_df.columns = ['dcterms:identifier', 'dcterms:title', 'ag:barcode']
        
        # バーコード列のNaNを空文字列に変換
        export_df['ag:barcode'] = export_df['ag:barcode'].fillna('')
        
        # 出力前に全角スペースを半角スペースに置換
        export_df = self.clean_fullwidth_spaces(export_df)
        
        # ファイル名を生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'./output/books_export_{timestamp}.csv'
        
        # outputディレクトリが存在しない場合は作成
        os.makedirs('./output', exist_ok=True)
        
        # CSV出力
        export_df.to_csv(filename, index=False, encoding='utf-8')
        print(f"冊子CSV出力完了: {filename}")
        print(f"出力件数: {len(export_df)}件")
        print(f"元データNo.がdcterms:identifierとして含まれています")
        
        return filename, books['No.'].tolist()
    
    def step4_create_individual_items_csv(self):
        """ステップ4: 個別資料のCSVデータを作成"""
        print("\n=== ステップ4: 個別資料CSV作成 ===")
        
        # 個別資料IDが存在し、かつインスタンスIDが未登録のレコードを抽出
        individual_items = self.df[
            (self.df['個別資料ID'].notna()) & 
            (self.df['個別資料ID'] != '') &
            (self.df['インスタンスID - AGMサーチ'].isna())  # インスタンスIDが未登録
        ].copy()
        
        print(f"個別資料未登録件数: {len(individual_items)}件")
        
        if len(individual_items) == 0:
            print("登録対象の個別資料がありません")
            return None
        
        # 必要な列を抽出（元データのNo.を含める）
        export_df = individual_items[[
            'No.', '個別資料ID', '説明', '由来', '登録日', 'バーコード'
        ]].copy()
        
        # 列名をマッピング先に変更
        export_df.columns = [
            'dcterms:identifier', 'dcterms:title', 'ag:description', 'ag:provenance', 
            'ag:available', 'barcode'
        ]
        
        # ag:exemplarOfの値を決定
        exemplar_of_values = []
        
        for _, row in export_df.iterrows():
            barcode = row['barcode']
            
            if pd.notna(barcode) and barcode != '':
                # バーコードが存在する場合、同じバーコードを持つ過去のリソースのインスタンスIDを探す
                same_barcode_items = self.df[
                    (self.df['バーコード'] == barcode) & 
                    (self.df['インスタンスID - AGMサーチ'].notna()) &
                    (self.df['No.'] != row['dcterms:identifier'])  # 自分以外
                ]
                
                if len(same_barcode_items) > 0:
                    # 最初に見つかったインスタンスIDを使用
                    first_instance_id = same_barcode_items.iloc[0]['インスタンスID - AGMサーチ']
                    exemplar_of_values.append(str(int(float(first_instance_id))) if pd.notna(first_instance_id) else '')
                else:
                    exemplar_of_values.append('')
            else:
                exemplar_of_values.append('')
        
        # ag:exemplarOf列を追加
        export_df['ag:exemplarOf'] = exemplar_of_values
        
        # 不要な列を削除
        export_df = export_df.drop(['barcode'], axis=1)
        
        # 説明から重複に関する情報を削除
        export_df['ag:description'] = export_df['ag:description'].fillna('')
        
        # 由来列のNaNを空文字列に変換
        export_df['ag:provenance'] = export_df['ag:provenance'].fillna('')
        
        # ag:exemplarOfは空白のまま（インスタンスIDが未登録のため）
        
        # 個別資料識別子列を追加（dcterms:titleと同じ値）
        export_df['ag:identifier'] = export_df['dcterms:title']
        
        # 新規項目を追加
        export_df['ag:holdingAgent'] = '211'
        export_df['ag:isPartOf'] = '4886'
        
        # 出力前に全角スペースを半角スペースに置換
        export_df = self.clean_fullwidth_spaces(export_df)
        
        # ファイル名を生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'./output/individual_items_export_{timestamp}.csv'
        
        # outputディレクトリが存在しない場合は作成
        os.makedirs('./output', exist_ok=True)
        
        # CSV出力（数値を文字列として出力）
        export_df.to_csv(filename, index=False, encoding='utf-8', float_format='%.0f')
        print(f"個別資料CSV出力完了: {filename}")
        print(f"出力件数: {len(export_df)}件")
        print(f"元データNo.がdcterms:identifierとして含まれています")
        
        # ag:exemplarOfの統計を表示
        exemplar_of_filled = len([x for x in exemplar_of_values if x != ''])
        print(f"ag:exemplarOfが設定された件数: {exemplar_of_filled}件")
        print(f"ag:exemplarOfが空白の件数: {len(exemplar_of_values) - exemplar_of_filled}件")
        
        return filename
    
    def update_instance_ids(self, filename, instance_ids):
        """インスタンスIDを更新（CSVインポート後の処理）"""
        print(f"\n=== インスタンスID更新処理 ===")
        print(f"ファイル: {filename}")
        print(f"更新対象ID数: {len(instance_ids)}")
        
        # ここでは手動でインスタンスIDを入力する必要があります
        print("CSVインポート後、生成されたインスタンスIDを手動で入力してください")
        
        # 更新用のCSVファイルを作成
        update_df = self.df[self.df['No.'].isin(instance_ids)].copy()
        update_df = update_df[['No.', 'ラベル', 'バーコード']]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        update_filename = f'./output/instance_id_update_{timestamp}.csv'
        
        # outputディレクトリが存在しない場合は作成
        os.makedirs('./output', exist_ok=True)
        
        update_df.to_csv(update_filename, index=False, encoding='utf-8')
        
        print(f"更新用CSV作成: {update_filename}")
        print("このファイルにインスタンスIDを追加してから、update_instance_ids_from_csv()を実行してください")
    
    def update_instance_ids_from_csv(self, update_csv_file):
        """更新用CSVからインスタンスIDを反映"""
        print(f"\n=== インスタンスID反映処理 ===")
        
        try:
            update_df = pd.read_csv(update_csv_file, encoding='utf-8')
            
            # 元のデータフレームを更新
            for _, row in update_df.iterrows():
                if 'インスタンスID - AGMサーチ' in row and pd.notna(row['インスタンスID - AGMサーチ']):
                    self.df.loc[self.df['No.'] == row['No.'], 'インスタンスID - AGMサーチ'] = row['インスタンスID - AGMサーチ']
            
            print("インスタンスID更新完了")
            
            # 更新されたデータを保存
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'./output/agm_index_updated_{timestamp}.csv'
            
            # outputディレクトリが存在しない場合は作成
            os.makedirs('./output', exist_ok=True)
            
            self.df.to_csv(backup_filename, index=False, encoding='utf-8')
            print(f"更新済みデータ保存: {backup_filename}")
            
        except Exception as e:
            print(f"エラー: {e}")
    
    def run_full_process(self, use_api=False):
        """全処理を実行"""
        print("AGMインデックス処理開始")
        print("=" * 50)
        
        # ステップ1: バーコード重複チェック更新
        self.step1_update_barcode_duplicates()
        
        # ステップ2: テーブルトップゲーム処理
        if use_api and self.api_key:
            print("\nAPIを使用してテーブルトップゲームを登録します")
            tabletop_result = self.step2_create_tabletop_games_via_api()
        else:
            print("\nCSVファイルを作成します")
            tabletop_result = self.step2_create_tabletop_games_csv()
        
        # ステップ3: 冊子CSV作成
        books_result = self.step3_create_books_csv()
        
        # ステップ4: 個別資料CSV作成
        individual_result = self.step4_create_individual_items_csv()
        
        print("\n" + "=" * 50)
        print("処理完了")
        print("\n次の手順:")
        if use_api and self.api_key:
            print("1. API登録が完了しました")
        else:
            print("1. 生成されたCSVファイルをAGMサーチのCSVインポートで登録")
        print("2. インスタンスIDが生成されたら、update_instance_ids_from_csv()で反映")
        print("3. 検索可能にする設定をAGMサーチ管理画面で実行")
        print("4. JSON出力とLinked Data変換")
        print("5. SPARQLエンドポイント登録")
        print("6. GitHubへのデータセット登録")

def main():
    """メイン処理"""
    # APIキーを設定（必要に応じて）
    api_key = None  # 'your_api_key_here'
    api_base_url = 'https://id.analoggamemuseum.org/api'
    
    processor = AGMIndexProcessor(api_base_url=api_base_url, api_key=api_key)
    
    if processor.df is None:
        print("データ読み込みに失敗しました")
        return
    
    # APIを使用するかどうか
    use_api = api_key is not None
    
    # 全処理を実行
    processor.run_full_process(use_api=use_api)

if __name__ == "__main__":
    main()

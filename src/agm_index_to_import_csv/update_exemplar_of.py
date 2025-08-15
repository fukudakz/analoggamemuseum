#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
個別資料のag:exemplarOfを更新するスクリプト
JSONファイルから個別資料のIDを取得し、CSVファイルのag:exemplarOfを上書き
"""

import json
import pandas as pd
import os
from datetime import datetime

def load_omeka_items(json_file_path):
    """Omeka SのJSONファイルからアイテムデータを読み込み"""
    print(f"JSONファイルを読み込み中: {json_file_path}")
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # JSONファイルが配列形式の場合
        if isinstance(data, list):
            items = data
        else:
            # オブジェクト形式の場合（o:itemsプロパティを持つ）
            items = data.get('o:items', [])
        
        print(f"読み込み完了: {len(items)}件のアイテム")
        
        return items
        
    except Exception as e:
        print(f"JSONファイル読み込みエラー: {e}")
        return []

def extract_identifier_mapping(items):
    """dcterms:identifierとo:idのマッピングを作成"""
    print("dcterms:identifierとo:idのマッピングを作成中...")
    
    identifier_mapping = {}
    
    for item in items:
        item_id = item.get('o:id')
        
        # dcterms:identifierプロパティを検索
        for value in item.get('dcterms:identifier', []):
            if isinstance(value, dict) and '@value' in value:
                identifier = value['@value']
                identifier_mapping[identifier] = item_id
                print(f"マッピング: {identifier} -> {item_id}")
    
    print(f"マッピング作成完了: {len(identifier_mapping)}件")
    return identifier_mapping

def update_csv_exemplar_of(csv_file_path, identifier_mapping):
    """CSVファイルのag:exemplarOfを更新"""
    print(f"CSVファイルを読み込み中: {csv_file_path}")
    
    try:
        # CSVファイルを読み込み（数値列を文字列として読み込む）
        df = pd.read_csv(csv_file_path, encoding='utf-8', dtype={
            'dcterms:identifier': str,
            'ag:isPartOf': str,
            'ag:exemplarOf': str
        })
        print(f"読み込み完了: {len(df)}件のレコード")
        
        # 更新前の統計
        original_filled = len(df[df['ag:exemplarOf'] != ''])
        original_empty = len(df[df['ag:exemplarOf'] == ''])
        
        print(f"更新前 - ag:exemplarOf設定済み: {original_filled}件, 空白: {original_empty}件")
        
        # ag:exemplarOfを更新（既に値がある場合は上書きしない）
        updated_count = 0
        skipped_count = 0
        for index, row in df.iterrows():
            identifier = str(row['dcterms:identifier'])
            current_exemplar_of = str(row['ag:exemplarOf'])
            
            if identifier in identifier_mapping:
                new_exemplar_of = str(identifier_mapping[identifier])
                
                # 既にag:exemplarOfが設定されている場合はスキップ
                if current_exemplar_of != '' and current_exemplar_of != 'nan':
                    print(f"スキップ: No.{identifier} (既に設定済み: {current_exemplar_of})")
                    skipped_count += 1
                elif current_exemplar_of != new_exemplar_of:
                    df.at[index, 'ag:exemplarOf'] = new_exemplar_of
                    updated_count += 1
                    print(f"更新: No.{identifier} -> ag:exemplarOf: {new_exemplar_of}")
        
        # 更新後の統計
        updated_filled = len(df[df['ag:exemplarOf'] != ''])
        updated_empty = len(df[df['ag:exemplarOf'] == ''])
        
        print(f"更新後 - ag:exemplarOf設定済み: {updated_filled}件, 空白: {updated_empty}件")
        print(f"更新されたレコード数: {updated_count}件")
        print(f"スキップされたレコード数: {skipped_count}件")
        
        return df
        
    except Exception as e:
        print(f"CSVファイル読み込みエラー: {e}")
        return None

def save_updated_csv(df, original_csv_path):
    """更新されたCSVファイルを保存"""
    # 元のファイル名から新しいファイル名を生成
    base_name = os.path.splitext(os.path.basename(original_csv_path))[0]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f"./output/{base_name}_exemplar_updated_{timestamp}.csv"
    
    # outputディレクトリが存在しない場合は作成
    os.makedirs('./output', exist_ok=True)
    
    # CSVファイルを保存（数値を文字列として出力）
    df.to_csv(new_filename, index=False, encoding='utf-8', float_format='%.0f')
    print(f"更新されたCSVファイルを保存: {new_filename}")
    
    return new_filename

def main():
    """メイン処理"""
    # ファイルパス
    json_file_path = "/Users/fukudakazufumi/Library/CloudStorage/OneDrive-学校法人立命館/Codes/agm_index/source/id.analoggamemuseum.org-items-20250723-044532.json"
    csv_file_path = "./output/individual_items_export_20250723_131729.csv"
    
    print("=== 個別資料ag:exemplarOf更新処理開始 ===")
    print("=" * 50)
    
    # 1. JSONファイルからアイテムデータを読み込み
    items = load_omeka_items(json_file_path)
    if not items:
        print("JSONファイルの読み込みに失敗しました")
        return
    
    # 2. dcterms:identifierとo:idのマッピングを作成
    identifier_mapping = extract_identifier_mapping(items)
    if not identifier_mapping:
        print("マッピングの作成に失敗しました")
        return
    
    # 3. CSVファイルのag:exemplarOfを更新
    updated_df = update_csv_exemplar_of(csv_file_path, identifier_mapping)
    if updated_df is None:
        print("CSVファイルの更新に失敗しました")
        return
    
    # 4. 更新されたCSVファイルを保存
    new_csv_path = save_updated_csv(updated_df, csv_file_path)
    
    print("\n" + "=" * 50)
    print("処理完了")
    print(f"更新されたファイル: {new_csv_path}")
    
    # マッピングの詳細を表示
    print(f"\nマッピング詳細:")
    for identifier, item_id in identifier_mapping.items():
        print(f"  {identifier} -> {item_id}")

if __name__ == "__main__":
    main() 
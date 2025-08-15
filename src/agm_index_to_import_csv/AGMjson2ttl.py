#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGM JSON to TTL Converter
Omeka SからエクスポートしたJSONファイルをTTL形式に変換するスクリプト
"""

from rdflib import Graph, Namespace
import os
from datetime import datetime

def convert_json_to_ttl(json_file_path, output_dir="./output"):
    """
    JSONファイルをTTL形式に変換
    
    Args:
        json_file_path (str): 入力JSONファイルのパス
        output_dir (str): 出力ディレクトリ
    """
    
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs(output_dir, exist_ok=True)
    
    # GraphとNamespaceを初期化
    g = Graph()
    
    # 名前空間を定義
    AG = Namespace("https://www.analoggamemuseum.org/ontology/")
    O = Namespace("http://omeka.org/s/vocabs/o#")
    DCTERMS = Namespace("http://purl.org/dc/terms/")
    
    # 名前空間をバインド
    g.bind("ag", AG)
    g.bind("o", O)
    g.bind("dcterms", DCTERMS)
    
    print(f"JSONファイルを読み込み中: {json_file_path}")
    
    try:
        # JSON-LDファイルをパース
        g.parse(json_file_path, format='json-ld')
        print(f"読み込み完了: {len(g)} トリプル")
        
        # adminNoteを削除
        print("adminNoteを削除中...")
        removed_admin_note = g.remove((None, AG["adminNote"], None))
        print(f"削除されたadminNote: {len(removed_admin_note)} トリプル")
        
        # dcterms:identifierを削除
        print("dcterms:identifierを削除中...")
        removed_identifier = g.remove((None, DCTERMS["identifier"], None))
        print(f"削除されたdcterms:identifier: {len(removed_identifier)} トリプル")
        
        # 出力ファイル名を生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"agmsearch_{timestamp}.ttl"
        output_path = os.path.join(output_dir, output_filename)
        
        # TTLファイルに出力
        g.serialize(destination=output_path, format='turtle')
        print(f"TTLファイル出力完了: {output_path}")
        print(f"出力トリプル数: {len(g)}")
        
        return output_path
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

def main():
    """メイン処理"""
    # 入力ファイルパス
    json_file_path = "./source/id.analoggamemuseum.org-items-20250723-103551.json" #ここを公開用Turtleの変換対象にする
    
    print("=== AGM JSON to TTL Converter ===")
    print("=" * 40)
    
    # ファイルの存在確認
    if not os.path.exists(json_file_path):
        print(f"エラー: ファイルが見つかりません: {json_file_path}")
        return
    
    # 変換実行
    output_path = convert_json_to_ttl(json_file_path)
    
    if output_path:
        print("\n" + "=" * 40)
        print("変換完了!")
        print(f"出力ファイル: {output_path}")
    else:
        print("\n変換に失敗しました。")

if __name__ == "__main__":
    main() 
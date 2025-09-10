#!/usr/bin/env python3
"""
Supabase接続テストスクリプト
別のPCでSupabaseが動作しない問題を診断します
"""
import os
import sys
from dotenv import load_dotenv

def test_supabase_connection():
    print("=" * 60)
    print("Supabase接続テスト開始")
    print("=" * 60)
    
    # 1. 環境変数の読み込み
    print("\n1. 環境変数の読み込み...")
    load_dotenv()
    load_dotenv('.env.supabase')
    
    # 2. 環境変数の確認
    print("\n2. 環境変数の確認...")
    url = os.getenv('SUPABASE_URL')
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    use_supabase = os.getenv('USE_SUPABASE', 'false')
    
    print(f"   USE_SUPABASE: {use_supabase}")
    print(f"   SUPABASE_URL: {'設定済み' if url else '未設定'}")
    print(f"   SUPABASE_ANON_KEY: {'設定済み' if anon_key else '未設定'}")
    print(f"   SUPABASE_SERVICE_ROLE_KEY: {'設定済み' if service_key and service_key != 'your-service-role-key' else '未設定'}")
    
    if use_supabase.lower() != 'true':
        print("\n⚠️ USE_SUPABASEがtrueに設定されていません")
        print("   SQLiteモードで動作します")
        return False
    
    # 3. Supabaseパッケージの確認
    print("\n3. Supabaseパッケージの確認...")
    try:
        from supabase import create_client, Client
        print("   ✅ supabaseパッケージがインストールされています")
    except ImportError as e:
        print(f"   ❌ supabaseパッケージがインストールされていません")
        print(f"   エラー: {e}")
        print("\n   以下のコマンドでインストールしてください:")
        print("   pip install supabase==2.0.3")
        return False
    
    # 4. Supabase接続テスト
    print("\n4. Supabase接続テスト...")
    
    if not url or not anon_key:
        print("   ❌ Supabase URLまたはキーが設定されていません")
        print("\n   .envファイルに以下を設定してください:")
        print("   SUPABASE_URL=https://your-project.supabase.co")
        print("   SUPABASE_ANON_KEY=your-anon-key")
        return False
    
    try:
        # サービスキーがあればそれを使用、なければAnonキーを使用
        key = service_key if service_key and service_key != 'your-service-role-key' else anon_key
        client = create_client(url, key)
        print("   ✅ Supabaseクライアントの作成に成功しました")
        
        # テーブルへの接続テスト
        print("\n5. テーブル接続テスト...")
        try:
            # device_attributesテーブルの存在確認
            response = client.table('device_attributes').select('id').limit(1).execute()
            print("   ✅ device_attributesテーブルに接続できました")
        except Exception as e:
            print(f"   ⚠️ device_attributesテーブルへの接続に失敗しました")
            print(f"   エラー: {e}")
            print("\n   テーブルが作成されていない可能性があります")
            print("   create_supabase_tables.pyを実行してテーブルを作成してください")
            return False
            
        print("\n✅ Supabase接続テスト成功！")
        return True
        
    except Exception as e:
        print(f"   ❌ Supabaseクライアントの作成に失敗しました")
        print(f"   エラー: {e}")
        print("\n   考えられる原因:")
        print("   1. URLまたはキーが正しくない")
        print("   2. ネットワーク接続の問題")
        print("   3. Supabaseプロジェクトが停止している")
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Supabaseを使用する準備ができています")
    else:
        print("❌ Supabaseの設定に問題があります")
        print("\n代替案: SQLiteモードで動作させる")
        print("USE_SUPABASE=false を.envファイルに設定してください")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
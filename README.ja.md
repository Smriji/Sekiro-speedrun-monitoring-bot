# Sekiro-speedrun-monitoring-bot
SEKIRO の Speedrun.com における世界記録（WR）の更新を監視し、Discord へ通知する Bot です。Google Cloud Run Jobs での動作を前提としており、記録の状態管理には Google Cloud Storage (GCS) を使用します。

## 主な機能
- **自動監視**: Speedrun.com API から最近承認（Verify）された記録を取得します。
- **サブカテゴリ対応**: ハードウェア（PC/コンソール）や独自のサブカテゴリ変数を識別して比較します。
- **サーバーレス運用**: Cloud Run Jobs を利用し、実行時のみリソースを消費するため低コストです。
- **状態の永続化**: GCS 上の `wr_list.json` に現在の記録を保持し、次回の実行時と比較します。

## 準備するもの
- Cloud Run と Cloud Storage が有効化された Google Cloud プロジェクト。
- Discord の Webhook URL。
- 監視対象を定義した `subcategories.json`（コンテナに同梱する必要があります）。

## 設定項目
### 環境変数
|Variable|Description|
|----|----|
|BUCKET_NAME|`wr_list.json` を保存する GCS バケット名|
|DISCORD_WEBHOOK_URL|通知先の Discord Webhook URL|

### 設定ファイル
- `subcategories.json`: 監視したいカテゴリー ID や変数 ID を記述します。スクリプトが GCS 上に WR リストを持っていない場合の初期化に使用されます。

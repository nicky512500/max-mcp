# MAX Exchange MCP Server

透過 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 將 MAX 交易所 API 整合至 Claude 等 AI 助理，讓 AI 可以直接查詢行情、管理帳戶、下單交易。

## 前置需求

- Python 3.11+
- MAX 交易所帳號與 API 金鑰（[前往申請](https://max.maicoin.com/api_tokens)）

## 安裝與啟動

### 方法一：直接使用 uvx（推薦）

無需手動安裝，直接從 GitHub 執行：

```bash
uvx --from git+https://github.com/nicky512500/max-mcp maxmcp
```

### 方法二：本地安裝

```bash
git clone https://github.com/nicky512500/max-mcp
cd max-mcp
pip install -e .
maxmcp
```

## 環境變數設定

需提供 MAX API 金鑰，支援兩種方式：

**方式一：`.env` 檔**（建議）

在專案根目錄建立 `.env`：

```
MAX_API_KEY=your_access_key
MAX_API_SECRET=your_secret_key
```

**方式二：系統環境變數**

```bash
export MAX_API_KEY=your_access_key
export MAX_API_SECRET=your_secret_key
```

> 公開查詢功能（行情、K線等）不需要 API 金鑰。

## 在 Claude Desktop 中使用

編輯 Claude Desktop 設定檔（`~/Library/Application Support/Claude/claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "max-exchange": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/nicky512500/max-mcp", "maxmcp"],
      "env": {
        "MAX_API_KEY": "your_access_key",
        "MAX_API_SECRET": "your_secret_key"
      }
    }
  }
}
```

重新啟動 Claude Desktop 後即可使用。

## 在 Claude Code 中使用

```bash
claude mcp add max-exchange -- uvx --from git+https://github.com/nicky512500/max-mcp maxmcp
```

---

## 可用功能一覽

### 公開資訊（無需 API 金鑰）

| 工具 | 說明 |
|------|------|
| `get_markets` | 取得所有可用交易市場列表 |
| `get_currencies` | 取得所有可用貨幣列表 |
| `get_timestamp` | 取得 MAX 伺服器目前時間 |
| `get_ticker` | 取得單一市場即時行情（最新價、買賣一口價、24h 量） |
| `get_tickers` | 取得多個市場即時行情（可一次查詢多個） |
| `get_depth` | 取得市場深度（掛單簿），最多 300 筆 |
| `get_public_trades` | 取得市場最近公開成交記錄 |
| `get_k` | 取得 K 線（蠟燭圖）資料，支援多種週期 |

**K 線週期（分鐘）**：`1 / 5 / 15 / 30 / 60 / 120 / 240 / 360 / 720 / 1440`

### M 錢包公開資訊（無需 API 金鑰）

| 工具 | 說明 |
|------|------|
| `get_m_index_prices` | 取得 M 錢包各幣種指數價格 |
| `get_m_limits` | 取得 M 錢包可用借貸額度上限 |
| `get_m_interest_rates` | 取得 M 錢包各幣種借貸利率 |

### 帳戶管理（需 API 金鑰）

| 工具 | 說明 |
|------|------|
| `get_user_info` | 取得帳戶資訊（KYC 狀態、帳號 ID 等） |
| `get_accounts` | 取得帳戶各幣種餘額（現貨或 M 錢包） |
| `get_deposit_address` | 取得指定幣種的充值地址 |
| `get_withdraw_addresses` | 取得已綁定的提現地址列表 |

### 訂單管理（需 API 金鑰）

| 工具 | 說明 |
|------|------|
| `submit_order` | 提交買賣訂單 |
| `get_open_orders` | 取得目前未成交的掛單列表 |
| `get_closed_orders` | 取得已關閉的訂單（已成交、已取消等） |
| `get_orders_history` | 依 ID 順序分頁取得訂單歷史 |
| `get_order` | 查詢單筆訂單詳情 |
| `cancel_order` | 取消單筆掛單 |
| `cancel_orders` | 批次取消某市場的掛單 |

**訂單類型（`ord_type`）**：`limit / market / stop_limit / stop_market / post_only / ioc_limit`

### 成交記錄（需 API 金鑰）

| 工具 | 說明 |
|------|------|
| `get_trades` | 取得個人歷史成交記錄 |
| `get_order_trades` | 取得特定訂單的所有成交明細 |

### 閃兌（需 API 金鑰）

| 工具 | 說明 |
|------|------|
| `submit_convert` | 執行幣種閃兌（即時換匯） |
| `get_convert` | 查詢單筆閃兌詳情 |
| `get_converts` | 取得閃兌歷史記錄 |

### 存提款（需 API 金鑰）

| 工具 | 說明 |
|------|------|
| `submit_withdrawal` | 提交加密貨幣提現申請 |
| `submit_twd_withdrawal` | 提交台幣（TWD）出金申請 |
| `get_withdrawal` | 查詢單筆提現詳情 |
| `get_withdrawals` | 取得提現歷史記錄 |
| `get_deposit` | 查詢單筆存款詳情 |
| `get_deposits` | 取得存款歷史記錄 |
| `get_internal_transfers` | 取得平台內部轉帳記錄（MAX 用戶間互轉） |
| `get_rewards` | 取得獎勵記錄（返傭、空投、利息獎勵等） |

### M 錢包（需 API 金鑰）

| 工具 | 說明 |
|------|------|
| `get_m_ad_ratio` | 取得 M 錢包 AD 比率（資產 / 借貸），低於門檻會觸發清算 |
| `submit_m_loan` | 向 M 錢包申請借貸 |
| `get_m_loans` | 取得 M 錢包借貸歷史記錄 |
| `submit_m_transfer` | 在現貨錢包與 M 錢包之間轉移資金 |
| `get_m_transfers` | 取得 M 錢包資金轉移記錄 |
| `submit_m_repayment` | 向 M 錢包還款 |
| `get_m_repayments` | 取得 M 錢包還款歷史記錄 |
| `get_m_liquidations` | 取得 M 錢包清算歷史記錄 |
| `get_m_liquidation` | 取得單筆 M 錢包清算詳情 |
| `get_m_interests` | 取得 M 錢包利息計費歷史記錄 |

---

## 使用範例

在 Claude 中直接用自然語言提問：

```
查詢 BTC/USDT 目前的價格
```

```
幫我看一下我的現貨帳戶餘額
```

```
查詢 btcusdt 最近 10 根 1 小時 K 線
```

```
幫我在 btcusdt 以限價 90000 掛買單 0.001 BTC
```

```
取消 btcusdt 所有未成交的買單
```

## 注意事項

- 提現、下單等操作為不可逆動作，請確認參數後再執行
- API 金鑰請妥善保管，不要提交至版本控制
- M 錢包涉及槓桿借貸，請確認 AD 比率以避免清算風險

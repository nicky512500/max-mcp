"""
MAX Exchange MCP Server
使用方式：
  uvx --from git+https://github.com/YOUR_GITHUB/max-mcp maxmcp

需要設定環境變數（或 .env 檔）：
  MAX_API_KEY=your_access_key
  MAX_API_SECRET=your_secret_key
"""

import json
import os
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from max_mcp.api import MaxAPI

load_dotenv()

api = MaxAPI(
    access_key=os.getenv("MAX_API_KEY", ""),
    secret_key=os.getenv("MAX_API_SECRET", ""),
)

mcp = FastMCP("MAX Exchange")


def _json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


# =============================================================================
# 公開端點
# =============================================================================


@mcp.tool()
def get_markets() -> str:
    """取得 MAX 所有可用交易市場列表"""
    return _json(api.get_markets())


@mcp.tool()
def get_currencies() -> str:
    """取得 MAX 所有可用貨幣列表"""
    return _json(api.get_currencies())


@mcp.tool()
def get_timestamp() -> str:
    """取得 MAX 伺服器目前時間（Unix 時間戳，秒）"""
    return _json(api.get_timestamp())


@mcp.tool()
def get_ticker(market: str) -> str:
    """
    取得單一市場即時行情（最新成交價、買賣一口價、24h 成交量等）
    :param market: 市場 ID，例如 'btcusdt'、'ethusdt'
    """
    return _json(api.get_ticker(market))


@mcp.tool()
def get_tickers(markets: Optional[str] = None) -> str:
    """
    取得多個市場即時行情，可一次查詢多個
    :param markets: 逗號分隔的市場 ID，例如 'btcusdt,ethusdt'；留空回傳全部
    """
    market_list = [m.strip() for m in markets.split(",")] if markets else None
    return _json(api.get_tickers(market_list))


@mcp.tool()
def get_depth(market: str, limit: int = 20) -> str:
    """
    取得市場深度（掛單簿），顯示買賣雙方的掛單價格與數量
    :param market: 市場 ID，例如 'btcusdt'
    :param limit: 回傳筆數，最多 300，預設 20
    """
    return _json(api.get_depth(market, limit=limit))


@mcp.tool()
def get_public_trades(market: str, limit: int = 30) -> str:
    """
    取得市場最近公開成交記錄（無需登入）
    :param market: 市場 ID，例如 'btcusdt'
    :param limit: 回傳筆數，預設 30
    """
    return _json(api.get_public_trades(market, limit=limit))


@mcp.tool()
def get_k(market: str, period: int = 1, limit: int = 30) -> str:
    """
    取得市場 K 線（蠟燭圖）資料
    :param market: 市場 ID，例如 'btcusdt'
    :param period: K 線週期（分鐘），可選 1/5/15/30/60/120/240/360/720/1440，預設 1
    :param limit: 回傳筆數，最多 10000，預設 30
    """
    return _json(api.get_k(market, period=period, limit=limit))


# =============================================================================
# 公開 M 錢包端點
# =============================================================================


@mcp.tool()
def get_m_index_prices() -> str:
    """取得 M 錢包各幣種指數價格"""
    return _json(api.get_m_index_prices())


@mcp.tool()
def get_m_limits() -> str:
    """取得 M 錢包目前可用借貸額度上限"""
    return _json(api.get_m_limits())


@mcp.tool()
def get_m_interest_rates() -> str:
    """取得 M 錢包各幣種目前借貸利率"""
    return _json(api.get_m_interest_rates())


# =============================================================================
# 用戶端點（需認證）
# =============================================================================


@mcp.tool()
def get_user_info() -> str:
    """取得目前登入帳戶的用戶資訊（KYC 狀態、帳號 ID 等）"""
    return _json(api.get_user_info())


# =============================================================================
# 帳戶 / 錢包端點（需認證）
# =============================================================================


@mcp.tool()
def get_accounts(wallet_type: str = "spot", currency: Optional[str] = None) -> str:
    """
    取得帳戶各幣種餘額
    :param wallet_type: 錢包類型，'spot'（現貨）或 'm'（M 錢包），預設 'spot'
    :param currency: 只查特定幣種，例如 'btc'；留空查全部
    """
    return _json(api.get_accounts(wallet_type=wallet_type, currency=currency))


@mcp.tool()
def get_deposit_address(currency_version: str) -> str:
    """
    取得指定幣種的充值地址
    :param currency_version: 幣種版本，例如 'eth'、'trc20usdt'、'erc20usdt'
    """
    return _json(api.get_deposit_address(currency_version))


@mcp.tool()
def get_withdraw_addresses(currency: Optional[str] = None) -> str:
    """
    取得已綁定的提現地址列表
    :param currency: 篩選特定幣種，例如 'btc'；留空查全部
    """
    return _json(api.get_withdraw_addresses(currency=currency))


# =============================================================================
# M 錢包私有端點（需認證）
# =============================================================================


@mcp.tool()
def get_m_ad_ratio() -> str:
    """取得 M 錢包目前 AD 比率（資產 / 借貸），低於門檻會觸發清算"""
    return _json(api.get_m_ad_ratio())


@mcp.tool()
def submit_m_loan(currency: str, amount: str) -> str:
    """
    向 M 錢包申請借貸
    :param currency: 借貸幣種，例如 'usdt'、'btc'
    :param amount: 借貸金額（字串），例如 '1000'
    """
    return _json(api.submit_m_loan(currency, amount))


@mcp.tool()
def get_m_loans(currency: Optional[str] = None, limit: int = 50, page: int = 1) -> str:
    """
    取得 M 錢包借貸歷史記錄
    :param currency: 篩選幣種；留空查全部
    :param limit: 每頁筆數，預設 50
    :param page: 頁碼，預設 1
    """
    return _json(api.get_m_loans(currency=currency, limit=limit, page=page))


@mcp.tool()
def submit_m_transfer(currency: str, amount: str, side: str) -> str:
    """
    在現貨錢包與 M 錢包之間轉移資金
    :param currency: 幣種，例如 'usdt'
    :param amount: 金額（字串），例如 '500'
    :param side: 方向，'in' = 轉入 M 錢包，'out' = 從 M 錢包轉出
    """
    return _json(api.submit_m_transfer(currency, amount, side))


@mcp.tool()
def get_m_transfers(currency: Optional[str] = None, limit: int = 50, page: int = 1) -> str:
    """
    取得 M 錢包資金轉移記錄
    :param currency: 篩選幣種；留空查全部
    :param limit: 每頁筆數，預設 50
    :param page: 頁碼，預設 1
    """
    return _json(api.get_m_transfers(currency=currency, limit=limit, page=page))


@mcp.tool()
def submit_m_repayment(currency: str, amount: str) -> str:
    """
    向 M 錢包還款
    :param currency: 還款幣種，例如 'usdt'
    :param amount: 還款金額（字串），例如 '1000'
    """
    return _json(api.submit_m_repayment(currency, amount))


@mcp.tool()
def get_m_repayments(currency: Optional[str] = None, limit: int = 50, page: int = 1) -> str:
    """
    取得 M 錢包還款歷史記錄
    :param currency: 篩選幣種；留空查全部
    :param limit: 每頁筆數，預設 50
    :param page: 頁碼，預設 1
    """
    return _json(api.get_m_repayments(currency=currency, limit=limit, page=page))


@mcp.tool()
def get_m_liquidations(limit: int = 50, page: int = 1) -> str:
    """
    取得 M 錢包清算歷史記錄
    :param limit: 每頁筆數，預設 50
    :param page: 頁碼，預設 1
    """
    return _json(api.get_m_liquidations(limit=limit, page=page))


@mcp.tool()
def get_m_liquidation(sn: str) -> str:
    """
    取得單筆 M 錢包清算詳情
    :param sn: 清算序號
    """
    return _json(api.get_m_liquidation(sn))


@mcp.tool()
def get_m_interests(currency: Optional[str] = None, limit: int = 50, page: int = 1) -> str:
    """
    取得 M 錢包利息計費歷史記錄
    :param currency: 篩選幣種；留空查全部
    :param limit: 每頁筆數，預設 50
    :param page: 頁碼，預設 1
    """
    return _json(api.get_m_interests(currency=currency, limit=limit, page=page))


# =============================================================================
# 訂單端點（需認證）
# =============================================================================


@mcp.tool()
def submit_order(
    market: str,
    side: str,
    volume: str,
    price: Optional[str] = None,
    ord_type: str = "limit",
    wallet_type: str = "spot",
    stop_price: Optional[str] = None,
    client_oid: Optional[str] = None,
) -> str:
    """
    提交買賣訂單
    :param market: 市場 ID，例如 'btcusdt'
    :param side: 方向，'buy' 或 'sell'
    :param volume: 交易數量（字串），例如 '0.001'
    :param price: 限價（字串），市價單可省略
    :param ord_type: 訂單類型，limit / market / stop_limit / stop_market / post_only / ioc_limit，預設 limit
    :param wallet_type: 錢包類型，'spot' 或 'm'，預設 'spot'
    :param stop_price: 止損觸發價，stop 系列訂單需填
    :param client_oid: 自訂訂單 ID（最長 36 字元）
    """
    return _json(
        api.submit_order(
            wallet_type=wallet_type,
            market=market,
            side=side,
            volume=volume,
            price=price,
            ord_type=ord_type,
            stop_price=stop_price,
            client_oid=client_oid,
        )
    )


@mcp.tool()
def get_open_orders(
    wallet_type: str = "spot",
    market: Optional[str] = None,
    limit: int = 50,
) -> str:
    """
    取得目前未成交的掛單列表
    :param wallet_type: 錢包類型，'spot' 或 'm'，預設 'spot'
    :param market: 篩選市場，例如 'btcusdt'；留空查全部
    :param limit: 回傳筆數，最多 1000，預設 50
    """
    return _json(api.get_open_orders(wallet_type=wallet_type, market=market, limit=limit))


@mcp.tool()
def get_closed_orders(
    wallet_type: str = "spot",
    market: Optional[str] = None,
    limit: int = 50,
    state: Optional[str] = None,
) -> str:
    """
    取得已關閉的訂單（已成交、已取消等）
    :param wallet_type: 錢包類型，'spot' 或 'm'，預設 'spot'
    :param market: 篩選市場；留空查全部
    :param limit: 回傳筆數，最多 1000，預設 50
    :param state: 狀態篩選，done / cancel / finalizing / failed；留空查全部
    """
    return _json(
        api.get_closed_orders(
            wallet_type=wallet_type, market=market, limit=limit, state=state
        )
    )


@mcp.tool()
def get_orders_history(
    market: str,
    wallet_type: str = "spot",
    from_id: Optional[int] = None,
    limit: int = 50,
) -> str:
    """
    依 ID 順序分頁取得訂單歷史（適合完整匯出）
    :param market: 市場 ID（必填），例如 'btcusdt'
    :param wallet_type: 錢包類型，'spot' 或 'm'，預設 'spot'
    :param from_id: 從指定訂單 ID 開始（用於翻頁）
    :param limit: 回傳筆數，預設 50
    """
    return _json(
        api.get_orders_history(
            market=market, wallet_type=wallet_type, from_id=from_id, limit=limit
        )
    )


@mcp.tool()
def get_order(order_id: Optional[int] = None, client_oid: Optional[str] = None) -> str:
    """
    查詢單筆訂單詳情
    :param order_id: 訂單 ID（與 client_oid 擇一）
    :param client_oid: 自訂訂單 ID（與 order_id 擇一）
    """
    return _json(api.get_order(order_id=order_id, client_oid=client_oid))


@mcp.tool()
def cancel_order(order_id: Optional[int] = None, client_oid: Optional[str] = None) -> str:
    """
    取消單筆掛單
    :param order_id: 訂單 ID（與 client_oid 擇一）
    :param client_oid: 自訂訂單 ID（與 order_id 擇一）
    """
    return _json(api.cancel_order(order_id=order_id, client_oid=client_oid))


@mcp.tool()
def cancel_orders(
    market: str,
    wallet_type: str = "spot",
    side: Optional[str] = None,
) -> str:
    """
    批次取消某市場的掛單
    :param market: 市場 ID（必填），例如 'btcusdt'
    :param wallet_type: 錢包類型，'spot' 或 'm'，預設 'spot'
    :param side: 只取消特定方向，'buy' 或 'sell'；留空取消雙向
    """
    return _json(api.cancel_orders(wallet_type=wallet_type, market=market, side=side))


# =============================================================================
# 成交記錄端點（需認證）
# =============================================================================


@mcp.tool()
def get_trades(
    wallet_type: str = "spot",
    market: Optional[str] = None,
    limit: int = 50,
) -> str:
    """
    取得個人歷史成交記錄
    :param wallet_type: 錢包類型，'spot' 或 'm'，預設 'spot'
    :param market: 篩選市場；留空查全部
    :param limit: 回傳筆數，預設 50
    """
    return _json(api.get_trades(wallet_type=wallet_type, market=market, limit=limit))


@mcp.tool()
def get_order_trades(order_id: Optional[int] = None, client_oid: Optional[str] = None) -> str:
    """
    取得特定訂單的所有成交明細
    :param order_id: 訂單 ID（與 client_oid 擇一）
    :param client_oid: 自訂訂單 ID（與 order_id 擇一）
    """
    return _json(api.get_order_trades(order_id=order_id, client_oid=client_oid))


# =============================================================================
# 兌換端點（需認證）
# =============================================================================


@mcp.tool()
def submit_convert(
    from_currency: str,
    to_currency: str,
    from_amount: Optional[str] = None,
    to_amount: Optional[str] = None,
) -> str:
    """
    執行幣種閃兌（即時換匯）
    :param from_currency: 賣出幣種，例如 'usdt'
    :param to_currency: 買入幣種，例如 'btc'
    :param from_amount: 賣出金額（與 to_amount 二擇一），例如 '1000'
    :param to_amount: 買入金額（與 from_amount 二擇一），例如 '0.01'
    """
    return _json(
        api.submit_convert(
            from_currency, to_currency, from_amount=from_amount, to_amount=to_amount
        )
    )


@mcp.tool()
def get_convert(uuid: str) -> str:
    """
    查詢單筆閃兌詳情
    :param uuid: 兌換單 UUID
    """
    return _json(api.get_convert(uuid))


@mcp.tool()
def get_converts(limit: int = 50, page: int = 1) -> str:
    """
    取得閃兌歷史記錄
    :param limit: 每頁筆數，預設 50
    :param page: 頁碼，預設 1
    """
    return _json(api.get_converts(limit=limit, page=page))


# =============================================================================
# 交易記錄端點（需認證）
# =============================================================================


@mcp.tool()
def submit_withdrawal(withdraw_address_uuid: str, amount: str) -> str:
    """
    提交加密貨幣提現申請
    :param withdraw_address_uuid: 提現地址 UUID（先用 get_withdraw_addresses 取得）
    :param amount: 提現金額（字串），例如 '100'
    """
    return _json(api.submit_withdrawal(withdraw_address_uuid, amount))


@mcp.tool()
def submit_twd_withdrawal(amount: str) -> str:
    """
    提交台幣（TWD）出金申請
    :param amount: 出金金額（字串），例如 '10000'
    """
    return _json(api.submit_twd_withdrawal(amount))


@mcp.tool()
def get_withdrawal(uuid: str) -> str:
    """
    查詢單筆提現詳情
    :param uuid: 提現 UUID
    """
    return _json(api.get_withdrawal(uuid))


@mcp.tool()
def get_withdrawals(
    currency: Optional[str] = None,
    limit: int = 50,
    page: int = 1,
    state: Optional[str] = None,
) -> str:
    """
    取得提現歷史記錄
    :param currency: 篩選幣種；留空查全部
    :param limit: 每頁筆數，預設 50
    :param page: 頁碼，預設 1
    :param state: 狀態篩選；留空查全部
    """
    return _json(api.get_withdrawals(currency=currency, limit=limit, page=page, state=state))


@mcp.tool()
def get_deposit(uuid: str) -> str:
    """
    查詢單筆存款詳情
    :param uuid: 存款 UUID
    """
    return _json(api.get_deposit(uuid))


@mcp.tool()
def get_deposits(
    currency: Optional[str] = None,
    limit: int = 50,
    page: int = 1,
    state: Optional[str] = None,
) -> str:
    """
    取得存款歷史記錄
    :param currency: 篩選幣種；留空查全部
    :param limit: 每頁筆數，預設 50
    :param page: 頁碼，預設 1
    :param state: 狀態篩選；留空查全部
    """
    return _json(api.get_deposits(currency=currency, limit=limit, page=page, state=state))


@mcp.tool()
def get_internal_transfers(
    currency: Optional[str] = None,
    limit: int = 50,
    page: int = 1,
    side: Optional[str] = None,
) -> str:
    """
    取得平台內部轉帳記錄（MAX 用戶間互轉）
    :param currency: 篩選幣種；留空查全部
    :param limit: 每頁筆數，預設 50
    :param page: 頁碼，預設 1
    :param side: 'in'（收款）或 'out'（付款）；留空查全部
    """
    return _json(
        api.get_internal_transfers(currency=currency, limit=limit, page=page, side=side)
    )


@mcp.tool()
def get_rewards(
    reward_type: Optional[str] = None,
    currency: Optional[str] = None,
    limit: int = 50,
    page: int = 1,
) -> str:
    """
    取得獎勵記錄（返傭、空投、利息獎勵等）
    :param reward_type: 獎勵類型篩選；留空查全部
    :param currency: 篩選幣種；留空查全部
    :param limit: 每頁筆數，預設 50
    :param page: 頁碼，預設 1
    """
    return _json(
        api.get_rewards(reward_type=reward_type, currency=currency, limit=limit, page=page)
    )


# =============================================================================
# 啟動
# =============================================================================

def main():
    mcp.run()


if __name__ == "__main__":
    main()

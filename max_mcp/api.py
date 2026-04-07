"""
MAX Exchange V3 API Client
用途：封裝所有 MAX V3 REST API，供 MCP 工具使用
"""

import hashlib
import hmac
import json
import time
import base64
from typing import Optional
import httpx

BASE_URL = "https://max-api.maicoin.com"


class MaxAPI:
    def __init__(self, access_key: str = "", secret_key: str = ""):
        self.access_key = access_key
        self.secret_key = secret_key
        self.client = httpx.Client(base_url=BASE_URL, timeout=30)

    # -------------------------------------------------------------------------
    # 認證簽名
    # -------------------------------------------------------------------------

    def _make_payload(self, path: str, data: dict, nonce: int) -> str:
        """產生已排序並 base64 編碼的 payload 字串"""
        payload = {"path": path, "nonce": nonce, **data}
        sorted_payload = dict(sorted(payload.items()))
        return base64.b64encode(
            json.dumps(sorted_payload, separators=(",", ":")).encode()
        ).decode()

    def _sign(self, encoded: str) -> str:
        return hmac.new(
            self.secret_key.encode(), encoded.encode(), hashlib.sha256
        ).hexdigest()

    def _auth_headers(self, encoded: str) -> dict:
        return {
            "X-MAX-ACCESSKEY": self.access_key,
            "X-MAX-PAYLOAD": encoded,
            "X-MAX-SIGNATURE": self._sign(encoded),
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: dict = None) -> dict:
        resp = self.client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    def _auth_get(self, path: str, params: dict = None) -> dict:
        nonce = int(time.time() * 1000)
        data = params or {}
        encoded = self._make_payload(path, data, nonce)
        # GET 請求須將 nonce 加入 query string
        query = {**(params or {}), "nonce": nonce}
        resp = self.client.get(path, params=query, headers=self._auth_headers(encoded))
        resp.raise_for_status()
        return resp.json()

    def _auth_post(self, path: str, body: dict) -> dict:
        nonce = int(time.time() * 1000)
        encoded = self._make_payload(path, body, nonce)
        resp = self.client.post(
            path, json={**body, "nonce": nonce}, headers=self._auth_headers(encoded)
        )
        resp.raise_for_status()
        return resp.json()

    def _auth_delete(self, path: str, body: dict) -> dict:
        nonce = int(time.time() * 1000)
        encoded = self._make_payload(path, body, nonce)
        resp = self.client.request(
            "DELETE", path, json={**body, "nonce": nonce}, headers=self._auth_headers(encoded)
        )
        resp.raise_for_status()
        return resp.json()

    # =========================================================================
    # 公開端點 (Public) — 無需認證
    # =========================================================================

    def get_markets(self) -> list:
        """取得所有可用交易市場"""
        return self._get("/api/v3/markets")

    def get_currencies(self) -> list:
        """取得所有可用貨幣"""
        return self._get("/api/v3/currencies")

    def get_timestamp(self) -> dict:
        """取得伺服器時間（Unix 時間戳，秒）"""
        return self._get("/api/v3/timestamp")

    def get_ticker(self, market: str) -> dict:
        """
        取得單一市場行情
        :param market: 市場 ID，例如 'btcusdt'
        """
        return self._get("/api/v3/ticker", params={"market": market})

    def get_tickers(self, markets: Optional[list[str]] = None) -> list:
        """
        取得多個市場行情
        :param markets: 市場 ID 列表；為 None 時回傳全部
        """
        params = {}
        if markets:
            params["markets[]"] = markets
        return self._get("/api/v3/tickers", params=params)

    def get_depth(
        self,
        market: str,
        limit: int = 300,
        sort_by_price: bool = True,
    ) -> dict:
        """
        取得市場深度（掛單簿）
        :param market: 市場 ID
        :param limit: 回傳筆數，1–300，預設 300
        :param sort_by_price: 是否依價格排序，預設 True
        """
        return self._get(
            "/api/v3/depth",
            params={
                "market": market,
                "limit": limit,
                "sort_by_price": str(sort_by_price).lower(),
            },
        )

    def get_public_trades(
        self,
        market: str,
        limit: int = 50,
        timestamp: Optional[int] = None,
        order_by: str = "desc",
    ) -> list:
        """
        取得市場最近成交記錄（公開，無需認證）
        :param market: 市場 ID
        :param limit: 回傳筆數
        :param timestamp: Unix 時間戳（毫秒），篩選起始時間
        :param order_by: 排序方式 asc / desc
        """
        params: dict = {"market": market, "limit": limit, "order_by": order_by}
        if timestamp is not None:
            params["timestamp"] = timestamp
        return self._get("/api/v3/trades", params=params)

    def get_k(
        self,
        market: str,
        limit: int = 30,
        period: int = 1,
        timestamp: Optional[int] = None,
    ) -> list:
        """
        取得 K 線資料
        :param market: 市場 ID
        :param limit: 回傳筆數 1–10000，預設 30
        :param period: K 線週期（分鐘）: 1/5/15/30/60/120/240/360/720/1440，預設 1
        :param timestamp: Unix 時間戳（秒），指定起始時間
        """
        params: dict = {"market": market, "limit": limit, "period": period}
        if timestamp is not None:
            params["timestamp"] = timestamp
        return self._get("/api/v3/k", params=params)

    # =========================================================================
    # 公開 M 錢包端點
    # =========================================================================

    def get_m_index_prices(self) -> dict:
        """取得 M 錢包各幣種指數價格"""
        return self._get("/api/v3/wallet/m/index_prices")

    def get_m_historical_index_prices(
        self,
        currency: str,
        period: int = 1,
        limit: int = 30,
        timestamp: Optional[int] = None,
    ) -> list:
        """
        取得 M 錢包歷史指數價格
        :param currency: 幣種 ID
        :param period: K 線週期（分鐘）
        :param limit: 回傳筆數
        :param timestamp: Unix 時間戳（秒）
        """
        params: dict = {"currency": currency, "period": period, "limit": limit}
        if timestamp is not None:
            params["timestamp"] = timestamp
        return self._get("/api/v3/wallet/m/historical_index_prices", params=params)

    def get_m_limits(self) -> dict:
        """取得 M 錢包可用借貸額度"""
        return self._get("/api/v3/wallet/m/limits")

    def get_m_interest_rates(self) -> dict:
        """取得 M 錢包各幣種借貸利率"""
        return self._get("/api/v3/wallet/m/interest_rates")

    # =========================================================================
    # 用戶端點 (User)
    # =========================================================================

    def get_user_info(self) -> dict:
        """取得當前用戶資訊（KYC 狀態、帳號等）"""
        return self._auth_get("/api/v3/info")

    # =========================================================================
    # 帳戶 / 錢包端點 (Wallet)
    # =========================================================================

    def get_accounts(
        self,
        wallet_type: str = "spot",
        currency: Optional[str] = None,
    ) -> list:
        """
        取得帳戶餘額
        :param wallet_type: 'spot' 或 'm'
        :param currency: 篩選特定幣種，例如 'btc'
        """
        params = {}
        if currency:
            params["currency"] = currency
        return self._auth_get(f"/api/v3/wallet/{wallet_type}/accounts", params=params)

    def get_deposit_address(self, currency_version: str) -> dict:
        """
        取得存款地址
        :param currency_version: 幣種版本，例如 'trc20usdt'、'eth'
        """
        return self._auth_get(
            "/api/v3/deposit_address",
            params={"currency_version": currency_version},
        )

    def get_withdraw_addresses(
        self,
        currency: Optional[str] = None,
        limit: int = 50,
    ) -> list:
        """
        取得提現地址列表
        :param currency: 篩選特定幣種
        :param limit: 回傳筆數
        """
        params: dict = {"limit": limit}
        if currency:
            params["currency"] = currency
        return self._auth_get("/api/v3/withdraw_addresses", params=params)

    # =========================================================================
    # M 錢包私有端點
    # =========================================================================

    def get_m_ad_ratio(self) -> dict:
        """取得 M 錢包目前 AD 比率（資產 / 借貸）"""
        return self._auth_get("/api/v3/wallet/m/ad_ratio")

    def submit_m_loan(self, currency: str, amount: str) -> dict:
        """
        申請 M 錢包借貸
        :param currency: 借貸幣種，例如 'usdt'
        :param amount: 借貸金額（字串）
        """
        return self._auth_post(
            "/api/v3/wallet/m/loan",
            body={"currency": currency, "amount": amount},
        )

    def get_m_loans(
        self,
        currency: Optional[str] = None,
        limit: int = 50,
        page: int = 1,
    ) -> list:
        """
        取得 M 錢包借貸歷史
        :param currency: 篩選幣種
        :param limit: 回傳筆數
        :param page: 頁碼
        """
        params: dict = {"limit": limit, "page": page}
        if currency:
            params["currency"] = currency
        return self._auth_get("/api/v3/wallet/m/loans", params=params)

    def submit_m_transfer(self, currency: str, amount: str, side: str) -> dict:
        """
        現貨錢包與 M 錢包之間轉帳
        :param currency: 幣種，例如 'usdt'
        :param amount: 金額（字串）
        :param side: 'in'（轉入 M 錢包）或 'out'（從 M 錢包轉出）
        """
        return self._auth_post(
            "/api/v3/wallet/m/transfer",
            body={"currency": currency, "amount": amount, "side": side},
        )

    def get_m_transfers(
        self,
        currency: Optional[str] = None,
        limit: int = 50,
        page: int = 1,
    ) -> list:
        """
        取得 M 錢包轉帳記錄
        :param currency: 篩選幣種
        :param limit: 回傳筆數
        :param page: 頁碼
        """
        params: dict = {"limit": limit, "page": page}
        if currency:
            params["currency"] = currency
        return self._auth_get("/api/v3/wallet/m/transfers", params=params)

    def submit_m_repayment(self, currency: str, amount: str) -> dict:
        """
        提交 M 錢包還款
        :param currency: 還款幣種
        :param amount: 還款金額（字串）
        """
        return self._auth_post(
            "/api/v3/wallet/m/repayment",
            body={"currency": currency, "amount": amount},
        )

    def get_m_repayments(
        self,
        currency: Optional[str] = None,
        limit: int = 50,
        page: int = 1,
    ) -> list:
        """
        取得 M 錢包還款歷史
        :param currency: 篩選幣種
        :param limit: 回傳筆數
        :param page: 頁碼
        """
        params: dict = {"limit": limit, "page": page}
        if currency:
            params["currency"] = currency
        return self._auth_get("/api/v3/wallet/m/repayments", params=params)

    def get_m_liquidations(
        self,
        limit: int = 50,
        page: int = 1,
    ) -> list:
        """
        取得 M 錢包清算歷史
        :param limit: 回傳筆數
        :param page: 頁碼
        """
        return self._auth_get(
            "/api/v3/wallet/m/liquidations",
            params={"limit": limit, "page": page},
        )

    def get_m_liquidation(self, sn: str) -> dict:
        """
        取得單筆清算詳情
        :param sn: 清算序號
        """
        return self._auth_get("/api/v3/wallet/m/liquidation", params={"sn": sn})

    def get_m_interests(
        self,
        currency: Optional[str] = None,
        limit: int = 50,
        page: int = 1,
    ) -> list:
        """
        取得 M 錢包利息歷史
        :param currency: 篩選幣種
        :param limit: 回傳筆數
        :param page: 頁碼
        """
        params: dict = {"limit": limit, "page": page}
        if currency:
            params["currency"] = currency
        return self._auth_get("/api/v3/wallet/m/interests", params=params)

    # =========================================================================
    # 訂單端點 (Order)
    # =========================================================================

    def submit_order(
        self,
        wallet_type: str,
        market: str,
        side: str,
        volume: str,
        price: Optional[str] = None,
        ord_type: str = "limit",
        stop_price: Optional[str] = None,
        client_oid: Optional[str] = None,
        group_id: Optional[int] = None,
    ) -> dict:
        """
        提交買賣訂單
        :param wallet_type: 'spot' 或 'm'
        :param market: 市場 ID，例如 'btcusdt'
        :param side: 'buy' 或 'sell'
        :param volume: 交易量（字串）
        :param price: 限價（市價單可省略）
        :param ord_type: limit / market / stop_limit / stop_market / post_only / ioc_limit
        :param stop_price: 止損觸發價（stop 系列訂單需填）
        :param client_oid: 自訂訂單 ID（最長 36 字元）
        :param group_id: 群組訂單 ID
        """
        body: dict = {
            "market": market,
            "side": side,
            "volume": volume,
            "ord_type": ord_type,
        }
        if price is not None:
            body["price"] = price
        if stop_price is not None:
            body["stop_price"] = stop_price
        if client_oid is not None:
            body["client_oid"] = client_oid
        if group_id is not None:
            body["group_id"] = group_id
        return self._auth_post(f"/api/v3/wallet/{wallet_type}/order", body=body)

    def get_open_orders(
        self,
        wallet_type: str = "spot",
        market: Optional[str] = None,
        limit: int = 50,
        order_by: str = "desc",
        timestamp: Optional[int] = None,
    ) -> list:
        """
        取得未成交訂單
        :param wallet_type: 'spot' 或 'm'
        :param market: 篩選市場
        :param limit: 回傳筆數 1–1000，預設 50
        :param order_by: asc / desc / asc_updated_at / desc_updated_at
        :param timestamp: 時間戳篩選（毫秒）
        """
        params: dict = {"limit": limit, "order_by": order_by}
        if market:
            params["market"] = market
        if timestamp is not None:
            params["timestamp"] = timestamp
        return self._auth_get(
            f"/api/v3/wallet/{wallet_type}/orders/open", params=params
        )

    def get_closed_orders(
        self,
        wallet_type: str = "spot",
        market: Optional[str] = None,
        limit: int = 50,
        order_by: str = "desc",
        timestamp: Optional[int] = None,
        state: Optional[str] = None,
    ) -> list:
        """
        取得已成交 / 已關閉訂單
        :param wallet_type: 'spot' 或 'm'
        :param market: 篩選市場
        :param limit: 回傳筆數 1–1000，預設 50
        :param order_by: asc / desc / asc_updated_at / desc_updated_at
        :param timestamp: 時間戳篩選（毫秒）
        :param state: 狀態篩選 done / cancel / finalizing / failed
        """
        params: dict = {"limit": limit, "order_by": order_by}
        if market:
            params["market"] = market
        if timestamp is not None:
            params["timestamp"] = timestamp
        if state:
            params["state"] = state
        return self._auth_get(
            f"/api/v3/wallet/{wallet_type}/orders/closed", params=params
        )

    def get_orders_history(
        self,
        market: str,
        wallet_type: str = "spot",
        from_id: Optional[int] = None,
        limit: int = 50,
        order_by: str = "asc",
    ) -> list:
        """
        依 ID 順序取得訂單歷史（適合分頁爬取）
        :param market: 市場 ID（必填），例如 'btcusdt'
        :param wallet_type: 'spot' 或 'm'
        :param from_id: 從指定訂單 ID 開始
        :param limit: 回傳筆數
        :param order_by: asc / desc
        """
        params: dict = {"market": market, "limit": limit, "order_by": order_by}
        if from_id is not None:
            params["from_id"] = from_id
        return self._auth_get(
            f"/api/v3/wallet/{wallet_type}/orders/history", params=params
        )

    def get_order(
        self,
        order_id: Optional[int] = None,
        client_oid: Optional[str] = None,
    ) -> dict:
        """
        取得單筆訂單詳情
        :param order_id: 訂單 ID
        :param client_oid: 自訂訂單 ID（與 order_id 擇一）
        """
        params = {}
        if order_id is not None:
            params["id"] = order_id
        if client_oid is not None:
            params["client_oid"] = client_oid
        return self._auth_get("/api/v3/order", params=params)

    def cancel_order(
        self,
        order_id: Optional[int] = None,
        client_oid: Optional[str] = None,
    ) -> dict:
        """
        取消單筆訂單
        :param order_id: 訂單 ID
        :param client_oid: 自訂訂單 ID（與 order_id 擇一）
        """
        body = {}
        if order_id is not None:
            body["id"] = order_id
        if client_oid is not None:
            body["client_oid"] = client_oid
        return self._auth_delete("/api/v3/order", body=body)

    def cancel_orders(
        self,
        wallet_type: str,
        market: str,
        side: Optional[str] = None,
        group_id: Optional[int] = None,
    ) -> dict:
        """
        批次取消訂單
        :param wallet_type: 'spot' 或 'm'
        :param market: 市場 ID（必填）
        :param side: 'buy' 或 'sell'（省略則取消雙向）
        :param group_id: 只取消指定群組的訂單
        """
        body: dict = {"market": market}
        if side is not None:
            body["side"] = side
        if group_id is not None:
            body["group_id"] = group_id
        return self._auth_delete(f"/api/v3/wallet/{wallet_type}/orders", body=body)

    # =========================================================================
    # 成交記錄端點 (Trade)
    # =========================================================================

    def get_trades(
        self,
        wallet_type: str = "spot",
        market: Optional[str] = None,
        limit: int = 50,
        order_by: str = "desc",
        timestamp: Optional[int] = None,
        from_id: Optional[int] = None,
    ) -> list:
        """
        取得個人成交記錄
        :param wallet_type: 'spot' 或 'm'
        :param market: 篩選市場
        :param limit: 回傳筆數
        :param order_by: asc / desc
        :param timestamp: 時間戳篩選（毫秒）
        :param from_id: 從指定成交 ID 開始
        """
        params: dict = {"limit": limit, "order_by": order_by}
        if market:
            params["market"] = market
        if timestamp is not None:
            params["timestamp"] = timestamp
        if from_id is not None:
            params["from_id"] = from_id
        return self._auth_get(
            f"/api/v3/wallet/{wallet_type}/trades", params=params
        )

    def get_order_trades(
        self,
        order_id: Optional[int] = None,
        client_oid: Optional[str] = None,
    ) -> list:
        """
        取得特定訂單的成交明細
        :param order_id: 訂單 ID
        :param client_oid: 自訂訂單 ID（與 order_id 擇一）
        """
        params = {}
        if order_id is not None:
            params["id"] = order_id
        if client_oid is not None:
            params["client_oid"] = client_oid
        return self._auth_get("/api/v3/order/trades", params=params)

    # =========================================================================
    # 兌換端點 (Convert)
    # =========================================================================

    def submit_convert(
        self,
        from_currency: str,
        to_currency: str,
        from_amount: Optional[str] = None,
        to_amount: Optional[str] = None,
    ) -> dict:
        """
        執行幣種閃兌
        :param from_currency: 來源幣種，例如 'usdt'
        :param to_currency: 目標幣種，例如 'btc'
        :param from_amount: 賣出金額（與 to_amount 二擇一）
        :param to_amount: 買入金額（與 from_amount 二擇一）
        """
        body: dict = {
            "from_currency": from_currency,
            "to_currency": to_currency,
        }
        if from_amount is not None:
            body["from_amount"] = from_amount
        elif to_amount is not None:
            body["to_amount"] = to_amount
        return self._auth_post("/api/v3/convert", body=body)

    def get_convert(self, uuid: str) -> dict:
        """
        取得單筆兌換詳情
        :param uuid: 兌換單 UUID
        """
        return self._auth_get("/api/v3/convert", params={"uuid": uuid})

    def get_converts(
        self,
        limit: int = 50,
        page: int = 1,
    ) -> list:
        """
        取得兌換歷史
        :param limit: 回傳筆數
        :param page: 頁碼
        """
        return self._auth_get(
            "/api/v3/converts", params={"limit": limit, "page": page}
        )

    # =========================================================================
    # 交易記錄端點 (Transaction)
    # =========================================================================

    def submit_withdrawal(
        self,
        withdraw_address_uuid: str,
        amount: str,
    ) -> dict:
        """
        提交加密貨幣提現
        :param withdraw_address_uuid: 提現地址 UUID（可由 get_withdraw_addresses 取得）
        :param amount: 提現金額（字串）
        """
        return self._auth_post(
            "/api/v3/withdrawal",
            body={
                "withdraw_address_uuid": withdraw_address_uuid,
                "amount": amount,
            },
        )

    def submit_twd_withdrawal(self, amount: str) -> dict:
        """
        提交台幣（TWD）出金
        :param amount: 出金金額（字串）
        """
        return self._auth_post(
            "/api/v3/withdrawal/twd",
            body={"amount": amount},
        )

    def get_withdrawal(self, uuid: str) -> dict:
        """
        取得單筆提現詳情
        :param uuid: 提現 UUID
        """
        return self._auth_get("/api/v3/withdrawal", params={"uuid": uuid})

    def get_withdrawals(
        self,
        currency: Optional[str] = None,
        limit: int = 50,
        page: int = 1,
        state: Optional[str] = None,
    ) -> list:
        """
        取得提現歷史
        :param currency: 篩選幣種
        :param limit: 回傳筆數
        :param page: 頁碼
        :param state: 狀態篩選
        """
        params: dict = {"limit": limit, "page": page}
        if currency:
            params["currency"] = currency
        if state:
            params["state"] = state
        return self._auth_get("/api/v3/withdrawals", params=params)

    def get_deposit(self, uuid: str) -> dict:
        """
        取得單筆存款詳情
        :param uuid: 存款 UUID
        """
        return self._auth_get("/api/v3/deposit", params={"uuid": uuid})

    def get_deposits(
        self,
        currency: Optional[str] = None,
        limit: int = 50,
        page: int = 1,
        state: Optional[str] = None,
    ) -> list:
        """
        取得存款歷史
        :param currency: 篩選幣種
        :param limit: 回傳筆數
        :param page: 頁碼
        :param state: 狀態篩選
        """
        params: dict = {"limit": limit, "page": page}
        if currency:
            params["currency"] = currency
        if state:
            params["state"] = state
        return self._auth_get("/api/v3/deposits", params=params)

    def get_internal_transfers(
        self,
        currency: Optional[str] = None,
        limit: int = 50,
        page: int = 1,
        side: Optional[str] = None,
    ) -> list:
        """
        取得內部轉帳記錄
        :param currency: 篩選幣種
        :param limit: 回傳筆數
        :param page: 頁碼
        :param side: 'in' 或 'out'
        """
        params: dict = {"limit": limit, "page": page}
        if currency:
            params["currency"] = currency
        if side:
            params["side"] = side
        return self._auth_get("/api/v3/internal_transfers", params=params)

    def get_rewards(
        self,
        reward_type: Optional[str] = None,
        currency: Optional[str] = None,
        limit: int = 50,
        page: int = 1,
    ) -> list:
        """
        取得獎勵歷史（返傭、空投等）
        :param reward_type: 獎勵類型篩選
        :param currency: 篩選幣種
        :param limit: 回傳筆數
        :param page: 頁碼
        """
        params: dict = {"limit": limit, "page": page}
        if reward_type:
            params["reward_type"] = reward_type
        if currency:
            params["currency"] = currency
        return self._auth_get("/api/v3/rewards", params=params)

import pytest
import project
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects, HTTPError
import requests
from unittest.mock import patch
import re


def test_coin_list():
    assets = project.Assets()

    sample_output = [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "platforms": {}
        },
        {
            "id": "bonk",
            "symbol": "bonk",
            "name": "Bonk",
            "platforms":
                {
                "solana": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
                "neon-evm": "0xd4b6520f7fb78e1ee75639f3376c581a71bcdb0e",
                "ethereum": "0x1151cb3d861920e07a38e03eead12c32178567f6",
                "aptos": "0x2a90fae71afc7460ee42b20ee49a9c9b29272905ad71fef92fbd8b3905a24b56",
                "unichain": "0xbbe97f3522101e5b6976cbf77376047097ba837f",
                "polygon-pos": "0xe5b49820e5a1063f6f4ddf851327b5e8b2301048",
                "binance-smart-chain": "0xa697e272a73744b343528c3bc4702f2565b2f422",
                "arbitrum-one": "0x09199d9a5f4448d0848e4395d065e1ad9c4a1f74"
                }
        },
        {
            "id": "solana",
            "symbol": "sol",
            "name": "Solana",
            "platforms": {}
        }
    ]

    # Replace the output of _get(), with "sample_output". Apply this sample response to coin_list to check that the layers of the response (list[dict]) are receieved and returned correctly.
    # If _get() actually ran, it would 1) require dependencies like hitting GEKO's API and 2) return nonstandard data
    with patch.object(assets,"_get", return_value=sample_output):
        result = assets.coin_list()

    # Check that outer layer is list
    assert isinstance(result,list)
    # Check that inner layer is dict
    assert isinstance(result[0],dict)
    # Check "id" field data return
    assert result[0]["id"] == "bitcoin"
    # Check "symbol" field data return
    assert result[1]["symbol"] == "bonk"
    # Check "name" field data return
    assert result[2]["name"] == "Solana"
    # Check "platforms" field data return
    assert result[1]["platforms"]["ethereum"] == "0x1151cb3d861920e07a38e03eead12c32178567f6"


def test_a_mkt_dict_build():
    assets = project.Assets()

    sample_output = [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "image": "https://coin-images.coingecko.com/coins/images/1/large/bitcoin.png?1696501400",
            "current_price": 91406,
            "market_cap": 1822524078423,
            "market_cap_rank": 1,
            "fully_diluted_valuation": 1822524078423,
            "total_volume": 73562163933,
            "high_24h": 93669,
            "low_24h": 90021,
            "price_change_24h": 85.7,
            "price_change_percentage_24h": 0.09385,
            "market_cap_change_24h": 193172477,
            "market_cap_change_percentage_24h": 0.0106,
            "circulating_supply": 19950440.0,
            "total_supply": 19950440.0,
            "max_supply": 21000000.0,
            "ath": 126080,
            "ath_change_percentage": -27.51133,
            "ath_date": "2025-10-06T18:57:42.558Z",
            "atl": 67.81,
            "atl_change_percentage": 134680.97135,
            "atl_date": "2013-07-06T00:00:00.000Z",
            "roi": None,
            "last_updated": "2025-11-19T13:43:34.135Z"
        }
        ,
        {
            "id": "ethereum",
            "symbol": "eth",
            "name": "Ethereum",
            "image": "https://coin-images.coingecko.com/coins/images/279/large/ethereum.png?1696501628",
            "current_price": 3076.15,
            "market_cap": 370939445797,
            "market_cap_rank": 2,
            "fully_diluted_valuation": 370939445797,
            "total_volume": 30961124769,
            "high_24h": 3162.95,
            "low_24h": 2995.06,
            "price_change_24h": 29.73,
            "price_change_percentage_24h": 0.97604,
            "market_cap_change_24h": 3645873744,
            "market_cap_change_percentage_24h": 0.99263,
            "circulating_supply": 120696080.2203551,
            "total_supply": 120696080.2203551,
            "max_supply": None,
            "ath": 4946.05,
            "ath_change_percentage": -37.76866,
            "ath_date": "2025-08-24T19:21:03.333Z",
            "atl": 0.432979,
            "atl_change_percentage": 710787.40776,
            "atl_date": "2015-10-20T00:00:00.000Z",
            "roi": {
                "times": 44.00085904812381,
                "currency": "btc",
                "percentage": 4400.08590481238
            },
            "last_updated": "2025-11-19T13:43:34.038Z"
        },
        {
            "id": "tera-smart-money",
            "symbol": "tera",
            "name": "TERA",
            "image": "https://coin-images.coingecko.com/coins/images/7861/large/yZtmK2L.png?1696508094",
            "current_price": 0.01991732,
            "market_cap": 15027565,
            "market_cap_rank": 1341,
            "fully_diluted_valuation": 19917316,
            "total_volume": 0.0,
            "high_24h": None,
            "low_24h": None,
            "price_change_24h": None,
            "price_change_percentage_24h": None,
            "market_cap_change_24h": None,
            "market_cap_change_percentage_24h": None,
            "circulating_supply": 754497500.0,
            "total_supply": 1000000000.0,
            "max_supply": None,
            "ath": 0.02827364,
            "ath_change_percentage": -29.55517,
            "ath_date": "2021-04-12T09:24:04.775Z",
            "atl": 2.01989e-10,
            "atl_change_percentage": 9860582409.45965,
            "atl_date": "2023-03-03T05:01:59.291Z",
            "roi": None,
            "last_updated": "2025-11-14T20:03:20.160Z"
        },
        {
            "id": "usd-coin-pulsechain",
            "symbol": "usdc",
            "name": "Bridged USD Coin (PulseChain)",
            "image": "https://coin-images.coingecko.com/coins/images/30514/large/usdc.png?1696529399",
            "current_price": 1.001,
            "market_cap_rank": 1340,
            "fully_diluted_valuation": 15031644,
            "total_volume": 1012025,
            "high_24h": 1.006,
            "low_24h": 0.990328,
            "price_change_24h": 0.00707756,
            "price_change_percentage_24h": 0.71189,
            "market_cap_change_24h": 169603,
            "market_cap_change_percentage_24h": 1.14118,
            "circulating_supply": 15019727.567132,
            "total_supply": 15019727.567132,
            "max_supply": None,
            "ath": 1.35,
            "ath_change_percentage": -26.09527,
            "ath_date": "2023-07-31T15:07:40.844Z",
            "atl": 0.867031,
            "atl_change_percentage": 14.93701,
            "atl_date": "2024-08-05T01:29:35.701Z",
            "roi": None,
            "last_updated": "2025-11-19T14:58:53.380Z"
        }
    ]

    data = []

    with patch.object(assets,"_get",return_value=sample_output):
        response = assets.coin_mkts()

    data.extend(response)
    dict_asset_main,dict_asset_full = project.a_mkt_dict_build(data)

    # Test USD Rfmt Helper
    assert dict_asset_main[0]["Price (USD)"] == "$91,406.00"
    # Test Thousands Rfmt Helper
    assert dict_asset_full[1]["Total Volume"] == "30,961,124,769.00"
    # Test Pct Rfmt Helper
    assert dict_asset_full[1]["Price % Chg 24h"] == "0.97604%"
    # Test Null Value Error Catch (else "null")
    assert dict_asset_main[2]["Price % Chg 24h"] == "null"
    # Test Missing Key Error Catch (.get() else "null")
    assert dict_asset_main[3]["Mkt Cap"] == "null"


def test_e_pair_dict_build():
    exchanges = project.Exchanges()

    sample_output = {
            "name": "Binance",
            "tickers":
            [
                {
                    "base": "ETH",
                    "target": "USDT",
                    "market": {
                        "name": "Binance",
                        "identifier": "binance",
                        "has_trading_incentive": False
                    },
                    "last": 2753.47,
                    "volume": 1198833.1736,
                    "converted_last": {
                        "btc": 0.03252443,
                        "eth": 0.99566563,
                        "usd": 2751.54
                    },
                    "converted_volume": {
                        "btc": 38991,
                        "eth": 1193637,
                        "usd": 3298640513
                    },
                    "trust_score": "green",
                    "bid_ask_spread_percentage": 0.010362,
                    "timestamp": "2025-11-21T19:44:11+00:00",
                    "last_traded_at": "2025-11-21T19:44:11+00:00",
                    "last_fetch_at": "2025-11-21T19:44:11+00:00",
                    "is_anomaly": False,
                    "is_stale": False,
                    "trade_url": "https://www.binance.com/en/trade/ETH_USDT?ref=37754157",
                    "token_info_url": None,
                    "coin_id": "ethereum",
                    "target_coin_id": "tether",
                    "coin_mcap_usd": 333646037636.68396
                },
                {
                    "base": "BTC",
                    "target": "USDT",
                    "market": {
                        "name": "Binance",
                        "identifier": "binance",
                        "has_trading_incentive": False
                    },
                    "last": 84076.61,
                    "volume": 72686.36112,
                    "converted_last": {
                        "btc": 1.000268,
                        "eth": 30.792459,
                        "usd": 84018
                    },
                    "converted_volume": {
                        "btc": 72706,
                        "eth": 2238192,
                        "usd": 6106944980
                    },
                    "trust_score": "green",
                    "bid_ask_spread_percentage": 0.010012,
                    "timestamp": "2025-11-21T20:39:33+00:00",
                    "last_traded_at": "2025-11-21T20:39:33+00:00",
                    "last_fetch_at": "2025-11-21T20:40:32+00:00",
                    "is_anomaly": False,
                    "is_stale": False,
                    "trade_url": "https://www.binance.com/en/trade/BTC_USDT?ref=37754157",
                    "token_info_url": None,
                    "coin_id": "bitcoin",
                    "target_coin_id": "tether",
                    "coin_mcap_usd": 1667199349325.389
                },
                {
                    "base": "ETH",
                    "target": "FDUSD",
                    "market": {
                        "name": "Binance",
                        "identifier": "binance",
                        "has_trading_incentive": False
                    },
                    "last": 2774.8,
                    "volume": 622884.3833,
                    "converted_last": {
                        "btc": 0.03269027,
                        "eth": 1.000088,
                        "usd": 2765.66
                    },
                    "converted_volume": {
                        "btc": 20362,
                        "eth": 622939,
                        "usd": 1722688078
                    },
                    "trust_score": "green",
                    "bid_ask_spread_percentage": 0.031685,
                    "timestamp": "2025-11-21T19:42:30+00:00",
                    "last_traded_at": "2025-11-21T19:42:30+00:00",
                    "last_fetch_at": "2025-11-21T19:44:00+00:00",
                    "is_anomaly": False,
                    "is_stale": False,
                    "trade_url": "https://www.binance.com/en/trade/ETH_FDUSD?ref=37754157",
                    "token_info_url": None,
                    "coin_id": "ethereum",
                    "target_coin_id": "first-digital-usd",
                    "coin_mcap_usd": 333646037636.68396
                },
                {
                    "base": "ETH",
                    "target": "BTC",
                    "market": {
                        "name": "Binance",
                        "identifier": "binance",
                        "has_trading_incentive": False
                    },
                    "last": 0.03262,
                    "volume": 110717.3233,
                    "converted_last": {
                        "btc": 0.03263132,
                        "eth": 0.99893768,
                        "usd": 2760.58
                    },
                    "converted_volume": {
                        "btc": 3613,
                        "eth": 110600,
                        "usd": 305644575
                    },
                    "trust_score": "green",
                    "bid_ask_spread_percentage": 0.030647,
                    "timestamp": "2025-11-21T19:44:11+00:00",
                    "last_traded_at": "2025-11-21T19:44:11+00:00",
                    "last_fetch_at": "2025-11-21T19:44:11+00:00",
                    "is_anomaly": False,
                    "is_stale": False,
                    "trade_url": "https://www.binance.com/en/trade/ETH_BTC?ref=37754157",
                    "token_info_url": None,
                    "coin_id": "ethereum",
                    "target_coin_id": "bitcoin",
                    "coin_mcap_usd": 333646037636.68396
                },
                {
                    "base": "BNB",
                    "target": "USDC",
                    "market": {
                        "name": "Binance",
                        "identifier": "binance",
                        "has_trading_incentive": False
                    },
                    "last": 824.9,
                    "volume": 538183.462,
                    "converted_last": {
                        "btc": 0.00978451,
                        "eth": 0.29998846,
                        "usd": 824.82
                    },
                    "converted_volume": {
                        "btc": 5266,
                        "eth": 161449,
                        "usd": 443903143
                    },
                    "trust_score": "green",
                    "bid_ask_spread_percentage": 0.014851,
                    "timestamp": "2025-11-21T19:46:22+00:00",
                    "last_traded_at": "2025-11-21T19:46:22+00:00",
                    "last_fetch_at": "2025-11-21T19:47:19+00:00",
                    "is_anomaly": False,
                    "is_stale": False,
                    "trade_url": "https://www.binance.com/en/trade/BNB_USDC?ref=37754157",
                    "token_info_url": None,
                    "coin_id": "binancecoin",
                    "target_coin_id": "usd-coin",
                    "coin_mcap_usd": 114014570693.30421
                },
                {
                    "base": "SOL",
                    "target": "USDC",
                    "market": {
                        "name": "Binance",
                        "identifier": "binance",
                        "has_trading_incentive": False
                    },
                    "last": 128.06,
                    "volume": 2422190.256,
                    "converted_last": {
                        "btc": 0.00151869,
                        "eth": 0.04656238,
                        "usd": 128.02
                    },
                    "converted_volume": {
                        "btc": 3679,
                        "eth": 112783,
                        "usd": 310096443
                    },
                    "trust_score": "green",
                    "bid_ask_spread_percentage": 0.017827,
                    "timestamp": "2025-11-21T19:45:29+00:00",
                    "last_traded_at": "2025-11-21T19:45:29+00:00",
                    "last_fetch_at": "2025-11-21T19:47:14+00:00",
                    "is_anomaly": False,
                    "is_stale": False,
                    "trade_url": "https://www.binance.com/en/trade/SOL_USDC?ref=37754157",
                    "token_info_url": None,
                    "coin_id": "solana",
                    "target_coin_id": "usd-coin",
                    "coin_mcap_usd": 71963171872.96947
                },
                {
                    "base": "XRP",
                    "target": "USDC",
                    "market": {
                        "name": "Binance",
                        "identifier": "binance",
                        "has_trading_incentive": False
                    },
                    "last": 1.95,
                    "volume": 114385796.3,
                    "converted_last": {
                        "btc": 2.313e-05,
                        "eth": 0.00070902,
                        "usd": 1.95
                    },
                    "converted_volume": {
                        "btc": 2645,
                        "eth": 81101,
                        "usd": 222988130
                    },
                    "trust_score": "green",
                    "bid_ask_spread_percentage": 0.015123,
                    "timestamp": "2025-11-21T19:46:22+00:00",
                    "last_traded_at": "2025-11-21T19:46:22+00:00",
                    "last_fetch_at": "2025-11-21T19:47:19+00:00",
                    "is_anomaly": False,
                    "is_stale": False,
                    "trade_url": "https://www.binance.com/en/trade/XRP_USDC?ref=37754157",
                    "token_info_url": None,
                    "coin_id": "ripple",
                    "target_coin_id": "usd-coin",
                    "coin_mcap_usd": 118029855598.59258
                },
                {
                    "base": "DOGE",
                    "target": "USDC",
                    "market": {
                        "name": "Binance",
                        "identifier": "binance",
                        "has_trading_incentive": False
                    },
                    "last": 0.13989,
                    "volume": 730804081.0,
                    "converted_last": {
                        "btc": 1.66e-06,
                        "eth": 5.086e-05,
                        "usd": 0.13985
                    },
                    "converted_volume": {
                        "btc": 1212,
                        "eth": 37171,
                        "usd": 102202770
                    },
                    "trust_score": "green",
                    "bid_ask_spread_percentage": 0.014308,
                    "timestamp": "2025-11-21T19:46:22+00:00",
                    "last_traded_at": "2025-11-21T19:46:22+00:00",
                    "last_fetch_at": "2025-11-21T19:47:19+00:00",
                    "is_anomaly": False,
                    "is_stale": False,
                    "trade_url": "https://www.binance.com/en/trade/DOGE_USDC?ref=37754157",
                    "coin_id": "dogecoin",
                    "target_coin_id": "usd-coin",
                    "coin_mcap_usd": 21371270999.86915
                }
            ]
        }

    data = []

    with patch.object(exchanges,"_get",return_value=sample_output):
        response = exchanges.exch_pairs("ethereum")

    # Exact same post-get pre-dictBuild flow as exchange_pairs() function
    data.append(response)
    dict_exch_pair_main,dict_exch_pair_full_fresh,dict_exch_pair_full_stale,asset_count_list = project.e_pair_dict_build(data)
    numassets = len(asset_count_list)


    # Dict Data propagation/rfmting Test
    # Test Exchange Name
    assert dict_exch_pair_full_fresh[0]["Exchange Name"] == "Binance"
    # Test Pair Code Generation
    assert dict_exch_pair_full_fresh[0]["Trading Pair"] == "ETH-USDT"
    assert dict_exch_pair_full_fresh[5]["Trading Pair"] == "SOL-USDC"
    assert dict_exch_pair_full_fresh[7]["Trading Pair"] == "DOGE-USDC"
    # Test Data Rfmt & None Vals/Missing Keys
    assert dict_exch_pair_full_fresh[7]["Volume"] == "730,804,081.00"
    assert dict_exch_pair_full_fresh[3]["Bid/Ask Spread %"] == "0.03065%"
    assert dict_exch_pair_full_fresh[4]["Base Asset Mkt Cap (USD)"] == "$114,014,570,693.30"
    # Test Missing Key (.get())
    assert dict_exch_pair_full_fresh[7]["Token Info URL"] == "null"
    # Test None value
    assert dict_exch_pair_full_fresh[3]["Token Info URL"] == "null"

    # Counter Tests
    # Test list sort by count
    for i in range(0,numassets-1):
        # End range at numassets-1 because last item in list has nothing to compare to
        assert asset_count_list[i]["Count"] >= asset_count_list[i+1]["Count"]
    # Test data propagation into counts listDict
    assert asset_count_list[0]["CoinGecko Asset ID"] == "usd-coin"
    assert asset_count_list[0]["Count"] == 4
    assert asset_count_list[1]["Asset"] == "ETH"
    assert asset_count_list[1]["Count"] == 3
    assert asset_count_list[5]["CoinGecko Asset ID"] == "binancecoin"
    assert asset_count_list[5]["Count"] == 1
    # Test Count on reversed pair (BTC is base in one pair and counter in another)
    assert asset_count_list[3]["Asset"] == "BTC"
    assert asset_count_list[3]["Count"] == 2


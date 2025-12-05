from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects, HTTPError
import json
import sys
import argparse
from tabulate import tabulate
import csv
from datetime import datetime
from time import sleep
import re
from collections import Counter


class Auth:
    """Authentication and Base Endpoint GET"""
    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, api_key=None):
        """
        Initialization of API Authentication
        :param api_key: API Key for CoinGecko API access. Default is my demo key.
        :type api_key: str
        """
        self._api_key = api_key or "CG-dmmndTzTq3trGas8h5b3aYCQ"
        self.base_url = self.BASE_URL

        self.session = Session()
        self.session.headers.update({
            "Accepts": "application/json",
            "x-cg-demo-api-key": self._api_key
        })


    def _get(self, endpoint: str, params=None) -> dict | list[dict]:
        """
        Base GET Request
        :param endpoint: API endpoint path to be appended to BASE_URL
        :type endpoint: str
        :param params: Query parameters for GET request. Optional for some endpoints
        :type params: dict
        :rtype: dict | list[dict]
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url, params=params)
            status_code = response.status_code
            response.raise_for_status()
            return response.json()
        # [for after project] Implement automated responses to errors such as RETRY, SKIP, etc
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            raise e(f"API request failed: {e}")
        except HTTPError as e:
            raise HTTPError(f"HTTP error {status_code}: {e}")


    @property
    def api_key(self):
        """ API Key Getter """
        return self._api_key

    @api_key.setter
    def api_key(self, api_key: str):
        """ API Key Setter """
        if not api_key:
            api_key = "CG-dmmndTzTq3trGas8h5b3aYCQ"
        self._api_key = api_key


class Assets(Auth):
    """ Asset GET Requests Class """
    def coin_list(self) -> list[dict]:
        """
        Get a list of Gecko Asset IDs, Asset Names, Codes, Blockchains, and Contract Addresses for all assets.
        The only parameter, 'include_platform', is set to 'true' by default so that data returned by the endpoint is as comprehensive as possible.
        Called by asset_list() function.

        :rtype: list[dict]
        """
        params = {
            "include_platform": "true",
        }
        try:
            print("Fetching data. One moment please.")
            data = self._get("coins/list", params)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print (f"API request failed: {e}")
            return None
        except HTTPError as e:
            print("No data returned. Please input a valid asset ID")
            return None
        return data


    def coin_mkts(
            self,
            ids: str | None = None,
            per_page: int | None = None,
            page: int | None = None
            ) -> list[dict]:
        """
        Get asset & market data.
        If the user does not input any values, the top 250 assets by market cap will be returned in descending order of mkt cap.
        If user inputs values for 'ids', specific assets will be returned.
        Otherwise, a number of assets specified by the user will be returned in order of market cap desc. For example, if the user says they want two assets returned, Bitcoin, having the highest market cap of any cryptoasset, will be #1, followed by Ethereum, which has the second highest, etc.
        Called by asset_mkts() function.

        :param ids: Optional parameter. Comma-separated CoinGecko asset IDs. A list of all assets and their IDs can be found using the coin_list function.
        :type ids: str | None
        :param per_page: Optional parameter. Number of results per page. Maximum = 250. Default = 100.
        :type per_page: int | None
        :param page: Optional parameter. Page number for paginated results.
        :type page: int | None
        :rtype: list[dict]
        """
        params = {
            "vs_currency": "usd",
            # ***User input should either be ids OR a number that the user inputs which the code then uses to calculate per_page and page values***
            "ids": ids,
            # per_page should be user-defined but if it exceeds 250 pagination is required.
            "per_page": per_page,
            # IF the per-page amount exceeds 250, "page" should be optional AND iterative
            "page": page,
            "price_change_percentage": "24h",
            "precision": 2
        }
        try:
            print("Fetching data. One moment please.")
            data = self._get("coins/markets/",params)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print (f"API request failed: {e}")
            return None
        except HTTPError as e:
            print("HTTPError: No data returned. Please check your asset and/or exchange ID and try again.")
            return None
        return data


    def coin_pairs(
            self,
            id: str,
            exchange_ids: str | None = None,
            page: int | None = None,
            order: str | None = None
            ) -> dict[list[dict]]:
        """
        Get data on a single asset's market pairs on the specified exchange(s).
        Data returned is ordered by CoinGecko's Trust Score, which is graded as 'green', 'yellow' or 'red'.
        If the user does not input a value for 'id', data returned will default to pairs containing 'bitcoin'.
        If the user does not input a value for 'exchange_id', data returned will encompass all Active exchanges covered by CoinGecko.
        If the user does not input a Gecko Asset ID or any exchange IDs, the first 100 market pairs containing Bitcoin that have a trust_score = 'Green' will be returned.
        Called by asset_pairs() function.

        :param id: The CoinGecko ID for the asset whose market pairs you wish to view. This is a path variable, not a parameter.
        :type id: str
        :param exchange_ids: Optional parameter. Comma-separated CoinGecko Exchange ID. Used to return the market pairs from specific exchanges. Default = 'binance'.
        :type exchange_ids: str | None
        :param page: Optional parameter. Page number for paginated results.
        :type page: int | None
        :param order: Static parameter, not currently moddable by user. Set the method by which results will be ordered. Default = 'trust_score_desc'. Acceptable values = (trust_score_desc, trust_score_asc, volume_desc, volume_asc)
        :type order: str | None
        :rtype: list[dict]
        """
        path = f"coins/{id}/tickers"
        params = {
            "exchange_ids": exchange_ids,
            "page": page,
        }

        try:
            print("Fetching data. One moment please.")
            data = self._get(path,params)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print (f"API request failed: {e}")
            return None
        except HTTPError as e:
            print("No data returned. Please input a valid asset ID")
            return None
        return data


class Exchanges(Auth):
    """ Exchanges GET Requests Class """
    def exch_list(self) -> list[dict]:
        """
        Get a list of Gecko Exchange IDs and Exchange Names for all of CoinGecko's Exchanges.
        The only parameter, 'status', is set to 'active' by default so that only active exchanges are returned.
        Called by exchange_list() function.

        :rtype: list[dict]
        """
        params = {
            "status": "active",
        }
        try:
            print("Fetching data. One moment please.")
            data = self._get("exchanges/list", params)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print (f"API request failed: {e}")
            return None
        except HTTPError as e:
            print("HTTPError: No data returned.")
            return None
        return data


    def exch_data(
            self,
            per_page: int | None = None,
            page: int | None = None
            ) -> list[dict]:
        """
        Query all supported exchanges and associated exchange data (ID, name, country, etc) that have active trading volumes on CoinGecko.
        Called by exchange_list() function.

        :param per_page: Optional parameter. Number of results to display per page. If not specified by user, code will default to max (250) to minimize # of API calls. Min = 1 Max = 250. API Default = 100/pg. Ordered by Gecko trust_score_rank. Multiple exchanges have trust_score = 10, not yet sure how they set rankings among exchanges with same score.
        :type per_page: int | None
        :param page: Optional parameter. Page number for paginated results. Not used unless user requests > 250 assets.
        :type page: int | None
        :rtype: list[dict]
        """
        params = {
            "per_page": per_page,
            "page": page
        }
        try:
            print("Fetching data. One moment please.")
            data = self._get("exchanges",params)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print (f"API request failed: {e}")
            return None
        except HTTPError as e:
            print("HTTPError: No data returned. Please check your asset and exchange ID and try again.")
            return None
        return data


    def exch_top100(
        self,
        id: str
        ) -> dict[list[dict]]:
        """
        Query exchange’s data (name, year established, country, links (url, social media), etc), exchange volume in BTC and top 100 tickers based on exchange’s ID.
        Essentially a combination of exch_list and exch_data datasets with the addition of exchange social media links.
        Called by exchange_top100() function.

        :param id: Required. Gecko Exchange ID. Only allowed query one exchange at a time.
        :type id: str
        :rtype: dict[list[dict]]
        """
        params = {
            # dex fmt API default = 'contract_address'. Code default = 'symbol' .
            "dex_pair_format": "contract_address"
        }
        path = f"exchanges/{id}"
        try:
            print("Fetching data. One moment please.")
            data = self._get(path,params)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print (f"API request failed: {e}")
            return None
        except HTTPError as e:
            print("HTTPError: No data returned. Please check your asset and exchange ID and try again.")
            return None
        return data


    def exch_pairs(
        self,
        id: str,
        coin_ids: str | None = None,
        page: int | None = None
        ) -> dict[list[dict]]:
        """
        Query an exchange’s market pairs based on exchange’s ID.
        Results are ordered by each pair's base asset's market cap descending. For example, if an exchange has BTC/USD and ETH/USD pairs, BTC/USD will be listed first because Bitcoin has a higher market cap than Ethereum.
        If viewing pairs on a DEX, the pair format will be displayed with each asset's contract address rather than their symbols. This is for ease of use - there is no uniqueness constraint on asset symbols, but contract addresses are unique. Can change 'dex_pair_format' to 'symbol' if desired, although this is not recommended.
        Called by exchange_pairs() function.

        :param id: Required. Gecko Exchange ID. Only allowed query one exchange at a time.
        :type id: str
        :param coin_ids: Optional parameter. Comma-separated list of coin IDs to filter results. If omitted, all pairs listed on the exchange are returned.
        :type coin_ids: str | None
        :param page: Optional parameter. Page number for paginated results. Not required unless number of pairs returned exceeds 100.
        :type page: int | None
        :rtype: dict[list[dict]]
        """

        params = {
            "id": id,
            "coin_ids": coin_ids,
            "page": page,
            # Default ordering is "trust_score_desc". Not moddable with inputs at the moment as I don't see a need to. If I do build that in post-project, another way to order is "base_target", which orders alphabetically by first the base asset symbol and then the target asset symbol. This method of ordering works the exact same way for DEXes with dex_pair_format = "contract_address", which means it's essentially useless for them with that pair format parameter applied
            "order": "market_cap_desc",
            "dex_pair_format": "contract_address"
        }
        path = f"exchanges/{id}/tickers"
        try:
            print("Fetching data. One moment please.")
            data = self._get(path,params)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print (f"API request failed: {e}")
            return None
        except HTTPError as e:
            print("HTTPError: No data returned. Please check your asset and exchange ID and try again.")
            return None
        return data



def main():
    """
    Starts program & handles interpretation of command-line arguments.
    If no arguments are provided, or invalid arguments are provided, the user is prompted for input.
    """
    if len(sys.argv) == 1:
        prompts()
    elif len(sys.argv) == 2 and sys.argv[1] == 'assetlist':
        asset_list()
    elif len(sys.argv) == 2 and sys.argv[1] == 'assetmkts':
        asset_mkts()
    elif len(sys.argv) == 2 and sys.argv[1] == 'assetpairs':
        asset_pairs()
    elif len(sys.argv) == 2 and sys.argv[1] == 'exchlist':
        exchange_list()
    elif len(sys.argv) == 2 and sys.argv[1] == 'exch100':
        exchange_top100()
    elif len(sys.argv) == 2 and sys.argv[1] == 'exchpairs':
        exchange_pairs()
    else:
        print("No valid command-line arguments entered.")
        prompts()


def prompts():
    """ Prompt user for input on the dataset that they would like to explore. """
    while True:
        baseprompt = input("\nWhat would you like to do?\n"
                    "For a basic list of asset names, symbols, blockchains, contract addresses, and their respective IDs on CoinGecko, type 'assetlist' and press enter.\n"
                    "For asset and market data, type 'assetmkts' and press enter.\n"
                    "For data on an asset's market pairs on specific exchanges, type 'assetpairs' and press enter.\n"
                    "For basic data on many exchanges, type 'exchlist' and press enter.\n"
                    "For expanded data on exchanges you want to examine, such as descriptions, social media links, and the top 100 assets on that exchange, type 'exch100' and press enter.\n"
                    "For data on the assets and pairs that an exchange has listed for trading, type 'exchpairs' and press enter.\n"
                    "To exit, type 'exit' and press enter. "
                    ).lower().strip()
        if baseprompt == "assetlist":
            asset_list()
            break
        elif baseprompt == "assetmkts":
            asset_mkts()
            break
        elif baseprompt == "assetpairs":
            asset_pairs()
            break
        elif baseprompt == "exchlist":
            exchange_list()
            break
        elif baseprompt == "exch100":
            exchange_top100()
            break
        elif baseprompt == "exchpairs":
            exchange_pairs()
            break
        elif baseprompt == "exit":
            sys.exit("Have a good day cowpoke!")
        else:
            print("Please input a valid command.\n")
            continue


def asset_list():
    """
    No user input required for data acquisition.
    Print tabulated Asset data (Name, Ticker, Gecko ID, Blockchain(s), Contract Address(es)) and allow user to export data from the a_list_dict_build() list dicts to CSV, explore other datasets, or exit.
    """
    assets = Assets()
    data = assets.coin_list()
    if not data:
        print("API Error. Returning to home.")
        prompts()
        return

    dict_asset_chainpop,dict_asset_chain_sep_assets = a_list_dict_build(data)

    first_twenty = dict_asset_chain_sep_assets[:20]

    # Return the first 20 assets in tabulated form. If they want to see the whole list, they can export to a csv.
    print(tabulate(first_twenty, headers="keys",showindex=False,tablefmt="simple_grid",maxcolwidths=20))
    while True:
        exportprompt = str(input(
            f"\nThere are a total of {len(dict_asset_chainpop)} assets and {len(dict_asset_chain_sep_assets)} associated blockchains listed.\n"
            "To view them all, please export to a csv with one of the following commands.\n"
            "To export a list of assets with all chains/addresses in one cell, type 'assets' and press enter.\n"
            "To export the list of assets separated into one row per asset chain/address, type 'chains' and press enter.\n"
            "To export data and then explore another dataset, type 'moredata' and press enter.\n"
            "To exit, type 'exit' and press enter. "
            )).lower().strip()

        if exportprompt == 'moredata':
            break
        elif exportprompt == 'exit':
            sys.exit("Exited successfully.")
        elif exportprompt == 'assets':
            print(csv_export(dict_asset_chainpop, "asset_list_base"))
            continue
        elif exportprompt == 'chains':
            print(csv_export(dict_asset_chain_sep_assets, "asset_list_chains"))
            continue
        else:
            print("Please input one of the following commands: 'assets', 'chains', 'moredata', or 'exit'. \n")
            continue
    prompts()

def a_list_dict_build(data: list[dict]) -> tuple[list[dict],list[dict]]:
    """
    Constructs and returns two dict lists from coin_list data.
    dict_asset_chainpop - A dict list containing asset info with all of an asset's blockchains + corresponding contract address in a nested dictionary.
    dict_asset_chain_sep_assets - A dict list containing asset info with each asset's blockchains + corresponding contract address separated into their own row.

    :param data: The data returned by the coin_list() Method.
    :type data: list[dict]
    :rtype: tuple(list[dict],list[dict])
    """

    dict_asset_chainpop = [
    {
        '#': data.index(asset)+1,
        'Gecko ID': asset["id"],
        'Name': asset["name"],
        'Code': asset["symbol"],
        'Blockchain&ContAdd': {"null": "null"} if len(asset["platforms"])==0 else asset["platforms"],
    }
        for asset in data
    ]

    """ Separates the assets out to one dictionary item per asset's Blockchain&ContAdd dictionary item OR one item if the asset's Blockchain/Contract Address values are 'null'. """
    dict_asset_chain_sep_assets = [
        {
            '#': asset["#"],
            'Gecko ID': asset["Gecko ID"],
            'Name': asset["Name"],
            'Code': asset["Code"],
            'Blockchain': "null" if chain=="null" else chain,
            'Address': "null" if address=="null" else address
        }
            # iterates through each asset in the dictionary list
            for asset in dict_asset_chainpop
            # iterates through each Blockchain + Contract Address pair in each asset's "Blockchain&ContAdd" dictionary
            for chain, address in asset["Blockchain&ContAdd"].items()
    ]

    return dict_asset_chainpop,dict_asset_chain_sep_assets


def asset_mkts():
    """
    User provides either a comma-separated string of Gecko Asset IDs or the number of top assets they would like to view.
    Print tabulated Asset Market data (Name, Ticker, Slug, Market Cap, Diluted Market Cap, 24h Price % Change, 7d Price % Change) and allow user to export data from the a_mkt_dict_build() list dicts to CSV, explore other datasets, or exit.
    """
    assets = Assets()
    data = []

    while True:
        modeprompt = (
            input("\nTo view specific assets, type 'ids' and press enter.\n"
        "To view a number of the top assets, type 'assets' and press enter.\n"
        "To explore another data set, type 'moredata' and press enter.\n"
        "To exit, type 'exit' and press enter. \n"
        "NOTE: All results will be displayed in order of market cap descending. "
        )).lower().strip()
        if modeprompt == 'moredata':
            prompts()
            return
        elif modeprompt == 'exit':
            sys.exit()
        elif modeprompt == 'ids':
            print("\n",end="")
            slugs = str(input("Please input a comma-separated string of asset IDs. Spaces are not necessary but will not impact results. ").lower().strip())
            # Could create a helper function for stripping spaces to modularize code further + improve scalability. Not necessary for project, do later
            idlist = slugs.split(",")
            idstrip = [i.strip() for i in idlist]
            stripped = ",".join(idstrip)
            idlength = len(idstrip)

            pages = (idlength // 250) + (1 if idlength % 250 else 0)
            for i in range(1,pages+1):
                response = assets.coin_mkts(ids=stripped,per_page=250,page=i)
                if response:
                    data.extend(response)
                    sleep(2)
                else:
                    continue
            print("Data pulled successfully.\n")

            data = data[:idlength]
            assetsreturned = len(data)
            # Check if number of assets returned by API is equal to number of assets inserted. If not, let the user know and then continue the workflow.
            if assetsreturned == idlength:
                break
            else:
                print("\nNote: Fewer assets were returned than the number of IDs inputted. Perhaps you missed a comma?\n")
                break
        elif modeprompt == 'assets':
            while True:
                try:
                    print("\n",end="")
                    numprompt = int(input("How many assets would you like to view? ").strip())

                    pages = (numprompt // 250) + (1 if numprompt % 250 else 0)
                    for i in range(1,pages+1):
                        response = assets.coin_mkts(per_page=250,page=i)
                        if response:
                            data.extend(response)
                            sleep(2)
                        else:
                            continue
                    print("Data pulled successfully.\n")
                    # Slice list to the number of items requested. This is necessary due to 250 assets/page limit, otherwise asset list would always contain assets in increments of 250.
                    data = data[:numprompt]
                    break
                except ValueError:
                    print("ValueError: Please enter an integer.")
        else:
            print("Please input one of the following commands: 'ids', 'assets', 'moredata', or 'exit'.\n",end="")
            continue
        break

    if not data:
        print("API Error. Returning to home.")
        prompts()
        return
    dict_asset_main,dict_asset_full = a_mkt_dict_build(data)

    dictlen = len(dict_asset_main)
    one_index = range(1, len(dict_asset_main)+1)
    if dictlen > 20:
        toptwenty = dict_asset_main[:20]
        one_index = one_index[:20]
        print("These are the top 20 assets in your list.")
        print(tabulate(toptwenty, headers="keys",showindex=one_index,tablefmt="simple_grid",maxcolwidths=20))
    elif dictlen <= 20:
        print(f"These are the {dictlen} assets in your list.")
        print(tabulate(dict_asset_main, headers="keys",showindex=one_index,tablefmt="simple_grid",maxcolwidths=20))


    while True:
        exportprompt = str(input(
            f"There are {dictlen} assets in your list.\n"
            "To export the displayed fields for all of your assets to a csv, type 'main' and press enter.\n"
            "To export all market data fields displayed fields for all of your assets to a csv, type 'all' and press enter.\n"
            "To skip exporting data and explore another dataset, please type 'moredata' and press enter.\n"
            "To exit, type 'exit' and press enter.\n"
            )).lower().strip()

        if exportprompt == 'moredata':
            break
        elif exportprompt == 'exit':
            sys.exit("Exited successfully.")
        elif exportprompt == 'main':
            print(csv_export(dict_asset_main, "asset_mkt_mainfields"))
            continue
        elif exportprompt == 'all':
            print(csv_export(dict_asset_full, "asset_mkt_allfields"))
            continue
        else:
            print("Please input one of the following commands: 'main', 'all', 'moredata', or 'exit'. \n")
            continue
    prompts()

def a_mkt_dict_build(data: list[dict]) -> tuple[list[dict],list[dict]]:
    """
    Constructs and returns 2 dict lists from coin_mkts data.
    dict_asset_main - A dict list containing select Asset Market fields (Gecko ID, Name, Code, Price, Price %Chg 24h, Mkt Cap, Mkt Cap Diluted, Mkt Cap Rank).
    dict_asset_full - A dict list containing all Asset Market fields.

    :param data: The data returned by the coin_mkts() Method.
    :type data: list[dict]
    :rtype: tuple(list[dict],list[dict])
    """
    dict_asset_main = [
        {
            "Gecko ID": asset["id"],
            "Name": asset["name"],
            "Code": asset["symbol"],
            "Price (USD)": helper_rfmt_usd(asset.get('current_price')) if asset.get('current_price') else "null",
            "Price % Chg 24h": helper_rfmt_pct(asset['price_change_percentage_24h']) if asset['price_change_percentage_24h'] else "null",
            "Mkt Cap": helper_rfmt_usd(asset.get('market_cap')) if asset.get('market_cap') else "null",
            "Mkt Cap Diluted": helper_rfmt_usd(asset['fully_diluted_valuation']) if asset['fully_diluted_valuation'] else "null",
            "Mkt Cap Rank": asset["market_cap_rank"]
        }
            for asset in data
    ]

    dict_asset_full = [
        {
            "Gecko ID": asset["id"],
            "Name": asset["name"],
            "Code": asset["symbol"],
            "Total Volume": helper_rfmt_1000(asset.get('total_volume')) if asset.get('total_volume') else "null",
            "Price (USD)": helper_rfmt_usd(asset.get('current_price')) if asset.get('current_price') else "null",
            "Price Change 24h": helper_rfmt_usd(asset['price_change_24h']) if asset['price_change_24h'] else "null",
            "Price % Chg 24h": helper_rfmt_pct(asset['price_change_percentage_24h']) if asset['price_change_percentage_24h'] else 0,
            "24h High": helper_rfmt_usd(asset['high_24h']) if asset['high_24h'] else "null",
            "24h Low": helper_rfmt_usd(asset['low_24h']) if asset['low_24h'] else "null",
            "Mkt Cap Rank": asset['market_cap_rank'],
            "Mkt Cap": helper_rfmt_usd(asset.get('market_cap')) if asset.get('market_cap') else "null",
            "Mkt Cap Diluted": helper_rfmt_usd(asset['fully_diluted_valuation']) if asset['fully_diluted_valuation'] else "null",
            "Mkt Cap Change 24h ": helper_rfmt_usd(asset['market_cap_change_24h']) if asset['market_cap_change_24h'] else "null",
            "Mkt Cap % Change 24h": helper_rfmt_pct(asset['market_cap_change_percentage_24h']) if asset['market_cap_change_percentage_24h'] else "null",
            "Circulating Supply": helper_rfmt_1000(asset['circulating_supply']) if asset['circulating_supply'] else "null",
            "Total Supply": helper_rfmt_1000(asset['total_supply']) if asset['total_supply'] else "null",
            "Max Supply": helper_rfmt_1000(asset['max_supply']) if asset['max_supply'] else "null",
            "ATH": helper_rfmt_usd(asset.get('ath')) if asset.get('ath') else "null",
            "ATH % Chg": helper_rfmt_pct(asset['ath_change_percentage']),
            "ATH Date": asset["ath_date"],
            "ATL": helper_rfmt_usd(asset.get('atl')) if asset.get('atl') else "null",
            "ATL % Chg": helper_rfmt_pct(asset['atl_change_percentage']),
            "ATL Date": asset["atl_date"],
            "Image": asset.get("image"),
            "Last Updated": asset["last_updated"],
        }
            for asset in data
    ]

    return dict_asset_main,dict_asset_full


def asset_pairs():
    """
    User provides either a Gecko Asset ID to view all market pairs on all exchanges, or a comma-separated list of Gecko Exchange IDs and a Gecko Asset ID to view market pairs on specific exchanges.
    Print tabulated Asset Pair data (Exchange ID, Pair Code, Base Asset, Counter Asset, Last Price (USD), Volume, etc) and allow user to export data from the a_pair_dict_build() list dicts to CSV, explore other datasets, or exit.
    """
    assets = Assets()
    data = []
    coin = []

    while True:
        modeprompt = (
            input("\nTo view the market pairs for an asset on all exchanges, type 'id' and press enter.\n"
        "To select a specific exchange or exchanges, type 'exch' and press enter.\n"
        "To explore another data set, type 'moredata' and press enter.\n"
        "To exit, type 'exit' and press enter. \n"
        "NOTE: All results will be displayed in order of market cap descending. "
        )
        ).lower().strip()

        if modeprompt == 'moredata':
            prompts()
            return
        elif modeprompt == 'exit':
            sys.exit("Exited successfully.")
        elif modeprompt == 'id':
            asset = str(input("\nPlease input an asset ID. This may take a while if your asset has many pairs. ").lower().strip())
            for i in range(1,100):
                response = assets.coin_pairs(id=asset,page=i)
                # Check if the response is the one they give when there's no more data to display. If it is, break out of FOR loop.
                # RegExp would work here, but simply checking if there's data in 'tickers' is much more robust and generally applicable.
                if isinstance(response, dict) and "tickers" in response and not response["tickers"]:
                    break
                elif not response:
                    break
                else:
                    # This endpoint returns a DICT rather than a LIST of DICTs. Used APPEND rather than EXTEND here so that I can keep the code as generalized as possible rather than having to reference the ["tickers"] list within the response.
                    data.append(response)
                    sleep(2)
            coin = asset
            print("Data pulled successfully.\n",end="")
            break
        elif modeprompt == 'exch':
            exchange = str(input("\nPlease input comma-separated Exchange ID(s). ").lower().strip())
            asset = str(input("Please input an asset ID. This may take a while if your asset has many pairs. ").lower().strip())
            for i in range(1,100):
                response = assets.coin_pairs(id=asset,page=i,exchange_ids=exchange)
                if isinstance(response, dict) and "tickers" in response and not response["tickers"]:
                    break
                elif not response:
                    break
                else:
                    data.append(response)
                    sleep(2)
            coin = asset
            print("Data pulled successfully.\n",end="")
            break
        else:
            print("Please input one of the following commands: 'id', 'exch', 'moredata', or 'exit'.\n",end="")
            continue

    if not data:
        print("API Error. Returning to home.")
        prompts()
        return
    dict_asset_exch_summary,dict_asset_pair_main,dict_asset_pair_full = a_pair_dict_build(data)

    dictlen = len(dict_asset_pair_main)
    if dictlen > 20:
        toptwenty = dict_asset_pair_main[:20]
        print(tabulate(toptwenty, headers="keys",showindex=False,tablefmt="simple_grid",maxcolwidths=20))
        print("These are the first 20 Markets in your list for {coin}.")
    elif dictlen <= 20:
        print(tabulate(dict_asset_pair_main, headers="keys",showindex=False,tablefmt="simple_grid",maxcolwidths=20))


    while True:
        """ User selects next step: Export either Dict List to a CSV, view more data, or exit program. If user exports to CSV, they are then given option to view more data. """
        exportprompt = str(input(
            f"\nThere are {dictlen} pairs across {len(dict_asset_exch_summary)} exchanges in your list.\n"
            "To export the displayed fields for all of your assets to a csv, type 'main' and press enter.\n"
            "To export all market data fields displayed fields for all of your assets to a csv, type 'all' and press enter.\n"
            "To export a summary CSV containing the unique exchanges and a count of their markets that include your asset, type 'summary' and press enter.\n"
            "To explore another dataset, type 'moredata' and press enter.\n"
            "To exit, type 'exit' and press enter.\n"
            )).lower().strip()

        if exportprompt == 'moredata':
            break
        elif exportprompt == 'exit':
            sys.exit("Exited successfully.")
        elif exportprompt == 'main':
            print(csv_export(dict_asset_pair_main, f"pair_list_mainfields_{coin}"))
            continue
        elif exportprompt == 'all':
            print(csv_export(dict_asset_pair_full, f"pair_list_allfields_{coin}"))
            continue
        elif exportprompt == 'summary':
            print(csv_export(dict_asset_exch_summary, f"exch_pair_summary_{coin}"))
            continue
        else:
            print("Please input one of the following commands: 'main', 'all', 'summary', 'moredata', or 'exit'. \n",end="")
            continue
    prompts()

def a_pair_dict_build(data: dict[list[dict]]) -> tuple[list[dict],list[dict],list[dict]]:
    """
    Constructs and returns 3 dict lists from coin_mkts() data.
    dict_asset_exch_summary - A dict list containing a summary of the number of markets an asset has on each exchange.
    dict_asset_pair_main - A dict list containing select fields for each market pair that the asset has on each exchange.
    dict_asset_pair_full - A dict list containing all fields for each market pair that the asset has on each exchange.

    :param data: The data returned by the coin_mkts() Method.
    :type data: dict[list[dict]]
    :rtype: tuple(list[dict],list[dict],list[dict])
    """

    exch_counts = Counter(pair["market"]["name"] for page in data for pair in page["tickers"])
    dict_asset_exch_summary = [
        {"Exchange": name, "Markets": count}
        for name, count in exch_counts.items()
    ]

    dict_asset_pair_main = [
        {
            "Exchange Name": pair["market"]["name"],
            "Trading Pair": f"{pair['base']}-{pair['target']}",
            "Base Asset": pair["base"],
            "Quote Asset": pair["target"],
            "Last Price (Quote)": f"{helper_rfmt_1000(pair['last'])} {pair['target']}",
            "Last Price (USD)": helper_rfmt_usd(pair['converted_last']['usd']),
            "Volume": helper_rfmt_1000(pair['volume']),
            "Market URL": pair["trade_url"],
        }
            # Filter stale data out of the output
            for page in data
            for pair in page["tickers"] if not pair["is_stale"]
    ]

    # Fields referenced with ".get" are sometimes not included in API output
    dict_asset_pair_full = [
        {
            "Exchange Name": pair["market"]["name"],
            "Trading Pair": f"{pair['base']}-{pair['target']}",
            "Base Asset": pair["base"],
            "Quote Asset": pair["target"],
            "Last Price (Quote)": f"{helper_rfmt_1000(pair['last'])} {pair['target']}",
            "Last Price (BTC)": helper_rfmt_1000(pair['converted_last']['btc']),
            "Last Price (ETH)": helper_rfmt_1000(pair['converted_last']['eth']),
            "Last Price (USD)": helper_rfmt_usd(pair['converted_last']['usd']),
            "Base Asset Mkt Cap (USD)": helper_rfmt_usd(pair.get('coin_mcap_usd')) if pair.get('coin_mcap_usd') else "null",
            "Cost to Move Up (USD)": helper_rfmt_usd(pair.get('cost_to_move_up_usd')) if pair.get('cost_to_move_up_usd') else "null",
            "Cost to Move Down (USD)": helper_rfmt_usd(pair.get('cost_to_move_down_usd')) if pair.get('cost_to_move_down_usd') else "null",
            "Volume": helper_rfmt_1000(pair['volume']),
            "Volume (BTC)": helper_rfmt_1000(pair['converted_volume']['btc']),
            "Volume (ETH)": helper_rfmt_1000(pair['converted_volume']['eth']),
            "Volume (USD)": helper_rfmt_usd(pair['converted_volume']['usd']),
            "Trust Score": pair["trust_score"],
            "Bid/Ask Spread %": helper_rfmt_pct(pair.get('bid_ask_spread_percentage')) if pair.get('bid_ask_spread_percentage') else "null",
            "Timestamp": pair["timestamp"],
            "Last Traded At": pair["last_traded_at"],
            "Last Fetch At": pair["last_fetch_at"],
            "Is Anomaly": pair["is_anomaly"],
            "Market URL": pair["trade_url"],
            "Exchange Has Trading Incentive?": pair["market"].get("has_trading_incentive"),
            "Exchange Logo": pair["market"].get("logo"),
            "CoinGecko Exchange ID": pair["market"].get("identifier"),
            "CoinGecko Base Asset ID": pair["coin_id"],
            "CoinGecko Quote Asset ID": pair.get("target_coin_id") if pair.get("target_coin_id") else "null",
            "Token Info URL": pair.get("token_info_url") if pair.get("token_info_url") else "null"
        }
            # Filter stale data out of the output
            for page in data
            for pair in page["tickers"] if not pair["is_stale"]
    ]

    return dict_asset_exch_summary,dict_asset_pair_main,dict_asset_pair_full


def exchange_list():
    """
    User provides input on whether they would like to see a basic list of exchange names and Gecko IDs, expanded data on a number of top exchanges, or expanded data on all exchanges.
    Print tabulated Exchange information (Gecko Exch ID, Exch Name, Year Established, Country, Description, URL, etc) and allow user to export data from the e_list_basic_dict_build() or e_list_dict_build() list dicts to CSV, explore other datasets, or exit.
    """
    exchanges = Exchanges()
    data = []

    exch_list_base = exchanges.exch_list()
    if not exch_list_base:
        print("API Error pulling base exchange list. Returning to home.")
        prompts()
        return
    exch_count = len(exch_list_base)

    while True:
        modeprompt = input(
        f"\nThere are {exch_count} exchanges with data on CoinGecko.\n"
        "To see a basic list of Exchange Names and CoinGecko IDs, type 'basic' and press enter.\n"
        "To see expanded data on a certain number of the top exchanges, type 'some' and press enter.\n"
        "To see expanded data on all exchanges, type 'all' and press enter.\n"
        "To explore another data set, type 'moredata' and press enter.\n"
        "To exit, type 'exit' and press enter.\n"
        "NOTE: All expanded data will be sorted by CoinGecko Trust Score Rank. Some exchanges do not yet have a Trust Score. \n"
        f"NOTE: Expanded data may not be available for all {exch_count} exchanges. "
                             ).lower().strip()
        if modeprompt == 'moredata':
            prompts()
            return
        elif modeprompt == 'exit':
            sys.exit("Exited successfully.")
        elif modeprompt == 'basic':
            break
        elif modeprompt == 'some':
            while True:
                try:
                    numprompt = int(input("How many exchanges would you like to see? ").strip())
                    # Could move pages calc into a helper function that references a dict containing max items per page for each endpoint. Not necessary for project but useful for scaling
                    pages = (numprompt // 250) + (1 if numprompt % 250 else 0)
                    for i in range(1,pages+1):
                        response = exchanges.exch_data(page = i, per_page = 250)
                        if response:
                            data.extend(response)
                            sleep(2)
                        else:
                            continue
                    data = data[:numprompt]
                    print("Data pulled successfully.\n")
                    break
                except ValueError:
                    print("ValueError: Please provide an integer value.")
                    continue
            break
        elif modeprompt == 'all':
            print("This may take a minute. Hang in there, pal.")
            pages = (exch_count // 250) + (1 if exch_count % 250 else 0)
            for i in range(1,pages+1):
                response = exchanges.exch_data(page = i, per_page = 250)
                if response:
                    data.extend(response)
                    sleep(2)
                else:
                    continue
            print("Exchange Data pulled successfully.\n")
            break
        else:
            print("Please input one of the following commands: 'basic', 'some', 'all', 'moredata', 'exit'. ",end="")
            continue

    first_twenty = []
    if not data:
        print("Only basic Exchange List is available.")
        # If data is empty (i.e the user just wants to see basic list), compile first_twenty list from the dict_exch_list_simple. Otherwise, compile from dict_exch_list_data.
        dict_exch_list_simple = e_list_basic_dict_build(exch_list_base)
        first_twenty = dict_exch_list_simple[:20]
    else:
        dict_exch_list_simple = e_list_basic_dict_build(exch_list_base)
        dict_exch_list_data,dict_exch_list_data_print = e_list_dict_build(data)
        first_twenty = dict_exch_list_data_print[:20]
        exch_count = len(dict_exch_list_data_print)

    # Return the first 20 exchanges in tabulated form. If they want to see the whole list, they can export to a csv.
    print(tabulate(first_twenty, headers="keys",showindex=False,tablefmt="simple_grid",maxcolwidths=20))
    while True:
        exportprompt = str(input(
            f"\nThere are a total of {exch_count} exchanges in your list.\n"
            "To view them all and then select another exchange dataset or exit the program, please export to a csv by typing 'listcsv' and press enter.\n"
            "To view further data on an exchange, such as information about the exchange, its social media links, and its top 100 trading pairs, type 'exch' and press enter.\n"
            "To view all of the trading pairs on an exchange, type 'pairs' and press enter.\n"
            "To skip exporting data and explore another dataset, type 'moredata'.\n"
            "To exit, type 'exit' and press enter. "
            )).lower().strip()

        if exportprompt == 'moredata':
            prompts()
            return
        elif exportprompt == 'exit':
            sys.exit("Exited successfully.")
        # Resetting the loop after exporting simplifies code. User can export and then look at other datasets or exit without me needing to nest other CSV exports/create additional commands.
        #### However, I don't love the "and data/and not data" piece because if "data" is populated then the user can't export simple list even though it exists.
        elif exportprompt == 'listcsv' and not data:
            print(csv_export(dict_exch_list_simple, "exch_list_simple"))
            continue
        elif exportprompt == 'listcsv' and data:
            print(csv_export(dict_exch_list_data, "exch_list_data"))
            continue
        elif exportprompt == 'exch':
            print("\n")
            exchange_top100()
            break
        elif exportprompt == 'pairs':
            print("\n")
            exchange_pairs()
            break
        else:
            print("Please input one of the following commands: 'listcsv', 'exch', 'pairs', 'moredata', or 'exit'. \n")
            continue

def e_list_basic_dict_build(exch_list_base: list[dict]) -> list[dict]:
    """
    Constructs and returns a simple dict list from exch_list() data.
    dict_exch_list_simple - A dict list containing Exchange Names and CoinGecko Exchange IDs.

    :param exch_list_base: Data returned by the exch_list() Method.
    :type exch_list_base: list[dict]
    :rtype: list[dict]
    """
    dict_exch_list_simple = [
        {
            "Gecko Exchange ID": exchange["id"],
            "Exchange Name": exchange["name"]
        }
        for exchange in exch_list_base
    ]

    return dict_exch_list_simple

def e_list_dict_build(data: list[dict]) -> tuple[list[dict],list[dict]]:
    """
    Constructs and returns 2 dict lists from exch_data() data.
    dict_exch_list_data - A dict list containing expanded exchange data.
    dict_exch_list_data_print - Identical to dict_exch_list_data with the exception of data in the "Description" field, which is replaced with "See CSV" to improve readability when printed to console.

    :param data: Data returned by the exch_data() Method.
    :type data: list[dict]
    :rtype: tuple(list[dict],list[dict])
    """
    dict_exch_list_data = [
        {
            "Gecko Exch ID": exchange["id"],
            "Exch Name": exchange["name"],
            "Year Established": exchange["year_established"] if exchange["year_established"] else "null",
            "Country": exchange["country"] if exchange["country"] else "null",
            "Description": exchange["description"] if exchange["description"] else "null",
            "URL": exchange["url"] if exchange["url"] else "null",
            "Trust Score": exchange["trust_score"] if exchange["trust_score"] else "null",
            "Trust Score Rank": exchange["trust_score_rank"] if exchange["trust_score_rank"] else "null",
            "24H BTC Trade Volume": exchange["trade_volume_24h_btc"],
            "Has Trading Incentive": exchange["has_trading_incentive"] if exchange["has_trading_incentive"] in [True, False] else "null",
        }
        for exchange in data
    ]

    # Replaces data in "description" field because of its length
    dict_exch_list_data_print = [
        {
            "Gecko Exch ID": exchange["Gecko Exch ID"],
            "Exch Name": exchange["Exch Name"],
            "Year Established": exchange["Year Established"],
            "Country": exchange["Country"],
            "Description": "See CSV",
            "URL": exchange["URL"],
            "Trust Score": exchange["Trust Score"],
            "Trust Score Rank": exchange["Trust Score Rank"],
            "24H BTC Trade Volume": exchange["24H BTC Trade Volume"],
            "Has Trading Incentive": exchange["Has Trading Incentive"],
        }
        for exchange in dict_exch_list_data
    ]

    return dict_exch_list_data,dict_exch_list_data_print


def exchange_top100():
    """
    User provides Gecko Exchange IDs either one at a time or as a comma-separated list.
    Print tabulated information on an exchange's Top 100 Market Pairs (Exch Name, Trading Pair, Base Asset, Quote Asset, Last Price (USD), etc) and allow user to export data from the e_top100_dict_build() list dicts to CSV, explore other datasets, or exit.
    """
    exchanges = Exchanges()
    data = []

    while True:
        modeprompt = str(input(
            f"\nTo see exchange data and the top 100 assets for a single exchange, type 'single' and press enter.\n"
            "To see the above data for multiple exchanges, type 'multiple' and press enter.\n"
            "To explore another data set, type 'moredata' and press enter.\n"
            "To exit, type 'exit' and press enter.\n"
            "NOTE: All data will be ranked by CoinGecko Trust Score. "
                                ).lower().strip())
        if modeprompt == 'moredata':
            prompts()
            return
        elif modeprompt == 'exit':
            sys.exit("Exited successfully.")
        elif modeprompt == 'single':
            while True:
                exchid = str(input("Please input a CoinGecko Exchange ID. ")).lower().strip()
                response = exchanges.exch_top100(id = exchid)
                if response:
                    data.append(response)
                    print("Data acquired successfully.")
                    again=[]
                    while True:
                        again = input("Would you like to add another exchange's data? Say 'yes' to add another exchange, or 'no' to move to the next part of the workflow. ").strip().lower()
                        if again in ["yes","no"]:
                            break
                        else:
                            print("Please say 'yes' or 'no'.")
                    if again == "yes":
                        continue
                    else:
                        break
                else:
                    continue
            break
        elif modeprompt == 'multiple':
            exids = str(input("Please input a comma-separated list of CoinGecko Exchange IDs. Spaces are not necessary but will not impact results. ").lower())
            exidsplit = exids.split(",")
            exidstrip = [i.strip() for i in exidsplit]
            while True:
                for exch in exidstrip:
                    response = exchanges.exch_top100(id = exch)
                    if response:
                        data.append(response)
                        sleep(2)
                    else:
                        continue
                break
            break
        else:
            print("Please input one of the following commands: 'single', 'multiple', 'moredata', or 'exit'. \n",end="")


    if not data:
        print("API Error. Returning to home.")
        prompts()
        return
    dict_exch_top100_main,dict_exch_top100_full,dict_exch_top100_data = e_top100_dict_build(data)

    first_twenty = dict_exch_top100_main[:20]
    print(tabulate(first_twenty, headers="keys",showindex=False,tablefmt="simple_grid",maxcolwidths=20))


    while True:
        exportprompt = str(input(
            f"\nThere are {len(dict_exch_top100_main)} pairs on {len(dict_exch_top100_data)} exchanges available for export.\n"
            "To view all of your data, please export to a csv with one of the following commands. \n"
            "To export exchange-level data, such as Exchange Name, Description, number of assets available for trading, and associated URLS, type 'exch' and hit enter.\n"
            "To export the pair-related datapoints seen in the above table, type 'basic' and hit enter.\n"
            "To export all pair-related datapoints, type 'all' and hit enter.\n"
            "To explore another dataset, type 'moredata' and hit enter.\n"
            "To exit, type 'exit' and hit enter. "
            )).lower().strip()

        if exportprompt == 'moredata':
            break
        elif exportprompt == 'exit':
            sys.exit("Exited successfully.")
        elif exportprompt == 'exch':
            print(csv_export(dict_exch_top100_data, "exch_info"))
            continue
        elif exportprompt == 'basic':
            print(csv_export(dict_exch_top100_main, "top100_mainfields"))
        elif exportprompt == 'all':
            print(csv_export(dict_exch_top100_full, "top100_allfields"))
        else:
            print("Please input one of the following commands: 'exch', 'basic', 'all', 'moredata', or 'exit'. \n",end="")
    prompts()

def e_top100_dict_build(data: dict[list[dict]]) -> tuple[list[dict],list[dict],list[dict]]:
    """
    Constructs and returns 3 dict lists from exch_top100() data.
    dict_exch_top100_main - A dict list containing select fields for each of the top 100 market pairs on each exchange.
    dict_exch_top100_full - A dict list containing all fields for each of the top 100 market pairs on each exchange.
    dict_exch_top100_data - A dict list containing exchange-level data for each exchange queried.

    :param data: Data returned by the exch_top100() Method.
    :type data: dict[list[dict]]
    :rtype: tuple(list[dict],list[dict],list[dict])
    """
    dict_exch_top100_main = [
        {
            "Exch Name": page["name"],
            "Gecko Exch ID": pair["market"]["identifier"],
            "Trading Pair": f"{pair['base']}-{pair['target']}",
            "Base Asset": pair["base"],
            "Quote Asset": pair["target"],
            "Last Price (Quote)": f"{helper_rfmt_1000(pair['last'])} {pair['target']}",
            "Last Price (USD)": helper_rfmt_usd(pair['converted_last']['usd']),
            "Volume": helper_rfmt_1000(pair['volume']),
            "Market URL": pair["trade_url"],
        }
            # Don't need to include the "if not pair[is_stale]" clause because these are all top 100 assets
            for page in data
            for pair in page["tickers"]
    ]

    # Only pair-level API field not included in this output is "is_stale" for the same reason it's not needed in the FOR loop definition
    dict_exch_top100_full = [
        {
            "Exchange Name": pair["market"]["name"],
            "Trading Pair": f"{pair['base']}-{pair['target']}",
            "Base Asset": pair["base"],
            "Quote Asset": pair["target"],
            "Last Price (Quote)": f"{helper_rfmt_1000(pair['last'])} {pair['target']}",
            "Last Price (BTC)": helper_rfmt_1000(pair['converted_last']['btc']),
            "Last Price (ETH)": helper_rfmt_1000(pair['converted_last']['eth']),
            "Last Price (USD)": helper_rfmt_usd(pair['converted_last']['usd']),
            "Base Asset Mkt Cap (USD)": helper_rfmt_usd(pair.get('coin_mcap_usd')) if pair.get('coin_mcap_usd') else "null",
            "Volume": helper_rfmt_1000(pair['volume']),
            "Volume (BTC)": helper_rfmt_1000(pair['converted_volume']['btc']),
            "Volume (ETH)": helper_rfmt_1000(pair['converted_volume']['eth']),
            "Volume (USD)": helper_rfmt_usd(pair['converted_volume']['usd']),
            "Trust Score": pair["trust_score"],
            "Bid/Ask Spread %": helper_rfmt_pct(pair.get('bid_ask_spread_percentage')) if pair.get('bid_ask_spread_percentage') else "null",
            "Timestamp": pair["timestamp"],
            "Last Traded At": pair["last_traded_at"],
            "Last Fetch At": pair["last_fetch_at"],
            "Is Anomaly": pair["is_anomaly"],
            "Market URL": pair["trade_url"],
            "Exchange Has Trading Incentive?": pair["market"].get("has_trading_incentive"),
            "Exchange Logo": pair["market"].get("logo"),
            "CoinGecko Exchange ID": pair["market"].get("identifier"),
            "CoinGecko Base Asset ID": pair["coin_id"],
            "CoinGecko Quote Asset ID": pair.get("target_coin_id"),
            "Token Info URL": pair.get("token_info_url") if pair.get("token_info_url") else "null"
        }
            for page in data
            for pair in page["tickers"]
    ]

    dict_exch_top100_data = [
        {
            "Exch Name": exch["name"],
            "CEX": exch["centralized"],
            "# Coins Listed": exch["coins"],
            "# Pairs Listed": exch["pairs"],
            "Year Established": exch["year_established"],
            "Country": exch["country"],
            "Description": exch["description"],
            "URL": exch["url"],
            "Trust Score": exch["trust_score"],
            "Trust Score Rank": exch["trust_score_rank"],
            "24H BTC Trade Volume": exch["trade_volume_24h_btc"],
            "Has Trading Incentive": exch["has_trading_incentive"],
            "Facebook": exch["facebook_url"],
            "Reddit": exch["reddit_url"],
            "Twitter ": f"https://x.com/{exch['twitter_handle']}",
            "Telegram": exch["telegram_url"],
            "Slack": exch["slack_url"],
            "Other URL 1": exch["other_url_1"],
            "Other URL 2": exch["other_url_2"],
            "Public Notice": exch["public_notice"],
            "Alert Notice": exch["alert_notice"],
            "Logo Image": exch["image"],
        }
            for exch in data
    ]

    return dict_exch_top100_main,dict_exch_top100_full,dict_exch_top100_data


def exchange_pairs():
    """
    User provides a comma-separated string of Gecko Asset IDs and a Gecko Exchange ID, or just a Gecko Exchange ID.
    Print tabulated information on an exchange's Market Pairs (Exch Name, Trading Pair, Base Asset, Quote Asset, Last Price (USD), etc) and allow user to export data from the e_pair_dict_build() list dicts to CSV, explore other datasets, or exit.
    """
    exchanges = Exchanges()
    data = []
    exch_name = []

    while True:
        modeprompt = (
            input("\nTo view the market pairs for specific assets on an exchange, type 'id' and press enter.\n"
            "To view the market pairs for all assets on an exchange, type 'exch' and press enter.\n"
            "To explore another data set, type 'moredata' and press enter.\n"
            "To exit, type 'exit' and press enter. \n"
            "NOTE: All results will be displayed in order of market cap descending. "
            )).lower().strip()

        if modeprompt == 'moredata':
            prompts()
            return
        elif modeprompt == 'exit':
            sys.exit("Exited successfully.")
        elif modeprompt == 'id':
            assets = str(input("\nPlease input a comma-separated list of CoinGecko Asset IDs. ").lower().strip())
            exch = str(input("Please input a CoinGecko Exchange ID. ").lower().strip())
            for i in range(1,100):
                response = exchanges.exch_pairs(id=exch,coin_ids=assets,page=i)
                if isinstance(response, dict) and "tickers" in response and not response["tickers"]:
                    break
                elif not response:
                    break
                else:
                    data.append(response)
                    sleep(2)
            exch_name = exch
            print("Data pulled successfully. ")
        elif modeprompt == 'exch':
            exch = str(input("\nPlease input a CoinGecko Exchange ID. ").lower().strip())
            for i in range(1,100):
                response = exchanges.exch_pairs(id=exch,page=i)
                if isinstance(response, dict) and "tickers" in response and not response["tickers"]:
                    break
                elif not response:
                    break
                else:
                    data.append(response)
                    sleep(2)
            exch_name = exch
            print("Data pulled successfully. ")
        else:
            print("Please input one of the following commands: 'id', 'exch', 'moredata', or 'exit'.\n")
            continue
        break


    if not data:
        print("API Error. Returning to home.")
        prompts()
        return
    dict_exch_pair_main,dict_exch_pair_full_fresh,dict_exch_pair_full_stale,asset_count_list = e_pair_dict_build(data)

    dictlen = len(dict_exch_pair_main)
    if dictlen > 20:
        toptwenty = dict_exch_pair_main[:20]
        print(tabulate(toptwenty, headers="keys",showindex=False,tablefmt="simple_grid",maxcolwidths=20))
        print("These are the first 20 markets in your list for {exch_name}.")
    elif dictlen <= 20:
        print(tabulate(dict_exch_pair_main, headers="keys",showindex=False,tablefmt="simple_grid",maxcolwidths=20))


    while True:
        """ User selects next step: Export either Dict List to a CSV, view more data, or exit program. If user exports to CSV, they are then given option to view more data. """
        exportprompt = str(input(
            f"\nThe {dictlen} non-stale markets in your {exch_name} data are composed of {len(asset_count_list)} assets.\n"
            "To export the displayed fields for all of the non-stale markets returned to a csv, type 'main' and press enter.\n"
            "To export all market data fields displayed fields for all of the non-stale markets returned to a csv, type 'fresh' and press enter.\n"
            "To export all market data fields displayed fields for all of the markets returned, including stale ones, to a csv, type 'stale' and press enter.\n"
            "To export a list of the assets returned, their CoinGecko IDs, and a count of how many pairs they are in, type 'assets' and press enter.\n"
            "To explore another dataset, type 'moredata' and press enter.\n"
            "To exit, type 'exit' and press enter.\n"
            )).lower().strip()

        if exportprompt == 'moredata':
            break
        elif exportprompt == 'exit':
            sys.exit("Exited successfully.")
        elif exportprompt == 'main':
            print(csv_export(dict_exch_pair_main, f"{exch_name}_fresh_pair_list_mainfields"))
            continue
        elif exportprompt == 'fresh':
            print(csv_export(dict_exch_pair_full_fresh, f"{exch_name}_fresh_pair_list_allfields"))
            continue
        elif exportprompt == 'stale':
            print(csv_export(dict_exch_pair_full_stale, f"{exch_name}_stale_pair_list_allfields"))
            continue
        elif exportprompt == 'assets':
            print(csv_export(asset_count_list, f"{exch_name}_asset_counts"))
            continue
        else:
            print("Please input one of the following commands: 'main', 'fresh', 'stale', 'moredata', or 'exit'. \n",end="")
            continue
    prompts()

def e_pair_dict_build(data: dict[list[dict]]) -> tuple[list[dict],list[dict],list[dict],list[dict]]:
    """
    Constructs and returns 4 dict lists from exch_top100() data.
    dict_exch_pair_main - A dict list containing select fields for each market pair on an exchange.
    dict_exch_pair_full_fresh - A dict list containing all fields for each market pair on an exchange. Excludes stale data.
    dict_exch_pair_full_stale - A dict list containing all fields for each market pair on an exchange. Includes stale data.
    asset_count_list - A summary dict list of unique assets and how many pairs they are available to trade in on the exchange.

    :param data: Data returned by the exch_top100() Method.
    :type data: dict[list[dict]]
    :rtype: tuple(list[dict],list[dict],list[dict],list[dict])
    """

    dict_exch_pair_main = [
        {
            "Exchange Name": pair["market"]["name"],
            "Trading Pair": f"{pair['base']}-{pair['target']}",
            "Base Asset": pair["base"],
            "Quote Asset": pair["target"],
            "Last Price (Quote)": f"{helper_rfmt_1000(pair['last'])} {pair['target']}",
            "Last Price (USD)": helper_rfmt_usd(pair['converted_last']['usd']),
            "Volume": helper_rfmt_1000(pair['volume']),
            "Market URL": pair["trade_url"],
        }
            # Filter stale data out of the output
            for page in data
            for pair in page["tickers"] if not pair["is_stale"]
    ]

    # Fields referenced with ".get" are sometimes not included in API output
    dict_exch_pair_full_fresh = [
        {
            "Exchange Name": pair["market"]["name"],
            "Trading Pair": f"{pair['base']}-{pair['target']}",
            "Base Asset": pair["base"],
            "Quote Asset": pair["target"],
            "Last Price (Quote)": f"{helper_rfmt_1000(pair['last'])} {pair['target']}",
            "Last Price (BTC)": helper_rfmt_1000(pair['converted_last']['btc']),
            "Last Price (ETH)": helper_rfmt_1000(pair['converted_last']['eth']),
            "Last Price (USD)": helper_rfmt_usd(pair['converted_last']['usd']),
            "Base Asset Mkt Cap (USD)": helper_rfmt_usd(pair.get('coin_mcap_usd')) if pair.get('coin_mcap_usd') else "null",
            "Cost to Move Up (USD)": helper_rfmt_usd(pair.get('cost_to_move_up_usd')) if pair.get('cost_to_move_up_usd') else "null",
            "Cost to Move Down (USD)": helper_rfmt_usd(pair.get('cost_to_move_down_usd')) if pair.get('cost_to_move_down_usd') else "null",
            "Volume": helper_rfmt_1000(pair['volume']),
            "Volume (BTC)": helper_rfmt_1000(pair['converted_volume']['btc']),
            "Volume (ETH)": helper_rfmt_1000(pair['converted_volume']['eth']),
            "Volume (USD)": helper_rfmt_usd(pair['converted_volume']['usd']),
            "Trust Score": pair["trust_score"],
            "Bid/Ask Spread %": helper_rfmt_pct(pair.get('bid_ask_spread_percentage')) if pair.get('bid_ask_spread_percentage') else "null",
            "Timestamp": pair["timestamp"],
            "Last Traded At": pair["last_traded_at"],
            "Last Fetch At": pair["last_fetch_at"],
            "Is Anomaly": pair["is_anomaly"],
            "Market URL": pair["trade_url"],
            "Exchange Has Trading Incentive?": pair["market"].get("has_trading_incentive"),
            "Exchange Logo": pair["market"].get("logo"),
            "CoinGecko Exchange ID": pair["market"].get("identifier"),
            "CoinGecko Base Asset ID": pair["coin_id"],
            "CoinGecko Quote Asset ID": pair.get("target_coin_id"),
            "Token Info URL": pair.get("token_info_url") if pair.get("token_info_url") else "null"
        }
            # Filter stale data out of the output
            for page in data
            for pair in page["tickers"] if not pair["is_stale"]
    ]

    dict_exch_pair_full_stale = [
        {
            "Exchange Name": pair["market"]["name"],
            "Trading Pair": f"{pair['base']}-{pair['target']}",
            "Base Asset": pair["base"],
            "Quote Asset": pair["target"],
            "Is Stale": pair["is_stale"],
            "Last Price (Quote)": f"{helper_rfmt_1000(pair['last'])} {pair['target']}",
            "Last Price (BTC)": helper_rfmt_1000(pair['converted_last']['btc']),
            "Last Price (ETH)": helper_rfmt_1000(pair['converted_last']['eth']),
            "Last Price (USD)": helper_rfmt_usd(pair['converted_last']['usd']),
            "Base Asset Mkt Cap (USD)": helper_rfmt_usd(pair.get('coin_mcap_usd')) if pair.get('coin_mcap_usd') else "null",
            "Cost to Move Up (USD)": helper_rfmt_usd(pair.get('cost_to_move_up_usd')) if pair.get('cost_to_move_up_usd') else "null",
            "Cost to Move Down (USD)": helper_rfmt_usd(pair.get('cost_to_move_down_usd')) if pair.get('cost_to_move_down_usd') else "null",
            "Volume": helper_rfmt_1000(pair['volume']),
            "Volume (BTC)": helper_rfmt_1000(pair['converted_volume']['btc']),
            "Volume (ETH)": helper_rfmt_1000(pair['converted_volume']['eth']),
            "Volume (USD)": helper_rfmt_usd(pair['converted_volume']['usd']),
            "Trust Score": pair["trust_score"],
            "Bid/Ask Spread %": helper_rfmt_pct(pair.get('bid_ask_spread_percentage')) if pair.get('bid_ask_spread_percentage') else "null",
            "Timestamp": pair["timestamp"],
            "Last Traded At": pair["last_traded_at"],
            "Last Fetch At": pair["last_fetch_at"],
            "Is Anomaly": pair["is_anomaly"],
            "Market URL": pair["trade_url"],
            "Exchange Has Trading Incentive?": pair["market"].get("has_trading_incentive"),
            "Exchange Logo": pair["market"].get("logo"),
            "CoinGecko Exchange ID": pair["market"].get("identifier"),
            "CoinGecko Base Asset ID": pair["coin_id"],
            "CoinGecko Quote Asset ID": pair.get("target_coin_id"),
            "Token Info URL": pair.get("token_info_url") if pair.get("token_info_url") else "null"
        }
            for page in data
            for pair in page["tickers"]
    ]

    # Get a count of each unique asset across all pairs in list
    asset_counts = Counter()
    for pair in dict_exch_pair_full_fresh:
        base_code = pair["Base Asset"]
        base_id = pair["CoinGecko Base Asset ID"]
        asset_counts[(base_code,base_id)] += 1
        quote_code = pair["Quote Asset"]
        quote_id = pair["CoinGecko Quote Asset ID"]
        asset_counts[(quote_code,quote_id)] += 1
    asset_count_list = [{"Asset": asset_symbol, "CoinGecko Asset ID": asset_id, "Count": count} for (asset_symbol,asset_id), count in asset_counts.items()]
    asset_count_list.sort(key=lambda x: x["Count"], reverse=True)

    return dict_exch_pair_main,dict_exch_pair_full_fresh,dict_exch_pair_full_stale,asset_count_list


def helper_rfmt_usd(num: float) -> str:
    """
    Convert a value to USD format with 2 decimal places (i.e. 1000.5214 = $1,000.52). Input can be float or integer.

    :param num:
    :type num: float
    :rtype: str
    """
    usd = f"${num:,.2f}"
    return usd

def helper_rfmt_1000(num: float) -> str:
    """
    Convert a value to thousands format with 2 decimal places (i.e. 1000.5214 = 1,000.52). Input can be float or integer.

    :param num:
    :type num: float
    :rtype: str
    """
    thousands = f"{num:,.2f}"
    return thousands

def helper_rfmt_pct(num: float) -> str:
    """
    Convert a value to percentage format with 5 decimal places (i.e. 5.10274 = 5.10274%). Input should be in percentage points.

    :param num:
    :type num: float
    :rtype: str
    """
    pct = f"{(num/100):.5%}"
    return pct


def csv_export(output: list[dict], prefix: str) -> str | None:
    """
    Export data to a CSV. If no data is available, return to prompts().

    :param output: Dictionary containing relevant function's data.
    :type output: list[dict]
    :param prefix: Descriptive component of filename.
    :type prefix: str
    """
    if not output:
        print("No data. Please try again.")
        prompts()
        return

    timestamp: datetime = datetime.now().strftime("%Y%m%d%H%M%S")
    filename: str = f"{prefix}_{timestamp}.csv"

    fileheaders = output[0].keys()

    with open(filename, "w" ,newline="") as file:
        writer = csv.DictWriter(file, fieldnames = fileheaders)
        writer.writeheader()
        writer.writerows(output)

    return f"CSV exported successfully! Filename: {filename}\n"



if __name__ == "__main__":
    main()


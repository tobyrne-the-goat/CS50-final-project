# CoinGecko Asset & Exchange Data Puller
#### Video Demo: https://www.youtube.com/watch?v=t1z-Nwgl3ZA
## Description:
Welcome to the CoinGecko Asset & Exchange Data Puller, your easy-to-use tool for downloading and exploring data from CoinGecko's APIs!

Are you tired of slogging through Crypto Data Provider websites like CoinGecko, looking at one coin or exchange at a time, manually copy + pasting + reformatting the data you want into spreadsheets? Do you wish it were easier to get a broader view of the Crypto markets, instead of frantically jumping between the hundreds of tabs you have open on your browser, so that you can just get on with the money making? Well friend, wish and be tired no longer. With a few simple inputs, you can download CSVs containing a wide variety of Asset, Market, Pair, & Exchange Data straight from CoinGecko's APIs!

Keep in mind, CoinGecko's data is expansive and fairly well managed but it is by no means complete. They do not have data on every asset and exchange that exists, and the ones that they do have data for may not have every datapoint populated or some static (non-price) datapoints may be out of date or lagged. That being said, the data for major assets and exchanges is much more often than not complete and up-to-date.

## Project Files
* `project.py` - Main body of code.
* `test_project.py` - Unit tests for several Functions/Methods in code.
* `requirements.txt` - pip-installable libraries used in project files.
* `README.md` - Description of code usage, components, quirks, and design choices.

## Libraries
[pytest](https://pypi.org/project/pytest/): The pytest framework makes it easy to write small tests, yet scales to support complex functional testing for applications and libraries.

**Note**: The `pytest` library is required to run `test_project.py`, **not** `project.py`.

[requests](https://pypi.org/project/requests/): Requests allows you to send HTTP/1.1 requests extremely easily. There’s no need to manually add query strings to your URLs, or to form-encode your PUT & POST data — but nowadays, just use the json method!

[tabulate](https://pypi.org/project/tabulate/): Pretty-print tabular data in Python, a library and a command-line utility.

## Installation & Program Start
1) Clone this repo to your machine.
2) Navigate to this project directory in your terminal with command `cd [path goes here]`
3) Run `pip install -r requirements.txt` in your terminal to install the required libraries.
4) Run `python project.py` in your terminal. See command-line arguments

## Usage Description
Data from 7 of CoinGecko's REST API endpoints is available. The flows to acquire this data can be accessed using command-line arguments or by simply running the program and answering prompts. Some flows will require a few inputs from the user on the data that they would like to pull, while others will only require user input on what they want to do with the data or what they want to look at next.

Once the data is pulled and parsed, a sample of up to 20 rows of the data will be displayed to the user in tabulated form. Each flow allows the user to export the data returned by the API to a CSV in multiple formats, such as a summary file containing a summary of particular fields, a condensed file containing only select fields from the API output, or a complete file containing all fields from the API output.

At the end of each flow, the user can choose to perform these CSV exports, examine more data, or exit the program. They are not restricted to one of these options - the input for this part of the flow loops until the function is exited.

Most endpoints require the user to input >=1 CoinGecko Asset ID, Exchange ID, or both. A complete list of these IDs can be found in the `asset_list()` and `exchange_list()` functions.

#### Command-Line Arguments
Command-line arguments allow you to immediately jump to a specific function. For descriptions of the use of each function, see **User Input Functions** in the **project.py Components** section of this document.
* `assetlist`: Jumps to the `asset_list()` function.
* `assetmkts`: Jumps to the `asset_mkts()` function.
* `assetpairs`: Jumps to the `asset_pairs()` function.
* `exchlist`: Jumps to the `exchange_list()` function.
* `exch100`: Jumps to the `exchange_top100()` function.
* `exchpairs`: Jumps to the `exchange_pairs()` function.

#### Endpoints:
* [Coins List (ID Map)](https://docs.coingecko.com/v3.0.1/reference/coins-list): Query all the supported coins on CoinGecko with coins ID, name and symbol.
* [Coins List with Market Data](https://docs.coingecko.com/v3.0.1/reference/coins-markets): Query all the supported coins with price, market cap, volume and market related data.
* [Coin Tickers by ID](https://docs.coingecko.com/v3.0.1/reference/coins-id-tickers): Query the coin tickers on both centralized exchange (CEX) and decentralized exchange (DEX) based on a particular coin ID.
* [Exchanges List (ID Map)](https://docs.coingecko.com/v3.0.1/reference/exchanges-list): Query all the exchanges with ID and name.
* [Exchanges List with Data](https://docs.coingecko.com/v3.0.1/reference/exchanges): Query all the supported exchanges with exchanges’ data (ID, name, country, …) that have active trading volumes on CoinGecko.
* [Exchange Data by ID](https://docs.coingecko.com/v3.0.1/reference/exchanges-id): Query exchange’s data (name, year established, country, …), exchange volume in BTC and top 100 tickers based on exchange’s ID.
* [Exchange Tickers by ID](https://docs.coingecko.com/v3.0.1/reference/exchanges-id-tickers): Query exchange’s tickers based on exchange’s ID.


## project.py Components
### Classes
#### Auth
* `__init__`: Initialization of API Authentication
* `_get`: Base GET request path. Is utilized by the methods in the Assets and Exchanges classes.
* `api_key` Getter & Setter Properties: Defines API key used for access to CoinGecko APIs. Currently has my API key populated for ease of use.

#### Assets
* `coin_list()`: Method for hitting **Coins List (ID Map)** endpoint.
    + Called by asset_list() function.
    + No user input required.
* `coin_mkts()`: Method for hitting **Coins List with Market Data** endpoint.
    + Called by asset_mkts() function.
    + User input optional. If no user input, results will be the top 250 assets by market cap.
* `coin_pairs()`: Method for hitting **Coin Tickers by ID** endpoint.
    + Called by asset_pairs() function.
    + User input (CoinGecko Asset ID) required. Has additional optional parameters.

#### Exchanges
* `exch_list()`: Method for hitting **Exchanges List (ID Map)** endpoint.
    + Called by exchange_list() function.
    + No user input required.
* `exch_data()`: Method for hitting **Exchanges List with Data** endpoint.
    + Called by exchange_list() function.
    + User input optional.
* `exch_top100()`: Method for hitting **Exchange Data by ID** endpoint.
    + Called by exchange_top100() function.
    + User input (CoinGecko Exchange ID) required.
* `exch_pairs()`: Method for hitting **Exchange Tickers by ID** endpoint.
    + Called by exchange_pairs() function.
    + User input (CoinGecko Exchange ID) required. Has additional optional parameters.


### Functions
#### Navigation Functions
* `main()`: Starts program & handles interpretation of command-line arguments. If no arguments are provided, or invalid arguments are provided, the `prompts()` function is called.
* `prompts()`: Prompt user for input on the dataset that they would like to explore.
#### User Input Functions
* `asset_list()`: Function for accessing basic Asset data (Name, Ticker, Gecko ID, Blockchain(s), and Contract Address(es)) on all assets.
* `asset_mkts()`: Function for accessing Asset Market data (Name, Ticker, Slug, Market Cap, Diluted Market Cap, 24h Price % Change, 7d Price % Change).
    + User is prompted to provide either a comma-separated string of Gecko Asset IDs or the number of top assets they would like to view.
* `asset_pairs()`: Function for accessing Asset Pair data (Exchange ID, Pair Code, Base Asset, Counter Asset, Last Price (USD), Volume, etc).
    + User is required to provide the Asset ID of the asset whose market pairs they wish to view. User may also provide Exchange IDs to see data from specific exchanges. If no Exchange ID is provided, every market pair that includes the user's asset across all exchanges will be returned.
* `exchange_list()`: Function for accessing the basic Exchange identifying data (Exchange Name, CoinGecko Exchange ID) of all exchanges, or expanded Exchange information (Exchange ID, Exch Name, Year Established, Country, Description, URL, Social Media Links, etc) on either all exchanges or a user-specified number of exchanges.
* `exchange_top100()`: Function for accessing one or more exchanges' Top 100 Market Pairs data (Exch Name, Trading Pair, Base Asset, Quote Asset, Last Price (USD), etc).
    + User is required to provide, either one at a time or as a comma-separated string, the Exchange ID(s) of the exchange(s) they wish to view.
* `exchange_pairs()`: Function for accessing a given Exchange's Market Pairs information (Exch Name, Trading Pair, Base Asset, Quote Asset, Last Price (USD), etc).
    + User is required to provide the Exchange ID of the exchange that they wish to view. User may also provide a comma-separated string of Asset IDs if they only wish to view pairs that include particular assets. If no Asset ID(s) are provided, data returned will include every pair on the exchange.

#### Dictionary Constructor Functions
* `a_list_dict_build()`: Called by `asset_list()` function. Constructs and returns two dict lists.
    + `dict_asset_chainpop`: Contains asset info with all of an asset's blockchains + corresponding contract address in a nested dictionary.
    + `dict_asset_chain_sep_assets`: Contains asset info with each asset's blockchains + corresponding contract address separated into their own row.
* `a_mkt_dict_build()`: Called by `asset_mkts()` function. Constructs and returns 2 dict lists.
    + `dict_asset_main` - Contains select Asset Market fields (Gecko ID, Name, Code, Price, Price %Chg 24h, Mkt Cap, Mkt Cap Diluted, Mkt Cap Rank).
    + `dict_asset_full` - Contains all Asset Market fields.
* `a_pair_dict_build()`: Called by `asset_pairs()` function. Constructs and returns 3 dict lists.
    + `dict_asset_exch_summary` - A summary of the number of markets each asset has on each exchange in the API output.
    + `dict_asset_pair_main` - Contains select fields for each market pair that the asset has on each exchange.
    + `dict_asset_pair_full` - Contains all fields for each market pair that the asset has on each exchange.
* `e_list_basic_dict_build()`: Called by `exchange_list()` function. Constructs and returns 1 dict list.
    + `dict_exch_list_simple` - Contains Exchange Names and CoinGecko Exchange IDs.
* `e_list_dict_build()`: Called by `exchange_list()` function. Constructs and returns 2 dict lists.
    + `dict_exch_list_data` - Contains expanded exchange data.
    + `dict_exch_list_data_print` - Identical to `dict_exch_list_data` with the exception of data in the `Description` field, which is replaced with "See CSV" to improve readability when printed to console.
* `e_top100_dict_build()`: Called by `exchange_top100()` function. Constructs and returns 3 dict lists.
    + `dict_exch_top100_main` - Contains select fields for each of the top 100 market pairs on each exchange.
    + `dict_exch_top100_full` - Contains all fields for each of the top 100 market pairs on each exchange.
    + `dict_exch_top100_data` - Contains exchange-level data for each exchange queried.
* `e_pair_dict_build()`: Called by `exchange_pairs()` function. Constructs and returns 4 dict lists.
    + `dict_exch_pair_main` - Contains select fields for each market pair on an exchange.
    + `dict_exch_pair_full_fresh` - Contains all fields for each market pair on an exchange. Excludes stale data.
    + `dict_exch_pair_full_stale` - Contains all fields for each market pair on an exchange. Includes stale data.
    + `asset_count_list` - A summary of unique assets and how many pairs they are available to trade in on the exchange.

#### Helper Functions
* `helper_rfmt_usd()`: Convert a value to USD format with 2 decimal places (i.e. 1000.5214 = $1,000.52). Input can be float or integer.
* `helper_rfmt_1000()`: Convert a value to thousands format with 2 decimal places (i.e. 1000.5214 = 1,000.52). Input can be float or integer.
* `helper_rfmt_pct()`: Convert a value to percentage format with 5 decimal places (i.e. 5.10274 = 5.10274%). Input should be in percentage points.

#### CSV Output Function
* `csv_export()`: Export data contained within a `list[dict]` to a CSV. If no data is available, return to prompts().

## My Design Choices
My design choices are primarily related to the modularization and/or scalability of my code, the importance of which became increasingly clear to me as I worked on this project. I plan to use the code in this project as the first piece of a crypto trading algorithm (or at least the first version of that first piece), so as I worked on it I was very often thinking about how easy scaling this code would be if I built it one way or another. There is still more to do to achieve maximum scalability and modularization, but the current code is a significant improvement over my initial attempts.
* **API Requests as Classes**: I had decided to put all API requests into Classes from the beginning for a variety of reasons, some of which are listed below and others I forgot because I wasn't taking rigorous notes on that particular brainstorm.
    + API calls are distinct parameter-wise but the code for the calls fairly repetitive in implementation, which makes them well-suited for classes.
    + It would allow me to organize the pieces of the API requests, and the endpoints themselves, cleanly.
    + Inheritance would let me build the base to be used in each API call (the `Auth` Class) a single time and minimize the code in the endpoint-specific methods.
* **Dictionary Constructors**: I had initially put all of my dictionary constructors inside of the functions that now call them (i.e. the `a_list_dict_build()` code was inside the `asset_list()` code, not a standalone function) and although it wasn't the most visually appealing code it worked just fine. Then, I started attempting to build tests for the data flowing into and out of the dict constructors. After a few days of reading documentation, looking through stackoverflow threads, and tests that didn't work, I had a bright idea: instead of trying to test these constructors that do not return data and happen in the middle of a function, I could just make them into standalone functions! My tests immediately became far simpler, they actually *worked*, and my blood pressure returned to normal.
* **Helper Functions**: My reformat helpers are another piece that weren't in my initial build. My dictionaries were originally riddled with f-strings, which made the fields and the formatting being applied to the fields an absolute mess to read through. It occurred to me that the only 7 endpoints that my code calls lead to the creation of 17 dictionaries. I then thought about the number of dict constructors I would need for 20, 50, or 100 endpoints and figured it would be better to solve this issue before it becomes an issue.
* **Honorable Mention: Using Jira**: This isn't a code design choice, but I was originally organizing my tasks/documentation/research in two Microsoft Word Docs, which after a certain point felt like it started costing me more time than it was saving. I decided to move everything to Jira instead and the difference was like night and day. I already knew from work that Jira was extremely useful, but I had never tried to manage a project outside of it and it is truly a nightmare if you're not using the right tools.

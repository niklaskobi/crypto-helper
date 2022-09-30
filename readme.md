# Crypto-Counter
This is a basic tool whose purpose is to add euro-price-values to the staking rewards. 
The staking rewards are expected to be .csv from kraken.com (they are called ledgers).
Tool is written with support of kraken-rest-api v.1.1.0. 
Documentation can be found [here](https://docs.kraken.com/rest/).

## Usage
Export your .csv from `kraken.com`. Rename it to `ledgers.csv` if it is named differently. Copy it to the `data` folder.
Run the tool. The resulting `.csv` should be in the `data` folder.

Python 3.x should be used

## Limitations
Currently, the tool is working only for :
- DOT, ADA and ETH2, 
- year 2021
- prices are volume-weighted average price on the daily basis
- historical prices are not saved locally and are fetched from kraken-api every time you run the tool

But You can easily extend the tool to your own needs.

## Improvements
The most obvious things to improve:
- [ ] Support more currency pairs.
- [ ] Save historical price data locally.
- [ ] Create cli-runnable version and add documentation on how to use it from cli.
- [ ] Implement ui and deploy, so that any one could use it.



 
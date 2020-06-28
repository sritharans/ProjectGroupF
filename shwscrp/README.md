# Shopee Item Web Scraper

This folder contains the tool to perform web scraping of the item data from Shopee categories on the Shopee website.
The data will be dumped into CSV upon successfull scraping.

Pre-scraped data using this tool is available in the `Samples.7z` archive. You can open it using the 7-Zip tool available at:
[7-Zip Downloads](https://www.7-zip.org)

## Instructions:

To successfully use this tool, the following steps are required:

### 1. Install the .Net Core 3.1 SDK

Get the latest .Net Core 3.1 SDK from here:
`https://dotnet.microsoft.com/download/dotnet-core/3.1`

Install it and run the following command in a Command Prompt to confirm that it is working:

`dotnet --info`

### 2. Restore and Build

In the `shwscrp` directory, run the following command from the Command Prompt to restore dependencies:

`dotnet restore`

Then run the following command in the same Command Prompt to build the tool:

`dotnet build`


### 3. Running the tool

After completing the above steps, we are now ready to launch the tool. Please run the following command in your Command Prompt to scrape the data from the Shopee web site:

`get-data.cmd`

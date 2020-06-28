# Shopee Item Rating Predictor

This folder contains a shop rating predictor tool that could be used to provide a rating (number of stars) a product listed by a seller could obtain. It also provides simple analytics for that item category in terms of the distribution of the item attributes, it's density and concentration of the data.

## Instructions:

To successfully launch this application, the following steps are required:

### 1. Data Loading
The `mega.txt` in the `data` folder needs to be imported into HDFS. Later we will then import the dataset into HBase from HDFS. Unzip the `mega.zip` in the `data` using the following command:

`unzip mega.zip`

Copy the 'mega.txt' dataset into HDFS using the following command:

`hadoop fs -cp file:///[folder name]/data/mega.txt /tmp`

Then create the table in HBase using `hbase shell`, with the following command:

`create 'Shopee_Items', 'Seller', 'Item'`

Exit `hbase shell` then run the following command to import the data into the HBase table:

`hbase org.apache.hadoop.hbase.mapreduce.ImportTsv -Dimporttsv.columns="HBASE_ROW_KEY,Item:Category,Item:Label,Item:Stars,Item:Ratings,Item:Sold,Item:PriceMin,Item:PriceMax,Item:Stock,Seller:Name,Seller:Ratings,Seller:Products,Seller:ResponseRate,Seller:ResponseTime,Seller:Joined,Seller:Followers,Item:URL" Shopee_Items /tmp/mega.txt`

### 2. Application Prerequisites

The web application is built on the StreamLit framework and other packages. This would have to be first installed before you can launch the application. We recommend using at least the Python 3.7 runtime. You will need to install the following packages in your Python environment, either using `pip` or `conda`:

- streamlit
- pandas
- numpy
- seaborn
- altair
- matplotlib
- scipy
- sklearn

Please also download the CData HBase driver from this location:
`https://www.cdata.com/drivers/hbase/python/`

Then follow the instructions to install the CData HBase driver here:
`http://cdn.cdata.com/help/RHE/py/pg_pywheelinstallation.htm`

### 3. Bringing it all together

After completing the above steps, we are now ready to launch the application. Please take note of hostname where you installed HBase and where you will be running the web application.

Launch the HBase rest service by running the following command, on the HBase server where you imported the data above:

`hbase-daemon.sh start rest`

Take note of your HBase hostname or IP address, then change line 36 in `sh_app.py` as per the instructions here:
`http://cdn.cdata.com/help/RHE/py/pg_connectionpy.htm`

Then launch the web application using the following command:
`streamlit run sh_app.py`

Then using your web browser, open the following URL:
`http://[your server]:8501/`

You should now be able to view the application loading in your browser.

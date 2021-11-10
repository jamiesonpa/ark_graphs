
from PIL.Image import ROTATE_90
import requests
import pandas as pd
from yahoo_fin import stock_info as si 
from pandas_datareader import DataReader
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import bs4
from bs4 import BeautifulSoup

def get_institutional_holders(ticks):

    base_link = "https://finance.yahoo.com/quote/"
    links = []
    for tick in ticks:
        link = base_link + tick + "/holders/"
        links.append(link)
    
    for link in links:
        req = requests.get(link)
        soup = BeautifulSoup(req.content, "html.parser")
        table_of_interest = []
        for table in soup.find_all("table"):
            st.write(str(table.content))

def get_arkg_tickers():
    #this is the link that downloads the csv of the current ARKG holdings
    hdr = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest"}
    arkg_holdings_csv = "https://ark-funds.com/wp-content/uploads/funds-etf-csv/ARK_GENOMIC_REVOLUTION_ETF_ARKG_HOLDINGS.csv"
    arkg_holdings = str(requests.get(arkg_holdings_csv, headers=hdr).content).split("ARKG")
    arkg_holdings = arkg_holdings[1:len(arkg_holdings)-1]
    arkg_tickers = []
    for line in arkg_holdings:
        ticker = line.split(",")[2].replace('"',"")
        if ticker.find(" ") != -1:
            ticker = ticker.split(" ")[0]
        if ticker != "":
            arkg_tickers.append(ticker)
    return arkg_tickers

def list_tickers(ticks):
    for tick in ticks:
        st.write(tick)

def get_sellside_pt(tickers):
    recommendations = []
    ticker_recs = [["TICKER","RATING","NUMBER OF ANALYSTS","CURRENT PRICE", "MEAN ANALYST PT", "ANALYST PT RANGE", "DIFFERENCE TO ANALYST PT MEAN","PERCENT DIF. TO ANALYST PT MEAN"]]
    print("accessing analyst PT change percentage (this can take several seconds)...")
    for ticker in tickers:
        lhs_url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/'
        rhs_url = '?formatted=true&crumb=swg7qs5y9UP&lang=en-US&region=US&' \
                'modules=upgradeDowngradeHistory,recommendationTrend,' \
                'financialData,earningsHistory,earningsTrend,industryTrend&' \
                'corsDomain=finance.yahoo.com'
        
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        url =  lhs_url + ticker + rhs_url
        r = requests.get(url, headers=headers)
        if not r.ok:
            recommendation = None
        try:
            result = r.json()['quoteSummary']['result'][0]
            recommendation = result['financialData']['recommendationMean']['fmt']
            analystpt_mean = result['financialData']['targetMeanPrice']['fmt']
            analystpt_range = str(result['financialData']['targetLowPrice']['fmt']) + "-" + str(result['financialData']['targetHighPrice']['fmt'])
            current_price = str(result['financialData']["currentPrice"]["fmt"])
            difference_to_mean = float(analystpt_mean) - float(current_price)
            percent_difference_to_mean = round((((float(current_price)+difference_to_mean) - float(current_price))/float(current_price)),2) * 100
        except:
            recommendation = None
            analystpt_mean = None
            analystpt_range = None
            current_price = None
            difference_to_mean = None
            percent_difference_to_mean = None
        
        if recommendation != None:
            normalized_rec = (6-float(recommendation))/3
        else:
            normalized_rec = None

        recommendations.append(normalized_rec)
        try:
            analysts = si.get_analysts_info(ticker)
            ea = analysts["Earnings Estimate"]
            analystnum = ea.iloc[0][1]
        except:
            analystnum = "???"

        if normalized_rec != None:
            ticker_recs.append([ticker, round(normalized_rec,2), analystnum, current_price, "$"+str(analystpt_mean), "$"+analystpt_range,round(difference_to_mean,2), str(percent_difference_to_mean)+"%"])
        else:
            ticker_recs.append([ticker, normalized_rec, analystnum, current_price, analystpt_mean, analystpt_range,difference_to_mean, str(percent_difference_to_mean)+"%"])


    print("ratings below 1 are a sell, higher numbers are better")
    print("--------------------------------------------")
    for item in ticker_recs:
        print(str(item))
    print("--------------------------------------------")

    data = {}
    for ticker in tickers:
        for item in ticker_recs[1:]:
            if item[0] == ticker:
                bad = False
                for subitems in item:
                    if item == None:
                        bad = True
                if bad == False:    
                    if item[1] != None:
                        data[ticker] = float(item[7].replace("%",""))
    companies = list(data.keys())
    ratings = list(data.values())
    titl = "ARKG Mean Sellside Analyst PT %Change from Current Price"
    plotdata = pd.DataFrame({"Ratings": ratings}, index=companies)
    plotdata = plotdata.sort_values("Ratings")
    plotdata.plot(kind="bar", title = titl, color = ["#8264ff"])
    fig, ax = plt.subplots()
    rects1 = ax.bar(ratings)
    fig.bar(companies, ratings, color='#8264ff')
    ax.set_xticks(companies, rotate=90)
    ax.set_xlabel("Companies")
    ax.set_ylabel("Mean Sellside Analyst PT %Change from Current Price")
    ax.bar_label(rects1)
    fig.tight_layout()
    
    # plt.xticks(rotation=90, horizontalalignment="center")
    # plt.ylabel("Mean Sellside Analyst PT %Change from Current Price")
    # plt.xlabel("Companies")
    st.pyplot(fig)
    st.write("Plotted sellside analyst PT percent difference from current price")

def get_sellside_ratings(tickers):
    recommendations = []
    ticker_recs = [["TICKER","RATING","NUMBER OF ANALYSTS","CURRENT PRICE", "MEAN ANALYST PT", "ANALYST PT RANGE", "DIFFERENCE TO ANALYST PT MEAN","PERCENT DIF. TO ANALYST PT MEAN"]]
    print("accessing analyst ratings...")
    for ticker in tickers:
        lhs_url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/'
        rhs_url = '?formatted=true&crumb=swg7qs5y9UP&lang=en-US&region=US&' \
                'modules=upgradeDowngradeHistory,recommendationTrend,' \
                'financialData,earningsHistory,earningsTrend,industryTrend&' \
                'corsDomain=finance.yahoo.com'
        
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        url =  lhs_url + ticker + rhs_url
        r = requests.get(url, headers=headers)
        if not r.ok:
            recommendation = None
        try:
            result = r.json()['quoteSummary']['result'][0]
            recommendation = result['financialData']['recommendationMean']['fmt']
            analystpt_mean = result['financialData']['targetMeanPrice']['fmt']
            analystpt_range = str(result['financialData']['targetLowPrice']['fmt']) + "-" + str(result['financialData']['targetHighPrice']['fmt'])
            current_price = str(result['financialData']["currentPrice"]["fmt"])
            difference_to_mean = float(analystpt_mean) - float(current_price)
            percent_difference_to_mean = round((((float(current_price)+difference_to_mean) - float(current_price))/float(current_price)),2) * 100
        except:
            recommendation = None
            analystpt_mean = None
            analystpt_range = None
            current_price = None
            difference_to_mean = None
            percent_difference_to_mean = None
        
        if recommendation != None:
            normalized_rec = (6-float(recommendation))/3
        else:
            normalized_rec = None

        recommendations.append(normalized_rec)
        try:
            analysts = si.get_analysts_info(ticker)
            ea = analysts["Earnings Estimate"]
            analystnum = ea.iloc[0][1]
        except:
            analystnum = "???"

        if normalized_rec != None:
            ticker_recs.append([ticker, round(normalized_rec,2), analystnum, current_price, "$"+str(analystpt_mean), "$"+analystpt_range,round(difference_to_mean,2), str(percent_difference_to_mean)+"%"])
        else:
            ticker_recs.append([ticker, normalized_rec, analystnum, current_price, analystpt_mean, analystpt_range,difference_to_mean, str(percent_difference_to_mean)+"%"])


    print("ratings below 1 are a sell, higher numbers are better")
    print("--------------------------------------------")
    for item in ticker_recs:
        print(str(item))
    print("--------------------------------------------")

    data = {}
    for ticker in tickers:
        for item in ticker_recs[1:]:
            if item[0] == ticker:
                bad = False
                for subitems in item:
                    if item == None:
                        bad = True
                if bad == False:    
                    if item[1] != None:
                        data[ticker] = item[1]
    companies = list(data.keys())
    ratings = list(data.values())
    titl = "ARKG Mean Sellside Analyst Rating (higher is better)"
    plotdata = pd.DataFrame({"Ratings": ratings}, index=companies)
    plotdata = plotdata.sort_values("Ratings")
    plotdata.plot(kind="bar", title = titl, color = ["#8264ff"])
    plt.xticks(rotation=90, horizontalalignment="center")
    plt.ylabel("Mean Sellside Analyst Rating")
    plt.xlabel("Companies")
    plt.show()

def get_rdrevenue(ticks):


    finaldata = {}
    truncated_data = {}
    for tick in ticks:
        try:
            print("accessing income statement for " + tick)
            incomestatement = si.get_income_statement(tick)
            column_names = list(incomestatement.columns.values)
            rownames = list(incomestatement.index)
            this_year_vals = list(incomestatement[column_names[0]])
            data ={}
            counter = 0
        except:
            pass
        try:
            for rowname in rownames:
                if this_year_vals[counter] != None:
                    data[rowname] = abs(this_year_vals[counter])
                counter+=1
        except:
            pass
        try:
            revenue = data["totalRevenue"]
            rnd = data["researchDevelopment"]
        except:
            pass
        try:
            if revenue != None:
                if rnd != None:
                    rnd_rev_multiple = rnd/revenue
                    if rnd_rev_multiple < 5:
                        finaldata[tick] = rnd_rev_multiple
                    else:
                        truncated_data[tick] = rnd_rev_multiple
        except:
            pass
        
    multiples = list(finaldata.values())
    companies = list(finaldata.keys())
    titl = "ARKG R&D/Revenue Most Recent Fiscal Year"
    plotdata = pd.DataFrame({"R&D/Revenue": multiples}, index=companies)
    plotdata = plotdata.sort_values("R&D/Revenue")
    plotdata.plot(kind="bar", title = titl, color = ["#8264ff"])
    plt.xticks(rotation=90, horizontalalignment="center")
    plt.ylabel("R&D/Revenue Multiple")
    plt.xlabel("Companies")
    plt.show()

    multiples = list(truncated_data.values())
    companies = list(truncated_data.keys())
    titl = "ARKG R&D/Revenue Most Recent Fiscal Year"
    plotdata = pd.DataFrame({"R&D/Revenue": multiples}, index=companies)
    plotdata = plotdata.sort_values("R&D/Revenue")
    plotdata.plot(kind="bar", title = titl, color = ["#8264ff"])
    plt.xticks(rotation=90, horizontalalignment="center")
    plt.ylabel("R&D/Revenue Multiple")
    plt.xlabel("Companies")
    plt.show()

def get_gross_margins(ticks):

    finaldata = {}
    for tick in ticks:
        try:
            print("accessing income statement for " + tick)
            incomestatement = si.get_income_statement(tick)
            column_names = list(incomestatement.columns.values)
            rownames = list(incomestatement.index)
            this_year_vals = list(incomestatement[column_names[0]])
            data ={}
        except:
            pass
        try:
            counter = 0
            for rowname in rownames:
                if this_year_vals[counter] != None:
                    data[rowname] = abs(this_year_vals[counter])
                counter+=1
        except:
            pass
        try:
            revenue = data["totalRevenue"]
            costofrevenue = data["costOfRevenue"]
        except:
            pass
        try:
            if revenue != None:
                if costofrevenue != None:
                    margins = (revenue-costofrevenue)/revenue
                    if margins < 0:
                        finaldata[tick] = 0
                    else:
                        finaldata[tick] = margins
        except:
            pass
        
    multiples = list(finaldata.values())
    companies = list(finaldata.keys())
    titl = "ARKG Gross Margins"
    plotdata = pd.DataFrame({"Gross Margins": multiples}, index=companies)
    plotdata = plotdata.sort_values("Gross Margins")
    plotdata.plot(kind="bar", title = titl, color = ["#8264ff"])
    plt.xticks(rotation=90, horizontalalignment="center")
    plt.ylabel("Gross Margins")
    plt.xlabel("Companies")
    plt.show()

def get_opex_over_revenue(ticks):
    finaldata = {}
    for tick in ticks:
        try:
            print("accessing income statement for " + tick)
            incomestatement = si.get_income_statement(tick,yearly=True)
            column_names = list(incomestatement.columns.values)
            rownames = list(incomestatement.index)
            this_year_vals = list(incomestatement[column_names[0]])
            data={}
        except:
            pass
        try:
            counter = 0
            for rowname in rownames:
                if this_year_vals[counter] != None:
                    data[rowname] = abs(this_year_vals[counter])
                counter+=1
        except:
            pass
        try:
            opex = data["totalOperatingExpenses"]
            revenue = data["totalRevenue"]
        except:
            pass
        try:
            if revenue != None:
                if opex != None:
                    opexoverrevenue = (opex)/revenue
                    if opexoverrevenue > 20:
                        finaldata[tick] = 20
                    else:
                        finaldata[tick] = opexoverrevenue
                        print(tick+" is " + str(opexoverrevenue))
        except:
            pass
        
    multiples = list(finaldata.values())
    companies = list(finaldata.keys())
    titl = "ARKG OpEx/Revenue"
    plotdata = pd.DataFrame({"OpExRevenue": multiples}, index=companies)
    plotdata = plotdata.sort_values("OpExRevenue")
    plotdata.plot(kind="bar", title = titl, color = ["#8264ff"])
    plt.xticks(rotation=90, horizontalalignment="center")
    plt.ylabel("OpEx/Revenue")
    plt.xlabel("Companies")
    plt.show()

def get_simons_multiple(ticks):

    finaldata = {}
    truncated_data = {}
    for tick in ticks:
        try:
            print("accessing income statement for " + tick)
            incomestatement = si.get_income_statement(tick)
            column_names = list(incomestatement.columns.values)
            rownames = list(incomestatement.index)
            this_year_vals = list(incomestatement[column_names[0]])
            last_year_vals = list(incomestatement[column_names[1]])
            thisyeardata ={}
            lastyeardata ={}
        except:
            pass
        try:
            counter = 0
            for rowname in rownames:
                if this_year_vals[counter] != None:
                    thisyeardata[rowname] = abs(this_year_vals[counter])
                counter+=1
        except:
            pass
        try:
            counter = 0
            for rowname in rownames:
                if last_year_vals[counter] != None:
                    lastyeardata[rowname] = abs(last_year_vals[counter])
                counter+=1
        except:
            pass
        try:
            lastyearrevenue = lastyeardata["totalRevenue"]
            thisyearevenue = thisyeardata["totalRevenue"]
            lastyearrnd = lastyeardata["researchDevelopment"]
            thisyearrnd = thisyeardata["researchDevelopment"]
        except:
            pass
        try:
            if thisyearevenue != None:
                if lastyearrevenue != None:
                    if lastyearrnd != None:
                        if thisyearrnd != None:
                            lastyearrndoverrevenue = lastyearrnd/lastyearrevenue
                            thisyearrndoverrevenue = thisyearrnd/thisyearevenue
                            simonsmultiple = (thisyearrndoverrevenue - lastyearrndoverrevenue)/lastyearrndoverrevenue
                            print(tick + " is " +str(simonsmultiple))
                            if abs(simonsmultiple) < 10:
                                finaldata[tick] = simonsmultiple
        except:
            pass
        
    multiples = list(finaldata.values())
    companies = list(finaldata.keys())
    titl = "ARKG Simon's Multiple For Most Recent Fiscal Year"
    plotdata = pd.DataFrame({"SimonsMultiple": multiples}, index=companies)
    plotdata = plotdata.sort_values("SimonsMultiple")
    plotdata.plot(kind="bar", title = titl, color = ["#8264ff"])
    plt.xticks(rotation=90, horizontalalignment="center")
    plt.ylabel("R&D/Revenue Change from Last year")
    plt.xlabel("Companies")
    plt.show()
            

st.title("ARKG Analytics Tool")

tickerlist = st.sidebar.checkbox(label="List Tickers")
sellside_ratings = st.sidebar.checkbox(label="Average Sellside Analyst Ratings")
sellside_pt = st.sidebar.checkbox(label="Average Sellside Analyst PT %Difference From Current Price")
rdrevmultiple = st.sidebar.checkbox(label="R&D/Revenue Multiple")
grossmargins = st.sidebar.checkbox(label="Gross Margins")
opexrev = st.sidebar.checkbox(label="Opex/Revenue")
simons = st.sidebar.checkbox(label="1y Growth Rate of (R&D/Revenue)")
inst = st.sidebar.checkbox(label="Proportion of Shares held by institutions")

analyze = st.sidebar.button("ANALYZYE")
st.write("Preparing Tool...")
tickers = get_arkg_tickers()
st.write("Ready...")
if analyze:

    if tickerlist:
        st.write("ARKG Tickers...")
        list_tickers(tickers)
    if sellside_ratings:
        st.write("Getting sellside ratings...")
        get_sellside_ratings(tickers)

    if sellside_pt:
        st.write("Getting sellside PTs...")
        get_sellside_pt(tickers)

    if rdrevmultiple:
        st.write("Getting R&D/Revenue Multiples...")
        get_rdrevenue(tickers)

    if grossmargins:
        st.write("Getting gross margins...")
        get_gross_margins(tickers)

    if opexrev:
        st.write("Getting OpEx/Revenue...")
        get_opex_over_revenue(tickers)

    if simons:
        st.write("Getting (R&D/Revenue) Growthrate...")
        get_simons_multiple(tickers)
    
    if inst:
        st.write("Getting share held by institutions...")
        get_institutional_holders(tickers)

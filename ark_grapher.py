
from PIL.Image import ROTATE_90
import requests
import pandas as pd
from yahoo_fin import stock_info as si 
from pandas_datareader import DataReader
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

def get_institutional_holders2(ticks):
    quandl.ApiConfig.api_key = 'FDbdXFJJ3bzri6Qizxy7'
    event_codes = [(11,"Entry into a Material Definitive Agreement"),(12,"Termination of a Material Definitive Agreement"),(13,"Bankruptcy or Receivership"),(14,"Mine Safety - Reporting of Shutdowns and Patterns of Violations"),(15,"Receipt of an Attorney's Written Notice Pursuant to 17 CFR 205.3(d) "),(21,"Completion of Acquisition or Disposition of Assets"),(22,"Results of Operations and Financial Condition"),(23,"Creation of a Direct Financial Obligation or an Obligation under an Off-Balance Sheet Arrangement of a Registrant"),(24,"Triggering Events That Accelerate or Increase a Direct Financial Obligation or an Obligation under an Off-Balance Sheet Arrangement"),(25,"Cost Associated with Exit or Disposal Activities"),(26,"Material Impairments"),(31,"Notice of Delisting or Failure to Satisfy a Continued Listing Rule or Standard; Transfer of Listing"),(32,"Unregistered Sales of Equity Securities"),(33,"Material Modifications to Rights of Security Holders"),(34,"Schedule 13G Filing"),(35,"Schedule 13D Filing"),(36,"Notice under Rule 12b25 of inability to timely file all or part of a Form 10-K or 10-Q"),(37,"Tender Offer Statement under Section 14(d)(1) or 13(e)(1) of the Securities Exchange Act of 1934"),(40,"Changes in Registrant's Certifying Accountant"),(41,"Changes in Registrant's Certifying Accountant"),(42,"Non-Reliance on Previously Issued Financial Statements or a Related Audit Report or Completed Interim Review"),(51,"Changes in Control of Registrant"),(52,"Departure of Directors or Certain Officers; Election of Directors; Appointment of Certain Officers: Compensatory Arrangements of Certain Officers"),(53,"Amendments to Articles of Incorporation or Bylaws; and/or Change in Fiscal Year"),(54,"Temporary Suspension of Trading Under Registrant's Employee Benefit Plans"),(55,"Amendments to the Registrant's Code of Ethics; or Waiver of a Provision of the Code of Ethics"),(56,"Change in Shell Company Status"),(57,"Submission of Matters to a Vote of Security Holders"),(58,"Shareholder Nominations Pursuant to Exchange Act Rule 14a-11"),(61,"ABS Informational and Computational Material"),(62,"Change of Servicer or Trustee"),(63,"Change in Credit Enhancement or Other External Support"),(64,"Failure to Make a Required Distribution"),(65,"Securities Act Updating Disclosure"),(71,"Regulation FD Disclosure"),(81,"Other Events"),(91,"Financial Statements and Exhibits")]
    # for tick in ticks:
    #     quandl.get(tick)

def get_finviz_data(tickers, param):
    base_link = "https://finviz.com/quote.ashx?t="
    links = []
    for ticker in tickers:
        links.append(base_link+ticker)

    return_vals = []
    for link in links:
        hdr = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest"}
        r = requests.get(link, headers = hdr)
        soup = BeautifulSoup(r.content, 'html.parser')
        table = None
        try:
            table = soup.find_all("table",{"class": "snapshot-table2"})
        except:
            pass
        if len(table) > 0:
            rows = table[0].find_all("tr")
            data = {}
            for row in rows:
                cells = row.find_all("td")
                counter = 0
                names = []
                
                for cell in cells:
                    name = ""
                    value = ""
                    if counter%2 == 0:
                        found = False
                        for name in names:
                            if cell.text == name:
                                found = True
                        if found == False:
                            names.append(cell.text)
                    else:
                        if found == False:
                            data[names[-1]] = cell.text
                    counter +=1
        ticker = link.split("=")[1]
        return_vals.append((ticker,data[param]))
        print(ticker + ": " + data[param])
    return return_vals

def get_news_data(tickers):
    base_link = "https://finviz.com/quote.ashx?t="
    links = []
    for ticker in tickers:
        links.append(base_link+ticker)

    return_vals = []
    for link in links:
        # print("\n")
        # print("getting news for " + link.split("=")[1])
        hdr = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest"}
        r = requests.get(link, headers = hdr)
        soup = BeautifulSoup(r.content, 'html.parser')
        table = None
        try:
            table = soup.find_all("table",{"class": "fullview-news-outer"})
        except:
            pass
        try:
            if len(table) > 0:
                rows = table[0].find_all("tr")
                data = {}
                months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
                most_recent_date = None
                most_recent_date_found = False
                second_most_recent_date = None
                second_most_recent_date_found = False
                for row in rows:
                    for month in months:
                        if row.text.find(month) != -1:
                            if most_recent_date_found == False:
                                most_recent_date = row.text.split(" ")[0]
                                # print("most recent : " + most_recent_date)
                                most_recent_date_found = True
                            else:
                                if second_most_recent_date_found == False:
                                    second_most_recent_date = row.text.split(" ")[0]
                                    # print("second most recent: " + second_most_recent_date)
                                    second_most_recent_date_found = True
                recent_news_list = []
                for row in rows:
                    if row != None:
                        if row.text.find(second_most_recent_date) != -1:
                            break
                        else:
                            if row.text.find("Motley Fool") == -1:
                                if row.text.find("TipRanks") == -1:
                                    if row.text.find("ACCESSWIRE") == -1:
                                        if row.text.find("Law Offices") == -1:
                                            if row.text.find("Business Daily") == -1:
                                                if row.text.find("INVESTOR ALERT") == -1:
                                                    recent_news_list.append(row.text.replace("\xa0\xa0"," "))
                st.write(((link.split("=")[1])))
                for item in recent_news_list:
                    st.write("\t" + item)
        except:
            pass

def get_institutional_holders(ticks):
    institutional_holders = {}
    institutional_shares = {}
    insider_shares = {}
    for tick in ticks:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        print("accessing income statement for " + tick)
        try:
            holders = si.get_holders(tick,headers=headers)
            data={}
            num_institutions = (holders["Major Holders"].iloc[3][0])
            instshares = (holders["Major Holders"].iloc[1][0])
            insishares = (holders["Major Holders"].iloc[0][0])
            institutional_holders[tick] = float(num_institutions.replace('%',""))
            institutional_shares[tick] = float(instshares.replace('%',""))
            insider_shares[tick] = float(insishares.replace('%',""))
        except:
            pass


    st.write("Number of institutions holding by stock")
    df1 = pd.DataFrame(list(institutional_holders.values()),index=institutional_holders.keys())
    st.bar_chart(df1)

    st.write("% Of Shares held by Institutions by stock")
    df2 = pd.DataFrame(list(institutional_shares.values()),index=institutional_shares.keys())
    st.bar_chart(df2)

    st.write("% Of Shares held by Insiders by stock")
    df3 = pd.DataFrame(list(insider_shares.values()),index=insider_shares.keys())
    st.bar_chart(df3)

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
    df = pd.DataFrame.from_dict(data, orient='index')
    st.bar_chart(df)
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
            

ticks = get_arkg_tickers()
tickers = ticks

st.title("ARKG Analytics Tool")
tickerlist = st.sidebar.checkbox(label="List Tickers")
sellside_ratings = st.sidebar.checkbox(label="Average Sellside Analyst Ratings")
sellside_pt = st.sidebar.checkbox(label="Average Sellside Analyst PT %Difference From Current Price")
rdrevmultiple = st.sidebar.checkbox(label="R&D/Revenue Multiple")
grossmargins = st.sidebar.checkbox(label="Gross Margins")
opexrev = st.sidebar.checkbox(label="Opex/Revenue")
simons = st.sidebar.checkbox(label="1y Growth Rate of (R&D/Revenue)")
inst = st.sidebar.checkbox(label="Institutional Holder Info")
news = st.sidebar.checkbox(label="ARKG News")
shortfloat = st.sidebar.checkbox(label="Short Float")
analyze = st.sidebar.button("ANALYZYE")
st.write("Preparing Tool...")
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
    
    if news:
        st.write("Getting news for all tickers in ARKG...")
        get_news_data(tickers)
    
    if shortfloat:
        st.write("Getting short float for ARKG tickers...")
        short_floats = get_finviz_data(tickers, "Short Float")
        sfkeys = []
        sfvals = []
        for item in short_floats:
            if item[1] != "-":
                sfkeys.append(item[0])
                sfvals.append(float((str(item[1]).replace("%",""))))
        df1 = pd.DataFrame(sfvals,index=sfkeys)
        st.bar_chart(df1)

# from package_check import check
# check(['tls_client',{'name':'httpx','version':'0.24.0'},'httpx[socks]','httpx[http2]','curl_cffi'])
import datetime,json,random,uuid,re,sys,platform,time,tls_client,certifi,httpx
import socket
from curl_cffi import requests
from support import supply
con = supply()

products = {"AIRPASS_BUSINESS":"AirPassBusiness","AIRPASS_COACH":"AirPassEconomy","AIRPASS_FIRST":"AirPassFirst","AIRPASS_INSTANTUPGRADE":"InstantUpgrade","AIRPASS_PLANAHEAD":"AirPassPlanAhead","AIRPASS_PREMIUM_ECONOMY":"AirPassPremiumEconomy","BASIC_ECONOMY":"BasicEconomy","BASIC_ECONOMY_PLUS":"BasicEconomy","BUSINESS":"Business","BUSINESS_FLEXIBLE":"BusinessFlexible","BUSINESS_PLUS":"BusinessPlus","COACH":"MainCabin","COACH_FLEXIBLE":"MainCabinFlexible","COACH_FULLY_FLEXIBLE":"MainCabinFullyFlexible","COACH_PLUS":"MainPlus","BUSINESS_PLUS_FLAGSHIP":"First","COACH_SELECT":"MainSelect","FIRST":"First","FIRST_FLAGSHIP":"FirstFlexible","FIRST_FLEXIBLE":"FirstFlexible","FLAGSHIP_BUSINESS":"FlagshipÃ‚Â®Business","FLAGSHIP_BUSINESS_FLEXIBLE":"FlagshipÃ‚Â®BusinessFlexible","FLAGSHIP_BUSINESS_PLUS":"FlagshipÃ‚Â®BusinessPlus","FLAGSHIP_FIRST":"FlagshipÃ‚Â®First","FLAGSHIP_FIRST_FLEXIBLE":"FlagshipÃ‚Â®FirstFlexible","MAIN":"Main","PREMIER":"Premier","PREMIER_FLEXIBLE":"PremierFlexible","PREMIUM":"Premium","PREMIUM_COACH":"PremiumEconomy","PREMIUM_ECONOMY":"PremiumEconomy","PREMIUM_ECONOMY_FLEXIBLE":"PremiumEconomyFlexible"}

def minstotime(value):
    _hr,_min = divmod(value,60)
    return "%02d:%02d"%(_hr,_min)

def extraction(pagesource):
    Priclass_dict = {'"PremiumEconomy-Full refund":"PremiumEconomy Full refund","MainCabin-Full credit refund":"MainCabin Full credit refund","Business-Full refund":"Business Full refund","MainPlus-Full credit refund":"MainPlus Full credit refund","Basic_economy-No refund":"BasicEconomy No refund","BasicEconomy-Partial credit refund":"BasicEconomy Partial credit refund","First-Full credit refund":"First Full credit refund","PremiumEconomy-Full credit refund":"PremiumEconomy Full credit refund","BUSINESS_FLAGSHIP-Full credit refund":"BUSINESSFLAGSHIP Full credit refund","First-Full refund":"First Full refund","Business-Full credit refund":"Business Full credit refund","FirstFlexible-Full credit refund":"FirstFlexible Full credit refund","BUSINESS_FLAGSHIP-Full refund":"BUSINESSFLAGSHIP Full refund","MainCabin-Full refund":"MainCabin Full refund","BasicEconomy-No refund":"BasicEconomy No refund"'}
    status2 = None; status5 = None
    if not pagesource['slices']:
        status2 = 2
        return status2,status5,None
    # sessionId = pagesource['responseMetadata']['sessionId']
    # solutionSet = pagesource['responseMetadata']['solutionSet']
    final_list = []
    print('Len of flights : ',len(pagesource['slices']))
    for flights in pagesource['slices']:
        airlinels=[];stopls=[];aircraftls=[];waitaggr=0;aircraftchange=0;multipleairline=0;pgroup={}
        product_Groups = flights['productGroups']
        product_grop_class = [cls_ for cls_ in product_Groups]
        for i in product_grop_class:
            refund = flights['productGroups'][i]
            for refunds in refund:
                for ref in refunds['refundableProducts']:
                    product_types = ref['productType']
                    jsonkey       = str(re.sub(r'-',' ',ref['jsonKey'])).capitalize()
                    pgroup[product_types]=jsonkey
        for segments in flights['segments']:
            airline = segments['flight']['carrierCode']
            airlinels.append(airline)
            flightnum = airline+'-'+str(segments['flight']['flightNumber'])
            airlinename = segments['flight']['carrierName']
            segment_data = segments['legs'][0]
            aircraft = segment_data['aircraft']['name']
            aircraftls.append(aircraft)
            depart_date,depart_time = segment_data['departureDateTime'].split('T')
            depart_time = re.sub(r':00\.000.*','',depart_time)
            arrival_date,arrival_time = segment_data['arrivalDateTime'].split('T')
            arrival_time = re.sub(r':00\.000.*','',arrival_time)
            origin = segment_data['origin']['code']
            destination = segment_data['destination']['code']
            flighttime = minstotime(segment_data['durationInMinutes'])
            wait = segment_data.get('connectionTimeInMinutes',0)
            waitaggr+=wait
            waittime = minstotime(wait)
            amenities = segment_data.get("amenities",None)
            stopls.append({"origin":origin,"destination":destination,"description":None,"departuredate":str(depart_date),"departuretime":str(depart_time),"arrivaldate":str(arrival_date),"arrivaltime":str(arrival_time),"airline":airline,"flightnumber":flightnum,"flighttime":flighttime,"waittime":waittime,"facilities":{},"aircraft":aircraft,"distance":None,'airlinename':airlinename,"operatedby":None})
        layover = minstotime(waitaggr)
        if len(set(aircraftls))>1:
            aircraftchange=1
        if len(set(airlinels))>1:
            multipleairline=1
        lenOfStop = len(stopls)-1
        if lenOfStop >= 2:continue 
        price_block = flights['pricingDetail']
        # Product_details = flights['productDetails'][0]['productType']
        PId = []
        for pricedetails in price_block:
            newamenities = amenities.copy()
            amenities = segment_data.get("amenities",None)
            # points = pricedetails['perPassengerAwardPoints']
            if 'allPassengerDisplayTotal' in str(pricedetails):
                if pricedetails['allPassengerDisplayTotal']:
                    # solutionid = pricedetails['solutionID']
                    MINIMUM_price = pricedetails['allPassengerDisplayTotal']['amount']
                    slicepricing = pricedetails['slicePricing']
                    totalprice = slicepricing['allPassengerDisplayTotal']['amount']
                    baseprice = slicepricing['allPassengerDisplayFareTotal']['amount']
                    taxprice = slicepricing['allPassengerDisplayTaxTotal']['amount']
                    currency = pricedetails['allPassengerDisplayTotal']['currency']
                    fbc = pricedetails['extendedFareCode']
                    if pricedetails['benefitKey'] in products:
                        product_class = products[pricedetails['benefitKey']]
                    else:
                        product_class = pricedetails['benefitKey']
                    faretype1 = pricedetails['productType']
                    if faretype1 not in pgroup and not pricedetails['refundableProducts']:
                        productclass = f"{str(faretype1).capitalize()} No refund"
                    else:
                        price_class_ = pgroup[faretype1]
                        productclass = f"{product_class} {price_class_}"
                    ProductGroup = pricedetails['productGroup']
                    if ProductGroup in ['PREMIUM','PREMIUM_ECONOMY']:continue
                    if totalprice:
                        flight_statuscode=200
                        taxstatus = 1
                    else:
                        flight_statuscode=201
                        taxstatus = None
                    if PId:continue
                    PId.append(True)
                    if productclass in Priclass_dict:
                        priclass_name = Priclass_dict[productclass]
                    else:
                        priclass_name = re.sub(r"_",'',str(productclass))
                    new_stopls = []
                    for stp in stopls:       
                        stp_copy = stp.copy() 
                        stp_copy['fbc'] = fbc
                        newamenities.append(f"1 free carryon baggage")
                        stp_copy['amenities'] = [','.join(newamenities)]
                        new_stopls.append(stp_copy)
                    tempdata = {"price":float(totalprice), "priceclass":priclass_name, "currency":currency ,"basefare":baseprice,"feesandothers":taxprice, "description":None,"numofstops":lenOfStop,"aircraftchange":aircraftchange,"multipleairline":multipleairline,"layover":layover,"stop":new_stopls,"flight_statuscode":flight_statuscode,"taxstatus":taxstatus,'roundtrip_price':MINIMUM_price}
                    # if routetype ==1:
                    final_list.append({'outbound':tempdata})
                    # if routetype == 2:
                    #     try:
                    #         in_response,proxy = inbound_load(headers,sessionId,solutionSet,solutionid,totalprice,faretype1,flyfrom,flyto,departdate,returndate,proxies)
                    #         if in_response is None:
                    #             in_response,proxy = inbound_load(headers,sessionId,solutionSet,solutionid,totalprice,faretype1,flyfrom,flyto,departdate,returndate,proxies)

                    #         if in_response is None or in_response.status_code != 200:
                    #             status5 = 5
                    #             return status2,status5,None,proxy
                            
                    #         jdata = json.loads(str(in_response.text))
                    #     except Exception as e:
                    #         _exc_type, _exc_value, exc_traceback = sys.exc_info()
                    #         except_errors=str(e)+"And Line number is:"+str(exc_traceback.tb_lineno)
                    #         print (except_errors)
                    #         status5 = 5
                    #         return status2,status5,None,proxy
                        
                    #     price_ls=[]
                    #     for in_flights in jdata['slices']:
                    #         airlinels_in=[];stopls_in=[];aircraftls_in=[];waitaggr_in=0;aircraftchange_in=0;multipleairline_in=0;pgroup_in={}
                    #         product_Groups_in = in_flights['productGroups']
                    #         product_grop_class_in = [cls_ for cls_ in product_Groups_in]
                    #         for i in product_grop_class_in:
                    #             refund_in = in_flights['productGroups'][i]
                    #             for refunds_block in refund_in:
                    #                 for ref in refunds_block['refundableProducts']:
                    #                     product_types = ref['productType']
                    #                     jsonkey       = str(re.sub(r'-',' ',ref['jsonKey'])).capitalize()
                    #                     pgroup_in[product_types]=jsonkey
                    #         for inbound_segments in in_flights['segments']:
                    #             airline = inbound_segments['flight']['carrierCode']
                    #             airlinels_in.append(airline)
                    #             flightnum = airline+'-'+str(inbound_segments['flight']['flightNumber'])
                    #             airlinename = inbound_segments['flight']['carrierName']
                    #             segment_data = inbound_segments['legs'][0]
                    #             aircraft = segment_data['aircraft']['name']
                    #             aircraftls_in.append(aircraft)
                    #             depart_date,depart_time = segment_data['departureDateTime'].split('T')
                    #             depart_time = re.sub(r':00\.000.*','',depart_time)
                    #             arrival_date,arrival_time = segment_data['arrivalDateTime'].split('T')
                    #             arrival_time = re.sub(r':00\.000.*','',arrival_time)
                    #             origin = segment_data['origin']['code']
                    #             destination = segment_data['destination']['code']
                    #             flighttime = minstotime(segment_data['durationInMinutes'])
                    #             wait = segment_data.get('connectionTimeInMinutes',0)
                    #             waitaggr_in+=wait
                    #             waittime = minstotime(wait)
                    #             amenities = segment_data.get("amenities",None)
                    #             stopls_in.append({"origin":origin,"destination":destination,"description":None,"departuredate":str(depart_date),"departuretime":str(depart_time),"arrivaldate":str(arrival_date),"arrivaltime":str(arrival_time),"airline":airline,"flightnumber":flightnum,"flighttime":flighttime,"waittime":waittime,"facilities":{},"aircraft":aircraft,"distance":None,'airlinename':airlinename,"operatedby":None})
                    #         layover = minstotime(waitaggr_in)
                    #         if len(set(aircraftls_in))>1:
                    #             aircraftchange_in=1
                    #         if len(set(airlinels_in))>1:
                    #             multipleairline_in=1
                    #         lenOfStop_in = len(stopls_in)-1
                    #         if lenOfStop_in >=2:continue
                    #         price_block_in = in_flights['pricingDetail']
                    #         Product_details_in = in_flights['productDetails'][0]['productType']
                    #         for pricedetails in price_block_in:
                    #             newamenities = amenities.copy()
                    #             amenities = segment_data.get("amenities",None)
                    #             if 'allPassengerDisplayTotal' in str(pricedetails):
                    #                 if pricedetails['allPassengerDisplayTotal']:
                    #                     solutionid = pricedetails['solutionID']
                    #                     INBOUND_MIN_price = pricedetails['allPassengerDisplayTotal']['amount']
                    #                     slicepricing = pricedetails['slicePricing']
                    #                     totalprice = slicepricing['allPassengerDisplayTotal']['amount']
                    #                     baseprice = slicepricing['allPassengerDisplayFareTotal']['amount']
                    #                     taxprice = slicepricing['allPassengerDisplayTaxTotal']['amount']
                    #                     currency = pricedetails['allPassengerDisplayTotal']['currency']
                    #                     fbc_in = pricedetails['extendedFareCode']
                    #                     if pricedetails['benefitKey'] in products:
                    #                         product_class = products[pricedetails['benefitKey']]
                    #                     else:
                    #                         product_class = pricedetails['benefitKey']
                    #                     faretype1_in = pricedetails['productType']
                    #                     if faretype1_in not in pgroup_in and not pricedetails['refundableProducts']:
                    #                         productclass_in = f"{str(faretype1_in).capitalize()} No refund"
                    #                     else:
                    #                         price_class_ = pgroup_in[faretype1_in]
                    #                         productclass_in = f"{product_class} {price_class_}"
                    #                     ProductGroup_in = pricedetails['productGroup']
                    #                     if ProductGroup_in in ['PREMIUM','PREMIUM_ECONOMY']:continue
                    #                     if totalprice:
                    #                         flight_statuscode=200
                    #                         taxstatus = 1
                    #                     else:
                    #                         flight_statuscode=201
                    #                         taxstatus = None
                    #                     if productclass_in in Priclass_dict:
                    #                         priclass_name_in = Priclass_dict[productclass_in]
                    #                     else:
                    #                         priclass_name_in = re.sub(r"_",'',str(productclass_in))
                    #                     new_stopls_in = []
                    #                     for stp in stopls_in:       
                    #                         stp_copy = stp.copy() 
                    #                         stp_copy['fbc'] = fbc_in
                    #                         newamenities.append(f"1 free carryon baggage")
                    #                         stp_copy['amenities'] = [','.join(newamenities)]
                    #                         new_stopls_in.append(stp_copy)                       
                    #                     if lenOfStop_in in [0,1]:
                    #                         if INBOUND_MIN_price in price_ls:
                    #                             continue
                    #                         if MINIMUM_price==INBOUND_MIN_price:
                    #                             price_ls.append(INBOUND_MIN_price)
                    #                             if Product_details_in == faretype1_in:
                    #                                 tempdata_in = {"price":float(totalprice), "priceclass":priclass_name_in, "currency":currency ,"basefare":baseprice,"feesandothers":taxprice, "description":None,"numofstops":lenOfStop_in,"aircraftchange":aircraftchange_in,"multipleairline":multipleairline_in,"layover":layover,"stop":new_stopls_in,"flight_statuscode":flight_statuscode,"taxstatus":taxstatus,'roundtrip_price':INBOUND_MIN_price}
                    #                             else:
                    #                                 continue
                    #                         else:
                    #                             continue
                    #                     if {'outbound':tempdata,'inbound':tempdata_in} not in final_list:final_list.append({'outbound':tempdata,'inbound':tempdata_in})
    return status2,status5,final_list

def headers_spoof(headers, domain):
    win_versions = ["137.0.7151.104","137.0.7151.103","137.0.7151.70","137.0.7151.69","137.0.7151.68","137.0.7151.57","137.0.7151.56","137.0.7151.55","137.0.7151.41","137.0.7151.40","136.0.7103.116","136.0.7103.115","136.0.7103.114","136.0.7103.113","136.0.7103.94","136.0.7103.93","136.0.7103.92","136.0.7103.49","136.0.7103.48","135.0.7049.117","135.0.7049.116","135.0.7049.115","135.0.7049.114","135.0.7049.97","135.0.7049.96","135.0.7049.95","135.0.7049.86","135.0.7049.85","135.0.7049.84","135.0.7049.43","135.0.7049.42","135.0.7049.41","134.0.6998.179","134.0.6998.178","134.0.6998.177","134.0.6998.167","134.0.6998.166","134.0.6998.165","134.0.6998.119","134.0.6998.118","134.0.6998.117","134.0.6998.90","134.0.6998.89","134.0.6998.88","134.0.6998.37","134.0.6998.36","134.0.6998.35","133.0.6943.143","133.0.6943.142","133.0.6943.141","133.0.6943.128","133.0.6943.127","133.0.6943.126","133.0.6943.100","133.0.6943.99","133.0.6943.98","133.0.6943.60","133.0.6943.59","133.0.6943.54","133.0.6943.53","133.0.6943.35","132.0.6834.197","132.0.6834.196","132.0.6834.162","132.0.6834.161","132.0.6834.160","132.0.6834.159","132.0.6834.112","132.0.6834.111","132.0.6834.110","132.0.6834.84","132.0.6834.83","131.0.6778.267","131.0.6778.266","131.0.6778.265","131.0.6778.264","131.0.6778.206","131.0.6778.205","131.0.6778.204","131.0.6778.141","131.0.6778.140","131.0.6778.139","131.0.6778.110","131.0.6778.109","131.0.6778.108","131.0.6778.87","131.0.6778.86","131.0.6778.85","131.0.6778.71","131.0.6778.70","131.0.6778.69","131.0.6778.33"]
    lin_versions = ["137.0.7151.103","137.0.7151.68","137.0.7151.55","136.0.7103.113","136.0.7103.92","136.0.7103.59","135.0.7049.114","135.0.7049.95","135.0.7049.84","135.0.7049.52","134.0.6998.165","134.0.6998.117","134.0.6998.88","134.0.6998.35","133.0.6943.141","133.0.6943.126","133.0.6943.98","133.0.6943.53","132.0.6834.159","132.0.6834.110","132.0.6834.83","131.0.6778.264","131.0.6778.204","131.0.6778.139","131.0.6778.108","131.0.6778.85","131.0.6778.69"]
    win64_versions = ["137.0.7151.104","137.0.7151.103","137.0.7151.70","137.0.7151.69","137.0.7151.68","137.0.7151.57","137.0.7151.56","137.0.7151.55","137.0.7151.41","137.0.7151.40","136.0.7103.116","136.0.7103.115","136.0.7103.114","136.0.7103.113","136.0.7103.94","136.0.7103.93","136.0.7103.92","136.0.7103.49","136.0.7103.48","135.0.7049.117","135.0.7049.116","135.0.7049.115","135.0.7049.114","135.0.7049.97","135.0.7049.96","135.0.7049.95","135.0.7049.86","135.0.7049.85","135.0.7049.84","135.0.7049.43","135.0.7049.42","135.0.7049.41","134.0.6998.179","134.0.6998.178","134.0.6998.177","134.0.6998.167","134.0.6998.166","134.0.6998.165","134.0.6998.119","134.0.6998.118","134.0.6998.117","134.0.6998.90","134.0.6998.89","134.0.6998.88","134.0.6998.37","134.0.6998.36","134.0.6998.35","133.0.6943.143","133.0.6943.142","133.0.6943.141","133.0.6943.128","133.0.6943.127","133.0.6943.126","133.0.6943.100","133.0.6943.99","133.0.6943.98","133.0.6943.60","133.0.6943.59","133.0.6943.54","133.0.6943.53","133.0.6943.35","132.0.6834.197","132.0.6834.196","132.0.6834.162","132.0.6834.161","132.0.6834.160","132.0.6834.159","132.0.6834.112","132.0.6834.111","132.0.6834.110","132.0.6834.84","132.0.6834.83","131.0.6778.267","131.0.6778.266","131.0.6778.265","131.0.6778.264","131.0.6778.206","131.0.6778.205","131.0.6778.204","131.0.6778.141","131.0.6778.140","131.0.6778.139","131.0.6778.110","131.0.6778.109","131.0.6778.108","131.0.6778.87","131.0.6778.86","131.0.6778.85","131.0.6778.71","131.0.6778.70","131.0.6778.69","131.0.6778.33"]
    
    machine_platform = platform.system()
    if machine_platform == "Linux":
        user_os = '(X11; Linux x86_64)'
        chrome_version = random.choice(lin_versions)
        user_agent = f'Mozilla/5.0 {user_os} AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36'
    else:
        win_byte = random.choice(["win", "win64"])
        if win_byte == "win":
            user_os = '(Windows NT 10.0)'
            chrome_version = random.choice(win_versions)
            user_agent = f'Mozilla/5.0 {user_os} AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36'
        else:
            user_os = random.choice(['(Windows NT 10.0; Win64; x64)','(Windows NT 11.0; Win64; x64)'])
            chrome_version = random.choice(win64_versions)
            user_agent = f'Mozilla/5.0 {user_os} AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36'
            
    os_type = '"Linux"' if "Linux" in user_agent else '"Windows"'
    chrome_v = re.search(r'(?s)(.*?)\.', str(chrome_version)).group(1)
    sh_ua = f'"Chromium";v="{chrome_v}", "Brave";v="{chrome_v}", "Not.A/Brand";v="99"',
    if domain == 'co.kr' or domain == 'nl':
        domainURL = f'www.american-airlines.{domain}'
    else:
        domainURL = f'www.americanairlines.{domain}'
    headers['sec-ch-ua'] = str(sh_ua)
    headers['sec-ch-ua-platform'] = str(os_type)
    headers['User-Agent'] = str(user_agent)
    headers['x-dtreferer'] = f'https://{domainURL}/'
    headers['X-Forwarded-For'] = ".".join(str(random.randint(1, 255)) for _ in range(4))
    headers['X-Real-IP'] = ".".join(str(random.randint(1, 255)) for _ in range(4))
    
    return headers

hostname = socket.gethostname()
machineip = socket.gethostbyname(hostname)
print(hostname)
    
def do_request(headers, json_data, resultset):
    try:

        def get_token():
            print("im here")
            url2 = "https://ryip-stg-int-api.aggregateintelligence.com/get_awsid/"
            response = requests.post(url2,json={"websitecode":244, "machineip": "127.0.0.10_sowmiya"})
            # if "no" in response.text:
            #     time.sleep(3)
            #     get_token()


            return json.loads(response.json()['token']),response.json()['proxy']
        
        for _ in range(3):
            # if resultset:
            #     proxy = con.proxy_refreshed(resultset[random.randrange(0, len(resultset))][0])
            # else:
            #     raise TypeError('Without Proxy should not be run.')
            # proxies = {"https": "http://"+proxy}
            # print('Proxies',proxies)
            random_domain = random.choice(["in","com","cn","jp","co.kr","com.au","cl","co.cr","fr","be","fi","de","ie","it","nl","es","ch","co.uk"])
            random_domain = "com"
            if random_domain == 'co.kr' or random_domain == 'nl':
                domainURL = f'www.american-airlines.{random_domain}'
            elif random_domain =='com':
                domainURL = f'www.aa.{random_domain}'
            else:
                domainURL = f'www.americanairlines.{random_domain}'
            random_ls = [1,2,3] #changed[1,2,3]
            Random_choice = random.choice(random_ls)

            token,proxy = get_token()
            proxy = proxy
            
            
            Random_choice =2
            # print(token)
            proxies = {"https": "http://"+proxy,
                       "http":"http://"+proxy}
            if Random_choice ==1:
                print('TLS CLient Session')
                browser_type=["zalando_ios_mobile","okhttp4_android","safari_ios_16","safari15_3","safari15_5","airbnb_android","nike_ios","chrome_103","chrome_104","chrome_105","chrome_106","chrome_107","chrome_108","chrome_109","chrome_110","chrome_111","chrome_112","chrome_116_PSK","chrome_117","chrome_120","safari_15_6_1","safari_16_0","safari_ipad_15_6","safari_ios_15_5","safari_ios_15_6","safari_ios_16_0","firefox_102","firefox_104","firefox_105","firefox_106","firefox_108","firefox_110","firefox_117","firefox_120","opera_89","opera_90","opera_91","zalando_android_mobile","zalando_ios_mobile","nike_ios_mobile","mms_ios","mms_ios_1","mms_ios_2","mms_ios_3","mesh_ios","mesh_ios_1","mesh_ios_2","mesh_android","mesh_android_1","mesh_android_2","confirmed_ios","confirmed_android","okhttp4_android_7","okhttp4_android_8","okhttp4_android_9","okhttp4_android_10","okhttp4_android_11","okhttp4_android_12","okhttp4_android_13"]
                browser=random.choice(browser_type)
                supported_delegated_credentials_algorithms = generate_random_supported_delegated_credentials_algorithms()
                ja3_string = generate_random_ja3_string()
                session = tls_client.Session(client_identifier=browser,random_tls_extension_order=True,ja3_string=ja3_string,supported_delegated_credentials_algorithms=supported_delegated_credentials_algorithms)
                session.proxies = proxies['https']
            elif Random_choice==2:
                print('Curl_cffi Session')
                browser_type=["chrome99","chrome100","chrome101","chrome104","chrome107","chrome110","chrome99_android","edge99","edge101","safari15_3","safari15_5"]
                browser=random.choice(browser_type)
                session = requests.Session(impersonate="chrome",proxies=proxies)
                # session.impersonate="chrome"
                # session.verify = certifi.where()
                # session.proxies = proxies
            else:
                print('Httpx Session')
                proxies = {
                    "http://":  f"socks5://{proxy}",
                    "https://": f"socks5://{proxy}",
                }
                session = httpx.Client(http2=True,proxies=proxies,timeout=30)
            
            # homepageheaders = {
            #     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            #     'accept-language': 'en-GB,en;q=0.7',
            #     'cache-control': 'no-cache',
            #     'pragma': 'no-cache',
            #     'priority': 'u=0, i',
            #     'referer': 'https://www.aa.com/',
            #     'sec-ch-ua': '"Chromium";v="142", "Brave";v="142", "Not_A Brand";v="99"',
            #     'sec-ch-ua-mobile': '?0',
            #     'sec-ch-ua-platform': '"Linux"',
            #     'sec-fetch-dest': 'document',
            #     'sec-fetch-mode': 'navigate',
            #     'sec-fetch-site': 'same-origin',
            #     'sec-fetch-user': '?1',
            #     'sec-gpc': '1',
            #     'upgrade-insecure-requests': '1',
            #     'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            # }

            # response = session.get(
            #     'https://www.americanairlines.in/booking/search',
            #     headers=homepageheaders,
            # )
            # print('Search Response',response)
            # bm_s = response.cookies['bm_s']

            # headers = headers_spoof(headers=headers,domain=domainURL)

            # cookies = None#{'bm_s': bm_s}
            ua_list = ['Mozilla/5.0 (Linux; Android 8.0.0; Nexus 5X Build/OPR4.170623.006) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.137 Mobile Safari/537.36','Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/126.0.6478.54 Mobile/15E148 Safari/604.1','Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/125.0.6422.80 Mobile/15E148 Safari/604.1','Mozilla/5.0 (iPhone; CPU iPhone OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/121.0.6167.152 Mobile/15E148 Safari/604.1','Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/126.0.6478.54 Mobile/15E148 Safari/604.1','Mozilla/5.0 (iPhone; CPU iPhone OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/109.0.5414.112 Mobile/15E148 Safari/604.1','Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/126.0 Mobile/15E148 Safari/605.1.15','Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/125.0 Mobile/15E148 Safari/605.1.15','Mozilla/5.0 (iPad; CPU OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/121.2 Mobile/15E148 Safari/605.1.15','Mozilla/5.0 (iPhone; CPU iPhone OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/109.0 Mobile/15E148 Safari/605.1.15','Mozilla/5.0 (iPad; CPU OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/108.2 Mobile/15E148 Safari/605.1.15','Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148','Mozilla/5.0 (iPad; CPU OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148','Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148','Mozilla/5.0 (iPhone; CPU iPhone OS 12_5_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148','Mozilla/5.0 (iPad; CPU OS 13_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148','Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.54 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.54 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.146 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.178 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.117 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 14; ONEPLUS A6013) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.54 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 13; CPH2413) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 14; Xiaomi 23049PCD8G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.54 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 14; M2007J3SY) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.54 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 13; H8324) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 14; moto g power 5G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.54 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 12; SM-A515F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.119 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 12; VOG-L29) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.65 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 13; RMX3312) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 14; ASUS_AI2401) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.54 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 14; SAMSUNG SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/24.0 Chrome/126.0.6478.54 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 14; SAMSUNG SM-S911U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/24.0 Chrome/126.0.6478.54 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 13; SAMSUNG SM-S916B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/23.0 Chrome/125.0.6422.146 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 12; SAMSUNG SM-G996B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/20.0 Chrome/109.0.5414.119 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/19.0 Chrome/96.0.4664.104 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.54 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 13; SM-S916B) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/125.0.6422.146 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 12; Mi 10T Pro) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/109.0.5414.119 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 11; SM-A515F) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/96.0.4664.104 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 10; Pixel 3a) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.181 Mobile Safari/537.36','Mozilla/5.0 (Android 14; Mobile; rv:126.0) Gecko/126.0 Firefox/126.0','Mozilla/5.0 (Android 13; Mobile; rv:125.0) Gecko/125.0 Firefox/125.0','Mozilla/5.0 (Android 12; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0','Mozilla/5.0 (Android 11; Mobile; rv:109.0) Gecko/109.0 Firefox/109.0','Mozilla/5.0 (Android 10; Mobile; rv:102.0) Gecko/102.0 Firefox/102.0','Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.54 Mobile Safari/537.36 EdgA/126.0.2592.56','Mozilla/5.0 (Linux; Android 13; SM-S916B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.146 Mobile Safari/537.36 EdgA/125.0.2535.92','Mozilla/5.0 (Linux; Android 12; M2007J3SY) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.178 Mobile Safari/537.36 EdgA/121.0.2277.113','Mozilla/5.0 (Linux; Android 11; J8110) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.119 Mobile Safari/537.36 EdgA/109.0.1518.83','Mozilla/5.0 (Linux; Android 10; Pixel 3a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.98 Mobile Safari/537.36 EdgA/97.0.1072.69','Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.54 Mobile Safari/537.36 OPR/82.0.4195.76','Mozilla/5.0 (Linux; Android 13; CPH2413) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.146 Mobile Safari/537.36 OPR/81.2.4190.25','Mozilla/5.0 (Linux; Android 12; SM-G996B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.178 Mobile Safari/537.36 OPR/73.3.3844.71473','Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.54 Mobile Safari/537.36 Brave/1.66.115','Mozilla/5.0 (Linux; Android 13; SM-S916B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.146 Mobile Safari/537.36 Brave/1.64.113','Mozilla/5.0 (Linux; Android 12; RMX3312) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.178 Mobile Safari/537.36 Brave/1.60.108','Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.54 Mobile Safari/537.36 Vivaldi/6.7.3329.39','Mozilla/5.0 (Linux; Android 13; M2007J3SY) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.146 Mobile Safari/537.36 Vivaldi/6.6.3271.48','Mozilla/5.0 (Linux; U; Android 12; en-US; RMX3312) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 UCBrowser/13.4.0.1306 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 11; VOG-L29) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 UCBrowser/13.3.2.1304 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 10; INE-LX1) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 UCBrowser/12.13.2.1207 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 11; CPH2413) AppleWebKit/537.36 (KHTML, like Gecko) YaApp_Android/10.92 YaSearchBrowser/10.92 BroPP/1.0 SA/1 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 12; 2107113SI) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.65 Mobile Safari/537.36 DuckDuckGo/5','Mozilla/5.0 (Linux; Android 11; Pixel 4a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.104 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 9; Mi 9T Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 8.1.0; Nexus 6P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.90 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 7.1.1; Moto G (5)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.126 Mobile Safari/537.36','Mozilla/5.0 (Mobile; LYF/F90M/LYF_F90M-000-01-20-300819; rv:48.0) Gecko/48.0 Firefox/48.0 KAIOS/2.5','Mozilla/5.0 (Mobile; Nokia_8110_4G; rv:48.0) Gecko/48.0 Firefox/48.0 KAIOS/2.5','Mozilla/5.0 (Mobile; BananaPhone; rv:45.0) Gecko/45.0 Firefox/45.0 KAIOS/2.5','Mozilla/5.0 (Linux; Android 14; Pixel Tablet) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.54 Safari/537.36','Mozilla/5.0 (Linux; Android 13; SM-X706B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.146 Safari/537.36','Mozilla/5.0 (Linux; Android 12; Lenovo TB-8505F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.119 Safari/537.36','Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148','Mozilla/5.0 (iPhone; CPU iPhone OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 334.0.0.22.70','Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 TikTok 35.1.0 rv:35.1.0','Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.54 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 13; SM-S916B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.146 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 12; M2007J3SY) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.178 Mobile Safari/537.36 TikTok 35.1.0','Mozilla/5.0 (iPhone; CPU iPhone OS 12_5_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Mobile/15E148 Safari/604.1','Mozilla/5.0 (iPhone; CPU iPhone OS 11_4 like Mac OS X) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0 Mobile/15E148 Safari/604.1','Mozilla/5.0 (iPad; CPU OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.0 Mobile/14E5239e Safari/602.1','Mozilla/5.0 (Linux; Android 14; SM-S926B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.54 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 13; CPH2487) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.146 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 12; V2149) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.178 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 11; KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.119 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 10; HRY-LX1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.54 Mobile Safari/537.36','Mozilla/5.0 (iPad; CPU OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1','Mozilla/5.0 (iPad; CPU OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1','Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1','Mozilla/5.0 (iPhone; CPU iPhone OS 13_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1','Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Mobile/15E148 Safari/604.1','Mozilla/5.0 (iPhone; CPU iPhone OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1','Mozilla/5.0 (iPhone; CPU iPhone OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1','Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1','Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1','Mozilla/5.0 (iPod touch; CPU iPhone OS 12_5_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Mobile/15E148 Safari/604.1']
            browser_version  =  random.randrange(100,140)
            ua_string = random.choice(ua_list)
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US',
                'content-type': 'application/json',
                'origin': f'https://{domainURL}',
                'priority': 'u=1, i',
                # 'referer': f'https://{domainURL}/booking/search/find-flights?tripType=roundTrip',
                'referer': 'https://www.aa.com/booking/choose-flights/1?sid=e7640fae-bc45-4b0a-bae9-4d4e3a02ebe3',
                'sec-ch-ua': f'"Not;A=Brand";v="99", "Google Chrome";v="{browser_version}", "Chromium";v="{browser_version}"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': ua_string,#'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            }
            # cookies = token

            

                  

            # cookies = {
            #     "bm_s":token
            # }
            




            try:
                response = session.post(f'https://{domainURL}/booking/api/search/itinerary', headers=token, json=json_data)
            except Exception as error:
                print(f'Failed to do request: {error}')
                continue

            if response.status_code == 200:
                print('Status code:', response.status_code)
                return response,proxy,domainURL
            else:
                print(f'Failed to do request: {response.status_code}')

        return None,proxy,domainURL
    except Exception as e:
        _exc_type, _exc_value, exc_traceback = sys.exc_info()
        except_errors=str(e)+"And Line number is:"+str(exc_traceback.tb_lineno)
        print(except_errors)

def generate_random_supported_delegated_credentials_algorithms():
            # List of possible signature algorithms
    algorithms = [
        "PKCS1WithSHA256",
        "PKCS1WithSHA384",
        "PKCS1WithSHA512",
        "PSSWithSHA256",
        "PSSWithSHA384",
        "PSSWithSHA512",
        "ECDSAWithP256AndSHA256",
        "ECDSAWithP384AndSHA384",
        "ECDSAWithP521AndSHA512",
        "PKCS1WithSHA1",
        "ECDSAWithSHA1"
    ]

    # Randomly select between 1 and 5 algorithms from the list
    selected_algorithms = random.sample(algorithms, random.randint(1, 7))

    # Return the selected algorithms
    return selected_algorithms

def generate_random_ja3_string():
    # Generate random values for the JA3 fields
    version = random.choice([769, 770, 771, 772])
    Cipher_ls = [4865, 4866, 4867,49195, 49199, 49196, 49200,52393, 52392]
    extension_ls = [0, 5, 10, 11, 13, 16, 18, 21, 23, 27, 28, 35, 43, 45, 51]
    curves = [29, 23, 24]
    cipher_suites = "-".join(str(random.choice(Cipher_ls)))
    extensions = "-".join(str(random.choice(extension_ls)))
    elliptic_curves = "-".join(str(random.choice(curves)))
    ec_point_formats = "-".join(str(0))
    # Combine into JA3 format
    ja3_string = f"{version},{cipher_suites},{extensions},{elliptic_curves},{ec_point_formats}"
    return ja3_string

def load(flyfrom,flyto,departdate,returndate,travelers,resultset,routetype):
    try:
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-GB',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://www.americanairlines.in',
            'Referer': 'https://www.americanairlines.in/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-GPC': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'X-CID': str(uuid.uuid4()),
            'X-XSRF-TOKEN': str(uuid.uuid4()),
            'sec-ch-ua': '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'x-dtreferer': 'https://www.americanairlines.in/',
            'X-Forwarded-For': '7.451.121.774',
            'X-Forwarded-Proto': 'https',
            'X-Real-IP': '7.451.121.774',
            'X-Forwarded-Host': 'www.americanairlines.in',
            'X-Forwarded-Port': '443',
            'X-Cache': 'HIT',
        }
        if routetype==1:
            json_data = {
                'metadata': {
                    'selectedProducts': [],
                    'tripType': 'OneWay',
                    'udo': {
                        'search_method': 'Lowest',
                    },
                },
                'passengers': [
                    {
                        'type': 'adult',
                        'count': travelers['adults'],
                    },
                ],
                'requestHeader': {
                    'clientId': 'AAcom',
                },
                'slices': [
                    {
                        'allCarriers': True,
                        'cabin': '',
                        'departureDate': str(departdate),
                        'destination': str(flyto),
                        'destinationNearbyAirports': False,
                        'maxStops': None,
                        'origin': str(flyfrom),
                        'originNearbyAirports': False,
                    },
                ],
                'tripOptions': {
                    'corporateBooking': False,
                    'fareType': 'Lowest',
                    'locale': 'en_US',
                    'pointOfSale': None,
                    'searchType': 'Revenue',
                },
                'loyaltyInfo': None,
                'version': 'cfr',
                'queryParams': {
                    'sliceIndex': 0,
                    'sessionId': '',
                    'solutionSet': '',
                    'solutionId': '',
                    'sort': 'CARRIER',
                },
            }
        else:
            json_data = {
                'metadata': {
                    'selectedProducts': [],
                    'tripType': 'RoundTrip',
                    'udo': {'search_method': 'Lowest',},
                },
                'passengers': [
                    {
                        'type': 'adult',
                        'count': 1,
                    },
                ],
                'requestHeader': {
                    'clientId': 'AAcom',
                },
                'slices': [
                    {
                        'allCarriers': True,
                        'cabin': '',
                        'departureDate': str(departdate),
                        'destination': flyto,
                        'destinationNearbyAirports': False,
                        'maxStops': None,
                        'origin': flyfrom,
                        'originNearbyAirports': False,
                    },
                    {
                        'allCarriers': True,
                        'cabin': '',
                        'departureDate': str(returndate),
                        'destination': flyfrom,
                        'destinationNearbyAirports': False,
                        'maxStops': None,
                        'origin': flyto,
                        'originNearbyAirports': False,
                    },
                ],
                'tripOptions': {
                    'corporateBooking': False,
                    'fareType': 'Lowest',
                    'locale': 'en_US',
                    'pointOfSale': None,
                    'searchType': 'Revenue',
                },
                'loyaltyInfo': None,
                'version': 'cfr',
                'queryParams': {
                    'sliceIndex': 0,
                    'sessionId': '',
                    'solutionSet': '',
                    'solutionId': '',
                    'sort': 'CARRIER',
                },
            }
        
        response,proxy,domainURL = do_request(headers=headers, json_data=json_data, resultset=resultset)
        # response = ses.post(f'https://{domainURL}/booking/api/search/itinerary',headers=headers,json=json_data,)
        print(response)
        return response,proxy,domainURL
    except Exception as e:
        _exc_type, _exc_value, exc_traceback = sys.exc_info()
        except_errors=str(e)+"And Line number is:"+str(exc_traceback.tb_lineno)
        print(except_errors)

def flightrates(flyfrom,flyto,resultset,refid,routetype,departdate,returndate,travelers,priceclass,source,pos,los):
    try:
        dtcollected = str(datetime.datetime.utcnow())

        try:
            
            response,proxy,response_url = load(flyfrom,flyto,departdate,returndate,travelers,resultset,routetype)
            if response is None or response.status_code != 200:
                response,proxy,response_url = load(flyfrom,flyto,departdate,returndate,travelers,proxy,routetype)
                if response is None or response.status_code != 200:
                    status = 5
                    jdata = {"refid":refid,"flyfrom":flyfrom,"flyto":flyto,"routetype":routetype,"los":los,"departdate":str(departdate),"returndate":str(returndate),"travellers":travelers,"source":source,"pos":pos,"ratedescription":None,"details":None,"dtcollected":str(dtcollected),"cabinclass":priceclass,"status_code":status,'proxy_used':proxy}
                    return json.dumps([jdata])
            
            js_val = response.json()
        except Exception as e:
            status = 5
            _exc_type, _exc_value, exc_traceback = sys.exc_info()
            except_errors=str(e)+"And Line number is:"+str(exc_traceback.tb_lineno)
            print(except_errors)
            jdata = {"refid":refid,"flyfrom":flyfrom,"flyto":flyto,"routetype":routetype,"los":los,"departdate":str(departdate),"returndate":str(returndate),"travellers":travelers,"source":source,"pos":pos,"ratedescription":None,"details":None,"dtcollected":str(dtcollected),"cabinclass":priceclass,"status_code":status}
            return json.dumps([jdata])
        
        status2,status5,final = extraction(js_val)
        if status5==5:
            status = 5
        elif status2==2:
            status = 2
        elif final:
            status = 0
        else:
            status = 2
        jdata = {"refid":refid,"flyfrom":flyfrom,"flyto":flyto,"routetype":routetype,"los":los,"departdate":str(departdate),"returndate":str(returndate),"travellers":travelers,"source":source,"pos":pos,"ratedescription":None,"details":final,"dtcollected":str(dtcollected),"cabinclass":priceclass,"status_code":status,'proxy_used':proxy,'domain_name':response_url}
        return json.dumps([jdata])
    except Exception as e:
        print('script error')
        status = 4
        _exc_type, _exc_value, exc_traceback = sys.exc_info()
        except_errors=str(e)+"And Line number is:"+str(exc_traceback.tb_lineno)
        print (except_errors)
        jdata = {"refid":refid,"flyfrom":flyfrom,"flyto":flyto,"routetype":routetype,"los":los,"departdate":str(departdate),"returndate":str(returndate),"travellers":travelers,"source":source,"pos":pos,"ratedescription":None,"details":None,"dtcollected":str(dtcollected),"cabinclass":priceclass,"status_code":status,'proxy_used':proxy}
        return json.dumps([jdata])

'''
proxyid = '68'
db,connect = con.connectSQL(8, 'United')
connect.execute(f"Select proxy from proxy_live where status in ({proxyid})")
resultset = connect.fetchall()
flyfrom    = 'ATW'
flyto      = 'ORD'
departdate = '2025-12-04'
returndate = '2025-12-18'
routetype  = 2
priceclass = 1
travelers  = {'adults':1,'infants':0}
los        = None
pos        = 'US-USD'
source     = ''
refid      = ''
value = flightrates(flyfrom,flyto,resultset,refid,routetype,departdate,returndate,travelers,priceclass,source,pos,los)
with open(f'AmericanAirlines_finaldata_{flyfrom}-{flyto}-{departdate}_alter_2.html','w') as f:f.write(str(value))
try:print("arrayLen:",len(json.loads(value)[0]['details']) )
except:print('---> No flights <---')
'''
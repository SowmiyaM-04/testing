# from package_check import check
# check(['pytz'])
import json,re,datetime,ast,random,sys,requests,uuid,psycopg2,psycopg2.extras
from functools import reduce
from operator import add
from support import supply
from pytz import timezone

# from random import randrange
con = supply()
pos_proxy = False
proxy = ''
def clean(match,repl,strg):
        return re.sub(match,repl,str(strg))
         
def regMatch(patn, blk, cln=False,repl=["'","''"]):
    if cln:
        return clean(repl[0],repl[1],re.search(patn, blk).group(1) if re.search(patn, blk) else '')
    else:
        return re.search(patn, blk).group(1) if re.search(patn, blk) else ''

def jsonMatch(key, subj, cln=False,repl=["'","''"]):
    if key in subj:
        c = subj[key] if subj[key] else ''
        return clean(repl[0], repl[1], c) if c and cln else c
    else:
        return ''
    
# def getProxy(pos):
#     if pos_proxy:
#         if pos in proxy_dict:
#             proxy = con.proxy_refreshed(random.choice(proxy_dict[pos]))
#             print("current_proxy_pos:",pos)
#             return proxy
#         else:
#             print("---POS not found---")
#             exit()
#     else:
#         proxy = con.proxy_refreshed(random.choice(random.choice(list(proxy_dict.values()))))
#         return proxy

# def getProxy_list(pos):
#     if pos_proxy:
#         if pos in proxy_dict:
#             return proxy_dict[pos]
#         else:
#             print("---POS not found---")
#             exit()
#     else:
#         return random.choice(list(proxy_dict.values()))


def getProxy(resultset1):
    proxy = con.proxy_refreshed(resultset1[random.randrange(0, len(resultset1))][0])
    return proxy


def insert(rows,outputtable):
    if len(rows) > 999:
        insertlist = [rows[x:x+999] for x in range(0, len(rows), 999)]
    else:
        insertlist = [rows]
    for dataInseret in insertlist:
        if dataInseret:
            # upsts       = 2 if len(dataInseret)==1 and dataInseret[0]['status_code']==202 else 1
            headers     = list(dataInseret[0].keys())
            insert      = 'INSERT INTO '+outputtable+' (' + ", ".join(headers) + ") VALUES "
            value       = []
            
            for room in dataInseret:
                for r in room.keys():
                    room[r] = 'NULL' if str(room[r])=='' or not room[r] or str(room[r]).lower()=='none' else room[r]
                row     = [re.sub(r"'","''",row) if type(row)==str else row for row in [room[column.lower()] for column in headers]]
                values  = map((lambda x: "'"+str(x)+"'" if x!='NULL' else x), row)
                value.append("("+ ", ".join(values) +")")
            insert += ", ".join(value) 
            # open('INSERT.txt','w').write(str(insert))

            try:
                cursor.mogrify(insert).decode('utf-8')
                cursor.execute(insert);
            except Exception as e:
                print('ERRROR',e)
                if 'closed' in str(e) or 'Not connected' or str(e):
                    db1, cursor2 = con.connectSQL(serverid, dbname)
                    cursor2.mogrify(insert).decode('utf-8')
                    cursor2.execute(insert);
                    db1.close()
        else:
            print('No Data return to insert please check')
            continue
        print(f'{outputtable} inserted')        
     
def update(inputtable,source_id,status,refid,Marketid):
    # if UA_chk:
    #     cursor.execute("update "+inputtable+" set status = %s,UA = '%s' where id= %s"%(status,UA_chk,refid))
    #     db.commit()
    #     print('updated web',websitecode,' status',status ,'And id--',refid)
    # else:

    query  = f"update {inputtable} set status = {status} where id = {refid} and marketid = {int(Marketid)}"
    try:
        cursor.execute(query);
        print('updated web',source_id,' status',status ,'And id--',refid)
    except Exception as e:
        print(e)
        if 'closed' in str(e) or 'Not connected' or str(e):
            db3, cursor3 = con.connectSQL(serverid, dbname)
            cursor3.execute(query);
            db3.close()

def sum_time(timeList,sumlist=False):
    #timeList = [ '0:00:00', '0:00:15', '9:30:56' ]
    if sumlist:
        totalSecs = 0
        for tm in timeList:
            timeParts = [int(s) for s in tm.split(':')]
            totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60
        totalSecs, _ = divmod(totalSecs, 60)
        hr, mins = divmod(totalSecs, 60)
    else:
        timeList = re.sub(r"(\d+\:\d+):\d+", r"\1",str(timeList))
        if not timeList: timeList = '0:00'
        hr   = str(timeList).split(':')[0];mins = str(timeList).split(':')[1]
    
    if str(hr) == "00" and str(mins)=='00':hr = '0'
    if str(hr) == "0" and str(mins)!='0' and str(mins)!='00':
        hr = '0'+str(hr)
    if len(str(hr)) ==1 and str(timeList)!='0:00' and str(hr)!='0': 
        hr = '0'+str(hr)
    if len(str(mins)) ==1:mins = '0'+str(mins)
    return "%s:%s"%(hr,mins)

def insert_update(status,LIST,outputtable,source_id,refid,inputtable,row_refid,Refid_table,Marketid):
    try:
        insert(LIST,outputtable)
        update(inputtable, source_id, status, refid,Marketid)
        # insert(row_refid,Refid_table)
        db.commit()
    except :
        cursor.rollback()

script,status, startid, endid, inputtable, outputtable,  proxyId, dbname, serverid,Websitecode = sys.argv
# status, startid, endid, inputtable, outputtable, Offline, proxyId, dbname, serverid, Websitecode = '1','12446','12446','united_input','united_output',False,'34','United',8,'244'

db, cursor = con.connectSQL(serverid, dbname)
dcursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor) 

selectq = "SELECT  id,flyfrom,flyto,routetype,depart,arrive,adults,websitecode,currency,cabin,pos,marketid,los,site_id,scheduleid,sourcename  from "+inputtable+"  where status = "+str(status)+" and id between "+str(startid)+" and "+str(endid)+" and websitecode = "+str(Websitecode)+" order by id"
dcursor.execute(selectq)
resultset = dcursor.fetchall() 

# proxy_dict = {}
# dcursor.execute("Select proxy,pos from proxy_live  where status in ("+proxyId+")")
# resultset1 = dcursor.fetchall()
#resultset1 = con.fetch_proxies(proxyId) 
resultset1 = []
# for p in resultset1:
#     pos_check = p['pos']
#     if pos_check:
#         pos_check = pos_check.upper().strip()
#     if pos_check not in proxy_dict:
#         proxy_dict[pos_check] = []
#     proxy_dict[pos_check].append(p['proxy'])

for row in resultset:
    start_time = datetime.datetime.now()
    inputid        = row[0]
    flyfrom        = row[1]
    flyto          = row[2]
    refid          = inputid
    routetype      = row[3]
    departdate     = row[4]
    returndate     = row[5]
    travellers     = {"adults": row[6],  "infants": 0}
    source         = row[7] 
    input_currency = row[8]
    cabin          = row[9]
    pos_           = row[10]
    if pos_:
        pos_ = pos_.upper().strip()
    marketid       = row[11]
    los            = row[12]
    site_id        = row[13]
    scheduleid      = row[14]
    sourcename      = row[15]
    source_id      = str(source)  
    if cabin.strip() == 'E':
        priceclass = 1
    elif cabin.strip() == 'B':
        priceclass = 2
    elif cabin.strip() == 'P':
        priceclass = 4
    elif cabin.strip() == 'F':
        priceclass = 3
    else:
        print('***Priceclass not found***')
        continue
    print('source_id',source_id)
    if str(proxyId) != '555':
        # proxy          = getProxy(pos_)
        proxy          = ''
    else:
        proxy = None
    PROXY = proxy
    PACIFIC = 'US/Pacific'
    EASTERN = 'US/Eastern'
    MOUNTAIN = 'US/Mountain'
    CENTRAL = 'US/Central'
    # los            = None
    # extract_dt  =datetime.datetime.utcnow().strftime('%Y-%m-%d')
    # extract_time= datetime.datetime.utcnow().strftime('%H:%M:%S')
    extract_dt   = datetime.datetime.now(timezone(CENTRAL)).strftime('%Y-%m-%d')
    extract_time = datetime.datetime.now(timezone(CENTRAL)).strftime('%H:%M:%S')
    # try:
    #     dcursor.execute(f"Select refid,status,marketid from united_refid where refid = {refid} and websitecode={int(source)} and marketid='{marketid}'")
    #     Refid_resultset = dcursor.fetchone()
    #     if Refid_resultset:
    #         United_refid = Refid_resultset[0]
    #         Refid_status = Refid_resultset[1]
    #         Marketid     = Refid_resultset[2]
    #         update(inputtable,source_id,Refid_status,United_refid,Marketid)
    #         print(f"The refid {United_refid} is Already Inserted")
    #         break
    #     db.commit()
    # except Exception as e:
    #     print(e)
    #     pass

    jdata={'888':'americanairlines_with_tax','999':'americanairlines_points','20':'google','124':'skyscanner','43':'alaska','264':'aircanada','42':'aeromexico','197':'airfrance','278':'allegiantair','244':'americanairline_united_flights(1)','279':'avelo','231':'avianca','276':'breezeairways','271':'delta','318':'caribbean','39':'copaair','40':'easternairlines','237':'frontier','37':'jetblue','24':'latam','277':'silverwings','26':'spirit','295':'suncountry','273':'united','270':'westjet','274':'kayak'}
    # sourcename     = jdata[str(source_id)]

    if str(source_id) in jdata:
        source =  jdata[str(source_id)]
        alternate = False;airlineid=''

        # if str(source_id) == '271':
        #     alternate = True
        #     airline_dic = {'271':'DL'}
        #     airlineid = [airline_dic[str(source_id)]]
        #     source = 'kayak'

        '''elif str(source_id) in ['318']:
            alternate = True
            airline_dic = {'318':'-32459','264':'-32695'}
            airlineid = airline_dic[str(source_id)]
            source = 'skyscanner'''

        if str(source_id) in ['39','264','270','318']:
            alternate = True
            airline_dic = {'273':'UA','278':'G4','39':'CM','237':'F9','264':'AC','270':'WS','43':'AS','318':'BW'}
            airlineid = [airline_dic[str(source_id)]]
            source = 'google'

        # if str(source_id) in ['20']:
        #     alternate = True
        #     # airline_dic = {'20':'NK'}
        #     airline_dic = {'20':'DL'}
        #     airlineid = [airline_dic[str(source_id)]]
        #     source = 'google'
        if str(source_id) in ['273']:
            alternate = True
            airline_dic = {'273':'UA',}
            airlineid = [airline_dic[str(source_id)]]
            source = 'expedia_filter'
        
        # if str(source_id) == '37':
        #     alternate=True
        #     airline_dic = {'37':'B6'}
        #     airlineid = [airline_dic[str(source_id)]]
        #     source='google_jetblue'

        if str(source_id) in ['124']:
            alternate = True
            # airlineid = ['UA','DL'] 
            airlineid = ['DL']
        
        if str(source_id) in ['20'] and str(inputtable)=='united_input':
            alternate = True
            # airline_dic = {'244':'AA'}
            airlineid = ['AA']#[airline_dic[str(source_id)]]
            source = 'google_united'
        

        exp = __import__(source, fromlist=[None])
        print("going to script", source)

        try:
            _rerun = 0
            while(_rerun <= 5):

                _rerun+=1          
                if str(source_id) in ['273','318','39','264','270']:#'37'
                    # PROXY = getProxy_list(pos_)
                    PROXY = getProxy(resultset1)
                if str(source_id) in ['24','124','20','122','295','273','318','39','264','270']:#'37',
                    POS=pos_+'-'+input_currency
                else:
                    POS = pos_
                print('refid',refid)
                if alternate:
                    if source in ['google','google_jetblue','kayak','expedia_filter','google_united']:
                        POS=pos_+'-'+input_currency
                        PROXY = resultset1
                    res_body = exp.flightrates(flyfrom,flyto,PROXY,refid,routetype,str(departdate),str(returndate),travellers,priceclass,source,POS,los,airlineid)
                
                elif str(source_id) in ['278','244','271']:
                    proxy_copy = ''
                    res_body = exp.flightrates(flyfrom,flyto,proxy_copy,refid,routetype,str(departdate),str(returndate),travellers,priceclass,source,POS,los)
                else:
                    res_body = exp.flightrates(flyfrom,flyto,PROXY,refid,routetype,str(departdate),str(returndate),travellers,priceclass,source,POS,los)
                # if int(Websitecode)==395:
                #     res_body = exp.flightrates(flyfrom,flyto,PROXY,refid,routetype,str(departdate),str(returndate),travellers,priceclass,source,POS,los,bgprogram)                    
                # if str(Websitecode) in ['5','420','421']:
                #     res_body = exp.flightrates(flyfrom,flyto,PROXY,refid,routetype,str(departdate),str(returndate),travellers,priceclass,source,POS,los,site_id,input_currency)                    
                # else:        
                #     res_body = exp.flightrates(flyfrom,flyto,PROXY,refid,routetype,str(departdate),str(returndate),travellers,priceclass,source,POS,los)                    
                try:
                    global UA_chk; UA_chk = None
                    if not res_body:
                        res_statuscode = '9'
                        break
                    res_statuscode = re.search(r'status_code.*?:\s*?(\d+)', str(res_body)).group(1)
                    proxy_used = json.loads(res_body)[0].get('proxy_used')
                except Exception as e:
                    # proxy = getProxy(pos_)
                    # proxy = getProxy(resultset1)
                    # con.eHandling()
                    continue
                print("res_statuscode :",res_statuscode,'refid',refid)
                if int(res_statuscode) == 5:
                    # proxy = getProxy(pos_)
                    # proxy = getProxy(resultset1)
                    # print("proxy :",proxy)
                    continue
                else:
                    break
            else:
                continue
        except Exception as e:
            print("error  :",con.eHandling())
            continue
        #======================================insert start=============
        
        if res_statuscode=='2':
            # if not Refid_resultset:
                status      = 2
                row_refid    = [{"refid":refid,"dtcollected":f"{extract_dt} {extract_time}","websitecode":source_id,'status':status,'marketid':str(marketid)}]
                Refid_table = 'united_refid'
                rows = [{'sourcecode':source_id, 'extract_dt':extract_dt, 'site':sourcename, 'extract_time':extract_time, 'refid':refid, 'status_code':202,'pos':pos_,'out_cabin':None,'in_cabin':None,'org':flyfrom,'dst':flyto,'out_dprt_dt':departdate,'marketid':marketid}]
                insert_update(status,rows,outputtable,source_id,refid,inputtable,row_refid,Refid_table,marketid)
                # try:
                #     insert(rows,outputtable)
                #     update(inputtable, source_id, status, refid)
                #     insert(row_refid,Refid_table)
                #     db.commit()
                # except:
                #     con.rollback()
            # finally:
            #     cursor.close()
            # continue
        # open('flightrates.html','w').write(res_body)
        # exit()
        # res_body = open('/home/ai/Desktop/booking2.html','r').read()
        try:
            data = json.loads(res_body)
        except Exception as e:
            data = json.loads(json.dumps(res_body))
        if str(source_id) in ['244','20']:
            bounds = ['outbound']
        else:
            bounds = ['outbound','inbound']
        rows=[];directstop_list=[];onestop_list=[];nearby_airport_flag_ls=[];dtcollected=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if res_statuscode=='0':
            if 'domain_name' in data:
                Domain_name = data[0]['domain_name']
            else:
                Domain_name = None
            for flights in data[0]['details']:
                pricels=[];basels=[];durationls=[];taxls=[]
                for boundid in bounds:
                    if boundid in flights:
                        # print('LEN-Stop',len(jsonMatch('stop',flights[boundid])))
                        # if len(jsonMatch('stop',flights[boundid])) > 2 and routetype==2:
                        #     break
                        stopNamels = [];froms=[];tos = [];f_num=[];craft=[];ddate=[];adate=[];dtime=[];atime=[];flighttimels=[];aname=[];waits=[];acode=[];stopcount=0;fbcls = [];departure_ls=[];arrive_ls=[];operatedbyls=[];booking_code_ls=[]
                        # stopLen = len(jsonMatch('stop',flights[boundid]))
                        if str(source_id) in ['20','124']:
                            channelname = flights['channel_name']
                            channeltype = flights['channel_type']
                        else:
                            channelname = channeltype = None
                        for stopcount,stops in enumerate(jsonMatch('stop',flights[boundid])):
                            org         = jsonMatch('origin',stops)
                            destination = jsonMatch('destination',stops)

                            if org not in stopNamels and stopcount != 0:
                                stopNamels.append(org)
                            froms.append(org)                                
                            tos.append(jsonMatch('destination',stops))
                            departure_date = datetime.datetime.strptime(jsonMatch('departuredate',stops),"%Y-%m-%d").strftime("%Y%m%d")
                            departure_time = datetime.datetime.strptime(jsonMatch('departuretime',stops),"%H:%M").strftime("%H%M")
                            arrival_date   = datetime.datetime.strptime(jsonMatch('arrivaldate',stops),"%Y-%m-%d").strftime("%Y%m%d")
                            arrival_time   = datetime.datetime.strptime(jsonMatch('arrivaltime',stops),"%H:%M").strftime("%H%M")
                            stop_details_dep= f"{org}{departure_date}{departure_time}"
                            stop_details_arr= f"{destination}{arrival_date}{arrival_time}"
                            departure_ls.append(stop_details_dep)
                            arrive_ls.append(stop_details_arr)
                            ddate.append(jsonMatch('departuredate',stops))
                            adate.append(jsonMatch('arrivaldate',stops))
                            dtime.append(jsonMatch('departuretime',stops))
                            atime.append(jsonMatch('arrivaltime',stops))
                            matchs = jsonMatch('flightnumber',stops)
                            if 'fbc' in stops:
                                FBC           = jsonMatch('fbc',stops)
                                booking_class = str(FBC)[0];booking_code_ls.append(booking_class)
                                fbcls.append(FBC)
                            else:
                                FBC = None
                            if matchs:
                                result = matchs.replace('-','').strip()
                            else:
                                result = jsonMatch('flightnumber',stops)
                            f_num.append(result)
                            acode.append(re.sub(r'\s.*|\-.*','',jsonMatch('flightnumber',stops).strip()))
                            aname.append(jsonMatch('airlinename',stops))
                            flighttimels.append(jsonMatch('flighttime',stops))
                            if jsonMatch('aircraft',stops): craft.append(jsonMatch('aircraft',stops))
                            wait        = waits.append(jsonMatch('waittime',stops))
                            operatedby  = jsonMatch('operatedby',stops)
                            operatedbyls.append(operatedby)
                        
                        price         = float(jsonMatch('price',flights[boundid])) if jsonMatch('price',flights[boundid]) else 0
                        currency      = jsonMatch('currency',flights[boundid])
                        basefare      = float(jsonMatch('basefare',flights[boundid])) if jsonMatch('basefare',flights[boundid]) else 0
                        feesandothers = float(jsonMatch('feesandothers',flights[boundid])) if jsonMatch('feesandothers',flights[boundid]) else 0
                        tax_status    = 1 if price else 0
                        amenities     = jsonMatch('features',jsonMatch('ancillaries',flights[boundid]))
                        Roundtrip_Price         = float(jsonMatch('roundtrip_price',flights[boundid])) if jsonMatch('roundtrip_price',flights[boundid]) else 0
                        if 'bookingCode' in flights[boundid]:
                            booking_class = flights[boundid]['bookingCode']
                            if booking_class :booking_code_ls.append(booking_class)
                        else:
                            booking_class = None
                        if str(source_id) in ['999']:
                            points    = float(jsonMatch('points',flights[boundid])) if jsonMatch('points',flights[boundid]) else 0#points
                            price      = float(jsonMatch('price',flights[boundid])) if jsonMatch('price',flights[boundid]) else 0#price
                        else:
                            points = 0
                            price  = price
                        # if basefare:
                        #     price_ins    = float(jsonMatch('basefare',flights[boundid])) if jsonMatch('basefare',flights[boundid]) else 0
                        # else:
                        #     price_ins   = float(jsonMatch('price',flights[boundid])) if jsonMatch('price',flights[boundid]) else 0
                        if not feesandothers:
                            if basefare and price:
                                feesandothers = price - basefare 
                        priceclass    = jsonMatch('priceclass',flights[boundid])
                        # if source == 'airindiaexpress' or source == 'salamair' or source == 'emitrates':
                        # priceclass    = jsonMatch('priceclass',flights[boundid])
                        stop_name     = ','.join(stopNamels)
                        try:
                            stp_count = stop_name.split(',')
                            if stopcount != len([i for i in stp_count if i]):
                                stopcount = len(stop_name.split(','))
                            if not stop_name and jsonMatch('technical_stop',stops):
                                technical_stop = stops['technical_stop']
                                stopcount = 1 if technical_stop else stopcount    
                        except Exception as e:
                            print("error:",e)  
                            continue
                        layover       = jsonMatch('layover',flights[boundid]) if jsonMatch('layover',flights[boundid]) else 0                             
                        flighttime    = sum_time(flighttimels,sumlist=True)
                        if layover:
                            totalduration = sum_time([flighttime,layover],sumlist=True)
                        else:
                            totalduration = flighttime
                        durationls.append(totalduration)
                        if str(layover)=='00:00': layover = '0'
                        numofstops = flights[boundid]['numofstops']
                        if numofstops==0 and len(f_num)>1:
                            raise TypeError('More than one Flightnumber is displayed')
                        pricels.append(price)
                        basels.append(basefare)
                        taxls.append(feesandothers)
                        airline       = ','.join(f_num)
                        aircraft      = ','.join(craft)
                        airlinename   = ','.join(aname)
                        airlinecode   = ','.join(acode)
                        departures    = ','.join(departure_ls)
                        arrivals      = ','.join(arrive_ls)
                        bound_id    = 1 if boundid=='outbound' else 2
                        status_code = 200 if res_statuscode=='0' else 202 
                        ow_rt       = "rt" if routetype == 2 else "ow"
                        fbc = ','.join(list(set(fbcls))) 
                        booking_class_codes = ','.join(list(set(booking_code_ls))) 
                        if str(source_id) in ['244','20']:
                            if routetype == 1:   
                                if flyfrom.strip().upper() != froms[0].strip().upper() or flyto.strip().upper() != tos[-1].strip().upper():
                                    continue 
                                row_dict = {'tax':feesandothers,'fare_base':basefare,'far_tot':price,'sourcecode':source_id, 'extract_dt':extract_dt, 'site':sourcename, 'extract_time':extract_time, 'carrier':airlinecode, 'org':froms[0], 'dst':tos[-1], "ow_rt":ow_rt, "out_flt_num": airline, 'out_dprt_dt':str(ddate[0]), 'out_dprt_time':str(dtime[0]), 'outbound_arrival_date':str(adate[-1]),'outbound_arrival_time':str(atime[-1]),'out_fbc':fbc,'out_class':booking_class_codes, 'out_connection':stop_name,  'currency':currency, 'out_price':price, 'refid':refid, 'status_code':status_code,'pos':pos_,'out_cabin':priceclass,'departures':departures,'arrivals':arrivals,"outbound_flighttime":totalduration,"outbound_layover":layover,"numstops":numofstops,'roundtrip_price':Roundtrip_Price,'domain_name':Domain_name,'marketid':marketid}#'out_provider':channelname
                                
                                if str(source_id) in ['999']:
                                    row_dict['far_tot'] = 0
                                    row_dict['out_price'] = 0
                                    rows.append(row_dict)
                                else:
                                    rows.append(row_dict)

                            else:
                                if bound_id == 1:
                                    if flyfrom.strip().upper() != froms[0].strip().upper() or flyto.strip().upper() != tos[-1].strip().upper():
                                        print('flyfrom',flyfrom,'froms',froms,'tos',tos,'flyto',flyto)
                                        continue 
                                    totalbasefare = reduce(add,basels)
                                    totalprice    = reduce(add,pricels)
                                    if totalbasefare and totalprice:
                                        totalfeesandothers = totalprice-totalbasefare
                                    else:
                                        totalfeesandothers=0
                                    # print('Roundtrip_price',Roundtrip_Price)
                                    # print('OUTCABIN',priceclass)
                                    row_dict = {'sourcecode':source_id, 'extract_dt':extract_dt, 'site':sourcename, 'extract_time':extract_time, 'carrier':airlinecode, 'org':froms[0], 'dst':tos[-1], "ow_rt":ow_rt, "out_flt_num": airline, 'out_dprt_dt':str(ddate[0]), 'out_dprt_time':str(dtime[0]), 'outbound_arrival_date':str(adate[-1]),'outbound_arrival_time':str(atime[-1]),'out_fbc':fbc,'out_class':booking_class_codes, 'out_connection':stop_name,  'currency':currency, 'out_price':price, 'refid':refid, 'status_code':status_code,'pos':pos_,'out_cabin':priceclass,'departures':departures,'arrivals':arrivals,"outbound_flighttime":totalduration,"outbound_layover":layover,"numstops":numofstops,'is_tax_inc_outin':1,'out_tax':feesandothers,'out_basefare':basefare,"roundtrip_price":Roundtrip_Price,'tax':totalfeesandothers,'fare_base':totalbasefare,'far_tot':totalprice, 'far_tot':totalprice,'domain_name':Domain_name,'marketid':marketid}#,'out_provider':channelname
                                if row_dict:rows.append(row_dict)
                        else:
                            if routetype == 1:   
                                if flyfrom.strip().upper() != froms[0].strip().upper() or flyto.strip().upper() != tos[-1].strip().upper():
                                    continue 
                                
                                row_dict = {'tax':feesandothers,'fare_base':basefare,'far_tot':price,'sourcecode':source_id, 'extract_dt':extract_dt, 'site':sourcename, 'extract_time':extract_time, 'carrier':airlinecode, 'org':froms[0], 'dst':tos[-1], "ow_rt":ow_rt, "out_flt_num": airline, 'out_dprt_dt':str(ddate[0]), 'out_dprt_time':str(dtime[0]), 'outbound_arrival_date':str(adate[-1]),'outbound_arrival_time':str(atime[-1]),'out_fbc':fbc,'out_class':booking_class_codes, 'out_connection':stop_name,  'currency':currency, 'out_price':price, 'refid':refid, 'status_code':status_code,'pos':pos_,'out_cabin':priceclass,'departures':departures,'arrivals':arrivals,"outbound_flighttime":totalduration,"outbound_layover":layover,"numstops":numofstops,'roundtrip_price':Roundtrip_Price,'out_basefare':basefare,'out_tax':feesandothers,'marketid':marketid}#'out_provider':channelname
                                
                                if str(source_id) in ['999']:
                                    row_dict['far_tot'] = 0
                                    row_dict['out_price'] = 0
                                    rows.append(row_dict)
                                else:
                                    rows.append(row_dict)

                            else:
                                if bound_id == 2:
                                    if not row_dict:status=1
                                    if flyfrom.strip().upper() != tos[-1].strip().upper() or flyto.strip().upper() != froms[0].strip().upper():
                                        continue 
                                    totalDuration = sum_time(durationls,sumlist=True)
                                    totalbasefare = reduce(add,basels)
                                    totalprice    = reduce(add,pricels)
                                    if totalbasefare and totalprice:
                                        totalfeesandothers = totalprice-totalbasefare
                                    else:
                                        totalfeesandothers=0
                                    if row_dict:
                                        row_dict.update({'tax':totalfeesandothers,'fare_base':totalbasefare,'far_tot':totalprice,'in_flt_num':airline, 'in_dprt_dt':ddate[0], 'in_dprt_time':dtime[0], 'in_class':booking_class_codes, 'far_tot':totalprice,' in_connection':stop_name, 'in_price':price,'in_cabin':priceclass,'in_fbc':fbc,'inbound_flighttime':totalduration,'inbound_arrival_date':str(adate[-1]),'inbound_arrival_time':str(atime[-1]),'inbound_layover':layover,'inbound_stopcount':numofstops,'roundtrip_price':Roundtrip_Price})#,'in_provider':channelname,'in_carrier':airlinecode,
                                else:
                                    row_dict = None
                                    if flyfrom.strip().upper() != froms[0].strip().upper() or flyto.strip().upper() != tos[-1].strip().upper():
                                        continue 
                                    row_dict = {'sourcecode':source_id, 'extract_dt':extract_dt, 'site':sourcename, 'extract_time':extract_time, 'carrier':airlinecode, 'org':froms[0], 'dst':tos[-1], "ow_rt":ow_rt, "out_flt_num": airline, 'out_dprt_dt':str(ddate[0]), 'out_dprt_time':str(dtime[0]), 'outbound_arrival_date':str(adate[-1]),'outbound_arrival_time':str(atime[-1]),'out_fbc':fbc,'out_class':booking_class_codes, 'out_connection':stop_name,  'currency':currency, 'out_price':price, 'refid':refid, 'status_code':status_code,'pos':pos_,'out_cabin':priceclass,'departures':departures,'arrivals':arrivals,"outbound_flighttime":totalduration,"outbound_layover":layover,"numstops":numofstops,'is_tax_inc_outin':1,'out_basefare':basefare,'out_tax':feesandothers,'marketid':marketid}#,'out_provider':channelname
                                    continue
                                if row_dict:
                                    if not row_dict["in_price"]:
                                        row_dict["in_price"] =None
                                        row_dict["out_price"]=None
                                if row_dict:rows.append(row_dict)
                        
            # open('rows.txt','w').write(str(rows)) 
            # exit()
            if rows:
                
                    data_status  = 1
                    row_refid    = [{"refid":refid,"dtcollected":f"{extract_dt} {extract_time}","websitecode":source_id,'status':data_status,'marketid':str(marketid)}]
                    Refid_table  = 'united_refid'
                    insert_update(data_status,rows,outputtable,source_id,refid,inputtable,row_refid,Refid_table,marketid)
                    
            else:
                
                    data_status  = 2
                    row_refid    = [{"refid":refid,"dtcollected":f"{extract_dt} {extract_time}","websitecode":source_id,'status':data_status,'marketid':str(marketid)}]
                    Refid_table  = 'united_refid'
                    rows = [{'sourcecode':source_id, 'extract_dt':extract_dt, 'site':sourcename, 'extract_time':extract_time, 'refid':refid, 'status_code':202,'pos':pos_,'out_cabin':None,'in_cabin':None,'org':flyfrom,'dst':flyto,'out_dprt_dt':departdate}]
                    insert_update(data_status,rows,outputtable,source_id,refid,inputtable,row_refid,Refid_table,marketid)

cursor.close()
db.close()

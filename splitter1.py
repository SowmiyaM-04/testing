import multiprocessing, threading, math, decimal, time, os, sys, requests,zipfile,shutil,platform,psycopg2



from support import supply


processId    = 34



ServerId     = 13



runstatus    = 0



crawltype    = 1



ScriptTable  = 'pyscripts'



supplier     = supply()



dbs = psycopg2.connect(
host="52.37.135.55",
database="united",
user="stealth",
password="tkeChB0dJp",
port="5432"
)
cursors = dbs.cursor()

IP           = supplier.machineIP()
IP = '2600:1f14:1f99:436a:46cd:9fbb:9508:39f5'
print(IP)

class Run():
    def crawl(self, start, end, filename, python_v, inputTable, outputTable, status, proxyid, offline, dbname, serverid,Websitecode):



        if python_v == None or python_v == 0: python_v = "python3"



        elif python_v == 1: python_v = 'python3'



        else: python_v = "python3"



        final = "{0} -W ignore {1} {2} {3} {4} {5} {6} {7} {8} {9} {10}".format(python_v, filename, status, start, end, inputTable, outputTable, proxyid, dbname, serverid,Websitecode)



        os.system(final)







    def Extraction(self, Files_script,t_count,Websitecode,processid,update_id,proxyid,inputtable,outputtable,Start_id,End_id,Status,dbname,crawltype,python_v, offline, serverid):



        print("Websitecode",Websitecode)



        start    = time.time()



        if platform.system() == 'Windows':



            filename =  'AT_spirit\\mainfile_united.py'



        else:



            filename = 'mainfile_united.py'





        inputTable  = inputtable



        outputTable = outputtable


        query="Select id from "+inputTable+" where websitecode = %s and id  between '%s' and '%s' and Status = '%s' order by id" % (Websitecode,Start_id, End_id, Status)


        cursors.execute(query)



        result = cursors.fetchall()



        if result:



            



            lastrun = "update "+ScriptTable+" set lastrun = now()::timestamp(0) where machineip = '%s' and id = %s and processid = %s"%(IP, update_id, processid)



            cursors.execute(lastrun)



            dbs.commit()



            threads  = []



            rset     = list(result)



            size     = len(rset)



            size     = decimal.Decimal(size)



            t_count  = int(t_count)



            count    = size / t_count



            count_tmp= count



            count    = math.ceil(count)



            count    = int(count)



            Start_rout = rset[0]



            Start_rout = Start_rout[0]



            print ("Size of Ids--:", size)



            for _ in range(t_count):



                if count > (size -1):



                    count = size -1



                    count = int(count)



                    end_rout = rset[count]



                    end_rout = end_rout[0]   



                else:



                    pasv = count - 1



                    Intpasv = int(pasv)



                    end_rout = rset[Intpasv]



                    end_rout = end_rout[0]



                    if Start_rout == end_rout:



                        end_rout = end_rout+1



                if Start_rout <= end_rout:



                    thread = threading.Thread(target=self.crawl, args=(Start_rout, end_rout, filename, python_v, inputTable, outputTable, Status, proxyid, offline, dbname, serverid, Websitecode,))



                    thread.start()



                    threads.append(thread)



                Start_rout = end_rout+1



                count      = count_tmp+count



            for thread in threads:



                if thread != thread.isAlive():



                    print(thread.getName() ,'Is Completed')



                thread.join()



            end     = time.time()



            elapsed = end - start



            print("Time taken: ", elapsed, "seconds.")



            print("%s to %s id's Over" % (Start_id, End_id))



        else:



            print("No Records Found in result set")



        #os.remove(filename)







if __name__ == '__main__':



    # for i in range(1):



    cpucount = 3#multiprocessing.cpu_count()



    # query    = "select script,threadcount,websitecode,processid,id,proxyid,input,output,startid,endid,status,db,crawltype,python3, offline,serverid from "+ScriptTable+" where processid = '{0}' and machineip = '{1}' and runstatus='{2}' and crawltype = '{3}' order by totalcount desc limit {4}".format(processId, IP, runstatus, crawltype,cpucount)



    # print(query)



    # cursors.execute(query)



    # results = cursors.fetchall()



    # if results:



    #     processes = []



    #     for urls in results:



    #         Files_script = urls[0]



    #         Thread_Count = urls[1]



    #         Websitecode  = urls[2]



    #         processid    = urls[3]



    #         update_id    = urls[4]



    #         proxyid      = urls[5]



    #         inputtable   = urls[6]



    #         outputtable  = urls[7]



    #         Start_id     = urls[8]



    #         End_id       = urls[9]



    #         Status       = urls[10]



    #         dbname       = urls[11]



    #         crawltype    = urls[12]



    #         python_v     = urls[13]



    #         offline      = urls[14]



    #         serverid     = urls[15]

    processes = []
    processid, update_id, proxyid = 1,1,1
    python_v, offline, serverid = None,None,12

    Files_script = 'mainfile_united.py'

    Thread_Count = 30

    Websitecode = 244

    dbname = 'united'

    inputtable = 'united_input'

    outputtable = 'united_output'

    # Start_id, End_id, Status = 120570 , 135264, -1
    Start_id, End_id, Status = 385874, 400750, -1

    ds = multiprocessing.Process(target=Run().Extraction, args=(Files_script, Thread_Count, Websitecode, processid, update_id, proxyid, inputtable, outputtable, Start_id, End_id, Status, dbname, crawltype, python_v, offline, serverid,))



    processes.append(ds)



for p in processes:



    p.start()



for p in processes:



    print(p.is_alive())



    p.join()



else:



    print("no result")



dbs.close()
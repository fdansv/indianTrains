import urllib2,urllib,pickle,datetime
from BeautifulSoup import BeautifulSoup
def addzero(number):
    if len(str(number))==1:
        return "0"+str(number)
    return str(number)
def india(depart,arrive,date,d=True):
##    print depart+"-"+arrive
    year=int(date[:4])
    month=int(date[4:6])
    day=int(date[6:8])
    dater=datetime.datetime(year,month,day,0,0)

    weekday=dater.weekday()

    output = open('indiastations.pkl', 'rb')
    stadic = pickle.load(output)
    output.close()
    thelist=[]
    try:
        dep=stadic[depart]
    except:
        return "deperror"
    try:
        arr=stadic[arrive]
    except:
        return "arrerror"
    url="http://erail.in/rail/getTrains.aspx?Station_From="+dep+"&Station_To="+arr+"&DataSource=0&Language=0"
    req=urllib2.Request(url)
#    print "Querying "+depart+"-"+arrive
    response=urllib2.urlopen(req)
    the_page=response.read()
    if the_page.find("No direct trains")!=-1 and d==True:
        check="http://erail.in/rail/getShortRoute.aspx?StationFrom="+dep+"&StationTo="+arr+"&StationTo2=&Major=1&Gauge=1"
        creq=urllib2.Request(check)
        cresponse=urllib2.urlopen(creq)
        cthe_page=cresponse.read().split("\n")
        for city in cthe_page[3:-2]:
            cityname=city.split(",")[2]
            first=india(depart,cityname,date,False)
            if first!=[]:
                hr=int(first[0]['dept'].split(".")[0])
                mins=int(first[0]['dept'].split(".")[1])
                datetimetransit=datetime.datetime(year,month,day,hr,mins)+datetime.timedelta(hours=hr,minutes=mins)
                newdate=str(datetimetransit.year)+addzero(datetimetransit.month)+addzero(datetimetransit.day)
                second=india(cityname,arrive,newdate,False)
                if second!=[]:
                    #print "second station found"
                    for train in second:
                        traindate=datetime.datetime(datetimetransit.year,datetimetransit.month,datetimetransit.day,int(train['dept'].split(".")[0]),int(train['dept'].split(".")[1]))
                        if traindate<datetimetransit:
                            second.remove(train)
                    return [first,second]
            
    if the_page.find("No direct trains")!=-1 and d==False:
        return []

    trains=the_page.split('^')[1:]
    servicelist=[]
    for service in trains:
        chars=service.split("~")
        while "" in chars:
            chars.remove("")
        servicelist.append(chars)
    servicelist.sort(key=lambda timedep: timedep[10])
    keys=['number','tname','comefrom','comefroma','goto',
          'gotoa','depc','depca','arrc','arrca','dept','arrt',
          'dur','days','av','type','unk1','days','unk2','unk3',
          'dated','unk4','dist','unk5','fares','unk6','unk7',
          'arp','unk8','unk9','note']
    for service in servicelist:
        thedic={}
        i=0
        for key in keys:
            
            thedic[key]=service[i]
            types=["adult","child","senmale","other","senfem"]
            i+=1
        thedic["days"]=service[13]
        if thedic['days'][weekday]=="1":
            thelist.append(thedic)
    return thelist
def getstations():
    page=urllib.urlopen("http://erail.in/js/cmp/Stations.js").read()
    page=page[page.find('"')+1:]
    page=page[:page.find('"')]
    properlist=[]
    i=0
    f=open('stations.js','wb')
    f.write("[")
    for item in page.split(","):
        if i%2==1:
            f.write('"'+item+'",')
        i+=1
    f.write("]")
    f.close()

#print india('Gwalior Jn','Madurai Jn','20120710')[0]['av']

import urllib, urllib2, re, xbmcplugin, xbmcgui, json

SERVICE_URL = "http://tv.aftonbladet.se/webbtv/"
SERVICE_TRANSLATIONS_SERVER = "http://aftonbladet-play.drlib.aptoma.no/video.json"
VIDEO_LINKS_SERVER = "http://aftonbladet-play.videodata.drvideo.aptoma.no/actions/video/native/"
PARAMS = "service=json"

MODE_CATEGORIES = 1
MODE_LIVE = 2
MODE_POPULAR = 3
MODE_PROGRAMS = 4
MODE_VIDEOLINKS = 5


def STARTMENU():
    addDir('Kategorier', '', MODE_CATEGORIES, '')
    addDir('LIVE', '', MODE_LIVE, '')
    addDir('Mest sett just nu', '', MODE_POPULAR, '')


def open_article(articleData):
    data = json.load(urllib2.urlopen("http://aftonbladet-play.drlib.aptoma.no/video.json?id=" + articleData['aptomaId']))
    videoId = data['items'][0]['videoId']
    videoLinks = json.load(urllib2.urlopen(VIDEO_LINKS_SERVER + "?id=" + videoId))
    addDir(data['title'], videoLinks['formats']['http'][0]['path'])


def CATEGORIES(url):
    get_program_categories(url, PARAMS)


def load_json(url, params):
    request = urllib2.Request(url + '?' + params, None, {'Accept': 'application/json', 'Accept-Charset': 'utf-8', 'Content-Type': 'application/json; charset=UTF-8'}, None, False)
    response = urllib2.urlopen(request)
    data = response.read()
    response.close()
    return json.loads(data, 'ISO-8859-1')


def get_program_categories(url, params):
    print "Opening url: " + url
    jsonData = load_json(url, params)
    for category in jsonData['categories']:
        children = category['children']
        if not children:
            dirMode = MODE_PROGRAMS
        else:
            dirMode = MODE_CATEGORIES
        print "Dirmode: " + str(dirMode)
        addDir(name=getEscapedField(category, 'title'), url=category['url'], mode=dirMode, iconimage='')


def getEscapedField(obj, name):
    try:
        return obj[name].encode("ascii", "ignore")
    except Exception, e:
        print e
        return 'FAILWHALE'


def PROGRAMS(url, name):
    pass


def VIDEOLINKS(url, name):
    req = urllib2.Request(url)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    match = re.compile('').findall(link)
    for url in match:
        addLink(name, url, '')


def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param


def addLink(name, url, iconimage):
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


params = get_params()
url = None
name = None
mode = None

try:
    url = urllib.unquote_plus(params["url"])
except:
    pass
try:
    name = urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass

print "Mode: " + str(mode)
print "URL: " + str(url)
print "Name: " + str(name)

if mode == None:
    print ""
    STARTMENU()

elif mode == MODE_CATEGORIES:
    if url == None:
        print "URL == None, setting default"
        url = SERVICE_URL
    CATEGORIES(url)

elif mode == MODE_PROGRAMS:
    print "" + url
    PROGRAMS(url, name)

elif mode == MODE_VIDEOLINKS:
    print "" + url
    VIDEOLINKS(url, name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))

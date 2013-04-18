# coding=utf-8
import urllib, urllib2, xbmcplugin, xbmcgui, json

SERVICE_URL = "http://tv.aftonbladet.se/webbtv/"
SERVICE_TRANSLATIONS_SERVER = "http://aftonbladet-play.drlib.aptoma.no/video.json"
VIDEO_LINKS_SERVER = "http://aftonbladet-play.videodata.drvideo.aptoma.no/actions/video/native/"
PARAMS = "service=json"

MODE_CATEGORIES = 1
MODE_LIVE = 2
MODE_POPULAR = 3
MODE_PROGRAMS = 4
MODE_VIDEOLINKS = 5
MODE_PROGRAM_SUBCATEGORY = 6
MODE_PROGRAMS_FOR_SUBCAT = 7


def STARTMENU():
    addDir('Kategorier', '', MODE_CATEGORIES, '')
    addDir('LIVE', '', MODE_LIVE, '')
    addDir('Mest sett just nu', '', MODE_POPULAR, '')


def add_video_link(articleData):
    data = json.load(urllib2.urlopen(SERVICE_TRANSLATIONS_SERVER + "?id=" + articleData['aptomaId']))
    videoId = None
    for item in data['items']:
        if item['id'] == articleData['aptomaId']:
            videoId = item['videoId']
    if videoId:
        videoLinks = json.load(urllib2.urlopen(VIDEO_LINKS_SERVER + "?id=" + videoId))
        addLink(getEscapedField(articleData, 'title'), videoLinks['formats']['http'][0]['path'],
                articleData['image']['moduleEpisodeUri'])


def CATEGORIES(url):
    get_program_categories(url, PARAMS)


def POPULAR(url):
    get_category(url, 'hotPrograms')


def LIVE(url):
    get_category(url, 'liveVideos')


def get_category(url, name):
    if url is None:
        print "URL == None, setting default"
        url = SERVICE_URL
    jsonData = load_json(url, PARAMS)
    if len(jsonData[name]) < 1:
        addDir(name='Inga videos för tillfället', url=url, mode=None, iconimage='')
        return
    for program in jsonData[name]:
        add_video_link(program)


def load_json(url, params):
    request = urllib2.Request(url + '?' + params, None, {'Accept': 'application/json', 'Accept-Charset': 'utf-8',
                                                         'Content-Type': 'application/json; charset=UTF-8'}, None,
                              False)
    response = urllib2.urlopen(request)
    data = response.read()
    response.close()
    return json.loads(data, 'ISO-8859-1')


def get_subcategories_for_category(url, params, name):
    jsonData = load_json(url, params)
    for category in jsonData['categories']:
        if name == getEscapedField(category, 'title'):
            for child in category['children']:
                cTitle = getEscapedField(child, 'title')
                cUrl = child['url']
                addDir(name=cTitle, url=cUrl, mode=MODE_PROGRAMS_FOR_SUBCAT, iconimage='')


def get_programs_for_subcategory(url, params, name):
    jsonData = load_json(url, params)
    for related in jsonData['playerData']['relatedVideos']:
        add_video_link(related)


def get_program_categories(url, params):
    print "Opening url: " + url
    jsonData = load_json(url, params)
    for category in jsonData['categories']:
        print category
        children = category['children']
        if not children:
            dirMode = MODE_PROGRAMS
        else:
            dirMode = MODE_CATEGORIES

        dirMode = MODE_PROGRAM_SUBCATEGORY

        #print "Dirmode: " + str(dirMode)

        addDir(name=getEscapedField(category, 'title'), url=category['url'], mode=dirMode, iconimage='')


def getEscapedField(obj, name):
    try:
        return obj[name].encode("utf-8", "ignore")
    except Exception, e:
        print e
        return 'FAILWHALE'


def PROGRAMS(url, name):
    pass


def VIDEOLINKS(url, name):
    pass


def get_params():
    param = []
    param_string = sys.argv[2]
    if len(param_string) >= 2:
        params = sys.argv[2]
        cleaned_params = params.replace('?', '')
        pairs_of_params = cleaned_params.split('&')
        param = {}
        for i in range(len(pairs_of_params)):
            split_params = pairs_of_params[i].split('=')
            if (len(split_params)) == 2:
                param[split_params[0]] = split_params[1]

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
#print "URL: " + str(url)
print "Name: " + str(name)

if mode == None:
    STARTMENU()

elif mode == MODE_CATEGORIES:
    if url == None:
        print "URL == None, setting default"
        url = SERVICE_URL
    CATEGORIES(url)

elif mode == MODE_POPULAR:
    POPULAR(url)

elif mode == MODE_LIVE:
    LIVE(url)

elif mode == MODE_PROGRAMS:
    PROGRAMS(url, name)

elif mode == MODE_VIDEOLINKS:
    VIDEOLINKS(url, name)

elif mode == MODE_PROGRAM_SUBCATEGORY:
    get_subcategories_for_category(url, PARAMS, name)

elif mode == MODE_PROGRAMS_FOR_SUBCAT:
    get_programs_for_subcategory(url, PARAMS, name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))

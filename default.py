# coding=utf-8
import urllib
import urllib2
import xbmcplugin
import xbmcgui
import json

SERVICE_URL = "http://tv.aftonbladet.se/webbtv/"
SERVICE_TRANSLATIONS_SERVER = "http://aftonbladet-play.drlib.aptoma.no/video.json"
VIDEO_LINKS_SERVER = "http://aftonbladet-play.videodata.drvideo.aptoma.no/actions/video/native/"
PARAMS = "service=json"

MODE_CATEGORIES = 1
MODE_LIVE = 2
MODE_POPULAR = 3
MODE_PROGRAM_SUBCATEGORY = 6
MODE_PROGRAMS_FOR_SUBCAT = 7


# magic; id of this plugin's instance - cast to integer
thisPlugin = int(sys.argv[1])


def get_start_menu():
    addDir('Kategorier', '', MODE_CATEGORIES, '')
    addDir('LIVE', '', MODE_LIVE, '')
    addDir('Mest sett just nu', '', MODE_POPULAR, '')


def add_video_link(articleData, linkCount):
    data = load_json(SERVICE_TRANSLATIONS_SERVER, "id=" + articleData['aptomaId'])
    videoId = None
    for item in data['items']:
        if item['id'] == articleData['aptomaId']:
            print "Found id"
            videoId = item['videoId']
    if videoId:
        videoLinks = load_json(VIDEO_LINKS_SERVER, "id=" + videoId)
        print "Found data: " + str(data)
        description = ''
        if articleData['description']:
            description = getEscapedField(articleData,'description')
        image = ''
        if articleData['image']:
            image = articleData['image']['moduleEpisodeUri']

        title  = getEscapedField(articleData, 'title')
        episode_ = articleData['episode']
        if episode_:
            title = title + " " + str(episode_)
        addLink(title, videoLinks['formats']['http'][0]['path'], image, description, linkCount)
    else:
        print "Could not find video Url for id " + articleData['aptomaId']


def get_most_popular_videos(url):
    get_category(url, 'hotPrograms')


def get_live_videos(url):
    get_category(url, 'liveVideos')


def get_category(url, name):
    if url is None:
        print "URL == None, setting default"
        url = SERVICE_URL
    jsonData = load_json(url, PARAMS)
    if len(jsonData[name]) < 1:
        addDir(name='Inga videos för tillfället', url=url, mode=None, iconimage='')
        return
    linkCount = len(jsonData[name])
    for program in jsonData[name]:
        add_video_link(program, linkCount)


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
    linkCount = len(jsonData['playerData']['relatedVideos'])
    for related in jsonData['playerData']['relatedVideos']:
        add_video_link(related, linkCount)


def get_program_categories(url, params):
    print "Opening url: " + url
    jsonData = load_json(url, params)
    for category in jsonData['categories']:
        iconimage = ''

        if category['image']:
            iconimage = category['image']['']
        dirMode = MODE_PROGRAM_SUBCATEGORY

        addDir(name=getEscapedField(category, 'title'), url=category['url'], mode=dirMode, iconimage='')


def getEscapedField(obj, name):
    try:
        return obj[name].encode("utf-8", "ignore")
    except Exception, e:
        print e
        return 'FAILWHALE'


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


def addLink(name, url, iconimage, description, linkCount):
    liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Description": description})
    ok = xbmcplugin.addDirectoryItem(handle=thisPlugin, url=url, listitem=liz, totalItems=linkCount)
    return ok


def addDir(name, url, mode, iconimage):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=thisPlugin, url=u, listitem=liz, isFolder=True)
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

if mode is None:
    get_start_menu()

elif mode == MODE_CATEGORIES:
    if url is None:
        print "URL == None, setting default"
        url = SERVICE_URL
    get_program_categories(url, PARAMS)

elif mode == MODE_POPULAR:
    get_most_popular_videos(url)

elif mode == MODE_LIVE:
    get_live_videos(url)

elif mode == MODE_PROGRAM_SUBCATEGORY:
    get_subcategories_for_category(url, PARAMS, name)

elif mode == MODE_PROGRAMS_FOR_SUBCAT:
    get_programs_for_subcategory(url, PARAMS, name)

xbmcplugin.endOfDirectory(thisPlugin)

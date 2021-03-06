#######################################
#python imports
import urlparse
from os import path
from urllib import quote
#######################################
#Zope and Plone imports
from zope.interface import implements, Interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
###############################################3
from Acquisition import aq_inner
from zope.component import getMultiAdapter
#utility control panel imports
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Acquisition import interfaces
##########################################
#Products Imports
from zope.app.component.hooks import getSite
from iw.fss.config import ZCONFIG
#################################
from cenditel.video import videoMessageFactory as _
from cenditel.transcodedeamon.convert import MFN as MFNI
from cenditel.transcodedeamon.convert import newtrans_init_
from cenditel.transcodedeamon.convert import MTD as MTDI
from cenditel.transcodedeamon.convert import ServiceList
from cenditel.transcodedeamon import manipulatefilename

##########################################
#Options Imports
from cenditel.transcodedeamon.interfaces import ITranscodeSetings


class IvideoView(Interface):
    """
    video view interface
    """

    def test():
        """ test method"""

class videoView(BrowserView):
    """
    video browser view
    """
    implements(IvideoView)
    
    def __init__(self, context, request):
	self.context = context
	self.request = request
	self.MyTitle = ""
	self.MyTitleWhitOutSpace = ""
	self.newfilename = ""
	self.filenamesaved= ""
	self.folderfile = ""
	self.StatusOfFile = ""
	self.filesize = ""
	self.SERVER = ""
	self.folderfileOGG=""
	self.PathOfFile=""
	self.STORAGE=""
	self.AbsoluteServerPath=""
	self.newfiletranscoded=""
	self.Error=False
	#print self.request.items()


    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()


    def RemoveSlash(self, path):
	reverse=path[::-1]
	newpath=""
	if reverse[0]=='/':
	    for x in cadena[:-1]:
		newcadena=newcadena+x
	    return newpath
	else:
	    return path

    def PlayingVideoType(self):
	#import pdb; pdb.set_trace()
	registry = getUtility(IRegistry)
	settings = registry.forInterface(ITranscodeSetings)
	self.SERVER = self.RemoveSlash(settings.adress_of_streaming_server)
	VIDEO_PARAMETRES_TRANSCODE = settings.ffmpeg_parameters_video_line
	AUDIO_PARAMETRES_TRANSCODE = settings.ffmpeg_parameters_audio_line
	audio_content_types=settings.audio_valid_content_types
	video_content_types=settings.video_valid_content_types
	portal = getSite()
	self.STORAGE=ZCONFIG.storagePathForSite(portal)
	self.MyTitle = self.context.Title()
	idvideo=self.context.getId()
	self.MyTitleWhitOutSpace = MFNI.DeleteSpaceinNameOfFolderFile(MFNI.TitleDeleteSpace(self.MyTitle))
	self.PathOfFile = self.context._getURL()
	virtualobject=self.context.getVideo()
	self.filenamesaved=virtualobject.filename
	self.extension=MTDI.CheckExtension(self.filenamesaved)
	if self.extension=="ogg" or self.extension=="ogv" or self.extension=="OGG" or self.extension=="OGV":
	    self.folderfileOGG=path.join(self.PathOfFile,quote(self.filenamesaved))
	    self.prefiletranscoded=path.join(self.STORAGE,self.PathOfFile,self.filenamesaved)
	    if path.isfile(self.prefiletranscoded)==True:
		self.StatusOfFile=ServiceList.available(idvideo,self.prefiletranscoded)
		if self.StatusOfFile == False:
		    ServiceList.AddReadyElement(idvideo,self.prefiletranscoded)
		    self.StatusOfFile=True
		    ServiceList.SaveInZODB()
		    self.AbsoluteServerPath = path.join(self.SERVER,self.folderfileOGG)
		else:
		    self.AbsoluteServerPath = path.join(self.SERVER,self.folderfileOGG)
	    else:
		print _("File not found "+self.prefiletranscoded)
		self.Error=True
		self.ErrorSituation()
	else:
	    newtrans_init_(self.STORAGE,
			   self.PathOfFile,
			   self.filenamesaved,
			   idvideo,
			   VIDEO_PARAMETRES_TRANSCODE,
			   AUDIO_PARAMETRES_TRANSCODE,
			   audio_content_types,
			   video_content_types)
	    self.folderfileOGG=MTDI.newname(path.join(self.PathOfFile,self.filenamesaved))
	    self.AbsoluteServerPath = path.join(self.SERVER,MTDI.nginxpath(self.folderfileOGG))
	    self.newfiletranscoded=MTDI.nginxpath(path.join(self.STORAGE,self.folderfileOGG))
	    self.StatusOfFile = ServiceList.available(idvideo,self.newfiletranscoded)
	    #import pdb;pdb.set_trace()
	    if self.StatusOfFile == True:
		self.newfilename=MTDI.newname(self.filenamesaved)
	    else:
		self.newfilename=_('The file is not ready yet, please contact site administration')
	return

    def ErrorSituation(self):
	#import pdb; pdb.set_trace()
	if self.Error==False:
	    return False
	else:
	    return True

    def TrueFile(self):
	if self.extension=="ogg" or self.extension=="ogv":
	    if path.isfile(self.prefiletranscoded):
		return True
	    else:
		return False
	else:
	    if path.isfile(self.newfiletranscoded)==False:
		return False
	    else:
		return True

    def GETFileSize(self):
	#import pdb;pdb.set_trace()
	if self.extension=='ogg' or self.extension=='ogv':
	    try:
		self.filesize = MFNI.ReturnFileSizeOfFileInHardDrive(path.join(self.STORAGE,self.folderfileOGG))
		thefilesize = self.filesize
		return thefilesize
	    except OSError:
		self.Error=True
		self.ErrorSituation()
		return "0 kb"
	else:
	    try:
		self.filesize = MFNI.ReturnFileSizeOfFileInHardDrive(self.newfiletranscoded)
		thefilesize = self.filesize
		return thefilesize
	    except OSError:
		self.Error=True
		self.ErrorSituation()
		return "0 kb"


    def GETAdressOfWebServer(self):
	"""
	This method return the server path to the <audio> label
	"""
	TheFilePath = self.AbsoluteServerPath
	return TheFilePath

    def GETStatusOfFile(self):
	TheStatus = self.StatusOfFile
	str(TheStatus)
	return TheStatus


    def GETNewNameVideo(self):
	if self.extension=='ogg' or self.extension=='ogv':
	    return self.filenamesaved
	else:
	    TheNewName = self.newfilename
	    return TheNewName

    def GETfolderfile(self):
	TheFolderFile = self.AbsoluteServerPath 
	return TheFolderFile 


    def GETMyTitle(self):
	MyTitleWhitOutSpace  = self.MyTitleWhitOutSpace
	return MyTitleWhitOutSpace

    def ExternalMethodforURL(self):
	return self.context.absolute_url()


    def URLElement(self):
	url = self.context.absolute_url()
	self.PathOfFile = MFNI.ReturnPathOfFile(url)
	return self.PathOfFile
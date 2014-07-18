#!/usr/bin/python3
import os, sys
import string
import pygame
from pygame.locals import *

if not pygame.font: print('Warning, fonts disabled')
if not pygame.font: print('Warning, sound disabled')

RET_SPACES = '   '
SCANLINE_SIZE = 2

class TermCmd:
    def help(self, list, arg):
        list.append(RET_SPACES+'This is help.')
        for cmd in dir(TermCmd):
            if cmd[:2] != '__':
                list.append(2*RET_SPACES+cmd)
    def quit(self, list, arg):
        sys.exit()
    def menu(self, list, arg):
        return 'setmenu'
    def dir(self, list, arg):
        imgdir = os.listdir('img')
        imgs = []
        for img in imgdir:
            if os.path.splitext(img)[1] == '.jpg' or os.path.splitext(img)[1] == '.png':
                imgs.append('/'+os.path.splitext(img)[0])
        dirs = { '/users': [ '/root', '/exec' ], '/docs': [], '/img': imgs, '/video': [] }
        if arg:
            if arg in dirs and dirs[arg]:
                for dir in dirs[arg]:
                    list.append(RET_SPACES+arg+dir)
            else:
                list.append(RET_SPACES+'Błąd dysku.')
        else:
            for dir in dirs:
                list.append(RET_SPACES+dir)
    def show(self, list, arg):
        isjpg = os.path.exists('img/'+arg+'.jpg')
        ispng = os.path.exists('img/'+arg+'.png')
        if isjpg or ispng:
            list.append(RET_SPACES+'Załadowano.')
            retval = []
            retval.append('showimg')
            if ispng:
                retval.append('img/'+arg+'.png')
            else:
                retval.append('img/'+arg+'.jpg')
            return retval
        elif arg:
            list.append(RET_SPACES+'Błąd źródła.')
        else:
            list.append(RET_SPACES+'Użycie: show [nazwa]. "Q" aby zakończyć.')


class PyManMain:
    def __init__(self, width=1280, height=1024):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), HWSURFACE | DOUBLEBUF | NOFRAME | RESIZABLE)
        self.size = self.screen.get_size()
        self.caption = pygame.display.set_caption('Fallout Terminal')
        pygame.mouse.set_visible(0)
        self.head = []
        self.head.append('system operacyjny centralnego zarządu przemysłu teletechnicznego')
        self.head.append('wszelkie prawa zastrzeżone, 2069-2077 eltra')
        self.head.append('wersja zmodyfikowana na potrzeby Flying Caravans')
        self.scansize = SCANLINE_SIZE
        self.showImg = False
        self.cmd = ''
        self.prompt = ''
        self.line = []
        self.promptMode = True
        self.menuLevel = 0
        if pygame.font:
            self.font = pygame.font.Font('fe.ttf', 36)

    def Rehead(self):
        self.line = []
        for txt in self.head:
            self.line.append('#!C'+txt.upper())


    def ScaleToFit(self, surface, size):
        x, y = surface.get_size()
        scale = size[0]/float(x)
        if y * scale > size[1]:
            scale = size[1]/float(y)
        return pygame.transform.scale(surface, (int(scale*x), int(scale*y)))

    def CreateSolid(self, size, color):
        solid = pygame.Surface(size)
        solid = solid.convert()
        solid.fill(color)
        return solid


    def CenterSurfaces(self, surface1, surface2):
        rect1 = surface1.get_rect()
        rect2 = surface2.get_rect()
        rect1.centerx = rect2.centerx
        rect1.centery = rect2.centery
        return rect1

    def OverlayScanlines(self, surface, size):
        bgw, bgh = surface.get_size()
        scanline = pygame.Surface((bgw, size))
        scanline = scanline.convert()
        scanline.fill((0, 0, 0))
        for place in range(0, bgh, 2*size):
            surface.blit(scanline, (0, place))

    def OverlayDarkener(self, surface, alpha):
        darkener = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        darkener = darkener.convert_alpha()
        darkener.fill((0, 0, 0))
        darkener.set_alpha(alpha)
        surface.blit(darkener, (0, 0))

    def LoadImage(self, name, colorkey):
        image = pygame.image.load(name)
        image = image.convert()
        if colorkey:
            image.set_colorkey(colorkey)
        return image

    def Prompter(self, event, name):
        if name in string.digits+string.ascii_letters+'/' and not self.ctrlMod:
            self.prompt += self.keyName
        if event == pygame.K_SPACE:
            self.prompt += ' '
        if event == pygame.K_UP:
            for prev in reversed(self.line):
                if prev[0] == '>' and prev[2:] != self.prompt:
                    self.prompt = prev[2:]
                    break
        if event == pygame.K_RETURN:
            self.cmd = self.prompt
            self.line.append('> '+self.prompt)
            self.prompt = ''
        if event == pygame.K_BACKSPACE:
            self.prompt = self.prompt[:-1]

    def MainLoop(self):
        self.Rehead()
        self.background = self.CreateSolid(self.size, (0, 32, 0))
        self.bgimage = self.ScaleToFit(self.LoadImage('fc.jpg', (0, 0, 0)), self.size)
        self.background.blit(self.bgimage, self.CenterSurfaces(self.bgimage, self.background))
        self.OverlayScanlines(self.background, SCANLINE_SIZE)

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    self.ctrlMod = None
                    self.keyEvent = event.key
                    self.keyName = pygame.key.name(self.keyEvent)
                    self.keyMods = pygame.key.get_mods()
                    if self.keyMods:
                        if self.keyMods & pygame.KMOD_LCTRL or self.keyMods & pygame.KMOD_RCTRL:
                            print('CTRL+', end='')
                            self.ctrlMod = True
                        if self.keyMods & pygame.KMOD_LSHIFT or self.keyMods & pygame.KMOD_RSHIFT and self.keyName in string.ascii_lowercase:
                            self.keyName = self.keyName.upper()
                    print(self.keyName, ': ', event.key)

                    if self.keyName == 'q' and self.showImg:
                        self.showImg = False
                    elif self.promptMode:
                        self.Prompter(self.keyEvent, self.keyName)
                    else:
                        if self.keyName == '0' and self.menuLevel == 0:
                            self.Rehead()
                            self.promptMode = True
                        elif self.keyName in string.digits:
                            if self.keyName == '0' and self.menuLevel > 0:
                                self.menuLevel = int(str(self.menuLevel)[1:])
                            else:
                                self.menuLevel = int(self.keyName+str(self.menuLevel))


                    print(str(self.menuLevel)+'> ', self.prompt)
                    if self.keyMods & pygame.KMOD_LCTRL and self.keyName == 'q':
                        sys.exit()

            if self.cmd:
                print('CMD: ', self.cmd)
                self.cmd = self.cmd.split(' ')
                self.tcmd = TermCmd()
                #if self.cmd == 'help':
                if hasattr(self.tcmd, self.cmd[0]):
                    retval = getattr(self.tcmd, self.cmd[0])(self.line, ' '.join(self.cmd[1:]) )
                    #TermCmd.help(self.line)
                    if retval == 'setmenu':
                        self.promptMode = False
                    if retval and retval[0] == 'showimg':
                        self.showImg = retval[1]
                else:
                    self.line.append('  Błąd składni.')
                self.cmd = ''

            if len(self.line) >= 20:
                del self.line[0:9]

            self.menu = [ ['Kartoteki', None], ['Kalendarium', None], ['Moduł kredytowy', None], ['Ewidencja', None], ['Odczyt z robotów moblinych', None], ['Otwórz drzwi', 'Nie posiadasz drzwi.'] ]
            #self.menu[6] = 'Nie posiadasz drzwi.'

            self.screen.blit(self.background, (0, 0))
            if pygame.font:
                if self.promptMode:
                    self.line.append('> '+self.prompt)
                else:
                        self.Rehead()
                        self.line.append('> '+str(self.menuLevel))
                        if str(self.menuLevel).endswith('0'):
                            for i, txt in enumerate(self.menu):
                                self.line.append(str(i+1)+' - '+txt[0])
                for i, txt in enumerate(self.line):
                    if txt[:3] == '#!C':
                        self.center = True
                        txt = txt[3:]
                    else:
                        self.center = False
                    self.label = self.font.render(txt, 1, (0, 255, 127))
                    self.linepos = 10 + (i*50)
                    self.textpos = self.label.get_rect()
                    if self.center:
                        self.textpos.centerx = self.screen.get_rect().centerx
                    else:
                        self.textpos.x = 10
                    self.textpos.y = self.linepos
                    #self.screen.blit(self.label, (10, self.linepos))
                    self.screen.blit(self.label, self.textpos)
                self.line.pop()
                #self.label = self.font.render('> '+self.prompt, 1, (0, 255, 127))
                #self.linepos = 10 + (self.currline*50)
                #self.screen.blit(self.label, (10, self.linepos))

            if self.showImg:
                self.imgview = self.LoadImage(self.showImg, None)
                self.screen.blit(self.imgview, (0, 0))
                self.OverlayScanlines(self.screen, SCANLINE_SIZE)

            pygame.display.flip()


if __name__ == "__main__":
    MainWindow = PyManMain()
    MainWindow.MainLoop()

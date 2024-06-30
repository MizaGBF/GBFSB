import aiohttp
import asyncio
from typing import Union, Optional
import json
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import math

# ----------------------------------------------------------------------------------------------------------------
# GBFSB 2.0
# Public Release
# ----------------------------------------------------------------------------------------------------------------
class GBFSB():
    MANIFESTS = [
        [
            "npc_{}_UUSS", "npc_{}_UUSS_s2", "npc_{}_UUSS_f1", "npc_{}_UUSS_f1_s2", "npc_{}_UUSS_0", "npc_{}_UUSS_0_s2", "npc_{}_UUSS_0_f1", "npc_{}_UUSS_0_f1_s2", "npc_{}_UUSS_1", "npc_{}_UUSS_1_s2", "npc_{}_UUSS_1_f1", "npc_{}_UUSS_1_f1_s2", "phit_{}SS", "phit_{}_UUSS", "nsp_{}_UUSS", "nsp_{}_UUSS_f1", "nsp_{}_UUSS_s2", "nsp_{}_UUSS_f1_s2", "nsp_{}_UUSS_s3", "nsp_{}_UUSS_f1_s3", "nsp_{}_UUSS_s2_a", "nsp_{}_UUSS_f1_s2_a", "nsp_{}_UUSS_s3_a", "nsp_{}_UUSS_f1_s3_a", "ab_{}SS_01", "ab_{}SS_02", "ab_{}SS_03", "ab_{}SS_04", "ab_{}SS_05", "ab_{}SS_06", "ab_all_{}SS_01", "ab_all_{}SS_02", "ab_all_{}SS_03", "ab_all_{}SS_04", "ab_all_{}SS_05", "ab_all_{}SS_06"
        ],
        [
            "summon_{}_UU_attack", "summon_{}_UU_damage", "summon_{}_UU_a_attack", "summon_{}_UU_a_damage", "summon_{}_UU_b_attack", "summon_{}_UU_b_damage"
        ],
        [
            "phit_{}", "sp_{}", "sp_{}_s2", "sp_{}_1_s2", "sp_{}_s3", "sp_{}_1_s3"
        ]
    ]
    COLORING = [
        [255, 181, 181, ["body", "arm", "leg", "head", "finger", "hand", "foot", "feet"]],
        [55, 120, 91, ["sword", "ax", "axe", "gun", "pistol", "staff", "book", "spear", "lance", "fist", "melee", "punch", "katana", "bow", "harp", "dagger", "knife", "blade", "weapon", "cane", "wepon", "weapon01", "wep", "wep1", "puppet", "pole", "waepon", "laser", "shaft", "subweapon", "rod", "holster", "sowrd", "roar", "weaponback", "spiear", "missile", "beam", "magic", "hammer", "oraora", "baton", "tome", "gunbelt", "muzzle", "gosen", "violin"]],
        [171, 140, 166, ["horn", "wing", "ponytail", "beard", "hair", "Rhair", "Lhair", "teil", "tail", "backhair", "bacckhair", "Wing", "pigtail", "pigtails", "chest", "neck", "thighs", "thigh", "Rthigh", "Lthigh", "Rarm", "Larm", "arm", "head", "shoulder", "Rshoulder", "Lshoulder", "chestBack", "LshoulderBack", "RshoulderBack", "leg", "Rleg", "Lleg", "mituami"]],
        [163, 136, 69, ["ribbon", "mantle", "hat", "sheath", "basket", "jewel", "skeleton", "barrier", "sunflower", "jwel", "rose", "shield", "shield2", "shild2", "potion", "flower", "angel", "spirit", "halloween", "heart", "sunshine", "butterfly", "dragon", "cape", "cloak", "loincloth", "realwing", "bird", "taiko", "hana", "doll", "scarf", "fang", "rainbow", "bookitem", "stall", "chopsticks", "friednoodles", "noodles", "frankfurter", "squid", "corn", "umbrella", "sunglasses", "armor", "candy", "Kerberos", "kerberos", "wire", "mask", "confetti", "onigiri", "facemask", "hood", "helmet", "dress", "star", "emblem", "fairy", "card", "glass", "toothpick"]],
        [207, 121, 50, ["sode", "Lsode", "Rsode", "sleeve", "robe", "collar", "cloth", "mant", "ribon", "frills", "frill", "colar", "belt", "necktie", "shoes", "earring", "skirt", "cape01", "backskirt", "scarf"]],
        [107, 23, 17, ["fire", "red", "hibana", "ball", "glow", "bomb"]],
        [17, 42, 107, ["water", "blue", "ice", "mizu", "bubble", "cold", "freeze", "snow", "wave", "sea", "nagare", "sui", "shabon"]],
        [107, 67, 17, ["earth", "orange", "rock", "stone", "quake", "syougeki", "iwa"]],
        [17, 107, 23, ["wind", "green", "tornado", "kaze", "air"]],
        [58, 17, 107, ["dark", "purple", "shadow", "blood"]],
        [106, 107, 17, ["light", "yellow", "gold", "sun", "ray", "aura", "thunder", "spark", "thiunde", "kira"]],
        [247, 0, 157, ["pink", "flower", "sakura"]],
        [40, 40, 40, ["eye"]],
        [135, 48, 32, ["ship"]],
        [88, 119, 76, ["grass"]],
        [148, 255, 241, ["sky"]],
        [255, 255, 255, ["cloud", "kumo"]],
        [64, 95, 112, ["win"]],
        [196, 65, 85, ["attack"]],
        [112, 69, 64, ["hit", "damage"]],
        [112, 64, 98, ["ef"]]
    ]
    DUMMY_COLORS = [
        (255, 255, 255, 255), (255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255), (255, 255, 0, 255), (255, 0, 255, 255), (0, 255, 255, 255),
        (255, 128, 128, 255), (128, 255, 128, 255), (128, 128, 255, 255), (255, 255, 128, 255), (255, 128, 255, 255), (128, 255, 255, 255),
        (180, 180, 180, 255), (180, 0, 0, 255), (0, 180, 0, 255), (0, 0, 180, 255), (180, 180, 0, 255), (180, 0, 180, 255), (0, 180, 180, 255),
        (180, 128, 128, 255), (128, 180, 128, 255), (128, 128, 180, 255), (180, 180, 128, 255), (180, 128, 180, 255), (128, 180, 180, 255),
        (120, 120, 120, 255), (120, 0, 0, 255), (0, 120, 0, 255), (0, 0, 120, 255), (120, 120, 0, 255), (120, 0, 120, 255), (0, 120, 120, 255),
        (60, 128, 128, 255), (128, 60, 128, 255), (128, 128, 60, 255), (60, 60, 128, 255), (60, 128, 60, 255), (128, 60, 60, 255),
        (60, 60, 60, 255), (60, 0, 0, 255), (0, 60, 0, 255), (0, 0, 60, 255), (60, 60, 0, 255), (60, 0, 60, 255), (0, 60, 60, 255)
    ]
    SS = (1000, 1000) # render size
    HS = (500, 500) # half size


    def __init__(self, client : aiohttp.ClientSession) -> None:
        self.client = client
        self.id = None
        self.uncap = "01"
        self.style = ""
        self.kind = None
        self.spritesheets = {}
        self.sfx = set()
        self.cjs = {}
        self.sts = {}
        self.dum = False
        self.hbox = False
        self.dum_font = ImageFont.truetype("assets/font.ttf", 14)
        self.dmp_font = ImageFont.truetype("assets/font.ttf", 18)
        self.dumc_c = 0

    """_debug_exportCJS()
    Export CJS data to a JSON file. For debug and development only.
    
    Parameters
    ----------
    cjs_term: CJS name search string
    search: Boolean, set to False for an exact match with cjs_term
    cjs_content: String matching an animation name. If set, only this animation will be exported.
    """
    def _debug_exportCJS(self, cjs_term : str, *, search : bool = True, cjs_content : str = None) -> None:
        files = []
        if search:
            for k in self.cjs:
                if cjs_term in k:
                    files.append(k)
        else:
            files.append(k)
        for k in files:
            if k in self.cjs:
                with open(k + ".json", "w") as outfile:
                    try:
                        if isinstance(cjs_content, str): 
                            data = {}
                            for kk in self.cjs[k]:
                                if cjs_content in kk:
                                    data[kk] = self.cjs[k][kk]
                            outfile.write(json.dumps(data, indent=4))
                            print("Exported " + k + ".json with '" + cjs_content + "' only keys")
                        else:
                            outfile.write(json.dumps(self.cjs[k], indent=4))
                            print("Exported " + k + ".json")
                    except:
                        pass

    """load()
    Load manifest files for a corresponding ID
    
    Parameters
    ----------
    eid: Integer, element ID
    uncap: Integer, uncap number
    style: String, style string
    
    Returns
    ----------
    bool: True if success, False if invalid parameter, already loaded, not found, etc...
    """
    async def load(self, eid : int, *, uncap : int = 1, style : str = "") -> bool:
        if self.id is not None: return False
        sid = str(eid)
        if len(sid) != 10 or eid < 1000000000 or eid >= 4000000000 or uncap < 0 or uncap > 99: return False
        self.id = eid
        self.uncap = str(uncap).zfill(2)
        self.style = style
        if self.style != "": self.style = '_' + self.style
        self.kind = {'1':2, '2':1, '3':0}[sid[0]]
        check_all = False if self.kind == 0 else True
        self.spritesheets = {}
        self.cjs = {}
        found = False
        for i in range(len(self.MANIFESTS[self.kind])):
            found = await self.manifest2sprites(self.MANIFESTS[self.kind][i].format(eid).replace('UU', self.uncap).replace('SS', self.style)) or found
            if not found and ((self.kind == 0 and i >= 6) or (self.kind != 0 and i == 0)) and not check_all:
                break
        if not self.exist():
            self.id = None
        return True

    """request()
    Make a HTTP GET request
    
    Parameters
    ----------
    url: String, url to request
    
    Returns
    ----------
    bytes: Url content, None if error
    
    """
    async def request(self, url : str) -> Optional[bytes]:
        try:
            res = await self.client.get(url)
            async with res:
                if res.status != 200: return None
                return await res.read()
        except:
            return None


    """manifest2sprites()
    Request a given manifest and extract spritesheet paths
    
    Parameters
    ----------
    file: String, manifest file name
    
    Returns
    ----------
    bool: True if success, False if invalid parameter
    """
    async def manifest2sprites(self, file):
        manifest = await self.request("https://prd-game-a-granbluefantasy.akamaized.net/assets_en/js/model/manifest/{}.js".format(file))
        if manifest is None: return False
        manifest = manifest.decode('utf-8')
        st = manifest.find('manifest:') + len('manifest:')
        ed = manifest.find(']', st) + 1
        data = json.loads(manifest[st:ed].replace('Game.imgUri+', '').replace('src:', '"src":').replace('type:', '"type":').replace('id:', '"id":'))
        res = []
        for l in data:
            src = l['src'].split('?')[0]
            res.append(src)
        self.spritesheets[file] = res
        return True

    """exist()
    Indicate if the element exists. To be used after load()
    
    Returns
    ----------
    bool: True if a spritesheet exists, False otherwise
    """
    def exist(self) -> bool:
        return (len(self.spritesheets.keys()) > 0)

    """loaded()
    Indicate if load() ran with success beforehand.
    
    Returns
    ----------
    bool: True if it did load, False otherwise
    """
    def loaded(self) -> bool:
        return (self.id is not None)

    """mc()
    Create transparent image of given size
    
    Parameters
    ----------
    size: Tuple, width and heigth
    transparent_bg: Boolean, put a transparent alpha channel
    
    Returns
    ----------
    Image: image object
    """
    def mc(self, size : tuple, transparent_bg : bool = True) -> Image:
        img = Image.new('RGB', size, "black")
        if transparent_bg:
            im_a = Image.new("L", img.size, "black")
            img.putalpha(im_a)
            im_a.close()
        return img

    """renderCJS()
    Load CJS files, parse CJS files and create dummy spritesheets
    
    Parameters
    ----------
    options:
        - build_dummy: Boolean (Default is False). If True, CJS files will be parsed for dummy spritesheet building.
        - build_sheet: Integer (Default is 0). build_dummy MUST be enabled. If 0, nothing happens. If 1, explanatory dummy spritesheets will be created. If 2, dummy spritesheets usable by GBFAP or GBFBP will be created.
        - bound_box: Boolean (Default is False). If True and build_sheet different of 0, draw bounding boxes instead.
        - normal_bound: Boolean (Default is False). If True and build_sheet is 2, the rectangles will have their normal sizes.
    
    Returns
    ----------
    dict: Contains:
        - 'dump': String. Detailed result of the CJS parsing.
        - 'img': List of bytes objects. One object for one image.
    """
    async def renderCJS(self, **options) -> dict:
        result = {
            'dump' : '',
            'img' : {}
        }
        for file in self.spritesheets:
            if file not in self.cjs: # load cjs if not
                await self.loadCJS(file)
            if file in self.cjs and options.get('build_dummy', False):
                await asyncio.sleep(0)
                build_sheet = options.get('build_sheet', 0)
                shts = None
                shk = []
                ssz = {}
                sbrct = {}
                tree = {}
                for k in self.cjs[file]:
                    scr = self.cjs[file][k]
                    if len(scr) > 0 and len(scr[0]) > 1 and scr[0][0] == "sourceRect":
                        sbrct[k] = scr[0][1]
                        if build_sheet == 1:
                            shts = ['_a', '_b', '_c', '_d']
                            shk = shts
                            try:
                                s = scr[0][2]
                                if s == "" or not s.startswith('_'): s = "_a"
                                if s not in shts:
                                    shts.append(s)
                            except:
                                s = "_a"
                            if s not in ssz: ssz[s] = (scr[0][1][2]+scr[0][1][0], scr[0][1][3]+scr[0][1][1])
                            else: ssz[s] = ((scr[0][1][2]+scr[0][1][0] if scr[0][1][2]+scr[0][1][0] > ssz[s][0] else ssz[s][0]), (scr[0][1][3]+scr[0][1][1] if scr[0][1][3]+scr[0][1][1] > ssz[s][1] else ssz[s][1]))
                if build_sheet == 2:
                    shts = {}
                    for k in self.spritesheets[file]:
                        n = k.split('/')[-1].split('.')[0].replace(file, '')
                        shts[n] = self.mc((1024, 2048))
                        shk.append(n)
                
                for k in self.cjs[file]:
                    if k in sbrct: continue
                    scr = self.cjs[file][k]
                    for cmd in scr:
                        if cmd[0] == "do" or cmd[0].startswith("instance"):
                            if cmd[0] == "do":
                                n = "do"
                            elif cmd[0].startswith("instance_"):
                                n = cmd[0][len("instance_"):]
                            else:
                                n = None
                            if cmd[1].startswith("new a."):
                                sn = cmd[1][len("new a."):].split("(")[0]
                            elif cmd[1].startswith("new lib."):
                                sn = cmd[1][len("new lib."):].split("(")[0]
                            elif cmd[1].startswith("new "):
                                sn = cmd[1][len("new "):].split("(")[0]
                                if n == "do": n = "do " + sn
                            else:
                                sn = cmd[1].split("(")[0]
                            if sn not in self.cjs[file]: continue
                            if k not in tree:
                                tree[k] = []
                            if sn not in tree[k]:
                                tree[k].append(sn)
                dump = ""
                for k in tree:
                    dump += "animation → " + k.replace(file + "_", "") + "\n"
                    for c in tree[k]:
                        dump += "  |→ " + c.replace(file + "_", "") + "\n"
                if len(list(sbrct.keys())) == 0:
                    continue
                result['dump'] += "####### " + file +"\n"
                result['dump'] += dump
                result['dump'] += "\n"
                if build_sheet in [1, 2]:
                    if build_sheet == 1:
                        w = 0
                        h = 0
                        for k in ssz:
                            w += ssz[k][0] + 200
                            if ssz[k][1] > h: h = ssz[k][1]
                        if w == 0: w = 200
                        img = self.mc((int(round(w)), int(round(h+200))), options.get('bound_box', False))
                        d = ImageDraw.Draw(img)
                    
                    txkk = {}
                    txsb = []
                    txll = []
                    for k in self.cjs[file]:
                        await asyncio.sleep(0)
                        scr = self.cjs[file][k]
                        if len(scr) > 0 and len(scr[0]) > 1 and scr[0][0] == "sourceRect":
                            sbrct[k] = scr[0][1]
                            try:
                                s = scr[0][2]
                                if build_sheet == 1 and s == "":
                                    s = "_a"
                                elif s not in shts:
                                    continue
                            except:
                                s = shk[0]
                            off_w = 0
                            if build_sheet == 1:
                                for st in ['_a', '_b', '_c', '_d']:
                                    if s == st: break
                                    off_w += ssz[st][0] + 200
                            fill = None
                            for itel in self.COLORING:
                                if fill is not None: break
                                for itelw in itel[3]:
                                    if itelw in k.replace(file, '').lower():
                                        if build_sheet == 1:
                                            fill = (itel[0], itel[1], itel[2])
                                        elif build_sheet == 2:
                                            fill = (itel[0], itel[1], itel[2], 200)
                                        break
                            bss = (off_w+scr[0][1][0], scr[0][1][1])
                            tss = self.dmp_font.getbbox(k.replace(file + "_", ""))
                            bbx = [bss[0], bss[1], bss[0]+tss[2], bss[1]+tss[3]]
                            for tbx in txsb:
                                while bbx[0] < tbx[2] and bbx[2] > tbx[0] and bbx[1] < tbx[3] and bbx[3] > tbx[1]:
                                    bbx[1] += 15
                                    bbx[3] += 15
                            txsb.append(bbx)
                            txkk[k] = bbx
                            txll.append([(int(round(off_w+scr[0][1][0])), int(round(scr[0][1][1]))), (int(round(bbx[0])), int(round(bbx[1])))])
                            if build_sheet == 1:
                                dsf = [(int(round(off_w+scr[0][1][0])), int(round(scr[0][1][1]))), (int(round(off_w+scr[0][1][2]+scr[0][1][0]-1)), int(round(scr[0][1][3]+scr[0][1][1]-1)))]
                                if options.get('bound_box', False):
                                    d.rectangle(dsf, outline=(0, 255, 0, 255))
                                else:
                                    d.rectangle(dsf, fill=fill, outline=(140,140,140))
                            elif build_sheet == 2:
                                if options.get('normal_bound', False):
                                    dsrt = [scr[0][1][2], scr[0][1][3]]
                                else:
                                    dsrt = [scr[0][1][2]*0.7, scr[0][1][3]*0.7]
                                    if dsrt[0] < 1: dsrt[0] = 1
                                    if dsrt[1] < 1: dsrt[1] = 1
                                dsf = [(scr[0][1][2] - dsrt[0]) / 2, (scr[0][1][3] - dsrt[1]) / 2]
                                dsf = [(int(round(scr[0][1][0]+dsf[0])), int(round(scr[0][1][1]+dsf[1]))), (int(round(scr[0][1][0]+dsf[0]+dsrt[0])), int(round(scr[0][1][1]+dsf[1]+dsrt[1])))]
                                if dsf[0][0] > dsf[1][0]: dsf = [(dsf[1][0], dsf[0][1]), (dsf[0][0], dsf[1][1])]
                                if dsf[0][1] > dsf[1][1]: dsf = [(dsf[0][0], dsf[1][1]), (dsf[1][0], dsf[0][1])]
                                d = ImageDraw.Draw(shts[s])
                                if options.get('bound_box', False):
                                    d.rectangle(dsf, outline=(0, 255, 0, 255))
                                else:
                                    d.rectangle(dsf, fill=fill)
                    if build_sheet == 1:
                        if not options.get('bound_box', False):
                            for k in txll:
                                if k[0] != k[1]:
                                    d.line(k, fill=(255, 0, 0), width=2)
                            for k in txkk:
                                d.text((txkk[k][0]+1, txkk[k][1]+1),k.replace(file + "_", ""),font=self.dmp_font,fill=(255,255,255), stroke_width=1, stroke_fill=(0, 0, 0))
                        nm = file.replace(file + '_', '') + ".png"
                        await asyncio.sleep(0)
                        with BytesIO() as output:
                            img.save(output, format="PNG")
                            img.close()
                            result['img'][nm] = output.getvalue()
                    elif build_sheet == 2:
                        for s in shts:
                            await asyncio.sleep(0)
                            n = file + s + ".png"
                            with BytesIO() as output:
                                shts[s].save(output, format="PNG")
                                shts[s].close()
                                result['img'][n] = output.getvalue()
        try: self.sfx.remove(str(self.id))
        except: pass
        return result

    """loadCJS()
    Used by renderCJS(). Request and load a CJS file in memory.
    
    Parameters
    ----------
    file: CJS file name.
    
    Returns
    ----------
    bool: True if success, False otherwise.
    """
    async def loadCJS(self, file : str):
        cjs = await self.request("https://prd-game-a-granbluefantasy.akamaized.net/assets_en/js/cjs/{}.js".format(file))
        if cjs is None: return False
        cjs = cjs.decode('utf-8')
        self.extractSFX(cjs)
        dt = {}
        self._parse_main(cjs, file, dt)
        self.cjs[file]= dt
        return True


    """extractSFX()
    Used by renderCJS(). Extract ID from used SE files.
    Mostly unused but can be used to detect if the target reuses SE from other characters/summons/weapons.
    Access the sfx attribute after it ran to check what it contains
    
    Parameters
    ----------
    cjs: CJS file content.
    """
    def extractSFX(self, cjs : str):
        try:
            tmp = cjs.split('"se/')
            for i in range(1, len(tmp)):
                f = tmp[i].split('.mp3')[0]
                if '_30' in f:
                    self.sfx.add('30' + f.split('_30')[1].split('_')[0])
                elif '_38' in f:
                    self.sfx.add('38' + f.split('_38')[1].split('_')[0])
                elif '_20' in f:
                    self.sfx.add('20' + f.split('_30')[1].split('_')[0])
                elif '_10' in f:
                    self.sfx.add('10' + f.split('_30')[1].split('_')[0])
                else:
                    pass
        except:
            pass

    """_parse_main()
    Internal use. First step of the parser.
    
    Parameters
    ----------
    ff: String, CJS file content.
    nm: String, CJS file name.
    dt: Dict, parser data.
    """
    def _parse_main(self, ff : str, nm : str, dt : dict) -> None:
        for i in range(0, len(ff)):
            if ff[i] == '{':
                ff = ff[i+1:]
                break
        ff = ff[ff.find(';')+1:]
        tps = []
        lvl = 0
        for i in range(len(ff)):
            if ff[i] == '(':
                lvl += 1
                if lvl == 1:
                    if len(tps) > 0 and not tps[-1].startswith('a.') and not tps[-1].startswith('b.') and not tps[-1].startswith('c.') and not tps[-1].startswith('lib.'):
                        tps.pop()
                    tps.append('')
                else:
                    tps[-1] += ff[i]
            elif ff[i] == ')':
                lvl -= 1
                if lvl > 0:
                    tps[-1] += ff[i]
            elif lvl > 0:
                tps[-1] += ff[i]
        if len(tps) > 0 and not tps[-1].startswith('a.') and not tps[-1].startswith('b.') and not tps[-1].startswith('c.') and not tps[-1].startswith('lib.'):
            tps.pop()
        for s in tps:
            self._parse_element(s, nm, dt)

    """_parse_element()
    Internal use. Second step. Animation parser.
    
    Parameters
    ----------
    ck: String, Animation content.
    nm: String, CJS file name.
    dt: Dict, parser data.
    """
    def _parse_element(self, ck : str, nm : str, dt : dict) -> None:
        eq = ck.find('=')
        com = ck.find(',')
        if eq != -1 and ((eq <= com and com != -1) or com == -1): pos = eq
        elif com != -1 and ((com <= eq and eq != -1) or eq == -1): pos = com
        current = ck[2:pos]
        content = ck[pos+1:].replace('\n', '')
        raw = []
        if pos == eq:
            lvl = [0]
            blvl = 0
            c = 0
        else:
            lvl = [0, 0]
            blvl = 1
            c = 0
        for i in range(len(content)):
            if content[i] == '{':
                blvl += 1
                lvl.append(0)
                if blvl == 1:
                    raw = []
                    c = i + 1
            elif content[i] == '}':
                blvl -= 1
                lvl.pop()
            elif content[i] == '(':
                lvl[-1] += 1
            elif content[i] == ')':
                lvl[-1] -= 1
            elif blvl == 1 and lvl[-1] == 0 and content[i] == ',':
                raw.append(content[c:i].replace('this.', ''))
                c = i + 1
        if len(raw) == 0 or content[c:i].replace('this.', '') != raw[-1]:
            raw.append(content[c:i].replace('this.', ''))
        if '.' in current:
            current = current.split('.')[-1]
        if current not in dt:
            dt[current] = []
        self._parse_detail(current, raw, nm, dt)

    """_parse_detail()
    Internal use. Final step.
    
    Parameters
    ----------
    current: String, Animation name.
    raw: List, raw data.
    nm: String, CJS file name.
    dt: Dict, parser data.
    """
    def _parse_detail(self, current : str, raw : list, nm : str, dt : dict) -> None:
        for r in raw:
            if r.startswith('sourceRect=new cjs.Rectangle('):
                rargs = r[len('sourceRect=new cjs.Rectangle('):-1].split(',')
                pargs = []
                for f in rargs:
                    pargs.append(float(f))
                dt[current].append(['sourceRect', pargs])
            elif r.startswith('sourceRect=new c.Rectangle('):
                rargs = r[len('sourceRect=new c.Rectangle('):-1].split(',')
                pargs = []
                for f in rargs:
                    pargs.append(float(f))
                dt[current].append(['sourceRect', pargs])
            elif r.startswith('instance=new a.'):
                dt[current].append(['instance of', r[len('instance=new a.'):]])
            elif r.startswith('instance=new lib.'):
                dt[current].append(['instance of', r[len('instance=new lib.'):]])
            elif r.startswith('shape=(new c.Shape).'):
                if len(dt[current]) > 0 and dt[current][-1][0] == 'shape':
                    dt[current][-1].append(r[len('shape=(new c.Shape).'):])
                else:
                    dt[current].append(['shape', r[len('shape=(new c.Shape).'):]])
            elif r.startswith('shape.'):
                if len(dt[current]) > 0 and dt[current][-1][0] == 'shape':
                    dt[current][-1].append(r[len('shape.'):])
                else:
                    dt[current].append(['shape', r[len('shape.'):]])
            elif r.startswith('instance.'):
                dt[current][-1].append(r[len('instance.'):])
            elif r.startswith('timeline.addTween('):
                ts = r[len('timeline.addTween(')+len('c.Tween.'):-1].split(").")
                dt[current].append(['timeline'])
                for t in ts:
                    if t.startswith('get('): dt[current][-1].append(t.replace('get(', ''))
                    elif t.startswith('to('):
                        try:
                            exp = '{"' + t[t.find('{')+1:t.find('}')+1].replace(',', ',"').replace(':', '":').replace(":.", ":0.").replace(":-.", ":-0.").replace('!0', 'true').replace('!1', 'false').replace('\n', '')
                            tts = json.loads(exp)
                            ks = list(tts.keys())
                            if len(ks) != 1 or ks[0] != "_off":
                                tf = [0, 0, 1, 1, 0, 0, 0, 0, 0]
                                tf[0] = tts.get('x', 0.0)
                                tf[1] = tts.get('y', 0.0)
                                tf[2] = tts.get('scaleX', 1.0)
                                tf[3] = tts.get('scaleY', 1.0)
                                tf[4] = tts.get('rotation', 0.0)
                                tf[5] = tts.get('skewX', 0)
                                tf[6] = tts.get('skewY', 0)
                                tf[7] = tts.get('regX', 0)
                                tf[8] = tts.get('regY', 0)
                                dt[current][-1].append(tf)
                        except:
                            #print("exp:", exp) # DEBUG
                            dt[current][-1].append(t+")")
                    elif t.startswith('wait('):
                        pass
                    else:
                        dt[current][-1].append(t+")")
                if len(dt[current][-1]) == 2:
                    dt[current].pop()
            elif r.startswith("instance_"):
                dot = r.find('.')
                eq = r.find('=')
                if dot >= 0 and (eq == -1 or dot <= eq): p = dot
                elif eq >= 0 and (dot == -1 or eq <= dot): p = eq
                else: continue
                n = r[len("instance_"):p]
                if len(dt[current]) > 0 and dt[current][-1][0] == 'instance_'+n:
                    dt[current][-1].append(r[p+1:])
                else:
                    dt[current].append(['instance_'+n, r[p+1:]])
            elif r.startswith("frame_"):
                dot = r.find('.')
                eq = r.find('=')
                if dot >= 0 and (eq == -1 or dot <= eq): p = dot
                elif eq >= 0 and (dot == -1 or eq <= dot): p = eq
                else: continue
                n = r[len("frame_"):p]
                p += len('function(){')
                if 'lib/sound' not in r[p+1:-1]:
                    ss = r[p+1:-1].split(',')
                    for s in ss:
                        dt[current].append(['frame_'+n, s])
            elif r.startswith("initialize("):
                if nm in r and len(dt[current]) > 0 and dt[current][-1][0] == 'sourceRect':
                    dt[current][-1].append(r.split('(')[1].replace('', '').replace(')', '').replace(';', '').replace(nm, '').split('.')[1])
            elif r.startswith("null"): # skip
                pass
            else:
                dot = r.find('.')
                eq = r.find('=')
                if dot >= 0 and (eq == -1 or dot <= eq): p = dot
                elif eq >= 0 and (dot == -1 or eq <= dot): p = eq
                else:
                    continue
                rf = r[p+1:].replace('new a.', 'new ')
                if len(dt[current]) > 0 and (dt[current][-1][0] == 'instance of' or dt[current][-1][0].startswith('instance_') or dt[current][-1][0] == 'shape') and (rf.startswith('Rectangle(') or rf.startswith('setTransform(') or rf.startswith('parent=')):
                    dt[current][-1].append(rf)
                elif len(dt[current]) > 0 and dt[current][-1][0] == 'do':
                    dt[current][-1].append(rf)
                else:
                    dt[current].append(['do', rf])

    """renderNPC()
    Function to render a NPC sprite.
    Use the chara_out animation first frame.
    
    Parameters
    ----------
    enable_dummy: Boolean (Default is True), allow dummy rendering if spritesheets are unavailable
    enable_hitbox: Boolean (Default is True), add green hitboxes over each part of the sprite (Non dummy mode only)
    force_dummy: Boolean (Default is False), if True, will force dummy rendering for any character
    
    Returns
    ----------
    bytes: Sprite if successful, else None.
    """
    async def renderNPC(self, *, enable_dummy=True, enable_hitbox=True, force_dummy=False):
        sp = None
        self.dumc_c = 0
        for k in self.spritesheets:
            if k.startswith('npc_') and '_f' not in k:
                self.sts = {}
                self.dum = False
                self.hbox = enable_hitbox
                if force_dummy:
                    self.dum = True
                else:
                    for path in self.spritesheets[k]:
                        data = await self.request("https://prd-game-a1-granbluefantasy.akamaized.net/assets_en/img/" + path)
                        if data is not None:
                            with BytesIO(data) as b:
                                self.sts[path.split('/')[-1]] = Image.open(b).convert('RGBA')
                        else:
                            self.dum = True
                            break
                if (enable_dummy and self.dum) or not self.dum:
                    s = SP(k, "mc_" + k + "_chara_out" , self) # chara out is a pretty good one to use as reference
                    s.PC()
                    sp = s.DR()
                for k in self.sts:
                    self.sts[k].close()
                break
        return sp

    """zm()
    Create a zero matrix of the given size
    
    Parameters
    ----------
    rows: Integer, given number of rows
    cols: Integer, given number of columns
    
    Returns
    ----------
    list: Resulting matrix
    """
    def zm(self, rows, cols):
        A = []
        for i in range(rows):
            A.append([])
            for j in range(cols):
                A[-1].append(0.0)

        return A

    """cm()
    Copy a matrix
    
    Parameters
    ----------
    M: List, matrix to copy
    
    Returns
    ----------
    list: Resulting matrix
    """
    def cm(self, M):
        rows = len(M)
        cols = len(M[0])

        MC = self.zm(rows, cols)

        for i in range(rows):
            for j in range(rows):
                MC[i][j] = M[i][j]

        return MC

    """im()
    Invert a matrix
    
    Parameters
    ----------
    A: List, matrix to invert
    
    Returns
    ----------
    list: Resulting matrix
    """
    def im(self, A):
        I = [[1,0,0],[0,1,0],[0,0,1]]
        AM = self.cm(A)
        IM = self.cm(I)
        n = len(AM)

        fd = 0
        fdS = 1. / AM[fd][fd]

        for j in range(n):
            AM[fd][j] = fdS * AM[fd][j]
            IM[fd][j] = fdS * IM[fd][j]

        n = len(A)
        inds = list(range(n))

        for i in inds[0:fd] + inds[fd+1:]:
            crS = AM[i][fd]
            for j in range(n):
                AM[i][j] = AM[i][j] - crS * AM[fd][j]
                IM[i][j] = IM[i][j] - crS * IM[fd][j]

        inds = list(range(n))
        for fd in range(1,n):
            fdS = 1.0 / AM[fd][fd]
            for j in range(n):
                AM[fd][j] *= fdS
                IM[fd][j] *= fdS
            
            for i in inds[:fd] + inds[fd+1:]:
                crS = AM[i][fd]
                for j in range(n):
                    AM[i][j] = AM[i][j] - crS * AM[fd][j]
                    IM[i][j] = IM[i][j] - crS * IM[fd][j]
        return IM

# ----------------------------------------------------------------------------------------------------------------
# Sprite Element
# Used only for NPC Sprite Rendering
# ----------------------------------------------------------------------------------------------------------------
class SP():
    """__init__()
    Constructor
    
    Parameters
    ----------
    file: String, CJS file name
    name: String, element name
    o: Renderer
    p: SP Object, parent (None if it has no parent)
    """
    def __init__(self, file : str, name : str, o : GBFSB, p : 'SP' = None) -> None:
        self.dt = {'name':name, 'childs':[]}
        self.o = o
        self.p = p
        self.f = file
        self.m = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        self.cp = False
        self.tis = False
        self.timeline = {} # new

    """rst()
    Reset internal matrix
    """
    def rst(self) -> None:
        self.m = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        self.cp = False
        self.tis = False

    """ST()
    Set internal Transform Matrix
    
    Parameters
    ----------
    t: List, matrix to set
    """
    def ST(self, t) -> None:
        self.dt['transform'] = t
        if len(self.dt['transform']) < 9:
            while len(self.dt['transform']) < 2: self.dt['transform'].append(0.0)
            while len(self.dt['transform']) < 4: self.dt['transform'].append(1.0)
            while len(self.dt['transform']) < 9: self.dt['transform'].append(0.0)

    """PC()
    Set internal Transform Matrix
    
    Returns
    ----------
    int: Unused
    """
    def PC(self) -> int:
        try:
            script = self.o.cjs[self.f][self.dt['name']]
        except:
            script = self.o.cjs[self.f]["mc_"+self.dt['name']]
        instcs = {}
        inst = ""
        for cmd in script:
            if cmd[0] == "do" or cmd[0].startswith("instance"):
                if cmd[0] == "do":
                    n = "do"
                elif cmd[0].startswith("instance_"):
                    n = cmd[0][len("instance_"):]
                elif cmd[0] == "instance of":
                    n = "instance"
                else:
                    n = None
                if cmd[1].startswith("new a."):
                    sn = cmd[1][len("new a."):].split("(")[0]
                elif cmd[1].startswith("new lib."):
                    sn = cmd[1][len("new lib."):].split("(")[0]
                elif cmd[1].startswith("new "):
                    sn = cmd[1][len("new "):].split("(")[0]
                    if n == "do": n = "do " + sn
                else:
                    sn = cmd[1].split("(")[0]
                if n == "instance" or n.isnumeric(): inst = sn
                if sn not in self.o.cjs[self.f] and "mc_"+sn not in self.o.cjs[self.f]:
                    continue
                self.dt['childs'].append(SP(self.f, sn, self.o, self))
                instcs[n] = self.dt['childs'][-1]
                for i in range(2, len(cmd)):
                    if cmd[i].startswith("setTransform("):
                        tf = cmd[i][len("setTransform("):-1].split(",")
                        for j in range(len(tf)):
                            try:
                                tf[j] = float(tf[j].split(')')[0])
                            except:
                                tf[j] = 0.0
                        instcs[n].ST(tf)
                    elif cmd[i].startswith("alpha="):
                        instcs[n].ap = float(cmd[i][len("alpha="):])
                    elif cmd[i].startswith("compositeOperation"):
                        instcs[n].cp = True
                instcs[n].PC()
            elif cmd[0] == "timeline":
                if cmd[1] == "this":
                    n = None
                elif cmd[1].startswith("instance_"):
                    n = inst
                elif cmd[1] == "instance":
                    n = inst
                elif cmd[1] in instcs:
                    n = cmd[1]
                else:
                    continue
                if n in self.timeline: continue
                self.timeline[n] = cmd[2:]
            elif cmd[0] == "shape":
                self.dt['shape'] = None
                return 0
            elif cmd[0] == "sourceRect":
                self.dt['rect'] = (cmd[1][0], cmd[1][1], cmd[1][0]+cmd[1][2], cmd[1][1]+cmd[1][3])
                try:
                    self.dt['sheet'] = cmd[2]
                except:
                    pass
                return 1

    """GT()
    Get transform matrix from given matrix
    
    Parameters
    ----------
    mt: List, matrix to transform into a transform matrix
    
    Returns
    ----------
    list: Transform matrix
    """
    def GT(self, mt : list) -> list:
        m = [
            [mt[0], mt[2], mt[4]],
            [mt[1], mt[3], mt[5]],
            [0,0,1]
        ]
        Tinv = self.o.im(m)
        return [Tinv[0][0],Tinv[0][1], Tinv[0][2], Tinv[1][0],Tinv[1][1],Tinv[1][2]]

    """TtM()
    Convert transformation to internal transform matrix
    
    Parameters
    ----------
    tf: List, transformation to transform
    """
    def TtM(self, tf : list) -> None:
        if tf is None: return
        self.tis = True
        self.m = self.T2M(tf)

    """apm()
    Apply two matrices together
    
    Parameters
    ----------
    mA: List, matrix A
    mB: List, matrix B
    
    Returns
    ----------
    list: Resulting matrix
    """
    def apm(self, mA : list, mB : list) -> list:
        mC = mA.copy()
        if mB[0] != 1 or mB[1] != 0 or mB[2] != 0 or mB[3] != 1:
            mC[0] = mA[0]*mB[0]+mA[2]*mB[1]
            mC[1] = mA[1]*mB[0]+mA[3]*mB[1]
            mC[2] = mA[0]*mB[2]+mA[2]*mB[3]
            mC[3] = mA[1]*mB[2]+mA[3]*mB[3]
        mC[4] += mA[0]*mB[4]+mA[2]*mB[5]
        mC[5] += mA[1]*mB[4]+mA[3]*mB[5]
        return mC

    """T2M()
    Convert transformation to transform matrix
    
    Parameters
    ----------
    tf: List, transformation to transform
    
    Returns
    ----------
    list: Resulting matrix
    """
    def T2M(self, tf : list) -> list:
        if tf is None: return None
        if tf[4] % 360 != 0:
            r = math.radians(tf[4])
            cos = math.cos(r)
            sin = math.sin(r)
        else:
            cos = 1
            sin = 0
        m = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        m = self.apm(m, [1, 0, 0, 1, self.o.HS[0], self.o.HS[1]])
        if tf[5] != 0 or tf[6] != 0:
            v = math.radians(tf[5])
            w = math.radians(tf[6])
            m = self.apm(m, [math.cos(w), math.sin(w), -math.sin(v), math.cos(v), tf[0], tf[1]])
            m = self.apm(m, [cos * tf[2], sin * tf[2], -sin * tf[3], cos * tf[3], 0, 0])
        else:
            m = self.apm(m, [cos * tf[2], sin * tf[2], -sin * tf[3], cos * tf[3], tf[0], tf[1]])
        m = self.apm(m, [1, 0, 0, 1, -self.o.HS[0], -self.o.HS[1]])
 
        if tf[7] != 0 or tf[8] != 0:
            m[4] -= tf[7]*m[0]+tf[8]*m[2]
            m[5] -= tf[7]*m[1]+tf[8]*m[3]
        return m

    """dR()
    Draw rectangle on image
    
    Parameters
    ----------
    img: Image object
    x: Top left corner X position
    y: Top left corner Y position
    w: Width
    h: Heigth
    color: Tuple, outline color
    """
    def dR(self, img : Image, x, y, w, h , color : tuple) -> None:
        ImageDraw.Draw(img, 'RGBA').rectangle([(x, y), (x+w-1, y+h-1)], fill=(0, 0, 0, 0), outline=color, width=2)

    """dR()
    Draw text on image
    
    Parameters
    ----------
    img: Image object
    x: X position
    y: Y position
    text: String to draw
    color: Tuple, text fill color
    """
    def dT(self, img : Image, x, y, text : str, color : tuple) -> None:
        ImageDraw.Draw(img, 'RGBA').text((x, y),text,font=self.o.dum_font,fill=color,stroke_width=1,stroke_fill=(0, 0, 0, 255))

    """pioi()
    Paste image on another image.
    Both images will be closed.
    
    Parameters
    ----------
    a: Receiving image
    o: Tuple, offset of the pasted image
    m: Image being pasted
    
    Returns
    ----------
    Image: resulting image object
    """
    def pioi(self, a : Image, o : tuple, m : Image) -> Image:
        l = Image.new('RGB', a.size, "black")
        la = Image.new("L", a.size, "black")
        l.putalpha(la)
        la.close()
        l.paste(m, o, m)
        r = Image.alpha_composite(a, l)
        l.close()
        a.close()
        return r

    """DR()
    Element rendering

    Returns
    ----------
    either:
        - Final image if the element has no parent
        - list containing:
            - list of images to process
            - list of the associated name (For dummy rendering)
    """
    def DR(self) -> Union[Image, list]:
        imgs = []
        txss = []
        self.TtM(self.dt.get('transform', None))
        if 'rect' in self.dt:
            if self.o.dum:
                self.o.dumc_c = (self.o.dumc_c + 1) % len(self.o.DUMMY_COLORS)
                img = self.o.mc(self.o.SS)
                w = self.dt['rect'][2] - self.dt['rect'][0]
                h = self.dt['rect'][3] - self.dt['rect'][1]
                self.dR(img, self.o.HS[0]+w//6, self.o.HS[1]+h//6, w*2//3, h*2//3, self.o.DUMMY_COLORS[self.o.dumc_c])
                dumm = (self.dt['name'].replace(self.f, '')[1:], self.o.DUMMY_COLORS[self.o.dumc_c])
                return [img], [dumm]
            else:
                try:
                    suffix = self.dt.get('sheet', '_a')
                    y = self.o.sts[self.f+suffix+".png"].copy()
                    x = y.crop(self.dt['rect'])
                    y.close()
                except:
                    y = self.o.sts[self.f+".png"].copy()
                    x = y.crop(self.dt['rect'])
                    y.close()
                img = self.o.mc(self.o.SS)
                if self.o.hbox: self.dR(img, self.o.HS[0], self.o.HS[1], self.dt['rect'][2]-self.dt['rect'][0], self.dt['rect'][3]-self.dt['rect'][1], (0, 255, 0, 255))
                img = self.pioi(img, self.o.HS, x)
                if self.tis:
                    x = img.transform(img.size, Image.Transform.AFFINE, self.GT(self.m),resample=Image.Resampling.BILINEAR)
                    img.close()
                    img = x
                return [img], []
        elif 'shape' in self.dt:
            return [], []
        else:
            prev = " "
            for c in reversed(self.dt['childs']):
                is_wam_wep = "_".join(c.dt['name'].split(self.f)[1:]).startswith('_weapon_move')
                if not is_wam_wep or (is_wam_wep and (prev[:-1] != c.dt['name'][:-1] or self.dt['name'] == c.dt['name'])): # hacky attempt for wamdus (note: some should be needed for hekate too)
                    prev = c.dt['name']
                    ar, tx = c.DR()
                    for i, x in enumerate(ar):
                        if self.tis:
                            ar[i] = x.transform(x.size, Image.Transform.AFFINE, self.GT(self.m),resample=Image.Resampling.BILINEAR)
                            x.close()
                        if not self.cp: # skip
                            imgs.append(ar[i])
                        else:
                            ar[i].close()
                    for i in tx:
                        if not self.cp:
                            txss.append(i)
        
        if self.p is None: # final phase, one value is returned
            img = self.o.mc(self.o.SS)
            for i in imgs:
                img = self.pioi(img, (0, 0), i)
                i.close()
            if len(txss) > 0:
                for i in range(len(txss)):
                    self.dT(img, 202, 102+i*17, '- '+txss[i][0], txss[i][1])
            n = "s_"+self.f+".png"
            x = img.crop((200, 100, 750, 600))
            img.close()
            img = x
            with BytesIO() as output:
                img.save(output, format="PNG")
                img.close()
                return output.getvalue()
            return n
        return imgs, txss

# EXAMPLE
async def example():
    from pathlib import Path # for folder creation
    target_id = 3040036000
    target_folder = str(target_id) + "/"

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=50)) as client:
        r = GBFSB(client)
        print("Loading element", target_id)
        await r.load(target_id, uncap=1, style='')
        if r.exist():
            Path(target_folder).mkdir(parents=True, exist_ok=True)
            print("Rendering CJS...")
            res = await r.renderCJS(build_dummy=True, build_sheet=1)
            for k in res['img']: # retrieve images
                with open(target_folder + k, "wb") as f:
                    f.write(res['img'][k])
            with open(target_folder + "dump.txt", mode="w", encoding="utf-8") as f: # retrieve dump
                f.write(res['dump'])
            print("Rendering NPC...")
            sp = await r.renderNPC()
            if sp is not None:
                with open(target_folder + "render.png", "wb") as f:
                    f.write(sp)
        else:
            print("No Positive Results")


if __name__ == "__main__":
    asyncio.run(example())
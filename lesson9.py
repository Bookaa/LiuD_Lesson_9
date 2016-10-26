# LiuD Lesson Nine

import Ast_LiuD as GDL
from Ast_LiuD import LiuD_Parser

type_none = 0
type_v = 1
type_s = 2
type_vlst = 3
type_slst = 4

type_to_prefix = {type_v : 'v', type_s : 's', type_vlst : 'vlst', type_slst : 'slst'}

class gen_common:
    def __init__(self, lst, lst_inline):
        self.itemlst = lst
        self.inlinelst = lst_inline
        self.predefines0 = ('NEWLINE','IDENTIN','IDENTOUT','IDENT')
        self.predefines = ('NAME', 'STRING', 'NUMBER')
    def get_type0(self, name):
        if name in self.itemlst:
            return type_v
        if name in self.predefines0:
            return type_none
        if name in self.predefines:
            return type_s
        if name in self.inlinelst:
            value_node = self.inlinelst[name]
            types = self.get_types(value_node)
            assert len(types) == 1
            return types[0]
        assert False
    def tolst(self, t):
        if t == type_v:
            return type_vlst
        if t == type_s:
            return type_slst
        assert False
    def get_type(self,node):
        if isinstance(node, GDL.LiuD_litstring):
            return type_none
        if isinstance(node, GDL.LiuD_litname):
            name = node.s
            return self.get_type0(name)
        if isinstance(node, GDL.LiuD_enclosed):
            return self.get_type(node.v)
        if isinstance(node, GDL.LiuD_itemd):
            t = self.get_type(node.v)
            return self.tolst(t)
        if isinstance(node, GDL.LiuD_series):
            lst = []
            for v1 in node.vlst:
                t = self.get_type(v1)
                if t == type_none:
                    continue
                lst.append(t)
            assert len(lst) == 1
            return lst[0]
        if isinstance(node, GDL.LiuD_string_or):
            return type_s
        assert False
    def get_types(self,node):
        lst = []
        v = node
        if isinstance(v, GDL.LiuD_series):
            for v1 in v.vlst:
                t = self.get_type(v1)
                if t == type_none:
                    continue
                lst.append(t)
            return lst
        if isinstance(v, GDL.LiuD_values_or):
            typ = None
            for name in v.slst:
                typ1 = self.get_type0(name)
                if typ is None:
                    typ = typ1
                else:
                    assert typ == typ1
            return [typ]
        if isinstance(v, GDL.LiuD_string_or):
            return [type_s]
        if isinstance(v, GDL.LiuD_jiap):
            typ = self.get_type0(v.s1)
            typ2 = self.tolst(typ)
            return [typ2]
        if isinstance(v, GDL.LiuD_multiop):
            return [type_v, type_s, type_v]

        assert False
    def get_prefix(self, types):
        #prefix = [type_to_prefix[b] for b in args]
        if len(types) > 1:
            pass
        lst = []
        for i,typ in enumerate(types):
            s = type_to_prefix[typ]
            if types.count(typ) == 1:
                lst.append(s)
                continue
            n = types[:i+1].count(typ)
            s2 = '%s%d' % (s, n)
            lst.append(s2)
        return lst

class cls_Gen00(gen_common):
    def __init__(self, lst, lst_inline):
        gen_common.__init__(self, lst, lst_inline)
        self.outtxt = ''
        self.prefix = 'XX'
        self.ntab = 0
        self.lastline = ''
    def visit_main(self, node):
        for v in node.vlst:
            v.walkabout(self)
    def visit_option1(self, node):
        s = node.s
        self.prefix = s
    def outp(self, s, ntab=0):
        if not self.lastline:
            self.outtxt += '    '*(self.ntab+ntab)+s+'\n'
        else:
            assert ntab == 0
            self.outtxt += self.lastline+s+'\n'
            self.lastline = ''
    def outs(self, s):
        if not self.lastline:
            self.lastline = '    '*self.ntab+s
        else:
            self.lastline += s
class cls_Gen01(cls_Gen00):
    def __init__(self, lst, lst_inline, prefix):
        cls_Gen00.__init__(self, lst, lst_inline)
        self.prefix = prefix
    def visit_state1(self, node):
        pass
    def visit_inline(self, node):
        pass
    def visit_stmt(self, node):
        name = node.s
        txt = '''class %s_%s:
    def __init__(self, %s):
'''
        types = self.get_types(node.v)
        prefix = self.get_prefix(types)
        argstr = ', '.join(prefix)
        self.outtxt += txt % (self.prefix, name, argstr)
        for s in prefix:
            self.outtxt += '        self.%s = %s\n' % (s, s)

        txt2 = '''    def walkabout(self, visitor):
        return visitor.visit_%s(self)
''' % name
        self.outtxt += txt2 + '\n'
        #node.v.walkabout(self)

def GetItemList(mod):
    lst = []
    lst2 = {}
    prefix = 'XX'
    for v in mod.vlst:
        if isinstance(v, GDL.LiuD_option1):
            prefix = v.s
        if isinstance(v, GDL.LiuD_stmt):
            name = v.s
            lst.append(name)
        if isinstance(v, GDL.LiuD_inline):
            name = v.s
            lst2[name] = v.v
    return lst, lst2, prefix


def Gen01(mod):

    lst, lst_inline, prefix = GetItemList(mod)

    the = cls_Gen01(lst, lst_inline, prefix)
    mod.walkabout(the)
    # print the.outtxt
    return the.outtxt

pos_onlyme = 1
pos_first = 2
pos_end = 3
pos_mid = 4

class cls_Gen02(cls_Gen00):
    def __init__(self, lst, lst_inline, prefix):
        cls_Gen00.__init__(self, lst, lst_inline)
        self.prefix = prefix
        self.outtxt = 'class %s_Parser(Parser00):\n' % prefix
        self.curpos = None
        self.curtyp = None
        self.curtypno = 0
        self.ntab = 2
        self.curskip = 'no'
    def visit_state1(self, node):
        s = node.s
        self.curskip = s
    def skipspace(self):
        if self.curskip == 'no':
            return
        if self.curskip == 'space':
            self.outp('self.skipspace()')
        elif self.curskip == 'crlf':
            self.outp('self.skipspacecrlf()')
    def visit_stmt(self, node):
        name = node.s
        if name == 'enclosedstrs':
            pass
        txt = '''
    def handle_%s(self):
''' % name
        #txt += '        pass\n'
        self.outtxt += txt
        self.curname = name

        types = self.get_types(node.v)
        prefix = self.get_prefix(types)
        self.curtyp = (types, prefix)
        self.curpos = pos_onlyme; self.curtypno = 0

        node.v.walkabout(self)

        if not isinstance(node.v, GDL.LiuD_multiop):
            self.outp('return %s_%s(%s)' % (self.prefix, name, ', '.join(prefix)))
        self.curtyp = None

    def visit_inline(self, node):
        name = node.s
        if name == 'datatype':
            pass
        txt = '''
    def hdl_%s(self):
''' % name
        #txt += '        pass\n'
        self.outtxt += txt
        self.curname = name

        types = self.get_types(node.v)
        prefix = self.get_prefix(types)
        self.curtyp = (types, prefix)
        self.curpos = pos_onlyme; self.curtypno = 0

        node.v.walkabout(self)

        self.outp('return %s' % prefix[0])
        self.curtyp = None

    def visit_series(self, node):
        assert self.curpos == pos_onlyme

        if len(node.vlst) == 1:
            self.curpos = pos_onlyme; self.curtypno = 0
            v = DirectToV(node.vlst[0])
            v.walkabout(self)
            self.curpos = None
            return
        j = 0
        for i,v in enumerate(node.vlst):
            self.curtypno = None
            typ = self.get_type(v)
            if typ != type_none:
                self.curtypno = j
                assert self.curtyp[0][j] == typ
                j += 1
            if i == 0:
                self.outp('savpos = self.pos')
                self.curpos = pos_first
            elif i == len(node.vlst) - 1:
                self.skipspace()
                self.curpos = pos_end
            else:
                self.skipspace()
                self.curpos = pos_mid
            v1 = DirectToV(v)
            v1.walkabout(self)
            self.curpos = None
    def visit_litname(self, node):
        name = node.s
        if name in self.predefines:
            vname = self.curtyp[1][self.curtypno]
            if self.curpos in (pos_onlyme, pos_first):
                self.outp('%s = self.handle_%s()' % (vname, name))
                self.outp('if not %s:' % vname)
                self.outp('return None', 1)
            else:
                self.outp('%s = self.handle_%s()' % (vname, name))
                self.outp('if not %s:' % vname)
                self.outp('return self.restorepos(savpos)', 1)
            return
            assert False
        if name in self.itemlst:
            vname = self.curtyp[1][self.curtypno]
            if self.curpos in (pos_onlyme, pos_first):
                self.outp('%s = self.handle_%s()' % (vname, name))
                self.outp('if not %s:' % vname)
                self.outp('return None', 1)
            else:
                self.outp('%s = self.handle_%s()' % (vname, name))
                self.outp('if not %s:' % vname)
                self.outp('return self.restorepos(savpos)', 1)
            return
        if name in self.inlinelst:
            vname = self.curtyp[1][self.curtypno]
            if self.curpos in (pos_onlyme, pos_first):
                self.outp('%s = self.hdl_%s()' % (vname, name))
                self.outp('if not %s:' % vname)
                self.outp('return None', 1)
            else:
                self.outp('%s = self.hdl_%s()' % (vname, name))
                self.outp('if not %s:' % vname)
                self.outp('return self.restorepos(savpos)', 1)
            return
        if name in self.predefines0:
            self.outp('if not self.handle_%s():' % name)
            if self.curpos in (pos_onlyme, pos_first):
                self.outp('return None', 1)
            else:
                self.outp('return self.restorepos(savpos)', 1)
            return
            assert False

        assert False
    def visit_litstring(self, node):
        s = node.s
        if self.curpos in (pos_onlyme, pos_first):
            self.outp("if not self.handle_str(%s):" % s)
            self.outp('return None', 1)
            return
        self.outp("if not self.handle_str(%s):" % s)
        self.outp('return self.restorepos(savpos)', 1)
    def visit_string_or(self, node):
        vname = self.curtyp[1][self.curtypno]
        for i,s in enumerate(node.slst):
            if i == 0:
                self.outp('%s = self.handle_str(%s)' % (vname, s))
            else:
                self.outp('if not %s:' % vname)
                self.outp('%s = self.handle_str(%s)' % (vname, s), 1)
        self.outp('if not %s:' % vname)
        if self.curpos in (pos_onlyme, pos_first):
            self.outp('return None', 1)
        else:
            self.outp('return self.restorepos(savpos)', 1)
        pass
    def visit_values_or(self, node):
        vname = self.curtyp[1][self.curtypno]
        for i,s in enumerate(node.slst):
            if s in self.itemlst:
                if i == 0:
                    self.outp('%s = self.handle_%s()' % (vname, s))
                else:
                    self.outp('if not %s:' % vname)
                    self.outp('%s = self.handle_%s()' % (vname, s), 1)
                continue
            if s in self.predefines:
                if i == 0:
                    self.outp('%s = self.handle_%s()' % (vname, s))
                else:
                    self.outp('if not %s:' % vname)
                    self.outp('%s = self.handle_%s()' % (vname, s), 1)
                continue
            if s in self.inlinelst:
                if i == 0:
                    self.outp('%s = self.hdl_%s()' % (vname, s))
                else:
                    self.outp('if not %s:' % vname)
                    self.outp('%s = self.hdl_%s()' % (vname, s), 1)
                continue
            assert False
        self.outp('if not %s:' % vname)
        self.outp('return None', 1)
    def visit_jiap(self, node):
        s1 = node.s1
        s2 = node.s2
        vname = self.curtyp[1][0]
        self.outp('savpos = self.pos')
        self.outp('%s = []' % vname)
        self.outp('s = self.handle_%s()' % s1)
        self.outp('if not s:')
        self.outp('return None', 1)
        self.outp('%s.append(s)' % vname)
        self.outp('while True:')
        self.ntab += 1
        self.skipspace()
        self.outp('if not self.handle_str(%s):' % s2)
        self.outp('break', 1)
        self.skipspace()
        self.outp('s = self.handle_%s()' % s1)
        self.outp('if not s:')
        self.outp('break', 1)
        self.outp('%s.append(s)' % vname)
        self.outp('savpos = self.pos')
        self.ntab -= 1
        self.outp('self.restorepos(savpos)')
        self.outp('if len(%s) < 2:' % vname)
        self.outp('return None', 1)
        '''
        savpos = self.pos
        slst = []
        s = self.handle_NAME()
        if not s:
            return None
        slst.append(s)
        while True:
            self.skipspace()
            if not self.handle_str('|'):
                break
            self.skipspace()
            s = self.handle_NAME()
            if not s:
                break
            slst.append(s)
            savpos = self.pos
        self.restorepos(savpos)
        if len(slst) < 2:
            return None
        '''
    def visit_itemd(self, node):
        if self.curpos == pos_onlyme:
            lstname = self.curtyp[1][self.curtypno]
            v1 = DirectToV(node.v)
            if isinstance(v1, GDL.LiuD_litname):
                name = v1.s
                if name in self.itemlst:
                    self.outp('v = self.handle_%s()' % name)
                    self.outp('if not v:')
                    self.outp('return None', 1)
                    self.outp('savpos = self.pos')
                    self.outp('%s = [v]' % lstname)
                    self.outp('while True:')
                    self.ntab +=1
                    self.skipspace()
                    self.outp('v = self.handle_%s()' % name)
                    self.outp('if not v:')
                    self.outp('break', 1)
                    self.outp('%s.append(v)' % lstname)
                    self.outp('savpos = self.pos')
                    self.ntab -=1
                    self.outp('self.restorepos(savpos)')
                    return
                if name in self.inlinelst:
                    typ = self.get_type0(name)
                    if typ == type_v:
                        self.outp('v = self.hdl_%s()' % name)
                        self.outp('if not v:')
                        self.outp('return None', 1)
                        self.outp('savpos = self.pos')
                        self.outp('%s = [v]' % lstname)
                        self.outp('while True:')
                        self.ntab +=1
                        self.skipspace()
                        self.outp('v = self.hdl_%s()' % name)
                        self.outp('if not v:')
                        self.outp('break', 1)
                    elif typ == type_s:
                        self.outp('s = self.hdl_%s()' % name)
                        self.outp('if not s:')
                        self.outp('return None', 1)
                        self.outp('savpos = self.pos')
                        self.outp('%s = [s]' % lstname)
                        self.outp('while True:')
                        self.ntab +=1
                        self.skipspace()
                        self.outp('s = self.hdl_%s()' % name)
                        self.outp('if not s:')
                        self.outp('break', 1)
                    else:
                        assert False
                    self.outp('%s.append(v)' % lstname)
                    self.outp('savpos = self.pos')
                    self.ntab -=1
                    self.outp('self.restorepos(savpos)')
                    return

            self.outp('%s = []' % lstname)
            self.outp('savpos = self.pos')
            self.outp('while True:')
            self.ntab +=1
            #self.outp('pass')
            self.inloop(node.v, lstname)
            self.ntab -=1
            self.outp('self.restorepos(savpos)')
            self.outp('if not %s:' % lstname)
            self.outp('return None', 1)
            return
        if self.curpos == pos_mid:
            lstname = self.curtyp[1][self.curtypno]
            v1 = DirectToV(node.v)
            if isinstance(v1, GDL.LiuD_litname):
                name = v1.s
                if name in self.itemlst:
                    pass
                if name in self.inlinelst:
                    typ = self.get_type0(name)
                    if typ == type_v:
                        self.outp('%s = []' % lstname)
                        self.outp('savpos2 = self.pos')
                        self.outp('while True:')
                        self.ntab +=1
                        self.outp('v = self.hdl_%s()' % name)
                        self.outp('if not v:')
                        self.outp('break', 1)
                    else:
                        assert False
                    self.outp('%s.append(v)' % lstname)
                    self.outp('savpos2 = self.pos')
                    self.skipspace()
                    self.ntab -=1
                    self.outp('self.restorepos(savpos2)')
                    return
                if name in self.predefines:
                    self.outp('%s = []' % lstname)
                    self.outp('savpos2 = self.pos')
                    self.outp('while True:')
                    self.ntab +=1
                    self.outp('s = self.handle_%s()' % name)
                    self.outp('if not s:')
                    self.outp('break', 1)
                    self.outp('%s.append(s)' % lstname)
                    self.outp('savpos2 = self.pos')
                    self.skipspace()
                    self.ntab -=1
                    self.outp('self.restorepos(savpos2)')
                    return
                assert False
            if isinstance(v1, GDL.LiuD_series):
                assert False
            pass
        assert False
    def inloop(self, node, lstname):
        node1 = DirectToV(node)
        if isinstance(node1, GDL.LiuD_series):
            vname = None
            for i,v in enumerate(node1.vlst):
                if i != 0:
                    self.skipspace()
                v = DirectToV(v)
                if isinstance(v, GDL.LiuD_litname):
                    name = v.s
                    if name in self.itemlst:
                        self.outp('v = self.handle_%s()' % name)
                        self.outp('if not v:')
                        self.outp('break', 1)
                        vname = 'v'
                        continue
                    if name in self.predefines0:
                        self.outp('if not self.handle_%s():' % name)
                        self.outp('break', 1)
                        continue
                    if name in self.inlinelst:
                        typ = self.get_type0(name)
                        if typ == type_v:
                            self.outp('v = self.hdl_%s()' % name)
                            self.outp('if not v:')
                            self.outp('break', 1)
                            vname = 'v'
                        elif typ == type_s:
                            self.outp('s = self.hdl_%s()' % name)
                            self.outp('if not s:')
                            self.outp('break', 1)
                            vname = 's'
                        else:
                            assert False
                        continue
                    assert False
            assert vname
            self.outp('%s.append(%s)' % (lstname, vname))
            self.outp('savpos = self.pos')
            self.skipspace()
            return
        if isinstance(node1, GDL.LiuD_litname):
            name = node1.s
            if name in self.itemlst:
                self.outp('v = self.handle_%s()' % name)
                self.outp('if not v:')
                self.outp('break', 1)
                vname = 'v'
            elif name in self.inlinelst:
                typ = self.get_type0(name)
                if typ == type_v:
                    self.outp('v = self.hdl_%s()' % name)
                    self.outp('if not v:')
                    self.outp('break', 1)
                    vname = 'v'
                elif typ == type_s:
                    self.outp('s = self.hdl_%s()' % name)
                    self.outp('if not s:')
                    self.outp('break', 1)
                    vname = 's'
                else:
                    assert False
            else:
                assert False
            self.outp('%s.append(v)' % lstname)
            self.outp('savpos = self.pos')
            self.skipspace()
            return
        assert False
    def visit_multiop(self, node):
        v1, s, v2 = self.curtyp[1]
        if node.s1 in self.inlinelst:
            self.outp('%s = self.hdl_%s()' % (v1, node.s1))
        else:
            self.outp('%s = self.handle_%s()' % (v1, node.s1))
        self.outp('if not %s:' % v1)
        self.outp('return None', 1)
        for i,v5 in enumerate(node.vlst):
            if isinstance(v5, GDL.LiuD_litstring):
                s5 = v5.s
            elif isinstance(v5, GDL.LiuD_enclosedstrs):
                lst = v5.slst
                s5 = ', '.join(lst)
            else:
                assert False

            self.outp('def multiop%d(v1):' % (i+1))
            self.ntab += 1
            if i > 0:
                self.outp('v1 = multiop%d(v1)' % i)
            self.outp('while True:')
            self.ntab += 1
            self.outp('savpos = self.pos')
            self.skipspace()
            self.outp('for %s in [%s]:' % (s, s5))
            self.outp('if self.handle_str(%s):' % s, 1)
            self.outp('break', 2)
            self.outp('else:')
            self.outp('self.restorepos(savpos)', 1)
            self.outp('return %s' % v1, 1)
            self.skipspace()
            if node.s2 in self.inlinelst:
                self.outp('%s = self.hdl_%s()' % (v2, node.s2))
            else:
                self.outp('%s = self.handle_%s()' % (v2, node.s2))
            self.outp('if not %s:' % v2)
            self.outp('self.restorepos(savpos)', 1)
            self.outp('return %s' % v1, 1)
            if i > 0:
                self.outp('%s = multiop%d(%s)' % (v2,i,v2))
            self.outp('%s = %s_%s(%s, %s, %s)' % (v1, self.prefix, self.curname, v1, s, v2))
            self.ntab -= 2
        self.outp('return multiop%d(%s)' % (i+1, v1))

def DirectToV(node):
    while True:
        if isinstance(node, GDL.LiuD_enclosed):
            node = node.v
            continue
        break
    return node


def Gen02(mod):

    lst, lst_inline, prefix = GetItemList(mod)

    the = cls_Gen02(lst, lst_inline, prefix)
    mod.walkabout(the)
    # print the.outtxt
    return the.outtxt

class cls_Gen03(cls_Gen00):
    def __init__(self, lst, lst_inline, prefix):
        cls_Gen00.__init__(self, lst, lst_inline)
        self.prefix = prefix
        self.curtyp = None
        self.curtypno = 0
        self.ntab = 1
        self.outtxt = '''
class %s_output:
    def __init__(self, outp):
        self.outp = outp
''' % prefix
    def visit_stmt(self, node):
        name = node.s
        if name == 'value0':
            pass

        types = self.get_types(node.v)
        prefix = self.get_prefix(types)
        self.curtyp = (types, prefix)
        self.curtypno = 0

        self.outp('def visit_%s(self, node):' % name)
        #self.outp('pass', 1)
        self.ntab += 1
        node.v.walkabout(self)
        self.ntab -= 1
        #print self.outtxt
        #self.outtxt = ''
    def visit_inline(self, node):
        name = node.s
        if name == 'value0':
            pass

        types = self.get_types(node.v)
        prefix = self.get_prefix(types)
        self.curtyp = (types, prefix)
        self.curtypno = 0

        self.outp('def visit_%s(self, node):' % name)
        #self.outp('pass', 1)
        self.ntab += 1
        node.v.walkabout(self)
        self.ntab -= 1
        #print self.outtxt
        #self.outtxt = ''
    def visit_state1(self, node):
        pass
    def visit_series(self, node):
        #for i,v in enumerate(node.vlst):
        #    if i > 0:
        #        self.outp("self.outp.puts(' ')")
        for v in node.vlst:
            v.walkabout(self)
    def visit_enclosed(self, node):
        node.v.walkabout(self)
        #self.outp("self.outp.outs('(')")
        #self.outp("node.v.walkabout(self)")
        #self.outp("self.outp.outs(')')")
    def visit_itemd(self, node):
        argname = self.curtyp[1][self.curtypno]
        self.curtyp[1][self.curtypno] = '-v'
        sav = self.curtypno
        #self.outp("for i,v in enumerate(node.%s):" % argname)
        self.outp("for v in node.%s:" % argname)
        self.ntab += 1
        #self.outp('if i > 0:')
        #self.outp("self.outp.puts(' ')", 1)
        node.v.walkabout(self)
        self.ntab -= 1
        #self.curtypno += 1
        assert sav + 1 == self.curtypno
    def visit_litname(self, node):
        s = node.s
        if s in self.itemlst:
            argname = self.curtyp[1][self.curtypno]; self.curtypno += 1
            self.outp("%s.walkabout(self)" % getargname(argname))
            return
        if s in self.predefines0:
            if s == 'NEWLINE':
                self.outp('self.outp.newline()')
            elif s == 'IDENT':
                self.outp('self.outp.ident()')
            elif s == 'IDENTIN':
                self.outp('self.outp.identin()')
            elif s == 'IDENTOUT':
                self.outp('self.outp.identout()')
            else:
                assert False
            return
        if s in self.predefines:
            argname = self.curtyp[1][self.curtypno]; self.curtypno += 1
            self.outp('self.outp.puts(%s)' % getargname(argname))
            return
        if s in self.inlinelst:
            argname = self.curtyp[1][self.curtypno]; self.curtypno += 1
            self.outp("%s.walkabout(self)" % getargname(argname))
            return
        assert False

        #self.outp("self.outp.outs('%s')" % node.s)
    def visit_litstring(self, node):
        self.outp("self.outp.puts(%s)" % node.s)
    def visit_string_or(self, node):
        argname = self.curtyp[1][self.curtypno]
        typ = self.curtyp[0][self.curtypno]
        self.curtypno += 1
        if typ == type_s:
            self.outp("self.outp.puts(%s)" % getargname(argname))
        else:
            self.outp("%s.walkabout(self)" % getargname(argname))
    def visit_values_or(self, node):
        argname = self.curtyp[1][self.curtypno]
        typ = self.curtyp[0][self.curtypno]
        self.curtypno += 1
        if typ == type_s:
            self.outp("self.outp.puts(%s)" % getargname(argname))
        else:
            self.outp("%s.walkabout(self)" % getargname(argname))
    def visit_jiap(self, node):
        argname = self.curtyp[1][self.curtypno]
        typ = self.curtyp[0][self.curtypno]
        self.curtypno += 1
        if typ == type_slst:
            s = "' | '.join(node.%s)" % argname
            self.outp("self.outp.puts(%s)" % s)
            return
        assert False
        self.outp("self.outp.outs(' ^+ ')")
        self.outp("self.outp.outs('%s')" % node.s2)
        #s = '%s ^+ %s' % (node.s1, node.s2)
        #self.outs(s)
        #s = ' | '.join(node.slst)
        #self.outp.puts(s)
    def visit_multiop(self, node):
        v1, s, v2 = self.curtyp[1]
        self.outp("node.%s.walkabout(self)" % v1)
        self.outp("self.outp.puts(node.%s)" % s)
        self.outp("node.%s.walkabout(self)" % v2)

def getargname(s):
    if s[0] == '-':
        return s[1:]
    return 'node.%s' % s

def Gen03(mod):
    lst, lst_inline, prefix = GetItemList(mod)

    the = cls_Gen03(lst, lst_inline, prefix)
    mod.walkabout(the)
    # print the.outtxt
    return the.outtxt

def Gen_All(txt):
    the = LiuD_Parser(txt)
    mod = the.handle_main()

    s1 = Gen01(mod)
    s2 = Gen02(mod)
    s3 = Gen03(mod)

    lst = txt.splitlines()
    lst2 = ['# ' + s for s in lst]
    s0 = '\n'.join(lst2)

    s = '''# auto generated

# LiuD syntax :

%s

from GDL_common import *

''' % s0
    s += s1 + s2 + s3
    return s


LiuD_syntax = '''option.prefix = LiuD
states.skip = space
main = (stmt1 NEWLINE)*
stmt1 := options | stmt | inline
inline = NAME ':=' stmt_value
options := option1 | state1
    option1 = 'option.prefix' '=' NAME
    state1 = 'states.skip' '=' NAME
stmt = NAME '=' stmt_value
stmt_value := multiop | values_or | string_or | jiap | series
    values_or = NAME ^+ '|'
    string_or = STRING ^+ '|'
    series = value*
    jiap = NAME '^+' STRING
    multiop = NAME ',' '(,' opstr* ')' NAME
        opstr := litstring | enclosedstrs
        enclosedstrs = '(' STRING* ')'

litname = NAME
litstring = STRING
value1 := litname | litstring | enclosed
    enclosed = '(' stmt_value ')'
value := itemd | value1
    itemd = value1 '*'
'''

syntax_GDL01 = '''option.prefix = GDL01
    states.skip = no
    stmts = (IDENT stmt)*
    deepstmts = IDENTIN stmts IDENTOUT

    states.skip = space
    main = stmts
    stmt := declare_with_value | declare | assign | funccall | if_stmt
    datatype = 'int' | 'long'
    declare = datatype NAME
    declare_with_value = datatype NAME '=' value
    value0 = NUMBER | NAME
    value1 := value0 | enclosed
        enclosed = '(' value ')'
    value2 := signed | value1
        signed = ('-' | '+') value1
    binvalue = value2, (, '**' ('*' '/') ('+' '-') ('>=' '>' '<=' '<' '==' '!=')) value1
    value := binvalue
    assign = NAME '=' value
    funccall = NAME '(' value ')'
    if_stmt = 'if' value ':' deepstmts IDENT else_stmt
    else_stmt = 'else' ':' deepstmts
    '''

import unittest
class Test(unittest.TestCase):
    def test1(self):
        s = Gen_All(LiuD_syntax)

        #open('Ast_LiuD.py', 'w').write(s)
        s2 = open('Ast_LiuD.py').read()
        self.assertEqual(s, s2)

    def test2(self):
        s = Gen_All(syntax_GDL01)
        #open('Ast_C2.py', 'w').write(s)
        s2 = open('Ast_C.py').read()
        self.assertEqual(s, s2)

    def test3(self):
        import Ast_LiuD
        the = Ast_LiuD.LiuD_Parser(LiuD_syntax)
        mod = the.handle_main()

        outp = Ast_LiuD.OutP()
        the2 = Ast_LiuD.LiuD_output(outp)
        mod.walkabout(the2)
        txt = outp.txt
        #print '<%s>' % txt
        txt2 = '''option.prefix = LiuD
states.skip = space
main = ( stmt1 NEWLINE ) *
stmt1 := options | stmt | inline
inline = NAME ':=' stmt_value
options := option1 | state1
option1 = 'option.prefix' '=' NAME
state1 = 'states.skip' '=' NAME
stmt = NAME '=' stmt_value
stmt_value := multiop | values_or | string_or | jiap | series
values_or = NAME ^+ '|'
string_or = STRING ^+ '|'
series = value *
jiap = NAME '^+' STRING
multiop = NAME ',' '(,' opstr * ')' NAME
opstr := litstring | enclosedstrs
enclosedstrs = '(' STRING * ')'
litname = NAME
litstring = STRING
value1 := litname | litstring | enclosed
enclosed = '(' stmt_value ')'
value := itemd | value1
itemd = value1 '*'
'''
        #print '<%s>' % txt2
        #print txt == txt2
        self.assertEqual(txt, txt2)

    def test4(self):
        sample = '''
int i = 22
int j = 3 + i
int k
if j > i:
    k = i - j * 3
    if k <= 0:
        k = -k
    else:
        k = +k
else:
    k =  -(i + j / 2)
print(k)
        '''

        import Ast_C
        the = Ast_C.GDL01_Parser(sample)
        mod = the.handle_main()

        outp = Ast_C.OutP()
        the2 = Ast_C.GDL01_output(outp)
        mod.walkabout(the2)
        txt = outp.txt
        print '<%s>' % txt
        txt2 = '''
int i = 22
int j = 3 + i
int k
if j > i :
     k = i - j * 3
     if k <= 0 :
         k = - k
     else :
         k = + k
else :
     k = - ( i + j / 2 )
print ( k )'''
        self.assertEqual(txt, txt2)


if __name__ == '__main__':
    print 'good'
    #the = Test(methodName='test4')
    #the.test4()

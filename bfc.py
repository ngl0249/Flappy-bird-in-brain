class BF:
    def __init__(s):
        s.code=[]; s.ptr=0; s.vars={}; s.next=0; s.free=[]
    def var(s,name):
        if name not in s.vars:
            s.vars[name]=s.next; s.next+=1
        return s.vars[name]
    def tmp(s):
        if s.free: return s.free.pop()
        c=s.next; s.next+=1; return c
    def rel(s,c): s.free.append(c)
    def mv(s,c):
        d=c-s.ptr; s.code.append('>'*d if d>0 else '<'*(-d)); s.ptr=c
    def emit(s,x): s.code.append(x)
    def clear(s,c): s.mv(c); s.emit('[-]')
    def add(s,c,n):
        n%=256; s.mv(c)
        s.emit('+'*n if n<=128 else '-'*(256-n))
    def setc(s,c,n): s.clear(c); s.add(c,n)
    def loop(s,c,body):
        s.mv(c); s.emit('['); body(); s.mv(c); s.emit(']')
    def addv(s,dst,src,sign=1):
        t=s.tmp()
        def b():
            s.add(src,-1); s.add(dst,sign); s.add(t,1)
        s.loop(src,b)
        s.loop(t,lambda:(s.add(t,-1),s.add(src,1)))
        s.rel(t)
    def subv(s,dst,src): s.addv(dst,src,-1)
    def copy(s,src,dst): s.clear(dst); s.addv(dst,src)
    def ccopy(s,src):
        t=s.tmp(); s.copy(src,t); return t
    def if_(s,cond,body):
        t=s.ccopy(cond)
        s.loop(t,lambda:(body(),s.clear(t)))
        s.rel(t)
    def ifelse(s,cond,a,b):
        t=s.ccopy(cond); e=s.tmp(); s.setc(e,1)
        s.loop(t,lambda:(a(),s.add(e,-1),s.clear(t)))
        s.loop(e,lambda:(b(),s.add(e,-1)))
        s.rel(e); s.rel(t)
    def free_flag(s,f): s.clear(f); s.rel(f)
    def iszero(s,x):
        f=s.tmp(); s.setc(f,1); t=s.ccopy(x)
        s.loop(t,lambda:(s.add(f,-1),s.clear(t)))
        s.rel(t); return f
    def eqc(s,x,n):
        t=s.ccopy(x); s.add(t,-n); f=s.tmp(); s.setc(f,1)
        s.loop(t,lambda:(s.add(f,-1),s.clear(t)))
        s.rel(t); return f
    def eqv(s,a,b):
        t=s.ccopy(a); s.subv(t,b); f=s.tmp(); s.setc(f,1)
        s.loop(t,lambda:(s.add(f,-1),s.clear(t)))
        s.rel(t); return f
    def ltv(s,a,b):
        ta=s.ccopy(a); tb=s.ccopy(b); r=s.tmp(); s.clear(r)
        def body():
            z=s.iszero(ta)
            s.ifelse(z,lambda:(s.setc(r,1),s.clear(tb)),
                       lambda:(s.add(ta,-1),s.add(tb,-1)))
            s.free_flag(z)
        s.loop(tb,body)
        s.clear(ta); s.rel(ta); s.rel(tb); return r
    def ltc(s,a,n):
        t=s.tmp(); s.setc(t,n); r=s.ltv(a,t); s.free_flag(t); return r
    def notf(s,f):
        g=s.tmp(); s.setc(g,1)
        t=s.ccopy(f); s.loop(t,lambda:(s.add(g,-1),s.clear(t))); s.rel(t)
        return g
    def out_str(s,txt):
        o=s.tmp(); s.clear(o); cur=0
        for ch in txt:
            s.add(o,ord(ch)-cur); s.emit('.'); cur=ord(ch)
        s.clear(o); s.rel(o)
    def out_var(s,c): s.mv(c); s.emit('.')
    def read(s,c): s.mv(c); s.emit(',')
    def mod(s,x,n):
        def cond():
            f=s.ltc(x,n); g=s.notf(f); s.free_flag(f); return g
        g=cond()
        def body():
            s.add(x,-n)
            f=s.ltc(x,n); s.clear(g); h=s.notf(f); s.addv(g,h); s.free_flag(h); s.free_flag(f)
        s.loop(g,body); s.rel(g)
    def result(s):
        src=''.join(s.code)
        import re
        prev=None
        while prev!=src:
            prev=src
            src=src.replace('<>','').replace('><','').replace('+-','').replace('-+','')
        return src

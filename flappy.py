from bfc import BF
W,H,GAP,BC,FLAP=20,12,4,4,2
s=BF()
V=lambda n:s.var(n)
one,y,score,seed,k,alive,mode,ch,r,c,rc,cc=[V(n) for n in
 "one y score seed k alive mode ch r c rc cc".split()]
pipes=[(V('p1x'),V('p1g')),(V('p2x'),V('p2g'))]

def rand_gap(g):
    t=s.tmp(); s.copy(seed,t)
    for _ in range(4): s.addv(seed,t)
    s.free_flag(t); s.add(seed,3)
    s.copy(seed,g); s.mod(g,7); s.add(g,1)

def print_num(x):
    n=s.ccopy(x)
    for d in (100,10):
        q=s.tmp(); s.clear(q)
        def cond():
            f=s.ltc(n,d); g=s.notf(f); s.free_flag(f); return g
        g=cond()
        def body():
            s.add(n,-d); s.add(q,1)
            f=s.ltc(n,d); s.clear(g); h=s.notf(f); s.addv(g,h); s.free_flag(h); s.free_flag(f)
        s.loop(g,body); s.rel(g)
        s.add(q,48); s.out_var(q); s.free_flag(q)
    s.add(n,48); s.out_var(n); s.free_flag(n)

def in_pipe_body(px,pg):
    f=s.eqv(c,px)
    def b():
        a=s.ltv(r,pg)
        bot=s.ccopy(pg); s.add(bot,GAP)
        l2=s.ltv(r,bot); s.free_flag(bot)
        n2=s.notf(l2); s.free_flag(l2)
        s.addv(a,n2); s.free_flag(n2)
        s.if_(a,lambda:s.setc(ch,ord('#')))
        s.free_flag(a)
    s.if_(f,b); s.free_flag(f)

def render():
    s.out_str("SCORE "); print_num(score); s.out_str("\n")
    s.clear(r); s.setc(rc,H)
    def row():
        s.clear(c); s.setc(cc,W)
        def col():
            s.setc(ch,32)
            for px,pg in pipes: in_pipe_body(px,pg)
            fb=s.eqc(c,BC)
            def bird():
                fy=s.eqv(r,y); s.if_(fy,lambda:s.setc(ch,ord('@'))); s.free_flag(fy)
            s.if_(fb,bird); s.free_flag(fb)
            s.out_var(ch)
            s.add(c,1); s.add(cc,-1)
        s.loop(cc,col)
        s.out_str("\n"); s.add(r,1); s.add(rc,-1)
    s.loop(rc,row)
    s.out_str("="*W+"\n")
    f1=s.eqc(mode,1); s.if_(f1,lambda:s.out_str("TAP TO FLY")); s.free_flag(f1)
    f2=s.eqc(mode,2); s.if_(f2,lambda:s.out_str("GAME OVER")); s.free_flag(f2)
    s.out_str("\n\f")

def wait_tap():
    s.clear(k); s.setc(alive,1)
    def b():
        render(); s.read(k)
        s.add(seed,1)
        s.if_(k,lambda:s.clear(alive))
    s.loop(alive,b)

def game():
    s.setc(y,5); s.clear(score)
    s.setc(pipes[0][0],W-1); s.setc(pipes[0][1],4)
    s.setc(pipes[1][0],W-1+int(W/2)); rand_gap(pipes[1][1])
    s.setc(mode,1); wait_tap()
    s.clear(mode); s.setc(alive,1)
    def frame():
        s.read(k)
        def flap():
            l=s.ltc(y,FLAP)
            s.ifelse(l,lambda:s.clear(y),lambda:s.add(y,-FLAP))
            s.free_flag(l); s.add(seed,7)
        s.ifelse(k,flap,lambda:s.add(y,1))
        for px,pg in pipes:
            z=s.iszero(px)
            s.if_(z,lambda px=px,pg=pg:(s.setc(px,W),rand_gap(pg)))
            s.free_flag(z); s.add(px,-1)
        l=s.ltc(y,H); n=s.notf(l); s.free_flag(l)
        s.if_(n,lambda:(s.clear(alive),s.setc(y,H-1))); s.free_flag(n)
        for px,pg in pipes:
            f=s.eqc(px,BC)
            def hit(pg=pg):
                a=s.ltv(y,pg)
                bot=s.ccopy(pg); s.add(bot,GAP)
                l2=s.ltv(y,bot); s.free_flag(bot)
                n2=s.notf(l2); s.free_flag(l2)
                s.addv(a,n2); s.free_flag(n2)
                s.if_(a,lambda:s.clear(alive)); s.free_flag(a)
            s.if_(f,hit); s.free_flag(f)
            f=s.eqc(px,BC-1); s.if_(f,lambda:s.add(score,1)); s.free_flag(f)
        f=s.iszero(alive); s.if_(f,lambda:s.setc(mode,2)); s.free_flag(f)
        render()
    s.loop(alive,frame)
    s.setc(mode,2); wait_tap()

s.setc(seed,42); s.setc(one,1)
s.loop(one,game)
src=s.result()
open('flappy.bf','w').write(src)
print(len(src), 'cells used', s.next)
import json
names=['']*s.next
for n,i in s.vars.items(): names[i]=n
json.dump({'src':src,'names':names},open('build.json','w'))

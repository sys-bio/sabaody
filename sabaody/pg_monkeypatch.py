import pygmo as pg

#def de_getstate(self):
    #return {'gen': algorithm.gen,
            #'F': algorithm.F,
            #'CR': algorithm.CR,
            #'variant': algorithm.variant,
            #'ftol': algorithm.ftol,
            #'xtol': algorithm.xtol,
            #'seed': algorithm.seed}
#pg.core.de.__getstate__ = de_getstate

#def de_setstate(self, state):
    #return pg.de(**state)
#pg.core.de.__setstate__ = de_setstate
#pg.core.de.__getstate_manages_dict__ = 1
#def de_getinitargs(self):
    #return ()
#pg.core.de.__getinitargs__ = de_getinitargs
def de_reduce(self):
    return (pg.de, (self.gen,
                    self.F,
                    self.CR,
                    self.variant,
                    self.ftol,
                    self.xtol,
                    self.seed))
pg.core.de.__reduce__ = de_reduce

def silly(self):
    print('silly')
pg.core.de.silly = silly
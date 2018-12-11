from sabaody.timecourse.timecourse_launcher import MemcachedMonitor

class RBRunMCMonitor(MemcachedMonitor):
    '''
    Abstracts some of the logic of setting up a parameter fitting problem.
    Provides information via MC for monitoring.
    '''
    def getDomain(self):
        return 'com.how2cell.sabaody.rb-driver.{}'.format(self.getName())


    def getNameQualifier(self):
        from toolz import partial
        from sabaody import getQualifiedName
        return partial(getQualifiedName, 'rb-driver', self.getName(), str(self.run))

# class RBRun(Evaluator):
#     '''
#     Abstracts some of the logic of setting up a parameter fitting problem.
#     Provides information via MC for monitoring.
#     '''
#     def getName(self):
#         return 'RB'
#
#     def getDomain(self):
#         return 'com.how2cell.sabaody.RB'
#
#     def calculateInitialScore(self):
#         self.initial_score = 0

# def make_problem():
#     import pygmo as pg
#     return pg.problem(pg.rosenbrock(5))

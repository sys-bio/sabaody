from sabaody.timecourse.timecourse_launcher import ProblemSetup

class RBRun(ProblemSetup):
    '''
    Abstracts some of the logic of setting up a parameter fitting problem.
    Provides information via MC for monitoring.
    '''
    def getName(self):
        return 'RB'

    def getDomain(self):
        return 'com.how2cell.sabaody.RB'

    def calculateInitialScore(self):
        self.initial_score = 0

def make_problem():
    import pygmo as pg
    return pg.problem(pg.rosenbrock(5))
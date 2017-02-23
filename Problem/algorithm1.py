import time
import os

#### NOTA: ASEGURARSE DE QUE EXISTA EL DIRECTORIO solutions
class AbstractSolution:
    def readInput(self, fname):
        """ Saves the name of the input file then calls the parse funcion. """
        self.fname=fname.replace('.in','')
        self.parseFile(fname)

    def parseFile(self, fname):
        """ Parse the input file with the problem instance. Needs to be implemented for each problem. """
        raise NotImplementedError

    def saveSolution(self, score=None):
        """
        Saves the current solution to a file based on the score/time of the solution.
        It will save it with the current solution's score, or the score passed as an argument.
        """
        if score is None:
            score = self.scoreSolution()
        output = os.path.join('solutions',self.fname+'_'+str(score)+'.out')
        self.writeSolution(output)

    def writeSolution(self, fname):
        """ Outputs the solution to a given file. Needs to be implemented for each problem. """
        raise NotImplementedError

    def scoreSolution(self):
        """
        Returns the score of the current solution.
        To return the correct score it needs to be implemented for each problem.
        Otherwise, it returns the current time in seconds since whenever.
        """
        return time.time()

    def findSolution(self):
        """
        Solves the problem.
        Either uses an iterative method (some auxiliary funcions need to be implemented),
        or can be implemented for the particular problem.
        """
        self.initialSolution()
        self.saveSolution(0)
        self.max_score = max(0,self.scoreSolution())
        while not self.stopSolution():
            self.iterateSolution()
            score = self.scoreSolution()
            if score > self.max_score:
                self.saveSolution(score)
                self.max_score = score

    def initialSolution(self):
        """ Give a first valid solution to iterate on. """
        raise NotImplementedError

    def iterateSolution(self):
        """ Iterate on current solution for a new (hopefully) better solution. """
        raise NotImplementedError

    def stopSolution(self):
        """ Decide when to stop iterating on the solutions. """
        raise NotImplementedError

    #### LLAMAR A ESTA PARA RESOLVER UN FICHERO .in
    def solveProblem(self, fname):
        """ Solve the problem for a .in file. """
        self.readInput(fname)
        self.findSolution()
        self.saveSolution()

    #### LLAMAR A ESTA PARA RESOLVER TODOS LOS FICHEROS .in
    def solveAll(self):
        """ Solve every .in file in the directory. """
        for f in sorted(os.listdir(),
                        key=lambda x:os.path.getsize(x)):
            if f.endswith('.in'):
                try:
                    print('solving',f)
                    self.solveProblem(f)
                except KeyboardInterrupt:
                    # Allow cut off with ^C
                    pass

class EndPoint:
    def __init__(self, L, K, connections, sorted_connections):
        self.L = L
        self.K = K
        self.c = connections
        self.sc = sorted_connections


class Solution(AbstractSolution):
    #### IMPLEMENTAR FUNCIONES NECESARIAS AQUI

    def parseFile(self, fname):
        f = open(fname)
        self.V, self.E, self.R, self.C, self.X = map(int, f.readline().split())
        self.v_size = list(map(int, f.readline().split()))
        self.ep = []

        # Read the endpoints
        for i in range(0, self.E):
            L, K = map(int, f.readline().split())
            connections = {}
            sorted_connections = []
            for j in range(0, K):
                c, Lc = map(int, f.readline().split())
                connections[c] = Lc
                sorted_connections.append((c,Lc))
            sorted_connections.sort(key=lambda x: x[1])
            self.ep.append(EndPoint(L, K, connections, sorted_connections))


        self.re = []
        for i in range(0, self.R):
            Rv, Re, Rn = map(int, f.readline().split())
            self.re.append((Rv, Re, Rn))


    def writeSolution(self, fname):
        f = open(fname, 'w')
        f.write(str(sum(1 for v in self.solution if v))+'\n')
        for i,v in enumerate(self.solution):
            if v:
                f.write(str(i)+' '+' '.join(map(str, v))+'\n')

    def validSolution(self):
        for v in self.solution:
            if sum(self.v_size[i] for i in v) > self.X:
                return False
        return True

    def initialSolution(self):
        # Empty solution
        self.solution = []
        for _ in range(self.C):
            self.solution.append(set())

        space = [self.X]*self.C
        for v,e,n in sorted(self.re, key=lambda x: x[2], reverse=True):
            cache = -1
            for c,l in self.ep[e].sc:
                if self.v_size[v] < space[c]:
                    cache = c
                    break
            if cache != -1:
                self.solution[cache].add(v)
                space[cache] -= self.v_size[v]

    # def iterateSolution(self):

    def stopSolution(self):
        return True

    def scoreSolution(self):
        if not self.validSolution():
            return -1
        saved = 0
        for v,e,n in self.re:
            ld = lat = self.ep[e].L
            conn = self.ep[e].c
            for c in conn:
                if conn[c] < lat and v in self.solution[c]:
                    lat = conn[c]
            saved += n*(self.ep[e].L - lat)
        return saved

if __name__ == "__main__":
    sol = Solution()
    sol.solveAll()
    #sol.solveProblem('me_at_the_zoo.in')


from time import time
from copy import deepcopy
import os
from random import shuffle
from random import random

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
        self.saveSolution()
        self.max_score = max(0,self.scoreSolution())
        improved = True
        while improved:
            print("Trying to improve...")
            improved = self.iterateSolution()
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
        t0 = time()
        self.findSolution()
        t1 = time()
        print("Time: ", t1-t0)
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
        if not self.validSolution():
            print("The obtained solution is not valid...")

        print("The solution has objective value", self.scoreSolution())    
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
        self.cache_used = [0]*self.C
        for _ in range(self.C):
            self.solution.append(set())

        coeff = random()
        # Sort the request by rn
        self.re.sort(key = lambda x: -x[2] / (1+0.001*coeff*self.v_size[x[0]]))
        # Set with the used videos
        videos = set()
        for r in self.re:
           if r[0] not in videos:
               for pair in self.ep[r[1]].sc:
                   if self.cache_used[pair[0]] + self.v_size[r[0]] <= self.X:
                       self.solution[pair[0]].add(r[0])
                       self.cache_used[pair[0]] += self.v_size[r[0]]
                       videos.add(r[0])
                       break

        # For each cache find the used videos
        self.cache_videos = []
        for _ in range(self.C):
            self.cache_videos.append({})
        for r in self.re:
            for pair in self.ep[r[1]].sc:
                if r[0] not in self.cache_videos[pair[0]]:
                    self.cache_videos[pair[0]][r[0]] = r[2]*(self.ep[r[1]].L - pair[1])
                else:
                    self.cache_videos[pair[0]][r[0]] += r[2]*(self.ep[r[1]].L - pair[1])

        coeff2 = random()
        self.cache_videosl = []
        for _ in range(self.C):
            self.cache_videosl.append([])
        for i in range(0, self.C):
            for x in self.cache_videos[i]:
                self.cache_videosl[i].append((x, self.cache_videos[i][x] / (1 + coeff2*float(self.v_size[x]))))
            #shuffle(self.cache_videosl[i])
            self.cache_videosl[i].sort(key = lambda x: -x[1])

        print("Finished first solution...")
            
        self.improveFirst2()

        print("Improved first time...")
            
    def iterateSolution(self):
        return self.improve()

    def improve(self):
        improved = False
        score = self.scoreSolutionHard()
        for c in range(0, self.C):
            cache = self.solution[c]
            for video, points in self.scorecvl[c]:
                cache.remove(video)
                self.cache_used[c] -= self.v_size[video]
                if self.improveFirst2(-1):
                    print("The solution has been inproved!!!!!")
                    return True
                elif self.scoreSolution() < 0.5*score:
                    cache.add(video)
                    self.cache_used[c] += self.v_size[video]

        print("We haven't improven the solution...")
        return improved        
        
    def improveFirst(self, v = -1):
        improved = False
        score = self.scoreSolution()
        #copy_s = deepcopy(self.solution)
        for c in range(0,self.C):
            cache = self.solution[c]
            for video, points in self.cache_videosl[c]:
                if video != v and video not in cache and self.cache_used[c] + self.v_size[video] <= self.X:
                    cache.add(video)
                    self.cache_used[c] += self.v_size[video]
                    if self.scoreSolution() <= score:
                        self.cache_used[c] -= self.v_size[video]
                        cache.remove(video)
        return improved

    def improveFirst2(self, v = -1):
        improved = False
        score = self.scoreSolution()
        #copy_s = deepcopy(self.solution)
        for r in self.re:
            for pair in self.ep[r[1]].sc:
                if r[0] not in self.solution[pair[0]]:
                    if self.cache_used[pair[0]] + self.v_size[r[0]] <= self.X:
                       self.solution[pair[0]].add(r[0])
                       self.cache_used[pair[0]] += self.v_size[r[0]]
                       break                    
                else:
                    break
                
    def stopSolution(self):
        return True

    def scoreSolution(self):
        self.scorecv = []
        for _ in range(0, self.C):
            self.scorecv.append
        saved = 0
        for v,e,n in self.re:
            ld = lat = self.ep[e].L
            conn = self.ep[e].c
            for c in conn:
                if conn[c] < lat and v in self.solution[c]:
                    lat = conn[c]
            saved += n*(self.ep[e].L - lat)
        return saved    
    
    def scoreSolutionHard(self):
        self.scorecv = []
        self.scorecvl = []
        for _ in range(0, self.C):
            self.scorecv.append({})
            self.scorecvl.append([])

        coeff = random()
        saved = 0
        for v,e,n in self.re:
            ld = lat = self.ep[e].L
            conn = self.ep[e].c
            cb = -1
            for c in conn:
                if conn[c] < lat and v in self.solution[c]:
                    lat = conn[c]
                    cb = c
            saved += n*(self.ep[e].L - lat)
            if v not in self.scorecv[cb]:
                self.scorecv[cb][v] = n*(self.ep[e].L - lat)
            else:
                self.scorecv[cb][v] += n*(self.ep[e].L - lat)

        for c in range(0, self.C):
            cache = self.scorecv[c]
            for video in cache:
                self.scorecvl.append((video, cache[video]))
            self.scorecvl[c].sort(key = lambda x: x[1] / (1+coeff*self.v_size[x[0]]))
                
        return saved

if __name__ == "__main__":
    sol = Solution()
    sol.solveAll()

import time
import os
import random

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
        self.max_score = max(0, self.scoreSolution())
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
        for f in os.listdir():
            if f.endswith('.in'):
                try:
                    print('solving',f)
                    self.solveProblem(f)
                except KeyboardInterrupt:
                    # Allow cut off with ^C
                    pass

class Solution(AbstractSolution):
    #### IMPLEMENTAR FUNCIONES NECESARIAS AQUI
    def parseFile(self, fname):
        f = open(fname)
        self.R, self.C, self.L, self.H = map(int, f.readline().split())
        self.pizza = []
        for row in f:
            self.pizza.append(row.split()[0])

    def writeSolution(self, fname):
        f = open(fname, 'w')
        f.write(str(len(self.slices))+'\n')
        for s in self.slices.values():
            f.write(' '.join((str(s[0]),str(s[2]),str(s[1]-1),str(s[3]-1)))+'\n')

    def initialSolution(self):
        self.slices = dict()
        self.taken = []
        for r in range(self.R):
            row = []
            for c in range(self.C):
                row.append(-1)
            self.taken.append(row)

    def iterateSolution(self):
        r = random.randrange(0, self.R)
        c = random.randrange(0, self.C)
        self.removeSlice(self.taken[r][c])
        s = (r,r,c,c)
        valid = False
        r2,c2 = r+1,c+1
        while r2 < self.R and c2 < self.C and (r2-r)*(c2-c) <= self.H:
            old_s = s
            old_valid = False
            r2 += random.randrange(0,min(self.R - r2+1,self.H-r2+r))
            c2 += random.randrange(0,min(self.C - c2+1,self.H-c2+c))
            s = (r,r2,c,c2)
            valid = self.validSlice(s)
            if not valid and old_valid:
                self.addSlice(old_s)
                return
        if valid:
            self.addSlice(s, True)


    def removeSlice(self, i):
        if i == -1:
            return
        s = self.slices[i]
        del self.slices[i]
        for r in range(s[0],s[1]):
            for c in range(s[2],s[3]):
                self.taken[r][c] = -1

    def addSlice(self, s, valid=None):
        if valid is None:
            valid = self.validSlice(s)
        if not valid:
            return
        # Remove overlapping slices first
        for o in self.overlapSlice(s):
            self.removeSlice(o)

        i = self.unusedKey()
        for r in range(s[0],s[1]):
            for c in range(s[2],s[3]):
                self.taken[r][c] = i
        self.slices[i] = s

    def unusedKey(self):
        array = list(self.slices)
        N = len(array)
        # Pass 1, move every value to the position of its value
        for cursor in range(N):
            target = array[cursor]
            while target < N and target != array[target]:
                new_target = array[target]
                array[target] = target
                target = new_target

        # Pass 2, find first location where the index doesn't match the value
        for cursor in range(N):
            if array[cursor] != cursor:
                return cursor
        return N

    def validSlice(self, s):
        count = {'T':0,'M':0}
        for r in range(s[0],s[1]):
            for c in range(s[2],s[3]):
                count[self.pizza[r][c]] += 1
        return (count['T'] >= self.L and count['M'] >= self.L and
                count['T'] + count['M'] <= self.H)

    def overlapSlice(self, s):
        ol = set()
        for r in range(s[0],s[1]):
            for c in range(s[2],s[3]):
                ol.add(self.taken[r][c])
        return ol

    def stopSolution(self):
        try:
            self.iters += 1
        except AttributeError:
            self.iters = 1
        return (self.iters > self.R*self.C*10 or
                self.max_score == self.R*self.C)

    def scoreSolution(self):
        score = 0
        for s in self.slices.values():
            score += abs((s[0]-s[1])*(s[2]-s[3]))
        return score


if __name__ == "__main__":
    sol = Solution()
    sol.solveAll()
    #sol.solveProblem('example.in')

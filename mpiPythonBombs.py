#!/usr/bin/env python3
from mpi4py import MPI
import sys
import string
import copy
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

def isInRange(target, bomb):
    return (bomb['x'] - bomb['r'] <= target['x'] and
        bomb['x'] + bomb['r'] >= target['x'] and
        bomb['y'] - bomb['r'] <= target['y'] and
        bomb['y'] + bomb['r'] >= target['y'])

def processHit(target, bomb):
    if (target['s'] < 0):
        target['s'] += bomb['s']
        if target['s'] > 0:
            target['s'] = 0
    if (target['s'] > 0):
        target['s'] -= bomb['s']
        if target['s'] < 0:
            target['s'] = 0

def throwBombsOnTargets(targets, bombs):
    for bomb in bombs:
        for target in targets:
            if (isInRange(target, bomb)):
                processHit(target, bomb)

def calculateEffectOfThrow(targets, originalTargets):
    result = {'mtd':0,
              'mtpd':0,
              'mtnt':0,
              'ctd':0,
              'ctpd':0,
              'ctnt':0}
    for i in range(len(targets)):
        if(originalTargets[i]['s'] < 0):
            if (targets[i]['s'] == 0):
                result['mtd'] += 1
            elif (targets[i]['s'] == originalTargets[i]['s']):
                result['mtnt'] += 1
            else:
                result['mtpd'] += 1
        if(originalTargets[i]['s'] > 0):
            if (targets[i]['s'] == 0):
                result['ctd'] += 1
            elif (targets[i]['s'] == originalTargets[i]['s']):
                result['ctnt'] += 1
            else:
                result['ctpd'] += 1
    return result

def sumResults(results):
    total = {'mtd':0,
              'mtpd':0,
              'mtnt':0,
              'ctd':0,
              'ctpd':0,
              'ctnt':0}
    for r in results:
        total['mtd'] += r['mtd']
        total['mtpd'] += r['mtpd']
        total['mtnt'] += r['mtnt']
        total['ctd'] += r['ctd']
        total['ctpd'] += r['ctpd']
        total['ctnt'] += r['ctnt']
    print('Military Targets totally destroyed:', total['mtd'])
    print('Military Targets partially destroyed:', total['mtpd'])
    print('Military Targets not affected:', total['mtnt'])
    print('Civilian Targets totally destroyed:', total['ctd'])
    print('Civilian Targets partially destroyed:', total['ctpd'])
    print('Civilian Targets not affected:', total['ctnt'])

def chunks(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0
    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out

def readTarget(line):
    l = line.split(' ')
    return {'x': int(l[0]), 'y': int(l[1]), 's': int(l[2])}

def readBomb(line):
    l = line.split(' ')
    return {'x': int(l[0]), 'y': int(l[1]), 'r':int(l[2]), 's': int(l[3])}

if rank == 0:
    startTime = time.time()
    file = open(sys.argv[1], "r")

    size = int(file.readline())
    numberOfTargets = int(file.readline())

    targets = []
    for i in range(numberOfTargets):
        t = readTarget(file.readline())
        targets.append(t)

    numberOfBombs = int(file.readline())
    bombs = []
    for i in range(numberOfBombs):
        b = readBomb(file.readline())
        bombs.append(b)

    numberOfWorkers = comm.Get_size()
    numberOfWorkers -= 1
    targetsInChunks = chunks(targets, numberOfWorkers)

    comm.bcast(bombs, root=0)
    for i in range(numberOfWorkers):
        comm.send(targetsInChunks[i], dest=i+1, tag=i+1)

    results = []
    for i in range(numberOfWorkers):
        r = comm.recv(source=i+1, tag=i+1)
        results.append(r)
    sumResults(results)
    print("%s seconds" % (time.time() - startTime))
else:
    bombs = None
    bombs = comm.bcast(bombs, root=0)
    targets = None
    targets = comm.recv(source=0, tag=rank)
    targetsBackup = []
    for t in targets:
        t2 = copy.deepcopy(t)
        targetsBackup.append(t2)
    print(rank, "lanzando", len(bombs), "en", len(targets), "objetivos")
    throwBombsOnTargets(targets, bombs)
    print(rank, "lanze todas", len(bombs), "en", len(targets), "objetivos")
    r = calculateEffectOfThrow(targets, targetsBackup)
    comm.send(r, dest=0, tag=rank)

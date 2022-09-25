# -*- coding: utf-8 -*-
"""PI II.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17Jzd0mmp9xhYkQ5l2EZutpn9sWs81_CM
"""

#Importe de las librerías requeridas
import copy
import numpy as np
import random
import math
import pandas as pd

#Lectura de los datos
with open('bp50-03.txt','r') as f:
  data=[[num for num in line.split(' ')] for line in f]
indexes_to_be_removed = [0, 1,3, len(data)-2]
data=[data[i] for i in range(len(data)) if i not in indexes_to_be_removed ]
data=[[int(num) for num in lista] for lista in data]
infoJobs=data.pop(0)
maq=data.pop(len(data)-1)
jobs=data

numMaq=2

#Primer paso: Se ordenan las tareas de forma ascendente respecto R_i
jOrd=sorted(jobs, key=lambda x: x[1])
seq= [i[0] for i in jOrd]

#Función auxiliar que calcula la función objetivo del problema
def funObj(lista,jobs):
  ter= jobs[lista[0]-1][1]+jobs[lista[0]-1][3]
  for i in range(1, len(lista)):
    if ter>=jobs[lista[i]-1][1]:
      ter=ter+jobs[lista[i]-1][3]
    else:
      ter=jobs[lista[i]-1][1]+jobs[lista[i]-1][3]
  return ter

#Función auxiliar que realiza las combinatorias de las tareas a realizar y retorna la mejor
def combinatorias(ordenActual,nuevaT,jOrd,jobs):
  mejorOrd=copy.deepcopy(ordenActual)
  mejorOrd.insert(0,nuevaT)
  mej=funObj(mejorOrd,jobs)
  for i in range(1,len(ordenActual)+1):
    combinacion=copy.deepcopy(ordenActual)
    combinacion.insert(i,nuevaT)
    funObjAc=funObj(combinacion,jobs)
    if funObjAc<=mej:
      mejorOrd=combinacion
      mej=funObjAc
  return mejorOrd,mej

#Método auxiliar que realiza la asignación de tareas y determina en qué máquina se realiza
def asignacionT(jOrd,jobs):
  tareas= [[],[]]
  tareas[0].append(jOrd[0][0])
  for i in range(1,len(jOrd)):
    nuevaT= jOrd[i][0]
    combiM1, funObjM1= combinatorias(tareas[0],nuevaT,jOrd,jobs)
    combiM2, funObjM2= combinatorias(tareas[1],nuevaT,jOrd,jobs)
    if funObjM1<= funObjM2:
      tareas[0]= combiM1
    else:
      tareas[1]= combiM2

  return tareas, max(funObj(tareas[0], jobs),funObj(tareas[1], jobs))

"""###Algoritmo profesor"""

def split(jOrd,seq,numM):
  tamaños=[line[2] for line in jOrd]
  if numM==1:
    ss=seq
  else:
    k=0
    sP= np.cumsum(tamaños)
    ss=[[] for i in range(numMaq)]
    for i in range(len(seq)-numMaq):
      if sP[i] >= int(sP[len(seq)-1]/numMaq):
        ss[0]= seq[0:i]
        k=i
        break     
    h=1
    for i in range(k+1,len(seq)):
      if h== numMaq-1:
        break
      if sP[i]-sP[k]>= int((sP[len(seq)-1]-sP[k])/(numMaq-h)):
        ss[h] = seq[k:i+1]
        h+=1
        k=i  
    ss[h] = seq[k:len(seq)]
  return ss

def tiempoBatch(lista,jobs):
  tInicio= [jobs[i-1][1] for i in lista]
  duracion=[jobs[i-1][3] for i in lista]
  return max(tInicio), max(duracion)

def batches(sec,jobs,maq):
  batch=[sec[0]]
  capB=jobs[sec[0]-1][2]
  tIniB, dur=tiempoBatch(batch,jobs)
  tProc= tIniB+dur
  batches=[]
  for i in range(1,len(sec)):
    tAct=sec[i]
    tProcAct=jobs[tAct-1][3]
    tam=jobs[tAct-1][2]
    tIniAct=jobs[tAct-1][1]
    if capB+tam<=maq[1]:
      if tProc+tProcAct>=max(tIniAct,tIniB) + max(tProcAct,dur):
        batch.append(tAct)
        capB+=tam
        tProc=max(tIniAct,tIniB) + max(tProcAct,dur)
        tIniB, dur=tiempoBatch(batch,jobs)
        tProc= tIniB+dur
      else:
        batches.append(batch)
        batch=[tAct]
        capB=tam
        tIniB,dur=tiempoBatch(batch,jobs)
        tProc= tIniB+dur
    else:
      batches.append(batch)
      batch=[tAct]
      capB=tam
      tIniB,dur=tiempoBatch(batch,jobs)
      tProc= tIniB+dur
  batches.append(batch)
    
  return batches

sec=split(jOrd,seq,numMaq)
batchesMaq= [batches(sec[i],jobs,maq) for i in range(len(sec))]

"""### Primero batches, luego máquinas"""

def funObjOrden(batchesMaq, jobs):
  term=0
  for j in batchesMaq:
    if len(j)==1:
      if term>=jobs[j[0]-1][1]:
        term += jobs[j[0]-1][3]
      else: 
        term = jobs[j[0]-1][1]+jobs[j[0]-1][3]
    else: 
      riBatchs= [jobs[k-1][1] for k in j]
      diBatchs= [jobs[k-1][3] for k in j] 
      if term>= max(riBatchs):
        term += max(riBatchs) 
      else: 
        term = max(riBatchs) + max(diBatchs)
  return term

def funObjCompleta(batchesM,jobs):
  lista= [funObjOrden(batchesM[i], jobs) for i in range(len(batchesM))]
  return lista, max(lista)

def asignacionBatches(jobs,seq,numMaq):
  batchesMaq= batches(seq,jobs,maq) 
  asignaciones=[[] for i in range(numMaq)]
  asignaciones[0].append(batchesMaq[0])

  for i in range(1, len(batchesMaq)):
    aux= copy.deepcopy(asignaciones)
    for j in aux:
      j.append(batchesMaq[i])
    funObjB, max= funObjCompleta(aux,jobs)
    mejorOpcion= np.argmin(funObjB)
    asignaciones[mejorOpcion]= aux[mejorOpcion]

  funObjs, maxFunObj = funObjCompleta(asignaciones,jobs)
  return asignaciones , funObjs, maxFunObj

asignacionBatches(jobs,seq,numMaq)

"""Soluciones aleatorias"""

def randomOrd(jobs):
 jobsP=copy.deepcopy(jobs)
 random.shuffle(jobsP)
 return jobsP

def ruidoOrd(jobs,a):
  jobsP=copy.deepcopy(jobs)
  for i in range(len(jobsP)):
    jobsP[i][1]+=random.randint(-a, a)
  jRu=sorted(jobsP, key=lambda x: x[1])
  return jRu

sec1=split(randomOrd(jobs),seq,numMaq)
batchesMaq1= [batches(sec1[i],jobs,maq) for i in range(len(sec1))]
lista= [funObjOrden(batchesMaq1[i], jobs) for i in range(len(batchesMaq1))]
print(lista, max(lista))
batchesMaq1

sec=split(jOrd,seq,numMaq)
batchesMaq= [batches(sec[i],jobs,maq) for i in range(len(sec))]
lista= [funObjOrden(batchesMaq[i], jobs) for i in range(len(batchesMaq))]
print(lista, max(lista))
batchesMaq

sec2=split(ruidoOrd(jobs,50),seq,numMaq)
batchesMaq2= [batches(sec2[i],jobs,maq) for i in range(len(sec2))]
lista= [funObjOrden(batchesMaq2[i], jobs) for i in range(len(batchesMaq2))]
print(lista, max(lista))
batchesMaq2

"""Split Ana Maria"""

def splitA(seq,jobs,maq):
  sec= copy.deepcopy(seq)
  sec.insert(0,0)
  jobs_c= copy.deepcopy(jobs)
  jobs_c.insert(0,[0,0,0,0])
  n=len(sec)
  V=[100000 for i in range(n)]
  V[0]=0
  I=np.zeros(n)

  for i in range(n-1):
    L,C,P,R=0,0,0,0
    j=i
    while j<n-1 and L+jobs_c[sec[j+1]][2]<=maq[1]:
      
      j+=1;
      L+=jobs_c[sec[j]][2]
      if P<jobs_c[sec[j]][3]:
        P=jobs_c[sec[j]][3]
      if R<jobs_c[sec[j]][1]:
        R=jobs_c[sec[j]][1]
      if R>V[i]:
        C=R+P
      else:
        C=V[i]+P
      if V[j]>C:
         V[j]=C
         I[j]=i
         i=i
  return V[-1],V,I
splitA(rs,jobs,maq)

def convertirB(I,seq):
  colI=[int(x) for x in I]
  coI= copy.deepcopy(colI)
  coI.pop(0)
  coI= np.array(coI)
  seq=np.array(seq)
  batches=[]
  i= int(len(coI)-1)
  while i>=0:
    int(coI[i])
    print(coI[i], i)
    seq[coI[i]:i+1]
    batches.append(list(seq[coI[i]:i+1]))
    print(batches)
    i=coI[i]-1 
  return batches

UB= 300

def two_level_split(seq, jobs,numMaq,maq,UB):
  V= [math.inf for i in range(len(seq)+1)]
  W= [math.inf for i in range(len(seq)+1)]
  V[0]=0
  W[0]=0
  C= np.ones((len(V),len(V)))*math.inf
  np.fill_diagonal(C,0)
  Ck= np.zeros((len(V),len(V)))
  P = np.zeros((numMaq,len(seq)+1))
  for k in range(1,numMaq+1):
    i= k-1
    while W[i] <= UB and i<len(seq):
      for j in range(i+1,len(seq)+1):
        if C[i][j-1] <= UB:
          if Ck[i][j] == 0:
             C[i][j],_,_ = splitA(seq[i:j],jobs,maq)
             Ck[i][j] = 1
          if max(W[i],C[i][j])<V[j]:
              V[j]=max(W[i],C[i][j])
              P[k-1][j] = i
        else:
          break
      i+=1
    for i in range(len(seq)+1):
      W[i]=V[i]

  return V[-1],P,V

two_level_split(rs,jobs,numMaq,maq,5000)

rs= randomOrd(seq)
rs

for i in range(len(seq)):
  for j in range(i+1,len(seq)):
    copSeq= copy.deepcopy(seq)
    copSeq[i]= seq[j]
    copSeq[j]= seq[i]
    fObj,_,_= two_level_split(copSeq,jobs,numMaq,maq,5000)
    print(fObj)

n= 1000
listSeq=[]
listfunObjs=[]
for i in range(n):
  seqAl= randomOrd(seq)
  listSeq.append(seqAl)
  funObj,_,_= two_level_split(seqAl,jobs,numMaq,maq,5000)
  listfunObjs.append(funObj)

numMejores=10
mejorObj,mejoresSeq= zip(*sorted(zip(listfunObjs,listSeq))) 
mejorObj= mejorObj[0:10]
mejoresSeq= mejoresSeq[0:10]

mejorObj

mejoresSeq[0]

seq

seqc= copy.deepcopy(seq)
index= seqc.index(mejoresSeq[0][0])
seqc[0]= seq[index]
seqc[index]= seq[0] 
f,_,_ = two_level_split(seqc,jobs,numMaq,maq,5000)
f

seqc= copy.deepcopy(seq)
index= seqc.index(mejoresSeq[0][0])
seqc[0:len(seq)-index]= seq[index:len(seq)]
seqc[len(seq)-index:len(seq)]= seq[0:index]
f,_,_ = two_level_split(seqc,jobs,numMaq,maq,5000)
f


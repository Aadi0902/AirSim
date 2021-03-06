# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 20:29:52 2020

@author: amk170930
"""
import numpy as np
import matrixmath
from airsim import Vector3r
import scipy
import control

def gainMatrix(Ts = 0.1, max_angular_vel = 6393.667 * 2 * np.pi / 60):

    m = 1 # Mass
    inertia_mat = np.array([[0.00234817178, 0, 0],
                            [0,0.00366767193,0],
                            [0,0,0.00573909376]])

    I = Vector3r(inertia_mat[0,0],inertia_mat[1,1],inertia_mat[2,2])
    d = 0.2275 # Center to rotor distance
    cT = 0.109919
    air_density = 1.225
    propeller_diameter = 0.2286
    cT = cT * air_density * (propeller_diameter**4)
    cQ = 1.3/4
    g = 9.8
    
    pwmHover = 0.5937
    sq_ctrl_hover = (pwmHover * max_angular_vel)**2
    cT = m*g/(4*sq_ctrl_hover)
    
    A = np.array([[0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                  [0, 0, 0, 0,-g, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, g, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
    
    Gamma = np.array([[cT ,    cT,   cT ,    cT],
                      [-d*cT,   0,  d*cT,     0],
                      [0  , -d*cT,    0 ,  d*cT],
                      [-cQ ,  cQ ,   -cQ,    cQ]])
    
    B = np.dot(np.array([[0,   0,   0,   0,   0,   0,   0,   0,  1/m,   0 ,   0 ,     0],
                         [0,   0,   0,   0,   0,   0,   0,   0,   0 , 1/I.x_val,   0 ,     0],
                         [0,   0,   0,   0,   0,   0,   0,   0,   0 ,   0 , 1/I.y_val,     0],
                         [0,   0,   0,   0,   0,   0,   0,   0,   0 ,   0 ,   0 ,   1/I.z_val]
                         ]).T,Gamma)
    
    C = np.identity(12)
    D = np.zeros((12,4))
   
    u_bar = np.dot(np.linalg.inv(Gamma),[[m*g],
                                         [0],
                                         [0],
                                         [0]])           
   
    Q = np.identity(12)
    R = np.identity(4)
    N = np.zeros((12,4))
   
    sys = scipy.signal.lti(A,B,C,D)
    sysd = scipy.signal.cont2discrete((sys.A,sys.B,sys.C,sys.D),Ts)
    dlqr = matrixmath.dare_gain(sysd[0],sysd[1], Q, R)
    #sys = control.matlab.StateSpace(A,B,C,D)
    #sysd = control.matlab.c2d(sys,Ts)
    #dlqr = matrixmath.dare_gain(sysd.A, sysd.B, Q, R)
    K = -dlqr[1]
    print(K)
    return(K, u_bar)
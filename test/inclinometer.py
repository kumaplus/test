# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import smbus
import math
from time import sleep
import csv
import os

f_path = "data.csv"
if os.path.exists(f_path) == True:
    os.remove(f_path)

GPIO.setmode(GPIO.BCM)

GPIO.setup(25, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
p0 = GPIO.PWM(25, 50)
p1 = GPIO.PWM(24, 50)
p2 = GPIO.PWM(23, 50)
p3 = GPIO.PWM(22, 50)
p0.start(0)
p1.start(0)
p2.start(0)
p3.start(0)

DEV_ADDR = 0x68

ACCEL_XOUT = 0x3b
ACCEL_YOUT = 0x3d
ACCEL_ZOUT = 0x3f
TEMP_OUT = 0x41
GYRO_XOUT = 0x43
GYRO_YOUT = 0x45
GYRO_ZOUT = 0x47

PWR_MGMT_1 = 0x6b
PWR_MGMT_2 = 0x6c   

sample_num = 100
meas_interval = 0.01
theta_mean = 0
theta_variance = 0
theta_dot_mean = 0
theta_dot_variance = 0

theta_update_freq = 400
theta_update_interval = 1.0 / theta_update_freq
theta_data_predict = [[0.0 for i in range(1)] for j in range(2)]
theta_data = [[0.0 for i in range(1)] for j in range(2)]
P_theta_predict = [[0.0 for i in range(2)] for j in range(2)]
P_theta = [[0.0 for i in range(2)] for j in range(2)] 
A_theta = [[1.0, -theta_update_interval],[0.0,1.0]]
B_theta = [[theta_update_interval],[0.0]]
C_theta = [[1.0,0.0]]

bus = smbus.SMBus(1)
bus.write_byte_data(DEV_ADDR, PWR_MGMT_1, 0)


def read_word(adr):
    try:
        high = bus.read_byte_data(DEV_ADDR, adr)
        low = bus.read_byte_data(DEV_ADDR, adr+1)
        val = (high << 8) + low
    except IOError:
        print("IOError")
        val = 0
        pass
    
    return val

# Sensor data read
def read_word_sensor(adr):
    val = read_word(adr)
    if (val >= 0x8000):         # minus
        return -((65535 - val) + 1)
    else:                       # plus
        return val

def get_temp():
    temp = read_word_sensor(TEMP_OUT)
    x = temp / 340 + 36.53      # data sheet(register map)記載の計算式.
    return x

def getGyro():
    x = read_word_sensor(GYRO_XOUT)/ 131.0
    y = read_word_sensor(GYRO_YOUT)/ 131.0
    z = read_word_sensor(GYRO_ZOUT)/ 131.0
    return [x, y, z]

def getAccel():
    x = read_word_sensor(ACCEL_XOUT)/ 16384.0
    y= read_word_sensor(ACCEL_YOUT)/ 16384.0
    z= read_word_sensor(ACCEL_ZOUT)/ 16384.0
    return [x, y, z]

def calc_slope_for_accel_3axis_deg(x, y, z): # degree
    # θ（シータ）
    theta = math.atan( x / math.sqrt( y*y + z*z ) )
    # Ψ（プサイ）
    psi = math.atan( y / math.sqrt( x*x + z*z ) )
    # Φ（ファイ）
    #phi = math.atan( math.sqrt( x*x + y*y ) / z )
    phi = 0 

    deg_theta = math.degrees( theta )
    deg_psi   = math.degrees( psi )
    deg_phi   = math.degrees( phi )
    return [deg_theta, deg_psi, deg_phi]

def calc_theta_deg(x, y, z):
    theta_deg = 0
    if y != 0:  
        theta_deg = math.degrees(math.atan( z / y))
    return theta_deg

def acc_init():
    global theta_variance
 
    #theta_array = [0] * sample_num
    theta_array = [[0.0 for i in range(1)] for j in range(sample_num)]
    for i in range(sample_num):
        ax, ay, az = getAccel()
        theta = calc_theta_deg(ax,ay,az)
        theta_array[i] = theta 
        sleep(meas_interval)

    theta_mean = 0
    for i in range(sample_num):
        theta_mean += theta_array[i]
    theta_mean /= sample_num

    temp = 0
    for i in range(sample_num):
        temp = theta_array[i] - theta_mean
        theta_variance += temp*temp
    theta_variance /= sample_num

def gyro_init():
    global theta_dot_variance
 
    #theta_dot_array = [0] * sample_num
    theta_dot_array  = [[0.0 for i in range(1)] for j in range(sample_num)]
    for i in range(sample_num):
        gx, gy, gz = getGyro()
        theta_dot_array[i] = gx 
        sleep(meas_interval)

    theta_dot_mean = 0
    for i in range(sample_num):
        theta_dot_mean += theta_dot_array[i]
    theta_dot_mean /= sample_num

    temp = 0
    for i in range(sample_num):
        temp = theta_dot_array[i] - theta_dot_mean
        theta_dot_variance += temp*temp
    theta_dot_variance /= sample_num

def mat_tran(m1, sol, row_original, column_original):
    for i in range(row_original):
        for j in range(column_original):
            k=j*row_original+i
            sol[j][i] = m1[i][j] 
            
def mat_mul(m1, m2, sol, row1, column1, row2, column2):
    for i in range(row1):
        for j in range(column2):
            sol[i][j] = 0
            for k in range(column1):
                sol[i][j] += m1[i][k]*m2[k][j]  

def mat_mul_const(m1, c, sol, row, column):
    for i in range(row):
        for j in range(column):
            sol[i][j] = c * m1[i][j]

def mat_add(m1, m2, sol, row, column):
    for i in range(row):
        for j in range(column):
            sol[i][j] = m1[i][j] + m2[i][j]
    
def mat_sub(m1, m2, sol, row, column):
    for i in range(row):
        for j in range(column):
            sol[i][j] = m1[i][j] - m2[i][j]

def update_theta():
    global P_theta_predict
    global theta_variance
    global theta_data_predict
    global theta_data
    global theta_dot_variance
    global A_theta

    ax, ay, az = getAccel()
    theta = calc_theta_deg(ax,ay,az)

    gx, gy, gz = getGyro()
    theta_dot_gyro = gx 

    P_CT = [[0.0 for i in range(1)] for j in range(2)]
    tran_C_theta = [[0.0 for i in range(1)] for j in range(2)]
    mat_tran(C_theta, tran_C_theta, 1, 2)
    mat_mul(P_theta_predict, tran_C_theta, P_CT, 2, 2, 2, 1)
    G_temp1  = [[0.0 for i in range(1)] for j in range(1)]
    mat_mul(C_theta, P_CT, G_temp1, 1, 2, 2, 1)
    G_temp2 = 1 / (G_temp1[0][0] + theta_variance)
    G = [[0.0 for i in range(1)] for j in range(2)]
    mat_mul_const(P_CT, G_temp2, G, 2, 1) 
    
    C_theta_theta  = [[0.0 for i in range(1)] for j in range(1)]
    mat_mul(C_theta, theta_data_predict, C_theta_theta, 1, 2, 2, 1)
    delta_y = theta - C_theta_theta[0][0]
    delta_theta  = [[0.0 for i in range(1)] for j in range(2)]
    mat_mul_const(G, delta_y, delta_theta, 2, 1)
    mat_add(theta_data_predict, delta_theta, theta_data, 2, 1)

    GC = [[0.0 for i in range(2)] for j in range(2)]
    I2 = [[1.0,0.0],[0.0,1.0]]
    mat_mul(G, C_theta, GC, 2, 1, 1, 2)
    I2_GC = [[0.0 for i in range(2)] for j in range(2)]
    mat_sub(I2, GC, I2_GC, 2, 2)
    mat_mul(I2_GC, P_theta_predict, P_theta, 2, 2, 2, 2)

    A_theta_theta  = [[0.0 for i in range(1)] for j in range(2)]
    B_theta_dot  = [[0.0 for i in range(1)] for j in range(2)]
    mat_mul(A_theta, theta_data, A_theta_theta, 2, 2, 2, 1)
    mat_mul_const(B_theta, theta_dot_gyro, B_theta_dot, 2, 1)
    mat_add(A_theta_theta, B_theta_dot, theta_data_predict, 2, 1)

    AP = [[0.0 for i in range(2)] for j in range(2)]
    APAT = [[0.0 for i in range(2)] for j in range(2)]
    tran_A_theta = [[0.0 for i in range(2)] for j in range(2)]
    mat_tran(A_theta, tran_A_theta, 2, 2)
    mat_mul(A_theta, P_theta, AP, 2, 2, 2, 2)
    mat_mul(AP, tran_A_theta, APAT, 2, 2, 2, 2)
    BBT = [[0.0 for i in range(2)] for j in range(2)]
    tran_B_theta = [[0.0 for i in range(2)] for j in range(1)]
    mat_tran(B_theta, tran_B_theta, 2, 1)
    mat_mul(B_theta, tran_B_theta, BBT, 2, 1, 1, 2)
    BUBT = [[0.0 for i in range(2)] for j in range(2)]
    mat_mul_const(BBT, theta_dot_variance, BUBT, 2, 2)
    mat_add(APAT, BUBT, P_theta_predict, 2, 2)

def write_csv(list):
    with open(f_path, 'a') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(list)

if __name__ == '__main__':
    acc_init()
    gyro_init()

    theta_data_predict[0][0] = 0
    theta_data_predict[1][0] = theta_dot_mean

    P_theta_predict[0][0] = 1  
    P_theta_predict[0][1] = 0  
    P_theta_predict[1][0] = 0  
    P_theta_predict[1][1] = theta_dot_variance

    while 1:
        update_theta()
        print("theta = " + str(theta_data[0][0]))
        ax, ay, az = getAccel()
        theta = calc_theta_deg(ax,ay,az)

        list = []
        list.append(theta_data[0][0])
        list.append(theta)
        write_csv(list)
        sleep(0.05) 
